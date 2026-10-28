"""Reproducible candidate evaluation on registered non-holdout scenarios."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inquest.core.builtins import default_registry
from inquest.core.config import load_config
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner
from simulator.core.export import write_export
from simulator.scenarios.registry import DEFAULT_EVAL_SCENARIOS, SCENARIO_GENERATORS

RUNS_DIR = ROOT / "runs" / "p2_eval"
RESULT_PATH = ROOT / "eval" / "p2_results.md"
METHODS = ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag", "ensemble", "latest_change_before_alert", "alert_order")
SEEDS = (1, 2, 3)
STAGES = ["s00_ingest", "s01_vault", "s02_signals", "s03_candidates"]


def _service(candidate: dict) -> str | None:
    return candidate.get("service") or (candidate.get("target") if candidate.get("target_type") == "service" else None)


def _ranked_services(candidates: list[dict]) -> list[str]:
    ordered = []
    for candidate in candidates:
        service = _service(candidate)
        if service and service not in ordered:
            ordered.append(service)
    return ordered


def _latest_change(bundle, signals) -> list[str]:
    if not signals.onsets:
        return []
    alert = min(onset.onset_time for onset in signals.onsets)
    uncertainty = max(onset.timestamp_uncertainty_ms for onset in signals.onsets) / 1000
    # Events within known source-clock uncertainty may be simultaneous with onset.
    prior = [event for event in bundle.changes if (event.timestamp - alert).total_seconds() <= uncertainty]
    if not prior:
        return []
    event = max(prior, key=lambda item: (item.timestamp, item.id))
    return [event.service]


def _rate(hit1: int, hit3: int, count: int) -> str:
    return f"{hit1}/{count} ({100 * hit1 / count:.0f}%) / {hit3}/{count} ({100 * hit3 / count:.0f}%)"


def evaluate() -> str:
    base = load_config(ROOT / "config.yaml")
    config = base.model_copy(update={
        "runs_dir": RUNS_DIR,
        "stages": {**base.stages, **{name: True for name in STAGES}},
        "candidate_methods": {name: True for name in ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag")},
    })
    cases: list[dict] = []
    for scenario in DEFAULT_EVAL_SCENARIOS:
        generator = SCENARIO_GENERATORS[scenario]
        for seed in SEEDS:
            dataset = generator(seed)
            export = ROOT / "simulator" / "exports" / dataset.manifest.scenario_id / f"seed_{seed}" / "export"
            truth_path = ROOT / "simulator" / "sim_truth" / scenario / f"seed_{seed}.truth.json"
            write_export(dataset, export, truth_path)
            truth = json.loads(truth_path.read_text(encoding="utf-8"))
            true_service = str(truth["injected_fault"]["service"])
            run_digest = hashlib.sha256(f"{dataset.manifest.scenario_id}|{seed}|p2-eval".encode()).hexdigest()[:16]
            run_id = f"eval_{run_digest}"
            context = RunContext(run_id=run_id, scenario_id=dataset.manifest.scenario_id, runs_dir=RUNS_DIR, clock=config.simulation_clock, config=config)
            report = StageRunner(default_registry(config)).run(context, STAGES, {"folder": str(export)})
            stage = next(item for item in report.stages if item.stage == "s03_candidates")
            if stage.status.value == "FAILED":
                raise RuntimeError(f"S03 failed for scenario={scenario} seed={seed}: {stage.error}")
            analysis = stage.output["analysis"]
            s02 = next(item for item in report.stages if item.stage == "s02_signals").output
            from inquest.contracts import CanonicalBundle, SignalAnalysis

            bundle = CanonicalBundle.model_validate(s02["bundle"])
            signals = SignalAnalysis.model_validate(s02["analysis"])
            ranked: dict[str, list[str]] = {}
            for method in METHODS[:4]:
                ranked[method] = _ranked_services(analysis["per_method"].get(method, []))
            ranked["ensemble"] = _ranked_services(analysis.get("candidates", []))
            ranked["latest_change_before_alert"] = _latest_change(bundle, signals)
            ranked["alert_order"] = list(signals.service_order)
            cases.append({"scenario": scenario, "seed": seed, "true": true_service, "ranked": ranked, "ensemble_candidates": analysis.get("candidates", []), "method_status": {item["method"]: item["status"] for item in analysis["method_results"]}, "disagreement": analysis["disagreement"], "report_status": report.status.value})

    scenario_rows = []
    for scenario in DEFAULT_EVAL_SCENARIOS:
        scenario_cases = [case for case in cases if case["scenario"] == scenario]
        cells = []
        method_hits: dict[str, tuple[int, int]] = {}
        for method in METHODS:
            hit1 = sum(bool(case["ranked"][method]) and case["ranked"][method][0] == case["true"] for case in scenario_cases)
            hit3 = sum(case["true"] in case["ranked"][method][:3] for case in scenario_cases)
            method_hits[method] = (hit1, hit3)
            cells.append(f"{hit1}/{len(scenario_cases)}; {hit3}/{len(scenario_cases)}")
        ensemble_hits = method_hits["ensemble"][0]
        best_single_hits = max(method_hits[name][0] for name in METHODS[:4])
        best_baseline_hits = max(method_hits[name][0] for name in METHODS[-2:])
        single_lead = ensemble_hits - best_single_hits
        baseline_lead = ensemble_hits - best_baseline_hits
        flag = " [FLAG: lead <= 1 case]" if single_lead <= 1 or baseline_lead <= 1 else ""
        margin = f"single {single_lead:+d}; baseline {baseline_lead:+d}{flag}"
        scenario_rows.append("| " + " | ".join([scenario, str(len(scenario_cases)), *cells, margin]) + " |")

    summaries = []
    for method in METHODS:
        hit1 = sum(bool(case["ranked"][method]) and case["ranked"][method][0] == case["true"] for case in cases)
        hit3 = sum(case["true"] in case["ranked"][method][:3] for case in cases)
        summaries.append(f"| {method} | {_rate(hit1, hit3, len(cases))} |")

    details = []
    for case in cases:
        cells = []
        for method in METHODS:
            ranked = case["ranked"][method]
            predicted = ranked[0] if ranked else "—"
            cells.append(f"{predicted}{' [OK]' if predicted == case['true'] else ' [MISS]'}")
        true_rank = case["ranked"]["ensemble"].index(case["true"]) + 1 if case["true"] in case["ranked"]["ensemble"] else "not ranked"
        ensemble_candidates = case["ensemble_candidates"]
        top_margin = ensemble_candidates[0]["score"] - ensemble_candidates[1]["score"] if len(ensemble_candidates) > 1 else (ensemble_candidates[0]["score"] if ensemble_candidates else 0.0)
        details.append("| " + " | ".join([f"{case['scenario']} / {case['seed']}", case["true"], *cells, str(true_rank), f"{top_margin:.5f}"]) + " |")

    text = "\n".join([
        "# Candidate evaluation after P3 hardening",
        "",
        f"Default evaluation includes {len(DEFAULT_EVAL_SCENARIOS)} non-holdout scenarios x {len(SEEDS)} seeds = {len(cases)} cases. `simulator/scenarios/holdout/` is not registered, imported, or evaluated.",
        "",
        "## Per-scenario top-1 / top-3 hits and ensemble lead (seed hits)",
        "",
        "| Scenario | Seeds | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble | latest_change_before_alert | alert_order | Ensemble lead (cases) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        *scenario_rows,
        "",
        "Each method cell is `top-1 hits; top-3 hits`. Lead is ensemble top-1 cases minus the best single-method and best-baseline top-1 counts. Any lead of one case or less is flagged. Overall percentages are included only after the per-scenario table.",
        "",
        "## Overall top-1 / top-3",
        "",
        "| Method | Hits / cases (rate) top-1 / top-3 |",
        "|---|---:|",
        *summaries,
        "",
        "## Per-case top-1 predictions ([MISS] identifies misses)",
        "",
        "| Scenario / seed | Truth service | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble | latest_change_before_alert | alert_order | Ensemble true rank | Top-score margin |",
        "|---|---|---|---|---|---|---|---|---|---:|---:|",
        *details,
        "",
        "Evaluation uses truth only from `simulator/sim_truth/`; Inquest stages receive only opaque IDs and exported telemetry. No holdout data is read or used for tuning.",
        "",
    ])
    RESULT_PATH.write_text(text, encoding="utf-8")
    return text


if __name__ == "__main__":
    print(evaluate())
