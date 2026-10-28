import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0,str(ROOT))
from datetime import datetime
from inquest.contracts import CanonicalBundle, SignalAnalysis
scenarios=("clean_bad_deploy","coincident_restart","red_herring_deploy","shared_dependency","missing_telemetry","long_seasonal","late_alerting_cause","silent_cause","concurrent_causes","noisy_alerts","partial_graph","red_herring_hard")
cases=[]
for s in scenarios:
 for seed in (4,5,6):
  t=json.loads((ROOT/'simulator'/'sim_truth'/s/f'seed_{seed}.truth.json').read_text())
  run=ROOT/'runs'/'p5_before'/f'p5_before_{s}_{seed}'
  def output(stage): return json.loads((run/f'{stage}'/'output.json').read_text())['output']
  a3=output('03_s03_candidates')['analysis']; a4=output('04_s04_verify')['analysis']; s02=output('02_s02_signals')
  def names(xs): return [x.get('service') or x.get('target') for x in xs if x.get('service') or x.get('target_type')=='service']
  methods={k:names(v) for k,v in a3['per_method'].items()}; methods['ensemble']=names(a3['candidates'])
  methods['alert_order']=s02['analysis'].get('service_order',[])
  bundle=CanonicalBundle.model_validate(s02['bundle']); signals=SignalAnalysis.model_validate(s02['analysis'])
  latest=[]
  if signals.onsets:
   onset=min(x.onset_time for x in signals.onsets); tolerance=max((x.timestamp_uncertainty_ms for x in signals.onsets),default=0)/1000
   events=[e for e in bundle.changes if (e.timestamp-onset).total_seconds()<=tolerance]
   if events: latest=[max(events,key=lambda x:(x.timestamp,x.id)).service]
  methods['latest_change_before_alert']=latest
  cases.append({'scenario':s,'seed':seed,'scenario_id':t['scenario_id'],'truth':t['injected_fault'],'methods':methods,'statuses':{x['target']:x['status'] for x in a4['decisions']},'checks':{m:{f['target']:{'verdict':f['verdict'],'evidence_ids':f['evidence_ids']} for f in fs} for m,fs in a4['per_method'].items()},'candidate_count':len(a3['candidates']),'stage_status':{stage:json.loads((run/stage/'status.json').read_text())['status'] for stage in ('00_s00_ingest','01_s01_vault','02_s02_signals','03_s03_candidates','04_s04_verify')}})
(ROOT/'eval'/'p5_archive'/'p5_before_results.json').write_text(json.dumps(cases,indent=2),encoding='utf-8')
print('collected',len(cases),'already-written baseline runs')
