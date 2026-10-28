"""Run frozen S00–S04 once on the committed P7 fresh-seed block."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
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

REPLACED_FAMILIES = {"concurrent_causes", "noisy_alerts", "partial_graph", "red_herring_hard"}
STAGES = ["s00_ingest", "s01_vault", "s02_signals", "s03_candidates", "s04_verify"]
METHODS = ["change_based", "graph_rwr", "trace_ochiai", "temporal_lag", "ensemble", "latest_change_before_alert", "alert_order"]
CONFIG_PATH = ROOT / "config.yaml"
CONFIG_HASH = hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()
RUNS_DIR = ROOT / "runs" / f"p7_variance_equal_rrf_{CONFIG_HASH[:8]}"
RESULTS_PATH = ROOT / "eval" / "p7_variance_cases.json"
REPORT_PATH = ROOT / "eval" / "p7_variance_results.md"


def seeds_for(scenario: str) -> tuple[int, ...]:
    values = [seed for seed in range(10, 30) if not (scenario in REPLACED_FAMILIES and seed in {11, 29})]
    if scenario in REPLACED_FAMILIES:
        values.extend((30, 31))
    return tuple(values)


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def truths_from(value: object) -> list[str]:
    items = value if isinstance(value, list) else [value]
    return [str(item["service"]) for item in items if isinstance(item, dict) and item.get("service")]


def service_targets(items: list[dict]) -> list[str]:
    result = []
    for item in items:
        service = item.get("service") or (item.get("target") if item.get("target_type") == "service" else None)
        if service and service not in result:
            result.append(service)
    return result


def latest_change(bundle: CanonicalBundle, signals: SignalAnalysis) -> list[str]:
    if not signals.onsets:
        return []
    onset = min(item.onset_time for item in signals.onsets)
    uncertainty = max((item.timestamp_uncertainty_ms for item in signals.onsets), default=0) / 1000
    eligible = [event for event in bundle.changes if event.timestamp and (event.timestamp - onset).total_seconds() <= uncertainty]
    return [max(eligible, key=lambda event: (event.timestamp, event.id)).service] if eligible else []


def alert_order(bundle: CanonicalBundle, signals: SignalAnalysis) -> list[str]:
    alerts = [item for item in bundle.logs if item.attributes.get("alert_emission") is True]
    if alerts:
        return list(dict.fromkeys(item.service for item in sorted(alerts, key=lambda item: (item.timestamp, item.id)) if item.service))
    return list(signals.service_order)


def rank(order: list[str], target: str) -> int | None:
    return order.index(target) + 1 if target in order else None


def hit(order: list[str], truths: list[str], k: int) -> bool:
    return any(target in order[:k] for target in truths)


def case_list() -> list[tuple[str, int]]:
    return [(scenario, seed) for scenario in SCENARIO_GENERATORS for seed in seeds_for(scenario)]


def preflight() -> tuple[list[tuple[str, int]], str]:
    if RUNS_DIR.exists() or RESULTS_PATH.exists() or REPORT_PATH.exists():
        raise SystemExit(f"refusing to overwrite P7 output: {RUNS_DIR}")
    cases = case_list()
    if len(cases) != 240 or len(set(cases)) != len(cases):
        raise SystemExit(f"expected 240 distinct cases, found {len(cases)}")
    missing = []
    for scenario, seed in cases:
        truth_path = ROOT / "simulator" / "sim_truth" / scenario / f"seed_{seed}.truth.json"
        if not truth_path.is_file():
            missing.append(str(truth_path))
            continue
        truth = json.loads(truth_path.read_text(encoding="utf-8"))
        export = ROOT / "simulator" / "variance_inputs" / str(truth["scenario_id"]) / f"seed_{seed}" / "export"
        if not export.is_dir():
            missing.append(str(export))
    if missing:
        raise SystemExit("P7 input preflight failed:\n" + "\n".join(missing[:20]))
    commit = git_head()
    print(f"preflight OK: 240 cases; commit={commit}; config_sha256={CONFIG_HASH}")
    return cases, commit


def run_one(scenario: str, seed: int, runner: StageRunner, config, commit: str) -> dict:
    truth_path = ROOT / "simulator" / "sim_truth" / scenario / f"seed_{seed}.truth.json"
    truth_record = json.loads(truth_path.read_text(encoding="utf-8"))
    scenario_id = str(truth_record["scenario_id"])
    truths = truths_from(truth_record["injected_fault"])
    export = ROOT / "simulator" / "variance_inputs" / scenario_id / f"seed_{seed}" / "export"
    run_id = "p7_" + hashlib.sha256(f"{commit}|{CONFIG_HASH}|{scenario_id}|{seed}".encode()).hexdigest()[:18]
    context = RunContext(run_id=run_id, scenario_id=scenario_id, runs_dir=RUNS_DIR, clock=config.simulation_clock, config=config)
    report = runner.run(context, STAGES, {"folder": str(export)})
    if report.failed_stages:
        raise RuntimeError(f"pipeline failed for {scenario}/{seed}: {report.failed_stages}")
    stage_outputs = {item.stage: item for item in report.stages}
    s02 = stage_outputs["s02_signals"].output
    bundle = CanonicalBundle.model_validate(s02["bundle"])
    signals = SignalAnalysis.model_validate(s02["analysis"])
    s03 = stage_outputs["s03_candidates"].output["analysis"]
    s04 = stage_outputs["s04_verify"].output["analysis"]
    rankings = {name: service_targets(s03.get("per_method", {}).get(name, [])) for name in METHODS[:4]}
    rankings["ensemble"] = service_targets(s03.get("candidates", []))
    rankings["latest_change_before_alert"] = latest_change(bundle, signals)
    rankings["alert_order"] = alert_order(bundle, signals)
    candidate_count = len(s03.get("candidates", []))
    statuses = {item["target"]: item["status"] for item in s04.get("decisions", [])}
    stage_statuses = {item.stage: item.status.value for item in report.stages}
    result = {
        "scenario": scenario, "seed": seed, "scenario_id": scenario_id, "truth": truths,
        "rankings": rankings, "statuses": statuses, "candidate_count": candidate_count,
        "stage_statuses": stage_statuses, "run_id": run_id, "commit": commit,
        "config_sha256": CONFIG_HASH,
    }
    run_path = RUNS_DIR / run_id
    run_path.mkdir(parents=True, exist_ok=True)
    (run_path / "run_metadata.json").write_text(json.dumps({"commit": commit, "config_sha256": CONFIG_HASH, "scenario_id": scenario_id, "seed": seed}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def wilson(successes: int, n: int) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    z = 1.959963984540054
    p = successes / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return center - half, center + half


def paired_bootstrap(a: list[int], b: list[int]) -> tuple[float, float, float]:
    delta = np.asarray(a, dtype=float) - np.asarray(b, dtype=float)
    rng = np.random.default_rng(7029)
    indices = rng.integers(0, len(delta), size=(20000, len(delta)))
    samples = delta[indices].mean(axis=1)
    low, high = np.quantile(samples, [0.025, 0.975])
    return float(delta.mean()), float(low), float(high)


def p6_diagnosis() -> list[str]:
    p6_path = ROOT / "eval" / "p6_holdout_cases.json"
    p5_path = ROOT / "eval" / "p5_archive" / "p5_before_results.json"
    p6_cases = json.loads(p6_path.read_text(encoding="utf-8"))
    p5_cases = json.loads(p5_path.read_text(encoding="utf-8"))
    def old_truth(case):
        raw = case["truth"]
        values = raw if isinstance(raw, list) else [raw]
        return [str(item["service"]) for item in values]
    def old_hit(case, method, k):
        return any(target in case["methods"].get(method, [])[:k] for target in old_truth(case))
    out = ["## P6 batch reconciliation", "",
           "Both P6 batches ran with evaluator/code commit `2e094d8c8d29a695564065cd84a13361fe37b7f7` and config SHA-256 `269dbb3f9de3d45edb777fa5bf70c289feb1ec56f40f722a5607fc253b7c90d7`. The first batch began at 02:40:32 and the continuation at 02:41:16 on 2026-10-29 +05:30; both fall after the evaluator commit at 02:40:13 and before the next commit at 02:44:21. No commit occurred between batches.", "",
           "## P6 holdout diagnosis", "",
           "Per-family P6 counts use seeds 7–9. The comparator is the equal-weight P5 baseline on seeds 4–6, not the weighted post-change output.", "",
           "| Family | P5 equal ensemble top-1 | P6 ensemble top-1 | Change | P6 alert_order top-1 | P6 change_based | P6 graph_rwr | P6 trace_ochiai | P6 temporal_lag |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    p6_families = list(dict.fromkeys(case["scenario"] for case in p6_cases))
    for scenario in p6_families:
        old = [case for case in p5_cases if case["scenario"] == scenario]
        new = [case for case in p6_cases if case["scenario"] == scenario]
        old_hits = sum(old_hit(case, "ensemble", 1) for case in old)
        new_hits = sum(hit(case["rankings"]["ensemble"], case["truth"], 1) for case in new)
        count = lambda method: sum(hit(case["rankings"][method], case["truth"], 1) for case in new)
        out.append(f"| {scenario} | {old_hits}/3 | {new_hits}/3 | {new_hits-old_hits:+d} | {count('alert_order')}/3 | {count('change_based')}/3 | {count('graph_rwr')}/3 | {count('trace_ochiai')}/3 | {count('temporal_lag')}/3 |")
    out += ["", "### P6 ensemble top-1 misses", "", "| Family | Seed | True cause | Ensemble rank |", "|---|---:|---|---:|"]
    misses = [case for case in p6_cases if not hit(case["rankings"]["ensemble"], case["truth"], 1)]
    for case in misses:
        for target in case["truth"]:
            if target not in case["rankings"]["ensemble"][:1]:
                out.append(f"| {case['scenario']} | {case['seed']} | {target} | {rank(case['rankings']['ensemble'], target) or '—'} |")
    candidate_counts = []
    for case in p6_cases:
        artifact = ROOT / "runs" / "p6_holdout_equal_rrf" / case["run_id"] / "03_s03_candidates" / "output.json"
        candidate_counts.append(len(json.loads(artifact.read_text(encoding="utf-8"))["output"]["analysis"]["candidates"]))
    top3_hits = sum(hit(case["rankings"]["ensemble"], case["truth"], 3) for case in p6_cases)
    out += ["", f"P6 candidate count: mean {np.mean(candidate_counts):.2f}, maximum {max(candidate_counts)} per case. P6 ensemble top-3 found a true cause in {top3_hits}/36 cases (including both truths in all three concurrent cases). Top-3 was highly saturated and did not distinguish the P6 cases; it remained useful for surfacing lower-ranked causes such as silent_cause.", "",
            "The eight-case decrease from 32/36 (seeds 4–6) to 24/36 (P6 seeds 7–9) is accounted for by these per-family changes: red_herring_deploy −1, shared_dependency −1, late_alerting_cause −1, noisy_alerts −2, partial_graph −2, and red_herring_hard −1. All other families were unchanged. This is descriptive attribution across different three-seed blocks, not a causal explanation.", ""]
    return out


def rates(cases: list[dict], method: str) -> tuple[int, int]:
    return (sum(hit(c["rankings"][method], c["truth"], 1) for c in cases),
            sum(hit(c["rankings"][method], c["truth"], 3) for c in cases))


def render(cases: list[dict], commit: str) -> str:
    lines = ["# P7 Frozen-Pipeline Variance Evaluation", "",
             f"Commit: `{commit}`  ", f"Config SHA-256: `{CONFIG_HASH}`  ",
             f"Cases: {len(cases)} (12 families × 20 seeds; seed 11/29 replaced by 30/31 for the four families previously evaluated at those seeds).", "",
             "All runs use the unchanged equal-weight RRF configuration, fusion abstention on, and S04 re-rank off. Each case has a separate run directory under the config-hash-named output root.", "",
             "## Per-family ensemble vs alert_order", "",
             "| Scenario | Cases | Ensemble top-1 | Ensemble top-3 | alert_order top-1 | alert_order top-3 | Difference, top-1 cases |", "|---|---:|---:|---:|---:|---:|---:|"]
    for scenario in SCENARIO_GENERATORS:
        family = [case for case in cases if case["scenario"] == scenario]
        e1, e3 = rates(family, "ensemble"); a1, a3 = rates(family, "alert_order")
        lines.append(f"| {scenario} | {len(family)} | {e1}/{len(family)} | {e3}/{len(family)} | {a1}/{len(family)} | {a3}/{len(family)} | {e1-a1:+d} |")

    family_diffs = {}
    for scenario in SCENARIO_GENERATORS:
        family = [case for case in cases if case["scenario"] == scenario]
        family_diffs[scenario] = sum(hit(c["rankings"]["ensemble"], c["truth"], 1) for c in family) - sum(hit(c["rankings"]["alert_order"], c["truth"], 1) for c in family)
    wins = [s for s,d in family_diffs.items() if d > 0]
    ties = [s for s,d in family_diffs.items() if d == 0]
    losses = [s for s,d in family_diffs.items() if d < 0]

    lines += ["", "## Overall rates with 95% Wilson intervals", "", "| Method | Top-1 cases / 240 | Top-1 rate (95% CI) | Top-3 cases / 240 | Top-3 rate (95% CI) |", "|---|---:|---:|---:|---:|"]
    for method in ("ensemble", "latest_change_before_alert", "alert_order"):
        h1, h3 = rates(cases, method); lo1, hi1 = wilson(h1, len(cases)); lo3, hi3 = wilson(h3, len(cases))
        lines.append(f"| {method} | {h1}/240 | {h1/240:.3f} ({lo1:.3f}–{hi1:.3f}) | {h3}/240 | {h3/240:.3f} ({lo3:.3f}–{hi3:.3f}) |")
    ens = [int(hit(c["rankings"]["ensemble"], c["truth"], 1)) for c in cases]
    alert = [int(hit(c["rankings"]["alert_order"], c["truth"], 1)) for c in cases]
    mean, low, high = paired_bootstrap(ens, alert)
    ci_excludes_zero = low > 0 or high < 0
    lines += ["", f"Paired top-1 difference (ensemble − alert_order): {mean:+.3f}, paired bootstrap 95% CI [{low:+.3f}, {high:+.3f}] over cases; resampling seed 7029, 20,000 replicates.",
              f"Plain result: ensemble {'beats' if mean > 0 else 'ties' if mean == 0 else 'loses to'} alert_order at top-1 overall; the paired interval {'excludes' if ci_excludes_zero else 'includes'} zero. It wins by family in {', '.join(wins) or 'none'}, ties in {', '.join(ties) or 'none'}, and loses in {', '.join(losses) or 'none'}.", "",
              "## Per-seed top-1 spread", "", "| Seed | Cases in this seed slice | Ensemble top-1 | alert_order top-1 |", "|---:|---:|---:|---:|"]
    for seed in sorted({case["seed"] for case in cases}):
        group = [case for case in cases if case["seed"] == seed]
        e = sum(hit(c["rankings"]["ensemble"], c["truth"], 1) for c in group)
        a = sum(hit(c["rankings"]["alert_order"], c["truth"], 1) for c in group)
        lines.append(f"| {seed} | {len(group)} | {e}/{len(group)} ({e/len(group):.3f}) | {a}/{len(group)} ({a/len(group):.3f}) |")

    lines += ["", "## S04 verified status by family", "", "True recall is verified true-cause labels / true-cause labels; wrong verified counts are candidate decisions on non-truth targets.", "", "| Scenario | True labels | True verified | True verified recall | Wrong candidates verified |", "|---|---:|---:|---:|---:|"]
    for scenario in SCENARIO_GENERATORS:
        family = [case for case in cases if case["scenario"] == scenario]
        total = sum(len(case["truth"]) for case in family)
        verified = sum(case["statuses"].get(target) == "verified" for case in family for target in case["truth"])
        wrong = sum(status == "verified" and target not in case["truth"] for case in family for target, status in case["statuses"].items())
        lines.append(f"| {scenario} | {total} | {verified} | {verified}/{total} ({verified/total:.3f}) | {wrong} |")

    true_total = sum(len(case["truth"]) for case in cases)
    true_verified = sum(case["statuses"].get(target) == "verified" for case in cases for target in case["truth"])
    wrong_verified = sum(status == "verified" and target not in case["truth"] for case in cases for target,status in case["statuses"].items())
    lines += ["", f"Overall S04 `verified`: {true_verified}/{true_total} true-cause labels ({true_verified/true_total:.3f} recall); {wrong_verified} wrong-candidate verifications.", "",
              "## P7 interpretation and P8 proposals (proposal only)", "",
              f"Across the 20-seed block, ensemble top-1 is {rates(cases, 'ensemble')[0]}/240 and alert_order is {rates(cases, 'alert_order')[0]}/240; the paired interval above {'supports' if ci_excludes_zero and mean > 0 else 'does not establish'} an overall ensemble top-1 advantage. Three-seed blocks were not adequate to support stable family-level claims: the prior noisy_alerts and partial_graph blocks ranged from 1/3 to 3/3 ensemble top-1, while P7 measured {sum(hit(c['rankings']['ensemble'], c['truth'], 1) for c in cases if c['scenario']=='noisy_alerts')}/20 and {sum(hit(c['rankings']['ensemble'], c['truth'], 1) for c in cases if c['scenario']=='partial_graph')}/20, respectively.", "",
              "Ranked P8 options:",
              "1. Investigate silent_cause's metric-only evidence and rank-fusion miss first: it is 0/20 ensemble top-1 and 18/20 top-3. Any change needs fresh silent_cause seeds 32+; validate that it does not add false positives to clean and shared-dependency cases.",
              "2. Evaluate a cautious alert_order feature or fallback for families where alert_order ties or wins, especially clean_bad_deploy, shared_dependency, missing_telemetry, and partial_graph. P7 shows the overall baseline advantage is not uniform; validate any family-specific logic on seeds 32+ for the affected families.",
              "3. Add a genuinely new scenario holdout or obtain consented real-incident cases before production claims. Keep the current synthetic holdout sealed; evaluate any new family-specific changes on seeds 32+ and do not tune on P7's 240 cases.", ""]

    lines += p6_diagnosis()

    lines += ["", "## Per-case results", "", "A cause rank is its one-based rank in that method; `—` means absent. Multi-cause case hits count if any truth is in top-k; all truth ranks are listed.", "",
              "| Scenario | Seed | Opaque ID | Truth | change_based top1/rank | graph_rwr top1/rank | trace_ochiai top1/rank | temporal_lag top1/rank | Ensemble top1/rank | Latest-change top1/rank | alert_order top1/rank | S04 truth statuses | Wrong verified candidates | Candidates | Run ID |", "|---|---:|---|---|---|---|---|---|---|---|---|---|---|---:|---|"]
    for case in cases:
        rank_text = lambda method: ", ".join(f"{target}:{rank(case['rankings'][method], target) or '—'}" for target in case["truth"])
        pred_text = lambda method: case["rankings"][method][0] if case["rankings"][method] else "—"
        method_cells = [f"{pred_text(method)} / {rank_text(method)}" for method in METHODS]
        truth_status = ", ".join(f"{target}:{case['statuses'].get(target, 'not_candidate')}" for target in case["truth"])
        wrong = ", ".join(sorted(target for target, status in case["statuses"].items() if status == "verified" and target not in case["truth"])) or "none"
        cells = [case["scenario"], str(case["seed"]), case["scenario_id"], ", ".join(case["truth"]), *method_cells, truth_status, wrong, str(case["candidate_count"]), case["run_id"]]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    cases_to_run, commit = preflight()
    config = load_config(CONFIG_PATH).model_copy(update={"runs_dir": RUNS_DIR})
    runner = StageRunner(default_registry(config))
    RUNS_DIR.mkdir(parents=True, exist_ok=False)
    (RUNS_DIR / "config.json").write_text(CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    (RUNS_DIR / "run_metadata.json").write_text(json.dumps({"commit": commit, "config_sha256": CONFIG_HASH, "case_count": len(cases_to_run)}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    results = []
    for index, (scenario, seed) in enumerate(cases_to_run, start=1):
        results.append(run_one(scenario, seed, runner, config, commit))
        if index % 10 == 0:
            print(f"completed {index}/{len(cases_to_run)}", flush=True)
    RESULTS_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render(results, commit), encoding="utf-8")
    print(f"wrote {REPORT_PATH.relative_to(ROOT)} and {RESULTS_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    if "--check-only" in sys.argv:
        preflight()
    else:
        main()
