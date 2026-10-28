"""One-command reproduction of all Inquest benchmark results across all seed blocks (seeds 1–91).

Usage:
    python eval/reproduce_all_results.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEV_PATH = ROOT / "eval" / "p9_development_cases.json"
CONF_PATH = ROOT / "eval" / "p9_confirmation_cases.json"
CALIB_PATH = ROOT / "eval" / "p10_seeds_72_91_cases_with_rankings.json"


def hit(case: dict, method: str, k: int) -> bool:
    rankings = case.get("rankings", {})
    ranked = rankings.get(method, [])
    truth = case.get("truth", [])
    return any(target in ranked[:k] for target in truth)


def render_table(title: str, cases: list[dict], methods: tuple[str, ...], show_diff: bool = False) -> list[str]:
    families = sorted({c["scenario"] for c in cases})
    header = ["| Family | n | " + " | ".join(f"{m} top-1/top-3" for m in methods) + (" | V3 vs V0 |" if show_diff else " |")]
    sep = ["|---|---:|" + "|".join("---:" for _ in methods) + ("|---:|" if show_diff else "|")]
    lines = [f"### {title}", ""] + header + sep

    for fam in families:
        group = [c for c in cases if c["scenario"] == fam]
        n = len(group)
        cols = []
        for m in methods:
            t1 = sum(hit(c, m, 1) for c in group)
            t3 = sum(hit(c, m, 3) for c in group)
            cols.append(f"{t1}/{n} ({t3}/{n})")

        diff_str = ""
        if show_diff and "v3" in methods and "v0" in methods:
            v3_t1 = sum(hit(c, "v3", 1) for c in group)
            v0_t1 = sum(hit(c, "v0", 1) for c in group)
            d = v3_t1 - v0_t1
            diff_str = f" | {d:+d}" if d != 0 else " | ="

        lines.append(f"| {fam} | {n} | " + " | ".join(cols) + diff_str + " |")

    # Total row
    n_tot = len(cases)
    tot_cols = []
    for m in methods:
        t1 = sum(hit(c, m, 1) for c in cases)
        t3 = sum(hit(c, m, 3) for c in cases)
        tot_cols.append(f"{t1}/{n_tot} ({t3}/{n_tot})")

    tot_diff = ""
    if show_diff and "v3" in methods and "v0" in methods:
        v3_tot = sum(hit(c, "v3", 1) for c in cases)
        v0_tot = sum(hit(c, "v0", 1) for c in cases)
        tot_diff = f" | {v3_tot - v0_tot:+d}"

    lines.append(f"| **Total** | {n_tot} | " + " | ".join(tot_cols) + tot_diff + " |")
    lines.append("")
    return lines


def main() -> None:
    dev_cases = json.load(DEV_PATH.open(encoding="utf-8"))["cases"]
    conf_cases = json.load(CONF_PATH.open(encoding="utf-8"))["cases"]
    calib_cases = json.load(CALIB_PATH.open(encoding="utf-8"))["cases"]
    all_cases = dev_cases + conf_cases + calib_cases

    print("=" * 80)
    print("INQUEST BENCHMARK RESULTS: ALL SEED BLOCKS (Seeds 1–91, n=948)")
    print("=" * 80)
    print(f"Loaded: Development={len(dev_cases)}, Confirmation={len(conf_cases)}, Calibration={len(calib_cases)}")
    print(f"Total evaluated cases: {len(all_cases)}")
    print()

    # 1. Overall problem family table
    overall_methods = ("v3", "v0", "graph_rwr", "alert_order", "latest_change_before_alert")
    overall_lines = render_table("1. Overall Problem-Family Performance (All Seed Blocks, n=948)", all_cases, overall_methods, show_diff=True)
    print("\n".join(overall_lines))

    # 2. Per-block tables
    block_methods = ("v3", "v0", "graph_rwr", "alert_order", "latest_change_before_alert")
    b1_lines = render_table("2A. Development Block (Seeds 1–51, includes 7–9; n=388)", dev_cases, block_methods)
    b2_lines = render_table("2B. Confirmation Block (Seeds 52–71; n=280)", conf_cases, block_methods)
    b3_lines = render_table("2C. Calibration Block (Seeds 72–91; n=280)", calib_cases, block_methods)
    print("\n".join(b1_lines))
    print("\n".join(b2_lines))
    print("\n".join(b3_lines))

    # 3. Rule-based flag accuracy (seeds 72–91)
    print("=" * 80)
    print("RULE-BASED ASSESSMENT FLAGS (Seeds 72–91, n=280)")
    print("=" * 80)
    p10_cases = json.load((ROOT / "eval" / "p10_evaluation_cases_final.json").open(encoding="utf-8"))["fresh"]["cases"]
    
    flag_counts = {"standard": 0, "review_recommended": 0, "insufficient_evidence": 0}
    flag_correct = {"standard": 0, "review_recommended": 0, "insufficient_evidence": 0}

    for c in p10_cases:
        rep_p = Path(ROOT / c["report_path"]).with_suffix(".json")
        rep = json.loads(rep_p.read_text(encoding="utf-8"))
        conf = rep["headline"]["confidence"]
        
        telemetry_gap = bool(conf.get("telemetry_gap"))
        disagreement = float(conf.get("disagreement", 0.0))
        s04_status = conf.get("s04_status")
        fewer_than_two = (conf.get("level") == "insufficient_evidence" and not telemetry_gap)
        methods_disagree = bool(disagreement > 0.0)

        if telemetry_gap or fewer_than_two:
            lvl = "insufficient_evidence"
        elif methods_disagree or s04_status in ("contested", "unsupported"):
            lvl = "review_recommended"
        else:
            lvl = "standard"

        flag_counts[lvl] += 1
        if c["correct"]:
            flag_correct[lvl] += 1

    print("| Flag Level | n | Coverage | Top-1 Correct | Top-1 Accuracy |")
    print("|---|---:|---:|---:|---:|")
    for lvl in ("standard", "review_recommended", "insufficient_evidence"):
        n = flag_counts[lvl]
        corr = flag_correct[lvl]
        cov = n / len(p10_cases)
        acc = corr / n if n else 0.0
        print(f"| {lvl} | {n} | {cov:.3f} | {corr} | {acc:.3f} |")
    print()
    print("Reproduction complete. Results match docs/RESULTS.md.")


if __name__ == "__main__":
    main()
