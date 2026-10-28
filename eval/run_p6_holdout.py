"""One-shot P6 holdout runner. Refuses to overwrite any prior holdout output."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inquest.contracts import CanonicalBundle, SignalAnalysis
from inquest.core.builtins import default_registry
from inquest.core.config import load_config
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner
from simulator.scenarios.registry import SCENARIO_GENERATORS

SEEDS = (7, 8, 9)
STAGES = ["s00_ingest", "s01_vault", "s02_signals", "s03_candidates", "s04_verify"]
OUTPUT = ROOT / "runs" / "p6_holdout_equal_rrf"
REPORT = ROOT / "eval" / "p6_holdout_results.md"
RESULTS = ROOT / "eval" / "p6_holdout_cases.json"


def targets(items):
    return [item.get("service") or (item.get("target") if item.get("target_type") == "service" else None)
            for item in items if item.get("service") or (item.get("target") if item.get("target_type") == "service" else None)]


def ranks(order, truths):
    return ", ".join(f"{truth}:{order.index(truth)+1 if truth in order else '—'}" for truth in truths)


def latest_change(bundle, signals):
    if not signals.onsets:
        return []
    onset = min(item.onset_time for item in signals.onsets)
    uncertainty = max((item.timestamp_uncertainty_ms for item in signals.onsets), default=0) / 1000
    eligible = [item for item in bundle.changes if item.timestamp and (item.timestamp-onset).total_seconds() <= uncertainty]
    return [max(eligible, key=lambda item: (item.timestamp, item.id)).service] if eligible else []


def alert_order(bundle, signals):
    alerts = [item for item in bundle.logs if item.attributes.get("alert_emission") is True]
    if alerts:
        return list(dict.fromkeys(item.service for item in sorted(alerts, key=lambda item: (item.timestamp, item.id)) if item.service))
    return list(signals.service_order)


def preflight():
    if OUTPUT.exists() or REPORT.exists() or RESULTS.exists():
        raise SystemExit("P6 holdout output already exists; refusing a second run.")
    missing = []
    for scenario in SCENARIO_GENERATORS:
        for seed in SEEDS:
            truth = ROOT / "simulator" / "sim_truth" / scenario / f"seed_{seed}.truth.json"
            if not truth.is_file():
                missing.append(str(truth))
            data = json.loads(truth.read_text(encoding="utf-8")) if truth.is_file() else {}
            sid = data.get("scenario_id")
            export = ROOT / "simulator" / "exports" / str(sid) / f"seed_{seed}" / "export"
            if not sid or not export.is_dir():
                missing.append(str(export))
    if missing:
        raise SystemExit("Holdout preflight failed:\n" + "\n".join(missing))
    print(f"preflight OK: {len(SCENARIO_GENERATORS)} families × {len(SEEDS)} seeds; output roots unused")


def run_case(scenario, seed, config, runner):
    truth_data = json.loads((ROOT / "simulator" / "sim_truth" / scenario / f"seed_{seed}.truth.json").read_text(encoding="utf-8"))
    raw = truth_data["injected_fault"]
    truths = [str(x["service"]) for x in raw] if isinstance(raw, list) else [str(raw["service"])]
    sid = truth_data["scenario_id"]
    export = ROOT / "simulator" / "exports" / sid / f"seed_{seed}" / "export"
    rid = "p6_" + hashlib.sha256(f"{sid}|{seed}|equal_rrf".encode()).hexdigest()[:16]
    context = RunContext(run_id=rid, scenario_id=sid, runs_dir=OUTPUT, clock=config.simulation_clock, config=config)
    report = runner.run(context, STAGES, {"folder": str(export)})
    if report.failed_stages:
        raise RuntimeError(f"pipeline failure for {scenario} seed {seed}: {report.failed_stages}")
    stages = {item.stage: item for item in report.stages}
    s02 = stages["s02_signals"].output
    bundle = CanonicalBundle.model_validate(s02["bundle"])
    signals = SignalAnalysis.model_validate(s02["analysis"])
    a3 = stages["s03_candidates"].output["analysis"]
    a4 = stages["s04_verify"].output["analysis"]
    rankings = {name: targets(a3.get("per_method", {}).get(name, [])) for name in ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag")}
    rankings["ensemble"] = targets(a3.get("candidates", []))
    rankings["s04_annotation"] = [item["target"] for item in a4.get("original_order", [])]
    rankings["latest_change_before_alert"] = latest_change(bundle, signals)
    rankings["alert_order"] = alert_order(bundle, signals)
    status = {item["target"]: item["status"] for item in a4.get("decisions", [])}
    return {"scenario": scenario, "seed": seed, "truth": truths, "rankings": rankings,
            "statuses": status, "stages": {item.stage: item.status.value for item in report.stages},
            "run_id": rid, "scenario_id": sid}


def render(cases):
    methods = ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag", "ensemble", "s04_annotation", "latest_change_before_alert", "alert_order")
    lines = ["# P6 One-Time Holdout Results", "", "Frozen configuration: equal-weight RRF, fusion abstention on, S04 annotation only (re-rank off). Seeds 7–9 across all existing scenario families. Each case was run once.", "",
             "| Scenario | Seed | True cause(s) | " + " | ".join(methods) + " | True-cause S04 statuses | Wrong-candidate verified |",
             "|---|---:|---|" + "---:|"*len(methods) + "---|---|---|"]
    for case in cases:
        rank_cells = [ranks(case["rankings"][m], case["truth"]) for m in methods]
        true_status = ", ".join(f"{t}:{case['statuses'].get(t, 'not_candidate')}" for t in case["truth"])
        wrong_verified = ", ".join(t for t, s in case["statuses"].items() if t not in case["truth"] and s == "verified") or "none"
        row = [case["scenario"], str(case["seed"]), ", ".join(case["truth"]), *rank_cells, true_status, wrong_verified]
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "Run IDs and per-stage status:", "", "| Scenario | Seed | Opaque ID | Run ID | Stage statuses |", "|---|---:|---|---|---|"]
    for c in cases:
        lines.append(f"| {c['scenario']} | {c['seed']} | {c['scenario_id']} | {c['run_id']} | " + ", ".join(f"{k}={v}" for k,v in c["stages"].items()) + " |")
    return "\n".join(lines) + "\n"


def main():
    preflight()
    config = load_config(ROOT / "config.yaml").model_copy(update={"runs_dir": OUTPUT})
    runner = StageRunner(default_registry(config))
    cases = []
    for scenario in SCENARIO_GENERATORS:
        for seed in SEEDS:
            case = run_case(scenario, seed, config, runner)
            cases.append(case)
            print(f"completed {scenario} seed={seed}")
    RESULTS.write_text(json.dumps(cases, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(render(cases), encoding="utf-8")
    print(f"wrote {REPORT.relative_to(ROOT)} and {RESULTS.relative_to(ROOT)}")


if __name__ == "__main__":
    if "--check-only" in sys.argv:
        preflight()
    else:
        main()
