"""Rebuild P9 final tables from committed, immutable per-case results."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
DEV_RECORD=json.loads((ROOT/"eval"/"p9_development_cases.json").read_text(encoding="utf-8"))
CONFIRM_RECORD=json.loads((ROOT/"eval"/"p9_confirmation_cases.json").read_text(encoding="utf-8"))
DEV=DEV_RECORD["cases"]
CONFIRM=CONFIRM_RECORD["cases"]


def hit(case:dict,method:str,k:int)->bool:
    return any(target in case["rankings"][method][:k] for target in case["truth"])


def report_table(title:str,cases:list[dict],methods:tuple[str,...]=( "v0","v3","alert_order"))->list[str]:
    lines=[f"## {title}","", "| Family | Cases | "+" | ".join(method.upper()+" top-1/top-3" for method in methods)+" |","|---|---:|"+"|".join("---" for _ in methods)+"|"]
    for family in sorted({case["scenario"] for case in cases}):
        group=[case for case in cases if case["scenario"]==family]
        entries=[]
        for method in methods:
            top1=sum(hit(case,method,1) for case in group); top3=sum(hit(case,method,3) for case in group)
            entries.append(f"{top1}/{len(group)} ({top3}/{len(group)})")
        lines.append("| "+" | ".join([family,str(len(group)),*entries])+" |")
    return lines+[""]


def write_config_tables()->None:
    for variant in ("v0","v1","v2","v3","v4"):
        matches=list((ROOT/"runs").glob(f"p9_development_{variant}_*"))
        if len(matches)!=1: raise RuntimeError(f"expected one development output root for {variant}, found {len(matches)}")
        output=matches[0]
        metadata=json.loads((output/"run_metadata.json").read_text(encoding="utf-8"))
        if metadata.get("variant")!=variant or not metadata.get("config_sha256","").startswith(output.name.rsplit("_",1)[-1]):
            raise RuntimeError(f"invalid output metadata for {output}")
        config=json.loads((output/"config.json").read_text(encoding="utf-8"))
        if config.get("fusion_variant")!=variant: raise RuntimeError(f"config mismatch in {output}")
        lines=[f"# Reproduced development table: {variant.upper()}","",f"Commit: `{metadata['commit']}`  ",f"Config SHA-256: `{metadata['config_sha256']}`","", "| Family | Cases | Top-1/top-3 |","|---|---:|---:|"]
        for family in sorted({case["scenario"] for case in DEV}):
            group=[case for case in DEV if case["scenario"]==family]
            lines.append(f"| {family} | {len(group)} | {sum(hit(case,variant,1) for case in group)}/{len(group)} ({sum(hit(case,variant,3) for case in group)}/{len(group)}) |")
        (output/"results_table.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    for variant in ("v0","v3"):
        matches=list((ROOT/"runs").glob(f"p9_confirmation_{variant}_*"))
        if len(matches)!=1: raise RuntimeError(f"expected one confirmation output root for {variant}, found {len(matches)}")
        output=matches[0]
        metadata=json.loads((output/"run_metadata.json").read_text(encoding="utf-8"))
        config=json.loads((output/"config.json").read_text(encoding="utf-8"))
        if metadata.get("variant")!=variant or config.get("fusion_variant")!=variant: raise RuntimeError(f"config mismatch in {output}")
        lines=[f"# Reproduced confirmation table: {variant.upper()}","",f"Commit: `{metadata['commit']}`  ",f"Config SHA-256: `{metadata['config_sha256']}`","", "| Family | Cases | Top-1/top-3 |","|---|---:|---:|"]
        for family in sorted({case["scenario"] for case in CONFIRM}):
            group=[case for case in CONFIRM if case["scenario"]==family]
            lines.append(f"| {family} | {len(group)} | {sum(hit(case,variant,1) for case in group)}/{len(group)} ({sum(hit(case,variant,3) for case in group)}/{len(group)}) |")
        (output/"results_table.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def main()->None:
    dev_by_key={(case["scenario"],case["seed"]):case for case in DEV}
    p5=json.loads((ROOT/"eval"/"p5_archive"/"p5_after_results.json").read_text(encoding="utf-8"))
    p7=json.loads((ROOT/"eval"/"p7_variance_cases.json").read_text(encoding="utf-8"))
    p6=json.loads((ROOT/"eval"/"p6_holdout_cases.json").read_text(encoding="utf-8"))
    fresh={(case["scenario"],case["seed"]) for case in p5+p7}
    # P4's predeclared four-family validation block: seeds 11, 29, and 47.
    fresh.update((family,seed) for family in ("concurrent_causes","noisy_alerts","partial_graph","red_herring_hard") for seed in (11,29,47))
    fresh_cases=[dev_by_key[key] for key in sorted(fresh) if key in dev_by_key]
    holdout_keys={(case["scenario"],case["seed"]) for case in p6}
    holdout=[dev_by_key[key] for key in sorted(holdout_keys)]
    all_development=DEV
    lines=["# P9 Final Summary Tables", "", "Selected default: V3 (per-case score-margin weighted RRF). The development block contains all 388 saved cases across seeds 1–51, including the already-seen P6 seeds 7–9. The P4–P7 fresh block is the union of P4 validation, P5 seeds 4–6, and P7 fresh cases (288 unique cases); it is nested within the development block. P6 seeds 7–9 are also shown separately as a nested block. Confirmation is the one-time seeds 52–71 run.", ""]
    lines+=report_table("Development (seeds 1–51; all 388 cases)",all_development)
    lines+=report_table("P4–P7 fresh blocks (unique union)",fresh_cases)
    lines+=report_table("P6 holdout seeds 7–9 (shown separately; already included in development)",holdout)
    lines+=report_table("P9 confirmation seeds 52–71",CONFIRM)
    total_v0=sum(hit(c,"v0",1) for c in CONFIRM); total_v3=sum(hit(c,"v3",1) for c in CONFIRM); total_alert=sum(hit(c,"alert_order",1) for c in CONFIRM)
    lines += ["## Confirmation totals", "",f"On 280 cases, V0 top-1={total_v0}/280, V3 top-1={total_v3}/280, alert_order top-1={total_alert}/280. See `p9_confirmation_results.md` for the preregistered two-way family×seed cluster-bootstrap intervals and exact config hashes.",""]
    output=ROOT/"eval"/"p9_final_summary.md"
    output.write_text("\n".join(lines),encoding="utf-8")
    # Rebuild both P9 evaluation reports from committed case-level result records;
    # this does not rerun Inquest stages or reuse the one-time confirmation seeds.
    from eval.run_p9_fusion import render_development
    from eval.run_p9_confirmation import bootstrap
    dev_report,selected,_=render_development(DEV,DEV_RECORD["commit"])
    (ROOT/"eval"/"p9_development_results.md").write_text(dev_report+"\n",encoding="utf-8")
    lines=["# P9 One-Time Confirmation (seeds 52–71)","",f"Commit: `{CONFIRM_RECORD['commit']}`  ",
           f"V0 config SHA-256: `{CONFIRM_RECORD['v0_config_sha256']}`; output `{CONFIRM_RECORD['v0_run_root']}`  ",
           f"V3 config SHA-256: `{CONFIRM_RECORD['v3_config_sha256']}`; output `{CONFIRM_RECORD['v3_run_root']}`  ",
           "Cases: 280 (14 families × 20 seeds). This is the only P9 confirmation run; no variants were re-selected afterward. Bootstrap intervals use 20,000 crossed family/seed cluster replicates, RNG seed 90909, and 95% percentile bounds.","",
           "## Per-family top-1/top-3","","| Family | Cases | V0 top-1/top-3 | V3 top-1/top-3 | alert_order top-1/top-3 | latest_change top-1/top-3 |","|---|---:|---:|---:|---:|---:|"]
    for family in sorted({case["scenario"] for case in CONFIRM}):
        group=[case for case in CONFIRM if case["scenario"]==family]
        values=[]
        for method in ("v0","v3","alert_order","latest_change_before_alert"):
            values.append(f"{sum(hit(case,method,1) for case in group)}/{len(group)} ({sum(hit(case,method,3) for case in group)}/{len(group)})")
        lines.append("| "+" | ".join([family,str(len(group)),*values])+" |")
    d0=bootstrap(CONFIRM,"v3","v0"); da=bootstrap(CONFIRM,"v3","alert_order")
    lines += ["","## Paired top-1 differences (two-way family × seed cluster bootstrap)","","| Comparison | Paired difference | 95% percentile interval |","|---|---:|---:|"]
    lines.append(f"| V3 − V0 | {d0[0]:+.3f} | [{d0[1]:+.3f}, {d0[2]:+.3f}] |")
    lines.append(f"| V3 − alert_order | {da[0]:+.3f} | [{da[1]:+.3f}, {da[2]:+.3f}] |")
    lines += ["",f"Plain result: on confirmation, V3 {'is no better than' if d0[0]<=0 else 'outperforms'} V0 at top-1 by {d0[0]:+.3f}/case; the interval {'includes' if d0[1]<=0<=d0[2] else 'excludes'} zero. Against alert_order, V3's paired difference is {da[0]:+.3f}, interval [{da[1]:+.3f}, {da[2]:+.3f}].","",
              "The complete per-case rankings and both config hashes are in `p9_confirmation_cases.json`.",""]
    (ROOT/"eval"/"p9_confirmation_results.md").write_text("\n".join(lines),encoding="utf-8")
    if selected!="v3": raise RuntimeError(f"re-rendered frozen development selection mismatch: {selected}")
    write_config_tables()
    print(f"Wrote {output.relative_to(ROOT)} from {len(DEV)} development, {len(fresh_cases)} P4–P7 fresh, {len(holdout)} P6 holdout, and {len(CONFIRM)} confirmation records.")


if __name__=="__main__":main()
