import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from inquest.core.builtins import default_registry
from inquest.core.config import load_config
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner

SCENARIOS=("clean_bad_deploy","coincident_restart","red_herring_deploy","shared_dependency","missing_telemetry","long_seasonal","late_alerting_cause","silent_cause","concurrent_causes","noisy_alerts","partial_graph","red_herring_hard")
SEEDS=(4,5,6)
RUNS=ROOT/"runs"/"p5_before"
if RUNS.exists(): raise SystemExit(f"refusing to overwrite {RUNS}")
base=load_config(ROOT/"config.yaml")
cfg=base.model_copy(update={"runs_dir":RUNS,"stages":{**base.stages,**{x:True for x in ("s00_ingest","s01_vault","s02_signals","s03_candidates","s04_verify")}},"candidate_methods":{x:True for x in ("change_based","graph_rwr","trace_ochiai","temporal_lag")},"verification_methods":{x:True for x in ("vault_evidence","dependency_path","temporal_consistency","recovery_check","alternative_check")},"verification_rerank":False})
cases=[]
for scenario in SCENARIOS:
 for seed in SEEDS:
  truth=json.loads((ROOT/"simulator"/"sim_truth"/scenario/f"seed_{seed}.truth.json").read_text())
  scenario_id=truth["scenario_id"]
  export=ROOT/"simulator"/"exports"/scenario_id/f"seed_{seed}"/"export"
  if not export.is_dir(): raise FileNotFoundError(export)
  run_id=f"p5_before_{scenario}_{seed}"
  ctx=RunContext(run_id=run_id,scenario_id=scenario_id,runs_dir=RUNS,clock=cfg.simulation_clock,config=cfg)
  report=StageRunner(default_registry(cfg)).run(ctx,("s00_ingest","s01_vault","s02_signals","s03_candidates","s04_verify"),{"folder":str(export)})
  outs={r.stage:r for r in report.stages}
  if outs["s03_candidates"].status.value=="FAILED" or outs["s04_verify"].status.value=="FAILED": raise RuntimeError((scenario,seed,report.failed_stages))
  a3=outs["s03_candidates"].output["analysis"]; a4=outs["s04_verify"].output["analysis"]
  def names(xs): return [x.get("service") or (x.get("target") if x.get("target_type")=="service" else None) for x in xs if x.get("service") or x.get("target_type")=="service"]
  methods={k:names(v) for k,v in a3.get("per_method",{}).items()}
  methods["ensemble"]=names(a3.get("candidates",[]))
  statuses={x["target"]:x["status"] for x in a4.get("decisions",[])}
  cases.append({"scenario":scenario,"seed":seed,"scenario_id":scenario_id,"truth":truth["injected_fault"],"methods":methods,"statuses":statuses,"candidate_count":len(a3.get("candidates",[]))})
  print(f"done {scenario}/{seed}")
(ROOT/"eval"/"p5_archive"/"p5_before_results.json").write_text(json.dumps(cases,indent=2),encoding="utf-8")
print(f"wrote {len(cases)} baseline cases under {RUNS}")
