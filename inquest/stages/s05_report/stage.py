"""S05 deterministic incident reporting from saved S00–S04 artifacts."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from inquest.contracts import (ConfidenceEstimate, EvidenceTimelineItem, IncidentCandidate, IncidentHeadline,
    IncidentReport, ReportStatement, RunnerUpFinding, StageInput, StageResult, StageStatus)
from inquest.core.artifacts import read_json, write_json, write_text
from inquest.core.context import RunContext
from inquest.core.vault import read_vault_ids
from .confidence import confidence_level, extract_features, load_model, predict_probability, rule_confidence_level

FOOTER = "Evidence is from synthetic scenarios only."
STAGE_ORDER = {"s00_ingest": 0, "s01_vault": 1, "s02_signals": 2, "s03_candidates": 3, "s04_verify": 4}


def _artifact(ctx: RunContext, stage: str) -> dict[str, Any]:
    matches = sorted(ctx.runs_dir.joinpath(ctx.run_id).glob(f"*_{stage}/output.json"))
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected one saved {stage} output, found {len(matches)}")
    return read_json(matches[0]).get("output", {})


def _evidence_or_fallback(ids: list[str], fallback: list[str], vault_ids: set[str]) -> list[str]:
    valid = sorted(set(ids) & vault_ids)
    if valid:
        return valid
    valid_fallback = sorted(set(fallback) & vault_ids)
    if valid_fallback:
        return valid_fallback
    if vault_ids:
        return [min(vault_ids)]
    raise ValueError("S05 cannot cite a report statement because the verified vault is empty")


def _stmt(text: str, ids: list[str], fallback: list[str], vault_ids: set[str]) -> ReportStatement:
    return ReportStatement(text=text, evidence_ids=_evidence_or_fallback(ids, fallback, vault_ids))


def _all_report_evidence(value: Any) -> set[str]:
    if isinstance(value, dict):
        found=set(value.get("evidence_ids", []))
        for child in value.values():
            found.update(_all_report_evidence(child))
        return found
    if isinstance(value, list):
        found=set()
        for child in value: found.update(_all_report_evidence(child))
        return found
    return set()


def _timeline(s00: dict[str, Any], s02: dict[str, Any], fallback: list[str], vault_ids: set[str]) -> list[EvidenceTimelineItem]:
    bundle = s02.get("bundle", {})
    metrics = bundle.get("metrics", [])
    analysis = s02.get("analysis", {})
    items: list[EvidenceTimelineItem] = []
    for onset in analysis.get("onsets", []):
        matched = [point for point in metrics if point.get("service") == onset.get("service") and point.get("metric") == onset.get("metric")]
        evidence: list[str] = []
        if matched:
            onset_time = datetime.fromisoformat(onset["onset_time"].replace("Z", "+00:00"))
            distance = min(abs((datetime.fromisoformat(point["timestamp"].replace("Z", "+00:00")) - onset_time).total_seconds()) for point in matched)
            evidence = [point["id"] for point in matched if abs((datetime.fromisoformat(point["timestamp"].replace("Z", "+00:00")) - onset_time).total_seconds()) == distance]
        evidence = _evidence_or_fallback(evidence, fallback, vault_ids)
        items.append(EvidenceTimelineItem(timestamp=datetime.fromisoformat(onset["onset_time"].replace("Z", "+00:00")), kind="metric_onset", service=onset.get("service"),
            summary=f"{onset.get('metric')} onset (detector confidence {float(onset.get('confidence', 0)):.3f}).", evidence_ids=evidence))
    for change in s02.get("bundle", {}).get("changes", []):
        kind = str(change.get("kind", "change"))
        evidence = _evidence_or_fallback([str(change.get("id", ""))], fallback, vault_ids)
        timestamp = datetime.fromisoformat(change["timestamp"].replace("Z", "+00:00")) if change.get("timestamp") else None
        change_ref = change.get("change_id")
        summary = f"{kind} event" + (f" ({change_ref})" if change_ref else "") + "."
        items.append(EvidenceTimelineItem(timestamp=timestamp, kind="change", service=change.get("service"), summary=summary, evidence_ids=evidence))
    for event in s02.get("bundle", {}).get("logs", []):
        if event.get("attributes", {}).get("alert_emission") is not True:
            continue
        evidence = _evidence_or_fallback([str(event.get("id", ""))], fallback, vault_ids)
        timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")) if event.get("timestamp") else None
        items.append(EvidenceTimelineItem(timestamp=timestamp, kind="alert", service=event.get("service"), summary=f"Alert emitted (level {event.get('level', 'unknown')}).", evidence_ids=evidence))
    max_time = datetime.max.replace(tzinfo=timezone.utc)
    items.sort(key=lambda item: (item.timestamp or max_time, item.kind, item.service or "", item.evidence_ids[0]))
    return items


def _runner_up_findings(s04: dict[str, Any], runner: dict[str, Any] | None, fallback: list[str], vault_ids: set[str]) -> list[RunnerUpFinding]:
    if not runner:
        return []
    target = runner.get("target")
    findings = [finding for entries in s04.get("per_method", {}).values() for finding in entries if finding.get("target") == target]
    result = [RunnerUpFinding(method=str(method), verdict=str(finding.get("verdict", "inconclusive")),
        effect_size=float(finding.get("effect_size", 0)), rationale=str(finding.get("rationale", "No rationale recorded.")),
        evidence_ids=_evidence_or_fallback(list(finding.get("evidence_ids", [])), list(runner.get("evidence_ids", [])) or fallback, vault_ids))
        for method, entries in s04.get("per_method", {}).items() for finding in entries if finding.get("target") == target]
    if not result:
        result.append(RunnerUpFinding(method="s04", verdict="inconclusive", effect_size=0.0,
            rationale="No S04 check finding was recorded for the runner-up.", evidence_ids=_evidence_or_fallback(list(runner.get("evidence_ids", [])), fallback, vault_ids)))
    return result


def render_markdown(report: IncidentReport) -> str:
    cite = lambda ids: " [evidence_ids: " + ", ".join(ids) + "]"
    lines = [f"# Incident report — {report.scenario_id}", "", f"Source: {report.source}. Synthetic: {str(report.synthetic).lower()}." + cite(report.headline.evidence_ids), "",
        "## Headline", ""]
    head = report.headline
    target = head.target or "no candidate available"
    if head.confidence.unvalidated_calibrated_probability is not None:
        lines.append(f"Most likely consistent with {head.target_type} {target}; confidence {head.confidence.level} (unvalidated probability: {head.confidence.unvalidated_calibrated_probability:.3f})." + cite(head.evidence_ids))
    else:
        lines.append(f"Most likely consistent with {head.target_type} {target}; confidence {head.confidence.level}." + cite(head.evidence_ids))
    lines.append(head.reason + cite(head.evidence_ids))
    lines += ["", "## Ranked candidates", ""]
    if report.top_candidates:
        for candidate in report.top_candidates:
            method_scores = ", ".join(f"{name}={score:.6f}" for name, score in sorted(candidate.per_method_scores.items())) or "none"
            s04_disp = candidate.s04_status or "unavailable"
            if candidate.s04_status in ("verified", "contested"):
                s04_disp = f"{candidate.s04_status} (experimental)"
            lines.append(f"{candidate.rank}. {candidate.target} — ensemble={candidate.ensemble_score:.6f}; methods={method_scores}; disagreement={candidate.disagreement:.3f}; S04={s04_disp}." + cite(candidate.evidence_ids))
    else:
        lines.append("No S03 candidate was available." + cite(head.evidence_ids))
    lines += ["", "## Evidence timeline", ""]
    for event in report.evidence_timeline:
        time = event.timestamp.isoformat() if event.timestamp else "time unavailable"
        service = f" {event.service}" if event.service else ""
        lines.append(f"- {time} — {event.kind}{service}: {event.summary}" + cite(event.evidence_ids))
    if not report.evidence_timeline:
        lines.append("No onset or event timestamp was available." + cite(head.evidence_ids))
    lines += ["", "## Why not the runner-up", ""]
    if report.runner_up_findings:
        for finding in report.runner_up_findings:
            lines.append(f"- {finding.method}: {finding.verdict} (effect={finding.effect_size:.3f}) — {finding.rationale}" + cite(finding.evidence_ids))
    else:
        lines.append("No runner-up candidate was available." + cite(head.evidence_ids))
    lines += ["", "## Unknowns", ""]
    lines.extend("- " + statement.text + cite(statement.evidence_ids) for statement in report.unknowns)
    lines += ["", "## Suggested next checks", ""]
    lines.extend("- " + statement.text + cite(statement.evidence_ids) for statement in report.suggested_next_checks)
    lines += ["", report.footer.text + cite(report.footer.evidence_ids)]
    if report.confidence_model_sha256:
        lines.append(f"Confidence model SHA-256 (unvalidated): {report.confidence_model_sha256}." + cite(report.footer.evidence_ids))
    lines.append("")
    return "\n".join(lines)


class ReportStage:
    name = "s05_report"

    def run(self, ctx: RunContext, inp: StageInput) -> StageResult:
        vault_ids = read_vault_ids(ctx.runs_dir / ctx.run_id / "vault" / "chain.jsonl")
        s00, s02, s03, s04 = (_artifact(ctx, name) for name in ("s00_ingest", "s02_signals", "s03_candidates", "s04_verify"))
        if not vault_ids:
            raise ValueError("S05 requires a non-empty verified evidence vault")
        analysis3 = s03.get("analysis", {})
        analysis4 = s04.get("analysis", {})
        analysis2 = s02.get("analysis", {})
        features, detail = extract_features(analysis3, analysis4, analysis2, vault_ids)
        methods_disagree = bool(detail["disagreement"] > 0.0 or detail["first_place_method_count"] < detail["methods_with_candidates"])
        level = rule_confidence_level(
            telemetry_gap=detail["telemetry_gap"],
            methods_with_candidates=detail["methods_with_candidates"],
            methods_disagree=methods_disagree,
            s04_status=detail["s04_status"],
        )
        unval_prob = None
        model_hash = None
        if ctx.config.unvalidated_calibrated_confidence:
            model_path = ctx.config.confidence_model_path
            if not model_path.is_absolute():
                model_path = Path(__file__).resolve().parents[3] / model_path
            model, model_hash = load_model(model_path, ctx.config.confidence_model_sha256)
            unval_prob = predict_probability(model, features)

        candidates = list(analysis3.get("candidates", []))
        top = candidates[0] if candidates else None
        fallback = _evidence_or_fallback(list(top.get("evidence_ids", [])) if top else [], [], vault_ids)
        confidence = ConfidenceEstimate(
            level=level,
            telemetry_gap=detail["telemetry_gap"],
            methods_disagree=methods_disagree,
            s04_status=detail["s04_status"],
            first_place_method_count=detail["first_place_method_count"],
            disagreement=detail["disagreement"],
            margin=detail["margin"],
            unvalidated_calibrated_probability=unval_prob,
            model_sha256=model_hash,
        )
        target = detail["target"]
        s04_disp = detail["s04_status"] or "unavailable"
        if detail["s04_status"] in ("verified", "contested"):
            s04_disp = f"{detail['s04_status']} (experimental)"
        reason = f"Ranked first by {detail['first_place_method_count']} available methods; S04 status is {s04_disp}."
        headline = IncidentHeadline(target=target, target_type=(top.get("target_type", "service") if top else "none"), confidence=confidence,
            reason=reason, evidence_ids=fallback)
        status_by_target = {item.get("target"): item.get("status") for item in analysis4.get("decisions", [])}
        top_reports=[]
        for rank,candidate in enumerate(candidates[:3],start=1):
            ids=_evidence_or_fallback(list(candidate.get("evidence_ids", [])),fallback,vault_ids)
            top_reports.append(IncidentCandidate(rank=rank,target=str(candidate.get("target", "")),target_type=candidate.get("target_type", "service"),
                ensemble_score=float(candidate.get("score", 0)),per_method_scores={str(k):float(v) for k,v in candidate.get("method_scores",{}).items()},
                disagreement=float(analysis3.get("disagreement",0)),s04_status=status_by_target.get(candidate.get("target")),evidence_ids=ids))
        runner = candidates[1] if len(candidates)>1 else None
        unknowns: list[ReportStatement]=[]
        bundle=s02.get("bundle", {})
        metrics=bundle.get("metrics", [])
        for gap in analysis2.get("coverage_gaps", []):
            matching=[point for point in metrics if point.get("service")==gap.get("service") and point.get("metric")==gap.get("metric")]
            ids=[point["id"] for point in matching[:2]]
            unknowns.append(_stmt(f"Metric coverage gap for {gap.get('service')} {gap.get('metric')} spans {gap.get('missing_windows')} window(s).",ids,fallback,vault_ids))
        gap_services=set(analysis3.get("verification_context",{}).get("telemetry_gaps", []))
        for service in sorted(gap_services):
            service_ids=[point["id"] for point in metrics if point.get("service")==service]
            unknowns.append(_stmt(f"Telemetry coverage is incomplete for service {service} (including absent trace coverage where applicable).",service_ids,fallback,vault_ids))
        for method in analysis3.get("disabled_methods", []):
            unknowns.append(_stmt(f"S03 method {method} was disabled.",fallback,fallback,vault_ids))
        for method in analysis3.get("method_results", []):
            if method.get("status") == "DEGRADED":
                unknowns.append(_stmt(f"S03 method {method.get('method')} was degraded; its output may be incomplete.",fallback,fallback,vault_ids))
        abstentions=analysis3.get("abstentions",{}).get(target,{}) if target else {}
        for method,why in sorted(abstentions.items()):
            unknowns.append(_stmt(f"S03 method {method} abstained for the headline candidate ({why}).",fallback,fallback,vault_ids))
        for method in analysis4.get("disabled_methods", []):
            unknowns.append(_stmt(f"S04 check {method} was disabled.",fallback,fallback,vault_ids))
        for method in analysis4.get("method_results", []):
            if method.get("status") == "DEGRADED":
                unknowns.append(_stmt(f"S04 check {method.get('method')} was degraded; its finding may be incomplete.",fallback,fallback,vault_ids))
        warnings=list(analysis2.get("warnings", []))
        seasonal="off_or_partial" if not metrics or any("Seasonal normalization not applied" in str(item) for item in warnings) else "on"
        seasonal_text=("Seasonal normalization was applied to supported metric series; fallback was used where two daily cycles were unavailable." if seasonal=="off_or_partial" else "Seasonal normalization was applied to the available metric series.")
        unknowns.append(_stmt(seasonal_text,[point["id"] for point in metrics[:2]],fallback,vault_ids))
        if not unknowns:
            unknowns.append(_stmt("No additional telemetry or method unknowns were recorded.",fallback,fallback,vault_ids))
        next_checks=[]
        runner_ids=list(runner.get("evidence_ids",[])) if runner else fallback
        runner_status=status_by_target.get(runner.get("target")) if runner else None
        if runner_status=="contested":
            next_checks.append(_stmt("Inspect the runner-up's cited dependency edge and compare its event timing with the onset.",runner_ids,fallback,vault_ids))
        elif runner_status=="unsupported":
            next_checks.append(_stmt("Verify the runner-up's cited source records and check the vault integrity record.",runner_ids,fallback,vault_ids))
        if level=="insufficient_evidence" or detail["telemetry_gap"]:
            next_checks.append(_stmt("Restore the missing metric or trace coverage for the headline service, then compare the onset again.",fallback,fallback,vault_ids))
        if detail["s04_status"]=="verified":
            next_checks.append(_stmt("Independently compare the cited upstream metric changes and the recorded change window.",fallback,fallback,vault_ids))
        if not next_checks:
            next_checks.append(_stmt("Collect an independent trace or deployment timestamp for the top-ranked service.",fallback,fallback,vault_ids))
        report=IncidentReport(scenario_id=str(s00.get("bundle",{}).get("manifest",{}).get("scenario_id",ctx.scenario_id)),source=s00.get("source","real"),
            synthetic=bool(s00.get("synthetic",False)),headline=headline,top_candidates=top_reports,evidence_timeline=_timeline(s00,s02,fallback,vault_ids),
            runner_up_findings=_runner_up_findings(analysis4,runner,fallback,vault_ids),unknowns=unknowns,suggested_next_checks=next_checks,
            seasonal_normalization=seasonal,confidence_model_sha256=model_hash,footer=ReportStatement(text=FOOTER,evidence_ids=fallback))
        report_data=report.model_dump(mode="python")
        referenced=_all_report_evidence(report_data)
        invalid=sorted(referenced-vault_ids)
        if invalid:
            raise ValueError(f"S05 report cited evidence absent from vault: {invalid}")
        report_json=report.model_dump(mode="json")
        report_dir=ctx.runs_dir/ctx.run_id/"05_s05_report"
        write_json(report_dir/"report.json",report_json)
        write_text(report_dir/"report.md",render_markdown(report))
        evidence_ids=sorted(referenced)
        return StageResult(stage=self.name,status=StageStatus.OK,output={"report":report_json,"report_path":"05_s05_report/report.md","confidence_model_sha256":model_hash},evidence_ids=evidence_ids,elapsed_ms=0)
