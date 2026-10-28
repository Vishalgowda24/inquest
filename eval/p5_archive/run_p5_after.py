"""P5 post-change fresh evaluation runner; refuses an existing output root."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from inquest.core.builtins import default_registry
from inquest.core.config import load_config
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner

SCENARIOS=("clean_bad_deploy","coincident_restart","red_herring_deploy","shared_dependency","missing_telemetry","long_seasonal","late_alerting_cause","silent_cause","concurrent_causes","noisy_alerts","partial_graph","red_herring_hard")
RUNS=ROOT/"runs"/"p5_after"
if RUNS.exists(): raise SystemExit(f"refusing to overwrite {RUNS}")
base=load_config(ROOT/"config.yaml")
cfg=base.model_copy(update={"runs_dir":RUNS,"stages":{**base.stages,**{x:True for x in ("s00_ingest","s01_vault","s02_signals","s03_candidates","s04_verify")}},"candidate_methods":{x:True for x in ("change_based","graph_rwr","trace_ochiai","temporal_lag")},"verification_methods":{x:True for x in ("vault_evidence","dependency_path","temporal_consistency","recovery_check","alternative_check")},"verification_rerank":False})
for scenario in SCENARIOS:
 for seed in (4,5,6):
  truth=json.loads((ROOT/"simulator"/"sim_truth"/scenario/f"seed_{seed}.truth.json").read_text())
  export=ROOT/"simulator"/"exports"/truth["scenario_id"]/f"seed_{seed}"/"export"
  if not export.is_dir(): raise FileNotFoundError(export)
  run_id=f"p5_after_{scenario}_{seed}"
  ctx=RunContext(run_id=run_id,scenario_id=truth["scenario_id"],runs_dir=RUNS,clock=cfg.simulation_clock,config=cfg)
  report=StageRunner(default_registry(cfg)).run(ctx,("s00_ingest","s01_vault","s02_signals","s03_candidates","s04_verify"),{"folder":str(export)})
  if any(r.status.value=="FAILED" for r in report.stages): raise RuntimeError((scenario,seed,report.failed_stages))
  print(f"done {scenario}/{seed}",flush=True)
print("P5 post-change runs complete; outputs are isolated under",RUNS)
