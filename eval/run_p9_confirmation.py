"""One-pass frozen V0/V3 confirmation run on seeds 52–71."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from eval.run_p9_fusion import alert_order, candidate_targets, latest_change, truths
from inquest.contracts import CanonicalBundle, SignalAnalysis
from inquest.core.builtins import default_registry
from inquest.core.config import load_config
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner
from simulator.scenarios.registry import SCENARIO_GENERATORS

BASE_CONFIG_PATH=ROOT/"config.yaml"
SEEDS=tuple(range(52,72))
STAGES=("s00_ingest","s01_vault","s02_signals","s03_candidates","s04_verify")
BASELINE_NAMES=("latest_change_before_alert","alert_order")


def hit(case:dict,method:str,k:int)->bool:
    return any(target in case["rankings"][method][:k] for target in case["truth"])


def config_for(variant:str):
    return load_config(BASE_CONFIG_PATH).model_copy(update={"fusion_variant":variant})


def config_payload(config)->dict:
    return config.model_dump(mode="json")


def config_hash(config)->str:
    encoded=json.dumps(config_payload(config),sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def run_variant(variant:str,commit:str)->tuple[list[dict],str,str]:
    config=config_for(variant)
    digest=config_hash(config)
    run_root=ROOT/"runs"/f"p9_confirmation_{variant}_{digest[:8]}"
    if run_root.exists(): raise FileExistsError(f"refusing to overwrite confirmation run root {run_root}")
    run_root.mkdir(parents=True)
    payload=json.dumps(config_payload(config),indent=2,sort_keys=True)+"\n"
    (run_root/"config.json").write_text(payload,encoding="utf-8")
    runner=StageRunner(default_registry(config))
    results=[]
    for index,(family,generator) in enumerate(SCENARIO_GENERATORS.items(),start=1):
        for seed in SEEDS:
            truth_path=ROOT/"simulator"/"sim_truth"/family/f"seed_{seed}.truth.json"
            truth_record=json.loads(truth_path.read_text(encoding="utf-8"))
            scenario_id=truth_record["scenario_id"]
            export=ROOT/"simulator"/"p9_inputs"/scenario_id/f"seed_{seed}"/"export"
            run_id=f"p9_{variant}_"+hashlib.sha256(f"{commit}|{digest}|{scenario_id}|{seed}".encode()).hexdigest()[:18]
            context=RunContext(run_id=run_id,scenario_id=scenario_id,runs_dir=run_root,clock=config.simulation_clock,config=config)
            report=runner.run(context,STAGES,{"folder":str(export)})
            if report.failed_stages:
                raise RuntimeError(f"pipeline failed for {family}/{seed}/{variant}: {report.failed_stages}")
            outputs={item.stage:item.output for item in report.stages}
            s00=outputs["s00_ingest"]; s02=outputs["s02_signals"]; s03=outputs["s03_candidates"]; s04=outputs["s04_verify"]
            bundle=CanonicalBundle.model_validate(s00["bundle"])
            signal=SignalAnalysis.model_validate(s02["analysis"])
            analysis=s03["analysis"]
            rankings={name:candidate_targets(analysis.get("per_method",{}).get(name,[])) for name in ("change_based","graph_rwr","trace_ochiai","temporal_lag")}
            rankings[variant]=candidate_targets(analysis.get("candidates",[]))
            rankings.update({"latest_change_before_alert":latest_change(bundle,signal),"alert_order":alert_order(bundle,signal)})
            results.append({"scenario":family,"seed":seed,"scenario_id":scenario_id,"truth":truths(truth_record),"rankings":rankings,
                            "statuses":{item["target"]:item["status"] for item in s04["analysis"].get("decisions",[])},
                            "candidate_count":len(analysis.get("candidates",[])),"run_id":run_id})
            if len(results)%40==0: print(f"{variant}: completed {len(results)}/280",flush=True)
    (run_root/"run_metadata.json").write_text(json.dumps({"commit":commit,"config_sha256":digest,"variant":variant,"case_count":len(results)},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (run_root/"cases.json").write_text(json.dumps(results,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return results,str(run_root.relative_to(ROOT)),digest


def bootstrap(cases:list[dict],selected:str,baseline:str,reps:int=20000)->tuple[float,float,float]:
    families=sorted({case["scenario"] for case in cases}); seeds=sorted({case["seed"] for case in cases})
    fi={family:i for i,family in enumerate(families)}; si={seed:i for i,seed in enumerate(seeds)}
    diffs=np.asarray([int(hit(case,selected,1))-int(hit(case,baseline,1)) for case in cases],dtype=float)
    rng=np.random.default_rng(90909)
    fm=rng.multinomial(len(families),[1/len(families)]*len(families),size=reps)
    sm=rng.multinomial(len(seeds),[1/len(seeds)]*len(seeds),size=reps)
    weights=fm[:,[fi[case["scenario"]] for case in cases]]*sm[:,[si[case["seed"]] for case in cases]]
    samples=(weights@diffs)/weights.sum(axis=1)
    return float(diffs.mean()),float(np.quantile(samples,.025)),float(np.quantile(samples,.975))


def main():
    commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    all_truth=list((ROOT/"simulator"/"sim_truth").glob("*/seed_52.truth.json"))
    if len(all_truth)!=len(SCENARIO_GENERATORS): raise RuntimeError("confirmation seeds are not complete; refusing the one-time run")
    for family in SCENARIO_GENERATORS:
        for seed in SEEDS:
            truth=json.loads((ROOT/"simulator"/"sim_truth"/family/f"seed_{seed}.truth.json").read_text(encoding="utf-8"))
            export=ROOT/"simulator"/"p9_inputs"/truth["scenario_id"]/f"seed_{seed}"/"export"
            if not export.is_dir(): raise RuntimeError(f"missing committed confirmation export {family}/{seed}")
    v0,root0,hash0=run_variant("v0",commit)
    v3,root3,hash3=run_variant("v3",commit)
    # The frozen selection is V3. Pair identical cases and preserve both config outputs.
    lookup={(case["scenario"],case["seed"]):case for case in v3}
    cases=[]
    for case in v0:
        other=lookup[(case["scenario"],case["seed"])]
        merged={**case,"rankings":{**case["rankings"],"v3":other["rankings"]["v3"]},"statuses_v3":other["statuses"],"run_id_v3":other["run_id"]}
        cases.append(merged)
    lines=["# P9 One-Time Confirmation (seeds 52–71)","",f"Commit: `{commit}`  ",f"V0 config SHA-256: `{hash0}`; output `{root0}`  ",f"V3 config SHA-256: `{hash3}`; output `{root3}`  ","Cases: 280 (14 families × 20 seeds). This is the only P9 confirmation run; no variants were re-selected afterward.","", "## Per-family top-1/top-3", "", "| Family | Cases | V0 top-1/top-3 | V3 top-1/top-3 | alert_order top-1/top-3 | latest_change top-1/top-3 |", "|---|---:|---:|---:|---:|---:|"]
    for family in sorted({case["scenario"] for case in cases}):
        group=[case for case in cases if case["scenario"]==family]
        counts=[]
        for method in ("v0","v3","alert_order","latest_change_before_alert"):
            k1=sum(hit(case,method,1) for case in group); k3=sum(hit(case,method,3) for case in group)
            counts.append(f"{k1}/{len(group)} ({k3}/{len(group)})")
        lines.append("| "+" | ".join([family,str(len(group)),*counts])+" |")
    for baseline in ("v0","alert_order"):
        pass
    delta0=bootstrap(cases,"v3","v0"); deltaa=bootstrap(cases,"v3","alert_order")
    lines += ["", "## Paired top-1 differences (two-way family × seed cluster bootstrap)", "", "| Comparison | Paired difference | 95% percentile interval |", "|---|---:|---:|"]
    lines.append(f"| V3 − V0 | {delta0[0]:+.3f} | [{delta0[1]:+.3f}, {delta0[2]:+.3f}] |")
    lines.append(f"| V3 − alert_order | {deltaa[0]:+.3f} | [{deltaa[1]:+.3f}, {deltaa[2]:+.3f}] |")
    lines += ["",f"Plain result: on confirmation, V3 {'is no better than' if delta0[0]<=0 else 'outperforms'} V0 at top-1 by {delta0[0]:+.3f}/case; the interval {'includes' if delta0[1]<=0<=delta0[2] else 'excludes'} zero. Against alert_order, V3's paired difference is {deltaa[0]:+.3f}, interval [{deltaa[1]:+.3f}, {deltaa[2]:+.3f}].", "", "## Per-case confirmation outcomes", "", "The full 280-row per-case table is stored with the committed report data `eval/p9_confirmation_cases.json`; each row includes V0, V3, both baselines, and run IDs for both one-pass configurations.", ""]
    (ROOT/"eval"/"p9_confirmation_results.md").write_text("\n".join(lines),encoding="utf-8")
    (ROOT/"eval"/"p9_confirmation_cases.json").write_text(json.dumps({"commit":commit,"v0_config_sha256":hash0,"v3_config_sha256":hash3,"v0_run_root":root0,"v3_run_root":root3,"cases":cases},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"confirmation complete: 280 cases; V0={root0}; V3={root3}")


if __name__=="__main__":main()
