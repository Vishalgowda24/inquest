"""Fit the preregistered P10 confidence models on P9 development only."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT))
from inquest.contracts import CandidateMethodResult
from inquest.core.vault import read_vault_ids
from inquest.stages.s03_candidates.ensemble import rank_aggregate
from inquest.stages.s05_report.confidence import FEATURE_NAMES, extract_features


def _fit(x:np.ndarray,y:np.ndarray)->dict:
    mean=x.mean(axis=0); scale=x.std(axis=0,ddof=0); scale=np.where(scale==0,1.0,scale)
    z=(x-mean)/scale; n=len(y)
    def objective(theta):
        weights=theta[:-1]; intercept=theta[-1]
        logits=z@weights+intercept
        loss=np.logaddexp(0.0,logits)-y*logits
        prob=1.0/(1.0+np.exp(-np.clip(logits,-700,700)))
        grad_weights=z.T@(prob-y)/n+weights
        grad_intercept=float(np.mean(prob-y))
        return float(np.mean(loss)+0.5*np.dot(weights,weights)),np.r_[grad_weights,grad_intercept]
    initial=np.zeros(x.shape[1]+1)
    result=minimize(objective,initial,jac=True,method="L-BFGS-B",options={"maxiter":2000,"ftol":1e-9})
    if not result.success:
        raise RuntimeError(f"L-BFGS-B failed: {result.message}")
    return {"mean":mean.tolist(),"scale":scale.tolist(),"coefficients":result.x[:-1].tolist(),"intercept":float(result.x[-1]),
            "optimizer":{"name":"L-BFGS-B","maxiter":2000,"ftol":1e-9,"success":bool(result.success),"iterations":int(result.nit)}}


def main()->None:
    cases=json.loads((ROOT/"eval"/"p9_development_cases.json").read_text(encoding="utf-8"))["cases"]
    features=[]; labels=[]; case_ids=[]; margins=[]
    for case in cases:
        stage_path=ROOT/case["source_artifact"]
        run_dir=stage_path.parent.parent
        raw3=json.loads(stage_path.read_text(encoding="utf-8"))["output"]["analysis"]
        raw4=json.loads((run_dir/"04_s04_verify"/"output.json").read_text(encoding="utf-8"))["output"]["analysis"]
        raw2=json.loads((run_dir/"02_s02_signals"/"output.json").read_text(encoding="utf-8"))["output"]["analysis"]
        vault=read_vault_ids(run_dir/"vault"/"chain.jsonl")
        method_results=[CandidateMethodResult.model_validate(item) for item in raw3["method_results"]]
        fused,disagreement,abstentions=rank_aggregate(method_results,variant="v3",abstain_without_evidence=True)
        s03={**raw3,"candidates":[item.model_dump(mode="json") for item in fused],"disagreement":disagreement,"abstentions":abstentions}
        vector,detail=extract_features(s03,raw4,raw2,vault)
        features.append(vector); margins.append([vector[0]])
        labels.append(int(detail["target"] in case["truth"]) if detail["target"] else 0)
        case_ids.append(case["scenario_id"])
    x=np.asarray(features,dtype=float); y=np.asarray(labels,dtype=float)
    full=_fit(x,y); margin=_fit(np.asarray(margins,dtype=float),y)
    model={"version":"confidence_logistic_v1","feature_names":list(FEATURE_NAMES),"mean":full["mean"],"scale":full["scale"],
           "coefficients":full["coefficients"],"intercept":full["intercept"],"margin_baseline":{"mean":margin["mean"][0],"scale":margin["scale"][0],
           "coefficient":margin["coefficients"][0],"intercept":margin["intercept"]},"training_base_rate":float(y.mean()),
           "training_rows":len(y),"training_seeds":[1,51],"training_case_ids":sorted(case_ids),"training_successes":int(y.sum()),
           "regularization":{"kind":"L2","lambda":1.0,"intercept_penalized":False},"optimizer":full["optimizer"],
           "margin_optimizer":margin["optimizer"],"fit_source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()}
    path=ROOT/"inquest"/"models"/"confidence_logistic_v1.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    contents=json.dumps(model,indent=2,sort_keys=True)+"\n"
    path.write_text(contents,encoding="utf-8")
    print(f"trained_rows={len(y)} successes={int(y.sum())} base_rate={y.mean():.6f} sha256={hashlib.sha256(contents.encode()).hexdigest()}")
    print(f"optimizer={full['optimizer']}")


if __name__=="__main__":main()
