"""Frozen P4 development and fresh-validation evaluation; only this module reads truth."""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inquest.contracts import CanonicalBundle, SignalAnalysis
from inquest.core.builtins import default_registry
from inquest.core.config import load_config
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner
from simulator.core.export import write_export
from simulator.scenarios.registry import SCENARIO_GENERATORS

SEEDS = (11, 29, 47)
DEV_SEEDS = (1, 2, 3)
DEV = ("clean_bad_deploy", "coincident_restart", "red_herring_deploy", "shared_dependency", "missing_telemetry", "long_seasonal", "late_alerting_cause", "silent_cause")
VALIDATION = ("concurrent_causes", "noisy_alerts", "partial_graph", "red_herring_hard")
METHODS = ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag", "ensemble_before", "ensemble_after", "s04_annotation", "latest_change_before_alert", "alert_order")
CHECKS = ("vault_evidence", "dependency_path", "temporal_consistency", "recovery_check", "alternative_check")
STAGES = ["s00_ingest", "s01_vault", "s02_signals", "s03_candidates", "s04_verify"]


def service(item):
    return item.get("service") or (item.get("target") if item.get("target_type") == "service" else None)


def services(items):
    output = []
    for item in items:
        name = service(item) if isinstance(item, dict) else item
        if name and name not in output:
            output.append(name)
    return output


def rank_for(items, truths):
    return {target: (items.index(target) + 1 if target in items else None) for target in truths}


def hit(items, truths, k):
    return any(target in items[:k] for target in truths)


def latest_change(bundle, signals):
    if not signals.onsets:
        return []
    onset = min(point.onset_time for point in signals.onsets)
    uncertainty = max((point.timestamp_uncertainty_ms for point in signals.onsets), default=0) / 1000
    events = [event for event in bundle.changes if (event.timestamp - onset).total_seconds() <= uncertainty]
    return [max(events, key=lambda event: (event.timestamp, event.id)).service] if events else []


def alert_order(bundle, signals):
    alerts = [item for item in bundle.logs if item.attributes.get("alert_emission") is True]
    if alerts:
        return services([item.service for item in sorted(alerts, key=lambda item: (item.timestamp, item.id))])
    return list(signals.service_order)


