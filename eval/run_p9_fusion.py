"""Evaluate preregistered fusion variants from saved S03 artifacts and truths."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
from inquest.contracts import CandidateMethodResult, CanonicalBundle, SignalAnalysis
from inquest.stages.s03_candidates.ensemble import rank_aggregate

VARIANTS = ("v0", "v1", "v2", "v3", "v4")
SCORED_METHODS = ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag", "v0", "v1", "v2", "v3", "v4", "latest_change_before_alert", "alert_order")
BASE_CONFIG = json.loads(subprocess.check_output([sys.executable, "-c", "import yaml,json;print(json.dumps(yaml.safe_load(open('config.yaml'))))"], cwd=ROOT, text=True))


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def candidate_targets(items) -> list[str]:
    result=[]
    for item in items:
        target=(item.service or item.target) if item.target_type == "change" else item.target
        if target not in result: result.append(target)
    return result


def latest_change(bundle: CanonicalBundle, signals: SignalAnalysis) -> list[str]:
    if not signals.onsets: return []
    onset=min(item.onset_time for item in signals.onsets)
    uncertainty=max((item.timestamp_uncertainty_ms for item in signals.onsets), default=0)/1000
    eligible=[event for event in bundle.changes if event.timestamp and (event.timestamp-onset).total_seconds() <= uncertainty]
    return [max(eligible,key=lambda event:(event.timestamp,event.id)).service] if eligible else []


def alert_order(bundle: CanonicalBundle, signals: SignalAnalysis) -> list[str]:
    alerts=[item for item in bundle.logs if item.attributes.get("alert_emission") is True]
    if alerts:
        return list(dict.fromkeys(item.service for item in sorted(alerts,key=lambda item:(item.timestamp,item.id)) if item.service))
    return list(signals.service_order)


def truths(record: dict) -> list[str]:
    value=record.get("injected_fault", [])
    items=value if isinstance(value,list) else [value]
    return [str(item["service"]) for item in items if isinstance(item,dict) and item.get("service")]


def scan_saved_cases() -> list[dict]:
    truth_by_id={}
    truth_path_by_key={}
    for path in (ROOT/"simulator"/"sim_truth").rglob("*.truth.json"):
        record=json.loads(path.read_text(encoding="utf-8"))
        key=(path.parent.name,int(record["seed"]))
        truth_by_id[record["scenario_id"]]=key
        truth_path_by_key[key]=path
    priority=("p9_confirm", "p8_alert_audit", "p7_variance", "p6_holdout", "p5_after", "p4_development", "p4_validation", "p3b_eval", "p5_before", "p2_eval")
    selected={}
    for path in (ROOT/"runs").rglob("03_s03_candidates/output.json"):
        try:
            s03=json.loads(path.read_text(encoding="utf-8"))
            run_dir=path.parent.parent
            ingest=json.loads((run_dir/"00_s00_ingest"/"input.json").read_text(encoding="utf-8"))
            match=re.search(r"scn_[a-f0-9]{12}",str(ingest.get("payload",{}).get("folder","")))
            if not match or match.group(0) not in truth_by_id: continue
            key=truth_by_id[match.group(0)]
            analysis=s03.get("output",{}).get("analysis",{})
            methods=analysis.get("method_results",[])
            if not methods or not analysis.get("per_method"): continue
            name=run_dir.parent.name
            rank=next((len(priority)-i for i,value in enumerate(priority) if value in name),0)
            # Within an artifact family, prefer the most recently completed saved run.
            stamp=(rank,path.stat().st_mtime_ns)
            if key not in selected or stamp>selected[key][0]:
                selected[key]=(stamp,path,match.group(0))
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            continue
    missing=sorted(set(truth_path_by_key)-set(selected))
    if missing:
        raise RuntimeError(f"Saved per-method S03 scores missing for {len(missing)} cases: {missing[:20]}")
    cases=[]
    for key,(stamp,path,scenario_id) in sorted(selected.items()):
        family,seed=key
        run_dir=path.parent.parent
        truth=json.loads(truth_path_by_key[key].read_text(encoding="utf-8"))
        s03=json.loads(path.read_text(encoding="utf-8"))["output"]["analysis"]
        method_results=[CandidateMethodResult.model_validate(item) for item in s03["method_results"]]
        s00=json.loads((run_dir/"00_s00_ingest"/"output.json").read_text(encoding="utf-8"))["output"]
        s02=json.loads((run_dir/"02_s02_signals"/"output.json").read_text(encoding="utf-8"))["output"]
        bundle=CanonicalBundle.model_validate(s00["bundle"])
        signal=SignalAnalysis.model_validate(s02["analysis"])
        rankings={name:candidate_targets(s03.get("per_method",{}).get(name,[])) for name in ("change_based","graph_rwr","trace_ochiai","temporal_lag")}
        for variant in VARIANTS:
            fused,_,_=rank_aggregate(method_results,variant=variant,abstain_without_evidence=True)
            rankings[variant]=candidate_targets(fused)
        rankings["latest_change_before_alert"]=latest_change(bundle,signal)
        rankings["alert_order"]=alert_order(bundle,signal)
        cases.append({"scenario":family,"seed":seed,"scenario_id":scenario_id,"truth":truths(truth),"rankings":rankings,
                      "candidate_count":len(rankings["v0"]),"source_artifact":str(path.relative_to(ROOT)),"source_run":run_dir.name})
    return cases


def hit(case:dict, method:str, k:int)->bool:
    return any(target in case["rankings"][method][:k] for target in case["truth"])


def family_summary(cases:list[dict], methods= SCORED_METHODS) -> list[str]:
    lines=["| Family | Cases | "+" | ".join(method.upper()+" top-1/top-3" for method in methods)+" |", "|---|---:|"+"|".join("---" for _ in methods)+"|"]
    for family in sorted({case["scenario"] for case in cases}):
        group=[case for case in cases if case["scenario"]==family]
        cells=[]
        for method in methods:
            top1=sum(hit(case,method,1) for case in group); top3=sum(hit(case,method,3) for case in group)
            cells.append(f"{top1}/{len(group)} ({top3}/{len(group)})")
        lines.append("| "+" | ".join([family,str(len(group)),*cells])+" |")
    return lines


def render_development(cases:list[dict], commit:str) -> str:
    methods=("change_based","graph_rwr","trace_ochiai","temporal_lag","v0","v1","v2","v3","v4","latest_change_before_alert","alert_order")
    family_scores={variant:np.mean([np.mean([hit(case,variant,1) for case in cases if case["scenario"]==family]) for family in sorted({case["scenario"] for case in cases})]) for variant in VARIANTS}
    v0_top3=sum(hit(case,"v0",3) for case in cases)
    guard={variant:{family:sum(hit(case,variant,1) for case in cases if case["scenario"]==family and 10<=case["seed"]<=29) for family in ("red_herring_deploy","shared_dependency")} for variant in VARIANTS}
    eligible=[variant for variant in VARIANTS if sum(hit(case,variant,3) for case in cases)>=v0_top3 and all(guard[variant][family]>=guard["v0"][family]-1 for family in guard[variant])]
    best=max(eligible,key=lambda variant:(family_scores[variant],-int(variant[1:]))) if eligible else "v0"
    selected=best if family_scores[best]-family_scores["v0"]>=.02 else "v0"
    lines=["# P9 Development Fusion Evaluation", "",f"Evaluation code commit: `{commit}`  ",f"Cases: {len(cases)} across {len({case['scenario'] for case in cases})} families; seed range in source records: 1–51. All saved truth-confirmed cases available at evaluation time are included.","", "No S03 method, evidence rule, threshold, or status rule was changed. Variant formula and selection rule were committed before evaluation in `DECISIONS.md`.","", "## Full per-family table (top-1 / top-3)",""]
    lines+=family_summary(cases,methods)
    lines += ["", "## Family-equal selection calculation", "", "| Variant | Family-equal top-1 | Aggregate top-3 | red_herring_deploy top-1 (seeds 10–29) | shared_dependency top-1 (seeds 10–29) | Eligible |", "|---|---:|---:|---:|---:|---|"]
    for variant in VARIANTS:
        elig=variant in eligible
        lines.append(f"| {variant.upper()} | {family_scores[variant]:.4f} | {sum(hit(case,variant,3) for case in cases)}/{len(cases)} | {guard[variant]['red_herring_deploy']}/20 | {guard[variant]['shared_dependency']}/20 | {'yes' if elig else 'no'} |")
    lines += ["",f"Selection under frozen rule: **{selected.upper()}**. Highest eligible family-equal top-1 is {family_scores[best]:.4f}; V0 is {family_scores['v0']:.4f}; improvement is {family_scores[best]-family_scores['v0']:+.4f}. Minimum required gain is 0.0200. No confirmation data has been read or generated at this point.","", "## V0 misses where graph_rwr ranks a true cause first", "", "| Family | Seed | Opaque scenario ID | Truth label(s) | V0 rank(s) | graph_rwr rank(s) | V0 top-1 |", "|---|---:|---|---|---|---|---|"]
    for case in cases:
        if hit(case,"v0",1): continue
        graph_ranks=[case["rankings"]["graph_rwr"].index(target)+1 if target in case["rankings"]["graph_rwr"] else "—" for target in case["truth"]]
        if 1 not in graph_ranks: continue
        v0_ranks=[case["rankings"]["v0"].index(target)+1 if target in case["rankings"]["v0"] else "—" for target in case["truth"]]
        lines.append("| "+" | ".join([case["scenario"],str(case["seed"]),case["scenario_id"],", ".join(case["truth"]),", ".join(map(str,v0_ranks)),", ".join(map(str,graph_ranks)),case["rankings"]["v0"][0] if case["rankings"]["v0"] else "—"])+" |")
    lines += ["", "## P6/P7 noisy-alert onset timing", "", "| Block | Cause alert before injected fault | Cases | Ensemble top-1 conditional on before-onset cause alert |", "|---|---:|---:|---:|"]
    for label,record_file in (("P6 seeds 7–9","p6_holdout_cases.json"),("P7 fresh block","p7_variance_cases.json")):
        p6p7=json.loads((ROOT/"eval"/record_file).read_text(encoding="utf-8"))
        subset=[case for case in p6p7 if case["scenario"]=="noisy_alerts"]
        before=[]
        for case in subset:
            truth=json.loads((ROOT/"simulator"/"sim_truth"/case["scenario"]/f"seed_{case['seed']}.truth.json").read_text(encoding="utf-8"))
            before.append(int(truth["alert_schedule"]["database"]<truth["injected_fault"]["start_step"]))
        successes=sum(before[i] and hit({"truth":case["truth"],"rankings":case["rankings"]},"ensemble",1) for i,case in enumerate(subset))
        lines.append(f"| {label} | {sum(before)}/{len(before)} ({sum(before)/len(before):.3f}) | {len(before)} | {successes}/{sum(before)} ({successes/sum(before):.3f}) |" if sum(before) else f"| {label} | 0/{len(before)} | {len(before)} | n/a |")
    lines += ["", "The primary P6/P7 baseline ensemble is the saved V0 RRF from each original run; these conditional figures use the matching original ensemble rankings, not a re-evaluated variant.", ""]
    return "\n".join(lines),selected,{v:float(family_scores[v]) for v in VARIANTS}


def main():
    commit=git_head()
    cases=scan_saved_cases()
    result,selected,scores=render_development(cases,commit)
    (ROOT/"eval"/"p9_development_results.md").write_text(result+"\n",encoding="utf-8")
    summary={"commit":commit,"case_count":len(cases),"selected_variant":selected,"family_equal_top1":scores,"cases":cases}
    (ROOT/"eval"/"p9_development_cases.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    for variant in VARIANTS:
        effective={**BASE_CONFIG,"fusion_variant":variant}
        config_text=json.dumps(effective,indent=2,sort_keys=True)+"\n"
        config_hash=hashlib.sha256(config_text.encode()).hexdigest()
        out=ROOT/"runs"/f"p9_development_{variant}_{config_hash[:8]}"
        if out.exists(): raise SystemExit(f"refusing to overwrite {out}")
        out.mkdir(parents=True)
        (out/"config.json").write_text(config_text,encoding="utf-8")
        (out/"run_metadata.json").write_text(json.dumps({"commit":commit,"config_sha256":config_hash,"variant":variant,"case_count":len(cases),"artifact_kind":"offline recomputation from saved per-method S03 results"},indent=2,sort_keys=True)+"\n",encoding="utf-8")
        (out/"cases.json").write_text(json.dumps([{**case,"variant_ranking":case["rankings"][variant]} for case in cases],indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"development_cases={len(cases)} selected={selected} commit={commit}")


if __name__=="__main__": main()
