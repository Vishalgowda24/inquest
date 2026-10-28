import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
cases=json.loads((ROOT/'eval'/'p5_archive'/'p5_after_results.json').read_text())
miss=[]
for c in cases:
    truth=c['truth']
    targets=[x['service'] for x in truth] if isinstance(truth,list) else [truth['service']]
    top=c['methods']['ensemble'][:1]
    if not any(x in top for x in targets): miss.append((c['scenario'],c['seed'],targets,top))
print('cases',len(cases),'misses',len(miss))
for row in miss: print(row)
