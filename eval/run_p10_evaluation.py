"""Run S05 once on seeds 72–91 and secondarily on saved seeds 52–71."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from eval.fit_p10_confidence import _fit
from inquest.contracts import StageInput
from inquest.core.artifacts import read_json
from inquest.core.builtins import default_registry
from inquest.core.config import load_config
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner
from inquest.core.vault import read_vault_ids
from inquest.stages.s05_report.confidence import predict_probability
from simulator.scenarios.registry import SCENARIO_GENERATORS

SEEDS_FRESH=tuple(range(72,92))
SEEDS_SECONDARY=tuple(range(52,72))
FULL_STAGES=["s00_ingest","s01_vault","s02_signals","s03_candidates","s04_verify","s05_report"]
P9_CASES_PATH=ROOT/"eval"/"p9_confirmation_cases.json"


def _hit(target,truth): return bool(target and target in truth)


def _record(case:dict,report:dict,model:dict,run_id:str,report_path:Path,mode:str)->dict:
    headline=report["headline"]; confidence=headline["confidence"]
    status=confidence.get("s04_status")
    onehot=[float(status==item) for item in ("verified","contested","insufficient_evidence","unsupported")]
    features=[float(confidence["margin"]),float(confidence["first_place_method_count"]),float(confidence["disagreement"]),*onehot,float(confidence["telemetry_gap"])]
    top=report["top_candidates"][0]["target"] if report["top_candidates"] else None
    p=float(confidence["probability"])
    base=float(model["training_base_rate"])
    margin_only=predict_probability(model,features,margin_only=True)
    # The stage's IE level is an exact recorded indicator that its required
    # evidence gate fired (telemetry gap or fewer than two producing methods).
    # Reuse that gate for the two probability baselines.
    condition={"telemetry_gap":bool(confidence["telemetry_gap"]),
        "methods_with_candidates":0 if confidence["level"]=="insufficient_evidence" and not confidence["telemetry_gap"] else 2}
    # Insufficient-evidence override also applies to baselines with the same missing-evidence condition.
    levels={"calibrated":confidence["level"]}
    from inquest.stages.s05_report.confidence import confidence_level
    for name,probability in (("constant",base),("margin_only",margin_only)):
        levels[name]=confidence_level(probability,telemetry_gap=condition["telemetry_gap"],methods_with_candidates=condition["methods_with_candidates"])
    return {"scenario":case["scenario"],"seed":case["seed"],"scenario_id":case["scenario_id"],"truth":case["truth"],"top1":top,
        "correct":_hit(top,case["truth"]),"probabilities":{"calibrated":p,"constant":base,"margin_only":margin_only},"levels":levels,
        "s04_status":status,"telemetry_gap":bool(confidence["telemetry_gap"]),"run_id":run_id,
        "report_path":str(report_path.relative_to(ROOT)),"mode":mode}


def _run_fresh_case(family:str,seed:int,ctx_config,runner,output_root:Path,commit:str,config_hash:str,model:dict)->dict:
    truth_path=ROOT/"simulator"/"sim_truth"/family/f"seed_{seed}.truth.json"
    truth=json.loads(truth_path.read_text(encoding="utf-8")); sid=truth["scenario_id"]
    export=ROOT/"simulator"/"p10_inputs"/sid/f"seed_{seed}"/"export"
    run_id="p10f_"+hashlib.sha256(f"{commit}|{config_hash}|{sid}|{seed}".encode()).hexdigest()[:18]
    context=RunContext(run_id=run_id,scenario_id=sid,runs_dir=output_root,clock=ctx_config.simulation_clock,config=ctx_config)
    pipeline=runner.run(context,FULL_STAGES,{"folder":str(export)})
    if pipeline.failed_stages:
        raise RuntimeError(f"S05 evaluation pipeline failed for {family}/{seed}: {pipeline.failed_stages}")
    stage_result=next(item for item in pipeline.stages if item.stage=="s05_report")
    if stage_result.status.value=="FAILED": raise RuntimeError(f"S05 failed for {family}/{seed}")
    run_dir=output_root/run_id
    report_path=run_dir/"05_s05_report"/"report.json"
    report=read_json(report_path)
    (run_dir/"run_metadata.json").write_text(json.dumps({"commit":commit,"config_sha256":config_hash,"scenario_id":sid,"seed":seed,"mode":"primary_fresh"},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    case={"scenario":family,"seed":seed,"scenario_id":sid,"truth":_true_services(truth.get("injected_fault"))}
    return _record(case,report,model,run_id,run_dir/"05_s05_report"/"report.md","primary_fresh")


def _true_services(value)->list[str]:
    items=value if isinstance(value,list) else [value]
    return [str(item["service"]) for item in items if isinstance(item,dict) and item.get("service")]


def _run_secondary_case(case:dict,source_run_root:Path,ctx_config,runner,output_root:Path,commit:str,config_hash:str,model:dict)->dict:
    source=source_run_root/case["run_id_v3"]
    run_id="p10s_"+hashlib.sha256(f"{commit}|{config_hash}|{case['scenario_id']}|{case['seed']}".encode()).hexdigest()[:18]
    destination=output_root/run_id
    if destination.exists(): raise FileExistsError(f"refusing to overwrite secondary run {destination}")
    destination.mkdir(parents=True)
    for folder in ("00_s00_ingest","01_s01_vault","02_s02_signals","03_s03_candidates","04_s04_verify","vault"):
        src=source/folder
        if not src.exists(): raise FileNotFoundError(f"secondary source artifact missing: {src}")
        shutil.copytree(src,destination/folder)
    metadata={"commit":commit,"config_sha256":config_hash,"scenario_id":case["scenario_id"],"seed":case["seed"],"mode":"secondary_saved_stages","source_run":case["run_id_v3"]}
    (destination/"run_metadata.json").write_text(json.dumps(metadata,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    context=RunContext(run_id=run_id,scenario_id=case["scenario_id"],runs_dir=output_root,clock=ctx_config.simulation_clock,config=ctx_config)
    result=runner.run_one(context,StageInput(stage="s05_report",payload={}),stage_index=5)
    if result.status.value=="FAILED": raise RuntimeError(f"secondary S05 failed for {case['scenario']}/{case['seed']}: {result.error}")
    report=read_json(destination/"05_s05_report"/"report.json")
    eval_case={"scenario":case["scenario"],"seed":case["seed"],"scenario_id":case["scenario_id"],"truth":case["truth"]}
    return _record(eval_case,report,model,run_id,destination/"05_s05_report"/"report.md","secondary_52_71")


def _scores(cases:list[dict],model_name:str)->tuple[float,float,float,dict]:
    y=np.asarray([int(case["correct"]) for case in cases],dtype=float)
    p=np.asarray([float(case["probabilities"][model_name]) for case in cases],dtype=float)
    brier=float(np.mean((p-y)**2)) if len(y) else 0.0
    bins=[]
    ece=0.0
    for index in range(10):
        mask=(p>=index/10)&((p<(index+1)/10) if index<9 else (p<=1.0))
        n=int(mask.sum())
        mean_p=float(p[mask].mean()) if n else None
        accuracy=float(y[mask].mean()) if n else None
        if n: ece+=(n/len(y))*abs(mean_p-accuracy)
        bins.append({"bin":f"[{index/10:.1f},{(index+1)/10:.1f}{']' if index==9 else ')'}","n":n,"mean_probability":mean_p,"accuracy":accuracy})
    return brier,float(ece),float(p.mean()) if len(p) else 0.0,{"reliability":bins}


def _level_table(cases:list[dict],probability_key:str="calibrated")->dict:
    counts=defaultdict(list)
    for case in cases:
        level=case["levels"][probability_key]
        counts[level].append(case)
    result={}
    for level in ("high","medium","low","insufficient_evidence"):
        group=counts.get(level,[])
        result[level]={"count":len(group),"coverage":len(group)/len(cases) if cases else 0.0,
            "accuracy":float(np.mean([case["correct"] for case in group])) if group else None}
    retained=[case for case in cases if case["levels"][probability_key] in {"high","medium"}]
    result["selective"]={"count":len(retained),"coverage":len(retained)/len(cases) if cases else 0.0,
        "accuracy":float(np.mean([case["correct"] for case in retained])) if retained else None}
    return result


def _dataset_metrics(cases:list[dict])->dict:
    result={}
    for model_name in ("calibrated","constant","margin_only"):
        brier,ece,mean_p,detail=_scores(cases,model_name)
        result[model_name]={"brier":brier,"ece":ece,"mean_probability":mean_p,**detail,"levels":_level_table(cases,model_name)}
    family_rows=[]
    for family in sorted({case["scenario"] for case in cases}):
        group=[case for case in cases if case["scenario"]==family]
        calibrated=result["calibrated"]
        levels=_level_table(group)
        family_rows.append({"family":family,"n":len(group),"accuracy":float(np.mean([x["correct"] for x in group])),
            "mean_probability":float(np.mean([x["probabilities"]["calibrated"] for x in group])),
            "brier":_scores(group,"calibrated")[0],"ece":_scores(group,"calibrated")[1],
            "high":levels["high"]["count"],"medium":levels["medium"]["count"],"low":levels["low"]["count"],
            "insufficient":levels["insufficient_evidence"]["count"],"selective_coverage":levels["selective"]["coverage"],
            "selective_accuracy":levels["selective"]["accuracy"],
            "constant_brier":_scores(group,"constant")[0],"constant_ece":_scores(group,"constant")[1],
            "margin_brier":_scores(group,"margin_only")[0],"margin_ece":_scores(group,"margin_only")[1]})
    result["families"]=family_rows
    result["confident_wrong"]=[{key:case[key] for key in ("scenario","seed","scenario_id","truth","top1","probabilities","levels")}
        for case in cases if case["levels"]["calibrated"]=="high" and not case["correct"]]
    result["special_families"]={}
    for family in ("silent_cause","late_alerting_cause","red_herring_deploy"):
        group=[case for case in cases if case["scenario"]==family]
        accuracy=float(np.mean([case["correct"] for case in group])) if group else None
        mean_probability=float(np.mean([case["probabilities"]["calibrated"] for case in group])) if group else None
        result["special_families"][family]={"n":len(group),"accuracy":accuracy,"mean_probability":mean_probability,
            "overstated":bool(mean_probability is not None and accuracy is not None and mean_probability>accuracy),
            "high_count":sum(case["levels"]["calibrated"]=="high" for case in group),
            "high_wrong":sum(case["levels"]["calibrated"]=="high" and not case["correct"] for case in group)}
    return result


def _render_dataset(name:str,cases:list[dict],metrics:dict)->list[str]:
    lines=[f"## {name}","", "### Per-family calibration and selective accuracy", "", "| Family | n | Accuracy | Mean p | Cal Brier/ECE | Const Brier/ECE | Margin Brier/ECE | High | Med | Low | Insuff | Selective coverage | Selective accuracy |","|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in metrics["families"]:
        lines.append(f"| {row['family']} | {row['n']} | {row['accuracy']:.3f} | {row['mean_probability']:.3f} | {row['brier']:.3f}/{row['ece']:.3f} | {row['constant_brier']:.3f}/{row['constant_ece']:.3f} | {row['margin_brier']:.3f}/{row['margin_ece']:.3f} | {row['high']} | {row['medium']} | {row['low']} | {row['insufficient']} | {row['selective_coverage']:.3f} | {row['selective_accuracy'] if row['selective_accuracy'] is not None else 'n/a'} |")
    lines += ["", "### Overall calibration scores", "", "| Confidence model | Cases | Brier | ECE | Mean probability |", "|---|---:|---:|---:|---:|"]
    for model in ("calibrated","constant","margin_only"):
        info=metrics[model]; lines.append(f"| {model} | {len(cases)} | {info['brier']:.4f} | {info['ece']:.4f} | {info['mean_probability']:.4f} |")
    lines += ["", "### Reliability table (fixed ten probability bins)", "", "| Model | Bin | n | Mean probability | Empirical accuracy |", "|---|---|---:|---:|---:|"]
    for model in ("calibrated","constant","margin_only"):
        for row in metrics[model]["reliability"]:
            lines.append(f"| {model} | {row['bin']} | {row['n']} | {row['mean_probability'] if row['mean_probability'] is not None else '—'} | {row['accuracy'] if row['accuracy'] is not None else '—'} |")
    lines += ["", "### Confidence-level accuracy and coverage", "", "| Model | Level | n | Coverage | Top-1 accuracy |", "|---|---|---:|---:|---:|"]
    for model in ("calibrated","constant","margin_only"):
        for level,info in metrics[model]["levels"].items():
            lines.append(f"| {model} | {level} | {info['count']} | {info['coverage']:.3f} | {info['accuracy'] if info['accuracy'] is not None else 'n/a'} |")
    lines += ["", "### High-confidence wrong cases", ""]
    if metrics["confident_wrong"]:
        lines += ["| Family | Seed | True cause(s) | Top candidate | Probability |", "|---|---:|---|---|---:|"]
        for case in metrics["confident_wrong"]:
            lines.append(f"| {case['scenario']} | {case['seed']} | {', '.join(case['truth'])} | {case['top1']} | {case['probabilities']['calibrated']:.3f} |")
    else: lines.append("None.")
    lines += ["", "### Silent, late-alert, and red-herring cases", "", "| Family | n | Accuracy | Mean probability | Probability overstated? | High | High and wrong |", "|---|---:|---:|---:|---|---:|---:|"]
    for family,info in metrics["special_families"].items():
        lines.append(f"| {family} | {info['n']} | {info['accuracy'] if info['accuracy'] is not None else 'n/a'} | {info['mean_probability'] if info['mean_probability'] is not None else 'n/a'} | {'yes' if info['overstated'] else 'no'} | {info['high_count']} | {info['high_wrong']} |")
    return lines+[""]


def main()->None:
    config_path=ROOT/"config.yaml"; config=load_config(config_path)
    config_hash=hashlib.sha256(config_path.read_bytes()).hexdigest()
    model_path=config.confidence_model_path if config.confidence_model_path.is_absolute() else ROOT/config.confidence_model_path
    model=json.loads(model_path.read_text(encoding="utf-8"))
    commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    fresh_root=ROOT/"runs"/f"p10_fresh_v3_{config_hash[:8]}"; secondary_root=ROOT/"runs"/f"p10_secondary_v3_{config_hash[:8]}"
    for root in (fresh_root,secondary_root):
        if root.exists(): raise FileExistsError(f"refusing to overwrite P10 evaluation root {root}")
        root.mkdir(parents=True)
        (root/"config.json").write_text(config_path.read_text(encoding="utf-8"),encoding="utf-8")
        (root/"run_metadata.json").write_text(json.dumps({"commit":commit,"config_sha256":config_hash,"mode":root.name,"case_count":280},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    runner=StageRunner(default_registry(config))
    fresh=[]
    for family in SCENARIO_GENERATORS:
        for seed in SEEDS_FRESH:
            truth=ROOT/"simulator"/"sim_truth"/family/f"seed_{seed}.truth.json"
            if not truth.exists(): raise FileNotFoundError(f"missing committed P10 truth {truth}")
            fresh.append(_run_fresh_case(family,seed,config,runner,fresh_root,commit,config_hash,model))
            if len(fresh)%40==0: print(f"fresh S05: {len(fresh)}/280",flush=True)
    p9=json.loads(P9_CASES_PATH.read_text(encoding="utf-8"))
    p9_root=ROOT/p9["v3_run_root"]
    secondary=[]
    for case in p9["cases"]:
        secondary.append(_run_secondary_case(case,p9_root,config,runner,secondary_root,commit,config_hash,model))
        if len(secondary)%40==0: print(f"secondary S05: {len(secondary)}/280",flush=True)
    fresh_metrics=_dataset_metrics(fresh); secondary_metrics=_dataset_metrics(secondary)
    report=["# P10 Calibrated Confidence Evaluation", "",f"Run commit: `{commit}`  ",f"Config SHA-256: `{config_hash}`  ",f"Confidence model SHA-256: `{config.confidence_model_sha256}`  ",
        "Primary evaluation: seeds 72–91 (280 cases). Secondary check: seeds 52–71 (280 cases), not used for fitting. Holdout seeds 7–9 were not run.",""]
    report+=_render_dataset("Primary fresh evaluation: seeds 72–91",fresh,fresh_metrics)
    report+=_render_dataset("Secondary evaluation: seeds 52–71",secondary,secondary_metrics)
    report += ["## Plain results", "",f"On seeds 72–91 the calibrated model has Brier {fresh_metrics['calibrated']['brier']:.4f} and ECE {fresh_metrics['calibrated']['ece']:.4f}; constant baseline Brier/ECE {fresh_metrics['constant']['brier']:.4f}/{fresh_metrics['constant']['ece']:.4f}; margin-only {fresh_metrics['margin_only']['brier']:.4f}/{fresh_metrics['margin_only']['ece']:.4f}.",
        f"Selective top-1 after withholding low and insufficient-evidence cases is {fresh_metrics['calibrated']['levels']['selective']['accuracy'] if fresh_metrics['calibrated']['levels']['selective']['accuracy'] is not None else 'n/a'} at coverage {fresh_metrics['calibrated']['levels']['selective']['coverage']:.3f}; full top-1 is {np.mean([case['correct'] for case in fresh]):.3f}.",
        "These are synthetic-only calibration results; no model refit or threshold adjustment occurred after the fresh evaluation.", ""]
    (ROOT/"eval"/"p10_evaluation_results.md").write_text("\n".join(report),encoding="utf-8")
    (ROOT/"eval"/"p10_evaluation_cases.json").write_text(json.dumps({"commit":commit,"config_sha256":config_hash,"model_sha256":config.confidence_model_sha256,
        "fresh":{"cases":fresh,"metrics":fresh_metrics},"secondary":{"cases":secondary,"metrics":secondary_metrics}},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    examples_dir=ROOT/"docs"/"examples"; examples_dir.mkdir(parents=True,exist_ok=True)
    example_specs=[("clean_bad_deploy",lambda case: True,"clean_bad_deploy"),
        ("silent_cause",lambda case:not case["correct"],"silent_cause_wrong"),
        ("missing_telemetry",lambda case: True,"missing_telemetry")]
    for family,predicate,label in example_specs:
        choices=[case for case in fresh if case["scenario"]==family and predicate(case)]
        if not choices: raise RuntimeError(f"No requested P10 example found for {family}")
        chosen=choices[0]
        src_json=ROOT/chosen["report_path"].replace("report.md","report.json")
        src_md=ROOT/chosen["report_path"]
        (examples_dir/f"{label}_seed_{chosen['seed']}.json").write_bytes(src_json.read_bytes())
        (examples_dir/f"{label}_seed_{chosen['seed']}.md").write_bytes(src_md.read_bytes())
    print(f"P10 evaluation complete: fresh={len(fresh)} secondary={len(secondary)} config_sha256={config_hash}")


if __name__=="__main__":main()