def run_case(scenario, seed, truth_root, runs_root, base_config):
    generator = SCENARIO_GENERATORS[scenario]
    dataset = generator(seed)
    export = ROOT / "simulator" / "exports" / dataset.manifest.scenario_id / f"seed_{seed}" / "export"
    truth_path = truth_root / scenario / f"seed_{seed}.truth.json"
    write_export(dataset, export, truth_path)
    truth = json.loads(truth_path.read_text(encoding="utf-8"))
    raw_fault = truth["injected_fault"]
    truths = [str(item["service"]) for item in raw_fault] if isinstance(raw_fault, list) else [str(raw_fault["service"])]

    def run_config(abstention):
        config = base_config.model_copy(update={
            "runs_dir": runs_root,
            "stages": {**base_config.stages, **{name: True for name in STAGES}},
            "candidate_methods": {name: True for name in ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag")},
            "verification_methods": {name: True for name in CHECKS},
            "verification_rerank": False,
            "fusion_abstention": abstention,
        })
        run_id = "p4_" + hashlib.sha256(f"{dataset.manifest.scenario_id}|{seed}|abstain={abstention}".encode()).hexdigest()[:16]
        context = RunContext(run_id=run_id, scenario_id=dataset.manifest.scenario_id, runs_dir=runs_root, clock=config.simulation_clock, config=config)
        report = StageRunner(default_registry(config)).run(context, STAGES, {"folder": str(export)})
        if any(stage.status.value == "FAILED" for stage in report.stages):
            raise RuntimeError(f"Pipeline failed for {scenario}/{seed}/{abstention}: {report.failed_stages}")
        return config, context, report

    config_on, context_on, report_on = run_config(True)
    outputs = {item.stage: item for item in report_on.stages}
    s02 = outputs["s02_signals"].output
    bundle = CanonicalBundle.model_validate(s02["bundle"])
    signals = SignalAnalysis.model_validate(s02["analysis"])
    a3 = outputs["s03_candidates"].output["analysis"]
    a4 = outputs["s04_verify"].output["analysis"]

    config_off, _, report_off = run_config(False)
    outputs_off = {item.stage: item for item in report_off.stages}
    a3_off = outputs_off["s03_candidates"].output["analysis"]

    ranked = {name: services(a3.get("per_method", {}).get(name, [])) for name in ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag")}
    ranked["ensemble_before"] = services(a3_off.get("candidates", []))
    ranked["ensemble_after"] = services(a3.get("candidates", []))
    ranked["s04_annotation"] = [item["target"] for item in a4["original_order"]]
    ranked["latest_change_before_alert"] = latest_change(bundle, signals)
    ranked["alert_order"] = alert_order(bundle, signals)

    decisions = {item["target"]: item for item in a4["decisions"]}
    checks = {name: {finding["target"]: finding for finding in findings} for name, findings in a4["per_method"].items()}
    s04_ablations = {}
    runner = StageRunner(default_registry(config_on))
    for check in CHECKS:
        flags = {name: name != check for name in CHECKS}
        ablated_config = config_on.model_copy(update={"verification_methods": flags})
        ablated_context = replace(context_on, config=ablated_config)
        result = runner.rerun(ablated_context, "s04_verify", 4)
        if result.status.value == "FAILED":
            raise RuntimeError(f"S04 ablation {check} failed for {scenario}/{seed}: {result.error}")
        analysis = result.output["analysis"]
        s04_ablations[check] = {
            "order": [item["target"] for item in analysis["original_order"]],
            "decisions": {item["target"]: item for item in analysis["decisions"]},
        }

    return {
        "scenario": scenario, "seed": seed, "truth": truths, "ranked": ranked,
        "decisions": decisions, "checks": checks, "ablations": s04_ablations,
        "abstentions": a3.get("abstentions", {}),
        "candidate_count": len(a3.get("candidates", [])),
        "status_counts": Counter(item["status"] for item in a4["decisions"]),
        "stage_status": {item.stage: item.status.value for item in report_on.stages},
        "coverage_gaps": sorted({gap.service for gap in SignalAnalysis.model_validate(s02["analysis"]).coverage_gaps}),
        "truth_description": truth.get("description", ""),
    }


def totals(cases, key):
    return (sum(hit(case["ranked"][key], case["truth"], 1) for case in cases), sum(hit(case["ranked"][key], case["truth"], 3) for case in cases))


def per_scenario(cases, scenario, key):
    selected = [case for case in cases if case["scenario"] == scenario]
    return (sum(hit(case["ranked"][key], case["truth"], 1) for case in selected), sum(hit(case["ranked"][key], case["truth"], 3) for case in selected))


def render(dataset_name, cases, scenarios):
    lines = [f"## {dataset_name}", "", "### Per-scenario top-1/top-3 hits (3 seeds per scenario)", "", "| Scenario | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble before abstention | ensemble after abstention | S04 annotation | latest_change_before_alert | alert_order |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for scenario in scenarios:
        cells = [f"{per_scenario(cases, scenario, method)[0]}/3; {per_scenario(cases, scenario, method)[1]}/3" for method in METHODS]
        lines.append(f"| {scenario} | " + " | ".join(cells) + " |")

    lines += ["", "### Per-case rankings, statuses, and evidence checks", "", "| Scenario | Seed | True cause(s) | change_based ranks | graph_rwr ranks | trace_ochiai ranks | temporal_lag ranks | ensemble before | ensemble after | S04 annotation | latest change | alert order | true status | other candidate statuses | per-cause check verdict/effect/evidence | rank movement before→after |", "|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for case in cases:
        targets = case["truth"]
        ranks = lambda key: ", ".join(f"{target}:{rank_for(case['ranked'][key], targets)[target] or '—'}" for target in targets)
        true_status = ", ".join(f"{target}:{case['decisions'].get(target, {}).get('status', 'not_candidate')}" for target in targets)
        decoys = ", ".join(f"{target}:{decision['status']}" for target, decision in case["decisions"].items() if target not in targets) or "none"
        checks = []
        for target in targets:
            findings = [f"{name}={item.get(target,{}).get('verdict','no finding')}({item.get(target,{}).get('effect_size','—')}; ids={','.join(item.get(target,{}).get('evidence_ids',[]))})" for name,item in case["checks"].items()]
            checks.append(target + ": " + "; ".join(findings))
        movement = ", ".join(f"{target}:{rank_for(case['ranked']['ensemble_before'], targets)[target] or '—'}→{rank_for(case['ranked']['s04_annotation'], targets)[target] or '—'}" for target in targets)
        row = [case["scenario"],str(case["seed"]),", ".join(targets),ranks("change_based"),ranks("graph_rwr"),ranks("trace_ochiai"),ranks("temporal_lag"),ranks("ensemble_before"),ranks("ensemble_after"),ranks("s04_annotation"),ranks("latest_change_before_alert"),ranks("alert_order"),true_status,decoys,"<br>".join(checks),movement]
        lines.append("| " + " | ".join(row) + " |")

    lines += ["", "### S04 false rejection and false confirmation", "", "| Scenario | False rejections (true cause contested/unsupported) | False confirmations (wrong candidate verified) |", "|---|---|---|"]
    for scenario in scenarios:
        sc = [case for case in cases if case["scenario"] == scenario]
        rejects=[]; confirms=[]
        for case in sc:
            for target in case["truth"]:
                status=case["decisions"].get(target,{}).get("status")
                if status in {"contested","unsupported"}:
                    responsible=[]
                    for check,findings in case["checks"].items():
                        finding=findings.get(target)
                        if finding and finding["verdict"]=="contradicts": responsible.append(f"{check}:{','.join(finding['evidence_ids'])}")
                    rejects.append(f"seed {case['seed']} {target}={status} ({'; '.join(responsible) or 'equal-score contest'})")
            for target,decision in case["decisions"].items():
                if target not in case["truth"] and decision["status"]=="verified":
                    supports=[f"{name}:{','.join(item[target]['evidence_ids'])}" for name,item in case["checks"].items() if target in item and item[target]["verdict"]=="supports"]
                    confirms.append(f"seed {case['seed']} {target} ({'; '.join(supports)})")
        lines.append(f"| {scenario} | {len(rejects)}: {'; '.join(rejects) or 'none'} | {len(confirms)}: {'; '.join(confirms) or 'none'} |")

    lines += ["", "### S04 status counts", "", "| Scenario | All candidates V/C/I/U | True causes V/C/I/U per seed | Affected missing-telemetry services and outcomes |", "|---|---|---|---|"]
    for scenario in scenarios:
        sc=[case for case in cases if case["scenario"]==scenario]
        distribution=Counter()
        true_rows=[]; affected=[]
        for case in sc:
            distribution.update(case["status_counts"])
            true_rows.append(f"{case['seed']}:" + ",".join(f"{target}={case['decisions'].get(target,{}).get('status','not_candidate')}" for target in case["truth"]))
            for svc in case["coverage_gaps"]:
                if svc in case["decisions"]:
                    affected.append(f"seed {case['seed']} {svc}={case['decisions'][svc]['status']}")
        all_counts="/".join(str(distribution[s]) for s in ("verified","contested","insufficient_evidence","unsupported"))
        lines.append(f"| {scenario} | {all_counts} | {'; '.join(true_rows)} | {'; '.join(affected) or 'none recorded'} |")

    lines += ["", "### Per-check contribution (supports/contradicts/inconclusive; true cause vs decoys)", "", "| Scenario | Check | True S/C/I | Decoy S/C/I | Discriminating? |", "|---|---|---:|---:|---|"]
    for scenario in scenarios:
        sc=[case for case in cases if case["scenario"]==scenario]
        for check in CHECKS:
            true_count=Counter(); decoy_count=Counter()
            for case in sc:
                for candidate, finding in case["checks"].get(check,{}).items():
                    if candidate in case["truth"]: true_count[finding["verdict"]]+=1
                    else: decoy_count[finding["verdict"]]+=1
            fmt=lambda c: "/".join(str(c[v]) for v in ("supports","contradicts","inconclusive"))
            same=fmt(true_count)==fmt(decoy_count)
            lines.append(f"| {scenario} | {check} | {fmt(true_count)} | {fmt(decoy_count)} | {'no; identical verdict counts' if same else 'yes; distributions differ'} |")

    lines += ["", "### Per-check ablation and fusion abstention on/off", "", "| Scenario | Fusion OFF top1/top3 | Fusion ON top1/top3 | Abstention effect | Check disabled | S04 order top1/top3 | True verified | Wrong verified | Check effect on status |", "|---|---:|---:|---|---|---:|---:|---:|---|"]
    for scenario in scenarios:
        sc=[case for case in cases if case["scenario"]==scenario]
        off=(sum(hit(c["ranked"]["ensemble_before"],c["truth"],1) for c in sc),sum(hit(c["ranked"]["ensemble_before"],c["truth"],3) for c in sc))
        on=(sum(hit(c["ranked"]["ensemble_after"],c["truth"],1) for c in sc),sum(hit(c["ranked"]["ensemble_after"],c["truth"],3) for c in sc))
        effect="helps" if on[0]>off[0] or on[1]>off[1] else "hurts" if on[0]<off[0] or on[1]<off[1] else "no top-k change"
        for check in CHECKS:
            order_hits=sum(hit(case["ablations"][check]["order"],case["truth"],1) for case in sc)
            order_top3=sum(hit(case["ablations"][check]["order"],case["truth"],3) for case in sc)
            true_verified=sum(case["ablations"][check]["decisions"].get(target,{}).get("status")=="verified" for case in sc for target in case["truth"])
            wrong_verified=sum(dec["status"]=="verified" for case in sc for target,dec in case["ablations"][check]["decisions"].items() if target not in case["truth"])
            lines.append(f"| {scenario} | {off[0]}/3; {off[1]}/3 | {on[0]}/3; {on[1]}/3 | {effect} | {check} | {order_hits}/3; {order_top3}/3 | {true_verified} | {wrong_verified} | S04 annotation order unchanged by policy; status counts recomputed (see counts above). |")

    # Explicitly flag all one-case differences in per-scenario top-k hit counts.
    lines += ["", "### One-case comparison flags", "", "Every pair of ranking methods whose per-scenario top-1 or top-3 hit count differs by exactly one case is listed.", "", "| Scenario | Metric | Method A | Hits A | Method B | Hits B |", "|---|---|---|---:|---|---:|"]
    for scenario in scenarios:
        sc=[case for case in cases if case["scenario"]==scenario]
        for k in (1,3):
            values={method:sum(hit(case["ranked"][method],case["truth"],k) for case in sc) for method in METHODS}
            for i,left in enumerate(METHODS):
                for right in METHODS[i+1:]:
                    if abs(values[left]-values[right])==1:
                        lines.append(f"| {scenario} | top-{k} | {left} | {values[left]}/3 | {right} | {values[right]}/3 |")
    return lines


def main():
    base=load_config(ROOT/"config.yaml")
    truth_root=ROOT/"simulator"/"sim_truth"
    dev_runs=ROOT/"runs"/"p4_development"
    val_runs=ROOT/"runs"/"p4_validation"
    development=[run_case(scenario,seed,truth_root,dev_runs,base) for scenario in DEV for seed in DEV_SEEDS]
    validation=[run_case(scenario,seed,truth_root,val_runs,base) for scenario in VALIDATION for seed in SEEDS]
    lines=["# P4 design fixes and fresh-scenario validation", "", "Part B thresholds/design were committed before evaluation. Part C specifications and simulator implementation were committed before S03/S04 ran. Holdout was not run.", "", "## Part A reconciliation", "", "- P3b top-1 arithmetic: S03 21/24; S04 19/24. `red_herring_deploy` loses 3, `silent_cause` gains 3, and `long_seasonal` loses 2: 21 - 3 + 3 - 2 = 19.", "- True-cause rank regressions in the reported P3b table: red_herring_deploy seeds 1,2,3 payments 1→3; long_seasonal seed 1 database 1→2; long_seasonal seed 3 database 1→2. The P3b report attributes false verification to graph checks, but retained artifacts disagree: alternative_check is disabled and database status is insufficient_evidence in red-herring seed 1. The provenance gap is documented in DECISIONS.md.", "- P3b per-check contribution table and all five check-ablation tables are preserved in `eval/p3b_results.md` C6-C7; its C6 omits the last two rows in the visible markdown. P4 repair audit must treat those counts cautiously until the raw artifact mismatch is resolved.", "", "## Scope and summary", "", f"Development: {len(development)} cases (the eight previously seen scenarios, seeds 1-3). Fresh validation: {len(validation)} cases (four new scenarios, seeds {', '.join(map(str,SEEDS))}). Holdout: not run.", "", "| Dataset | Method | Top-1 | Top-3 |", "|---|---|---:|---:|"]
    for label,cases in (("development",development),("validation",validation)):
        for method in METHODS:
            one,three=totals(cases,method)
            lines.append(f"| {label} | {method} | {one}/{len(cases)} | {three}/{len(cases)} |")
    lines += render("Development details",development,DEV)
    lines += render("Fresh validation details",validation,VALIDATION)

    lines += ["", "## Required findings", ""]
    dev_silent=[x for x in development if x["scenario"]=="silent_cause"]
    silent_off=sum(hit(c["ranked"]["ensemble_before"],c["truth"],1) for c in dev_silent)
    silent_on=sum(hit(c["ranked"]["ensemble_after"],c["truth"],1) for c in dev_silent)
    harmed=[scenario for scenario in DEV+VALIDATION if per_scenario(development+validation,scenario,"ensemble_after")[0] < per_scenario(development+validation,scenario,"ensemble_before")[0] or per_scenario(development+validation,scenario,"ensemble_after")[1] < per_scenario(development+validation,scenario,"ensemble_before")[1]]
    lines.append(f"- Fusion abstention and silent_cause: top-1 changed {silent_off}/3 → {silent_on}/3 in development. Scenarios with a top-k regression under abstention: {', '.join(harmed) or 'none'}.")
    noisy=[c for c in validation if c["scenario"]=="noisy_alerts"]
    for scenario,cases in (("noisy_alerts",noisy),("late_alerting_cause",[c for c in development if c["scenario"]=="late_alerting_cause"]),("silent_cause",dev_silent)):
        ens=per_scenario(development+validation,scenario,"ensemble_after"); s04=per_scenario(development+validation,scenario,"s04_annotation"); alert=per_scenario(development+validation,scenario,"alert_order")
        lines.append(f"- {scenario}: abstention ensemble top-1/top-3={ens[0]}/3,{ens[1]}/3; S04 annotation={s04[0]}/3,{s04[1]}/3; alert_order={alert[0]}/3,{alert[1]}/3.")
    false_before=5
    false_after=sum(dec["status"]=="verified" for case in development+validation for target,dec in case["decisions"].items() if target not in case["truth"])
    lines.append(f"- `verified`: prior P3b report recorded {false_before} false confirmations; P4 emits {false_after} wrong-candidate verified decisions across dev+validation. This includes fresh validation and is not a tuned result.")
    dev_top=totals(development,"ensemble_after"); val_top=totals(validation,"ensemble_after")
    lines.append(f"- Development vs validation ensemble-after-abstention: top-1/top-3 {dev_top[0]}/{len(development)},{dev_top[1]}/{len(development)} vs {val_top[0]}/{len(validation)},{val_top[1]}/{len(validation)}. The per-scenario tables above show where the generalization difference comes from.")
    lines.append("- No tuning or holdout execution occurred. The only post-freeze change before evaluation was the unit-test-discovered integrity-family accounting correction logged in DECISIONS.md.")
    OUT=ROOT/"eval"/"p4_results.md"
    OUT.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"Wrote {OUT} with {len(development)} development and {len(validation)} fresh validation cases")


if __name__ == "__main__":
    main()
