"""Frozen P8 alert-order audit; reads truth only in this eval module."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from inquest.contracts import CanonicalBundle, SignalAnalysis
from inquest.core.builtins import default_registry
from inquest.core.config import load_config
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner
from simulator.scenarios.registry import SCENARIO_GENERATORS

NEW_FAMILIES = ("cause_alerts_2_4", "unordered_plausible_alerts")
SEEDS = tuple(range(32, 52))
STAGES = ["s00_ingest", "s01_vault", "s02_signals", "s03_candidates", "s04_verify"]
CONFIG_PATH = ROOT / "config.yaml"
CONFIG_HASH = hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()
RUNS_DIR = ROOT / "runs" / f"p8_alert_audit_equal_rrf_{CONFIG_HASH[:8]}"
RESULTS_PATH = ROOT / "eval" / "p8_alert_audit_cases.json"
REPORT_PATH = ROOT / "eval" / "p8_alert_audit_results.md"


def head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def rank(order: list[str], target: str) -> int | None:
    return order.index(target) + 1 if target in order else None


def hit(case: dict, method: str, k: int) -> bool:
    return any(target in case["rankings"][method][:k] for target in case["truth"])


def truths_from(value: object) -> list[str]:
    items = value if isinstance(value, list) else [value]
    return [str(item["service"]) for item in items if isinstance(item, dict) and item.get("service")]


def service_targets(items: list[dict]) -> list[str]:
    result = []
    for item in items:
        target = item.get("service") or (item.get("target") if item.get("target_type") == "service" else None)
        if target and target not in result:
            result.append(target)
    return result


def latest_change(bundle: CanonicalBundle, signals: SignalAnalysis) -> list[str]:
    if not signals.onsets:
        return []
    onset = min(point.onset_time for point in signals.onsets)
    uncertainty = max((point.timestamp_uncertainty_ms for point in signals.onsets), default=0) / 1000
    events = [event for event in bundle.changes if event.timestamp and (event.timestamp - onset).total_seconds() <= uncertainty]
    return [max(events, key=lambda event: (event.timestamp, event.id)).service] if events else []


def alert_order(bundle: CanonicalBundle, signals: SignalAnalysis) -> list[str]:
    alerts = [event for event in bundle.logs if event.attributes.get("alert_emission") is True]
    if alerts:
        return list(dict.fromkeys(event.service for event in sorted(alerts, key=lambda event: (event.timestamp, event.id)) if event.service))
    return list(signals.service_order)


def case_list():
    return [(family, seed) for family in NEW_FAMILIES for seed in SEEDS]


def preflight():
    if RUNS_DIR.exists() or RESULTS_PATH.exists() or REPORT_PATH.exists():
        raise SystemExit(f"refusing to overwrite P8 results: {RUNS_DIR}")
    missing = []
    for family, seed in case_list():
        truth_path = ROOT / "simulator" / "sim_truth" / family / f"seed_{seed}.truth.json"
        if not truth_path.is_file():
            missing.append(str(truth_path)); continue
        truth = json.loads(truth_path.read_text(encoding="utf-8"))
        export = ROOT / "simulator" / "audit_inputs" / truth["scenario_id"] / f"seed_{seed}" / "export"
        if not export.is_dir():
            missing.append(str(export))
    if missing:
        raise SystemExit("P8 input preflight failed:\n" + "\n".join(missing))
    commit = head()
    print(f"preflight OK: 40 cases; commit={commit}; config_sha256={CONFIG_HASH}")
    return commit


def run_case(family: str, seed: int, runner, config, commit: str) -> dict:
    truth_record = json.loads((ROOT / "simulator" / "sim_truth" / family / f"seed_{seed}.truth.json").read_text(encoding="utf-8"))
    sid = truth_record["scenario_id"]
    export = ROOT / "simulator" / "audit_inputs" / sid / f"seed_{seed}" / "export"
    truths = truths_from(truth_record["injected_fault"])
    run_id = "p8_" + hashlib.sha256(f"{commit}|{CONFIG_HASH}|{sid}|{seed}".encode()).hexdigest()[:18]
    context = RunContext(run_id=run_id, scenario_id=sid, runs_dir=RUNS_DIR, clock=config.simulation_clock, config=config)
    report = runner.run(context, STAGES, {"folder": str(export)})
    if report.failed_stages:
        raise RuntimeError(f"pipeline failed for {family}/{seed}: {report.failed_stages}")
    stages = {item.stage: item for item in report.stages}
    s02 = stages["s02_signals"].output
    bundle = CanonicalBundle.model_validate(s02["bundle"])
    signals = SignalAnalysis.model_validate(s02["analysis"])
    s03 = stages["s03_candidates"].output["analysis"]
    s04 = stages["s04_verify"].output["analysis"]
    rankings = {name: service_targets(s03.get("per_method", {}).get(name, [])) for name in ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag")}
    rankings["ensemble"] = service_targets(s03.get("candidates", []))
    rankings["latest_change_before_alert"] = latest_change(bundle, signals)
    rankings["alert_order"] = alert_order(bundle, signals)
    result = {
        "scenario": family, "seed": seed, "scenario_id": sid, "truth": truths,
        "rankings": rankings, "candidate_count": len(s03.get("candidates", [])),
        "statuses": {item["target"]: item["status"] for item in s04.get("decisions", [])},
        "stage_statuses": {item.stage: item.status.value for item in report.stages},
        "run_id": run_id, "commit": commit, "config_sha256": CONFIG_HASH,
    }
    run_root = RUNS_DIR / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "run_metadata.json").write_text(json.dumps({"commit": commit, "config_sha256": CONFIG_HASH, "scenario_id": sid, "seed": seed}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def two_way_bootstrap(cases: list[dict], reps: int = 20000) -> dict:
    families = sorted({case["scenario"] for case in cases})
    seeds = sorted({case["seed"] for case in cases})
    family_index = {family: i for i, family in enumerate(families)}
    seed_index = {seed: i for i, seed in enumerate(seeds)}
    ens = np.asarray([int(hit(case, "ensemble", 1)) for case in cases], dtype=float)
    alert = np.asarray([int(hit(case, "alert_order", 1)) for case in cases], dtype=float)
    fi = np.asarray([family_index[case["scenario"]] for case in cases])
    si = np.asarray([seed_index[case["seed"]] for case in cases])
    rng = np.random.default_rng(80808)
    fm = rng.multinomial(len(families), [1 / len(families)] * len(families), size=reps)
    sm = rng.multinomial(len(seeds), [1 / len(seeds)] * len(seeds), size=reps)
    weights = fm[:, fi] * sm[:, si]
    denom = weights.sum(axis=1)
    def interval(samples):
        return [float(np.quantile(samples, .025)), float(np.quantile(samples, .975))]
    e = (weights @ ens) / denom
    a = (weights @ alert) / denom
    d = (weights @ (ens - alert)) / denom
    return {"cases": len(cases), "ensemble_hits": int(ens.sum()), "alert_hits": int(alert.sum()),
            "ensemble_rate": float(ens.mean()), "alert_rate": float(alert.mean()), "delta": float((ens-alert).mean()),
            "ensemble_ci": interval(e), "alert_ci": interval(a), "delta_ci": interval(d),
            "families": families, "seeds": seeds, "cluster_bootstrap_replicates": reps}


def metric_table(cases: list[dict]) -> list[str]:
    lines = ["| Scenario | Cause positions in alert_order (cause labels) | Cases with any cause first | Candidate count distribution |", "|---|---|---:|---|"]
    for family in list(dict.fromkeys(case["scenario"] for case in cases)):
        group = [case for case in cases if case["scenario"] == family]
        positions = [rank(case["rankings"]["alert_order"], target) for case in group for target in case["truth"]]
        pos_counts = Counter(positions)
        pos_text = ", ".join(f"{position if position is not None else 'absent'}:{count}" for position, count in sorted(pos_counts.items(), key=lambda item: (item[0] is None, item[0] or 0)))
        first_cases = sum(any(rank(case["rankings"]["alert_order"], target) == 1 for target in case["truth"]) for case in group)
        candidate_counts = Counter(case["candidate_count"] for case in group)
        candidate_text = ", ".join(f"{count} candidates:{n}" for count, n in sorted(candidate_counts.items()))
        lines.append(f"| {family} | {pos_text} | {first_cases}/{len(group)} ({first_cases/len(group):.3f}) | {candidate_text} |")
    return lines


def p6_p7_audit() -> list[str]:
    p6 = json.loads((ROOT / "eval" / "p6_holdout_cases.json").read_text(encoding="utf-8"))
    p7 = json.loads((ROOT / "eval" / "p7_variance_cases.json").read_text(encoding="utf-8"))
    old_data_commit = "8f31d05e079de945e8ab0c83e336b83532e1843d"
    variance_data_commit = "74646e85d7b90a8c4c0db1ddbc1a1fb5fc39fc08"
    source_commit = "6138071bb7242f96d568d529f08d7180a10bca90"
    out = ["## Part A: P6 vs P7 simulator/config audit", "",
           f"The family implementation for noisy_alerts and partial_graph is unchanged since `{source_commit}`. P6's seed materializer was committed in `{old_data_commit}`; P7's seed materializer was committed in `{variance_data_commit}`. P6 analysis used commit `2e094d8c8d29a695564065cd84a13361fe37b7f7`; P7 used `77b469dfc8cfa203caf97f74c9298439652619d5`. Both used config SHA-256 `269dbb3f9de3d45edb777fa5bf70c289feb1ec56f40f722a5607fc253b7c90d7`. There is no diff in `inquest/` or `config.yaml` between those analysis commits.", "",
           "Both generators used the same scenario parameters: database fault starts at step 10, intensity 1.4, threshold 42, 20 steps. noisy_alerts emits one alert per service at seeded random steps 5–15, with three healthy-service alerts (75% false-alert share); partial_graph omits only payments→database (one dropped edge). Candidate count is four in every audited case.", "",
           "| Family | Block | Cause position in alert_order | Alert noise rate | Dropped edges | Candidate count |", "|---|---|---|---|---|---|"]
    for family in ("noisy_alerts", "partial_graph"):
        for block, data, seeds in (("P6 seeds 7–9", p6, (7,8,9)), ("P7 fresh block", p7, None)):
            group = [case for case in data if case["scenario"] == family and (seeds is None or case["seed"] in seeds)]
            positions = Counter(rank(case["rankings"]["alert_order"], case["truth"][0]) for case in group)
            positions_text = ", ".join(f"{pos if pos is not None else 'absent'}:{n}" for pos,n in sorted(positions.items(), key=lambda item:(item[0] is None,item[0] or 0)))
            noise=[]; dropped=[]
            for case in group:
                truth = json.loads((ROOT/"simulator"/"sim_truth"/family/f"seed_{case['seed']}.truth.json").read_text(encoding="utf-8"))
                schedule=truth.get("alert_schedule",{})
                noise.append(f"{len(truth.get('spurious_alert_services',[]))}/{len(schedule)}" if schedule else "n/a")
                dropped.append(len(truth.get("omitted_dependency_edges",[])))
            candidate_counts=[]
            for case in group:
                if "candidate_count" in case:
                    candidate_counts.append(case["candidate_count"])
                else:
                    artifact=ROOT/"runs"/"p6_holdout_equal_rrf"/case["run_id"]/"03_s03_candidates"/"output.json"
                    candidate_counts.append(len(json.loads(artifact.read_text(encoding="utf-8"))["output"]["analysis"]["candidates"]))
            out.append(f"| {family} | {block} | {positions_text} | {', '.join(sorted(set(noise)))} | {dict(Counter(dropped))} | {dict(Counter(candidate_counts))} |")
    p6_noisy_steps=[]; p7_noisy_steps=[]
    for case in p6:
        if case["scenario"]=="noisy_alerts":
            truth=json.loads((ROOT/"simulator"/"sim_truth"/"noisy_alerts"/f"seed_{case['seed']}.truth.json").read_text(encoding="utf-8"))
            p6_noisy_steps.append(truth["alert_schedule"]["database"])
    for case in p7:
        if case["scenario"]=="noisy_alerts":
            truth=json.loads((ROOT/"simulator"/"sim_truth"/"noisy_alerts"/f"seed_{case['seed']}.truth.json").read_text(encoding="utf-8"))
            p7_noisy_steps.append(truth["alert_schedule"]["database"])
    out += ["", f"Additional noisy-alert timing detail: database alerts arrived at steps {p6_noisy_steps} in P6 (all 3 before the step-10 fault onset), versus {sum(step < 10 for step in p7_noisy_steps)}/20 before onset in P7. P6 therefore sampled an unusually early cause-alert realization, although P7 also contains many pre-onset alerts and its ensemble still ranked the cause first in all 20 cases.", ""]
    out += ["", "### P6 per-case ranks and failures", "", "A method is a top-1 failure when the cause rank is not 1; ranks shown include all S03 methods, ensemble, and alert_order.", "", "| Family | Seed | Cause | Cause alert position | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble | alert_order |", "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    for family in ("noisy_alerts", "partial_graph"):
        for case in p6:
            if case["scenario"] != family: continue
            target=case["truth"][0]; alert_pos=rank(case["rankings"]["alert_order"],target)
            ranks=[rank(case["rankings"][method],target) or "—" for method in ("change_based","graph_rwr","trace_ochiai","temporal_lag","ensemble","alert_order")]
            out.append("| " + " | ".join([family,str(case["seed"]),target,str(alert_pos or "absent"),*[str(x) for x in ranks]]) + " |")
    out += ["", "Classification: **seed-specific data/rank-fusion edge cases; no different generator, config, or structural scenario parameter was found.** For noisy_alerts, P6 had alert-order positions 1, 3, 3 and P7 spans positions 1–4; both blocks had the same 75% spurious-alert rate. For partial_graph, both blocks dropped exactly one edge and had four candidates, with the cause first in alert_order throughout. In P6, graph_rwr ranked the cause first in all six cases, but in four cases trace/temporal decoys pushed the ensemble cause to rank 2. This implies the P6 1/3 result is a noisy three-seed estimate, not evidence of a systematic generator/config discrepancy.", ""]
    return out


def p7_composition(cases: list[dict]) -> list[str]:
    groups = {
        "designed_or_seasonal": {"late_alerting_cause", "noisy_alerts", "long_seasonal"},
        "other_nine": {case["scenario"] for case in cases} - {"late_alerting_cause", "noisy_alerts", "long_seasonal"},
        "silent_cause_only": {"silent_cause"},
    }
    lines=["## Part B: composition-adjusted P7 comparison", "",
           "Intervals are crossed family-and-seed cluster-bootstrap 95% percentile intervals (20,000 replicates; deterministic seed 80808). Each bootstrap weight is the product of independently resampled family and seed cluster multiplicities. silent_cause has one family, so its family dimension is necessarily degenerate; the interval is effectively seed-cluster-only.", "",
           "| Group | Cases | Ensemble top-1 | Ensemble 95% CI | alert_order top-1 | alert_order 95% CI | Paired difference | Paired 95% CI |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    stats={}
    for name, families in groups.items():
        group=[case for case in cases if case["scenario"] in families]
        result=two_way_bootstrap(group); stats[name]=result
        lines.append(f"| {name} | {result['cases']} | {result['ensemble_hits']}/{result['cases']} ({result['ensemble_rate']:.3f}) | [{result['ensemble_ci'][0]:.3f}, {result['ensemble_ci'][1]:.3f}] | {result['alert_hits']}/{result['cases']} ({result['alert_rate']:.3f}) | [{result['alert_ci'][0]:.3f}, {result['alert_ci'][1]:.3f}] | {result['delta']:+.3f} | [{result['delta_ci'][0]:+.3f}, {result['delta_ci'][1]:+.3f}] |")
    a=stats["designed_or_seasonal"]["delta"]; b=stats["other_nine"]["delta"]
    breakeven=(-b)/(a-b) if a!=b else float("nan")
    lines += ["", f"Plain statement: the overall +0.133 top-1 paired difference depends on the family mix. The three designed-or-seasonal families contribute +0.600/case, while the other nine contribute {b:+.3f}/case. At those observed group rates, the ensemble/alert_order mix breaks even when the designed-or-seasonal families make up {breakeven:.1%} of cases; the P7 mix was 25%. This is composition arithmetic, not an intrinsic, scenario-independent advantage.", ""]
    return lines


def render(new_cases: list[dict], commit: str) -> str:
    p7=json.loads((ROOT/"eval"/"p7_variance_cases.json").read_text(encoding="utf-8"))
    lines=["# P8 Simulator Difficulty Audit (no method changes)", "",
           f"P8 analysis commit: `{commit}`  ", f"Frozen config SHA-256: `{CONFIG_HASH}`  ", f"P8 new-family cases: {len(new_cases)} (two families × seeds 32–51).", "",
           "No method, weight, threshold, status rule, or config was changed. P6 seeds 7–9 were read from their saved artifacts only; they were not rerun.", ""]
    lines += p6_p7_audit()
    lines += p7_composition(p7)
    all_cases=p7+new_cases
    lines += ["## Part C1: alert-order difficulty by family", "",
              "Position is the true cause's position in the alert_order baseline. When explicit alert-emission events exist, this is their emission order; otherwise the frozen baseline falls back to signal onset order. Candidate counts are S03 ensemble candidates per case.", ""]
    lines += metric_table(all_cases)
    lines += ["", "## Part C2–C3: new-family top-1/top-3 and case results", "", "| New family | Cases | Ensemble top-1 | Ensemble top-3 | alert_order top-1 | alert_order top-3 | Outcome |", "|---|---:|---:|---:|---:|---:|---|"]
    for family in NEW_FAMILIES:
        group=[case for case in new_cases if case["scenario"]==family]
        e1=sum(hit(case,"ensemble",1) for case in group); e3=sum(hit(case,"ensemble",3) for case in group)
        a1=sum(hit(case,"alert_order",1) for case in group); a3=sum(hit(case,"alert_order",3) for case in group)
        outcome="beats" if e1>a1 else "ties" if e1==a1 else "loses to"
        lines.append(f"| {family} | {len(group)} | {e1}/{len(group)} | {e3}/{len(group)} | {a1}/{len(group)} | {a3}/{len(group)} | ensemble {outcome} alert_order at top-1 |")
    lines += ["", "### New-family per-case rankings", "", "| Family | Seed | Opaque ID | Cause | Cause alert position | change_based rank | graph_rwr rank | trace_ochiai rank | temporal_lag rank | Ensemble rank | alert_order rank | latest_change rank | Candidate count | Run ID |", "|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for case in new_cases:
        target=case["truth"][0]
        ranks=[rank(case["rankings"][method],target) or "—" for method in ("change_based","graph_rwr","trace_ochiai","temporal_lag","ensemble","alert_order","latest_change_before_alert")]
        cells=[case["scenario"],str(case["seed"]),case["scenario_id"],target,str(rank(case["rankings"]["alert_order"],target) or "absent"),*[str(x) for x in ranks],str(case["candidate_count"]),case["run_id"]]
        lines.append("| " + " | ".join(cells) + " |")

    lines += ["", "## Part D1: silent_cause method ranks and diagnosis", "", "| Seed | change_based | graph_rwr | trace_ochiai | temporal_lag | Ensemble | alert_order | Method top-1 candidates (change/graph/trace/lag) |", "|---:|---:|---:|---:|---:|---:|---:|---|"]
    for case in p7:
        if case["scenario"]!="silent_cause": continue
        target=case["truth"][0]
        ranks=[rank(case["rankings"][method],target) or "—" for method in ("change_based","graph_rwr","trace_ochiai","temporal_lag","ensemble","alert_order")]
        tops=[case["rankings"][method][0] if case["rankings"][method] else "—" for method in ("change_based","graph_rwr","trace_ochiai","temporal_lag")]
        lines.append("| " + " | ".join([str(case["seed"]),*[str(x) for x in ranks],", ".join(tops)]) + " |")
    lines += ["", "Mechanism evidence: graph_rwr ranks database first in 19/20 cases; trace_ochiai ranks it first in 7/20 and second in 9/20. change_based ranks database in none, temporal_lag ranks it in none, and temporal_lag's top-1 is payments in 11 and inventory in 9. The ensemble's top-1 is payments in 13 and inventory in 7; database ranks third in 17 cases, fourth in two, and second in one. This is vote mass on decoys despite one strong graph signal, not a configured threshold or tie-break. No fix is applied. Proposal: test an evidence-aware anomaly-only fusion path for candidates supported by graph/metric propagation even without changes or alerts. It could harm shared_dependency and partial_graph, where graph paths and missing edges can favor a shared-ancestry decoy; validate those families on fresh seeds before adoption.", "",
              "## Part D2: late_alerting_cause misses", "", "| Seed | Cause rank ensemble | change_based | graph_rwr | trace_ochiai | temporal_lag | Ensemble top-1 | alert_order rank |", "|---:|---:|---:|---:|---:|---:|---|---:|"]
    late=[case for case in p7 if case["scenario"]=="late_alerting_cause" and not hit(case,"ensemble",1)]
    for case in late:
        target=case["truth"][0]
        ranks=[rank(case["rankings"][method],target) or "—" for method in ("ensemble","change_based","graph_rwr","trace_ochiai","temporal_lag")]
        top=case["rankings"]["ensemble"][0] if case["rankings"]["ensemble"] else "—"
        lines.append("| " + " | ".join([str(case["seed"]),*[str(x) for x in ranks],top,str(rank(case["rankings"]["alert_order"],target) or "absent")]) + " |")
    lines += ["", f"There are {len(late)} top-1 misses in P7's 20 late_alerting_cause cases (the six misses referenced in the request). In all six, graph_rwr ranks the cause first, change_based emits no cause, and alert_order puts the cause fourth; trace/temporal rank mass favors callers, leaving the ensemble cause second or third. No changes were applied.", ""]
    return "\n".join(lines)


def main():
    commit=preflight()
    config=load_config(CONFIG_PATH).model_copy(update={"runs_dir":RUNS_DIR})
    runner=StageRunner(default_registry(config))
    RUNS_DIR.mkdir(parents=True,exist_ok=False)
    (RUNS_DIR/"config.json").write_text(CONFIG_PATH.read_text(encoding="utf-8"),encoding="utf-8")
    (RUNS_DIR/"run_metadata.json").write_text(json.dumps({"commit":commit,"config_sha256":CONFIG_HASH,"case_count":40},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    results=[]
    for i,(family,seed) in enumerate(case_list(),start=1):
        results.append(run_case(family,seed,runner,config,commit))
        if i%5==0: print(f"completed {i}/40",flush=True)
    RESULTS_PATH.write_text(json.dumps(results,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    REPORT_PATH.write_text(render(results,commit)+"\n",encoding="utf-8")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)} and {RESULTS_PATH.relative_to(ROOT)}")


if __name__=="__main__":
    if "--check-only" in sys.argv:
        preflight()
    else:
        main()
