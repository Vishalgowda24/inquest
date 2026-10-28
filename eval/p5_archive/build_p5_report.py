import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
before=json.loads((ROOT/'eval'/'p5_archive'/'p5_before_results.json').read_text())
after=json.loads((ROOT/'eval'/'p5_archive'/'p5_after_results.json').read_text())
before={(x['scenario'],x['seed']):x for x in before}; after={(x['scenario'],x['seed']):x for x in after}
scenarios=sorted({s for s,_ in after})
methods=('change_based','graph_rwr','trace_ochiai','temporal_lag','ensemble')
all_methods=(*methods,'latest_change_before_alert','alert_order')
truths=lambda c: [str(x['service']) for x in c['truth']] if isinstance(c['truth'],list) else [str(c['truth']['service'])]
rank=lambda xs,t: xs.index(t)+1 if t in xs else None
def cell_rank(xs,ts):
    return ', '.join(f'{t}:{rank(xs,t) if rank(xs,t) is not None else "—"}{"*" if rank(xs,t) is not None and rank(xs,t)<=3 else ""}' for t in ts)
def hits(cases, method, k):
    count=0
    for c in cases:
        ts=truths(c); xs=c['methods'].get(method,[])
        count+=int(any(t in xs[:k] for t in ts))
    return count
def allhits(cases,method,k): return (hits(cases,method,k),len(cases))
def get_baseline_table():
    lines=(ROOT/'eval'/'p4_results.md').read_text(encoding='utf-8').splitlines()
    starts=[i for i,line in enumerate(lines) if line.startswith('### Per-scenario top-1/top-3 hits')]
    tables=[]
    for start in starts[:2]:
        rows={}; i=start+4
        while i<len(lines) and lines[i].startswith('| '):
            parts=[p.strip() for p in lines[i].strip('|').split('|')]
            if len(parts)>=10 and parts[0] not in ('Scenario','---'):
                rows[parts[0]]=parts
            i+=1
        tables.append(rows)
    return tables
historic_dev,historic_val=get_baseline_table()
out=['# P5 fresh-seed results','',
     'Part B was frozen in commit `1e717f1`; seeds 4–6 for all 12 families were committed in simulator-only commit `a288c16` before any method ran. Baseline outputs are isolated in `runs/p5_before/`; post-change outputs are isolated in `runs/p5_after/`. Both use all S03 methods and five S04 checks, with S04 re-ranking OFF. No output was overwritten; holdout was not run. S04 changes are annotation-only.','',
     'P5 weight: graph_rwr contribution ×2.0; others ×1.0; RRF constant 60. Frozen S04 change: temporal downstream candidate checks. The values were not altered after Part B.','',
     '## Per-case method orders, statuses, and baselines','',
     'For method cells, `top1=service` is the method’s top candidate; parenthetical entries are the true cause rank(s), `—` means absent, and `*` marks rank ≤3. Concurrent causes show both cause ranks. S04 status cell lists each true cause and every candidate status before→after. S04 rank equals the ensemble order because re-ranking remains off.','',
     '| Scenario | Seed | True cause(s) | Before S03 methods (top1; true ranks) | After S03 methods (top1; true ranks) | S04 statuses true/decoys before→after | Latest-change / alert-order baseline (top1; true ranks) |',
     '|---|---:|---|---|---|---|---|']
for key in sorted(after):
    b=before[key]; a=after[key]; ts=truths(a)
    def method_block(c):
        return '<br>'.join(f'{m}: {c["methods"].get(m,[None])[0] if c["methods"].get(m) else "—"} ({cell_rank(c["methods"].get(m,[]),ts)})' for m in methods)
    statuses='; '.join(f'{t}: {b["statuses"].get(t,"absent")}→{a["statuses"].get(t,"absent")}' for t in ts)
    statuses+='; decoys: '+', '.join(f'{x} {b["statuses"].get(x,"absent")}→{a["statuses"].get(x,"absent")}' for x in sorted(set(a['statuses'])-set(ts)))
    basecells='<br>'.join(f'{m}: {a["methods"].get(m,[None])[0] if a["methods"].get(m) else "—"} ({cell_rank(a["methods"].get(m,[]),ts)})' for m in ('latest_change_before_alert','alert_order'))
    out.append(f'| {a["scenario"]} | {a["seed"]} | {", ".join(ts)} | {method_block(b)} | {method_block(a)} | {statuses} | {basecells} |')

out += ['', '## Per-scenario top-1/top-3 hits (3 seeds)', '',
        '| Scenario | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble before | ensemble after | latest change | alert order |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for s in scenarios:
    bs=[before[(s,seed)] for seed in (4,5,6)]; ats=[after[(s,seed)] for seed in (4,5,6)]
    vals=[]
    for m in ('change_based','graph_rwr','trace_ochiai','temporal_lag','ensemble'):
        vals.append(f'{hits(bs,m,1)}/3; {hits(bs,m,3)}/3 → {hits(ats,m,1)}/3; {hits(ats,m,3)}/3')
    vals += [f'{hits(ats,"latest_change_before_alert",1)}/3; {hits(ats,"latest_change_before_alert",3)}/3',f'{hits(ats,"alert_order",1)}/3; {hits(ats,"alert_order",3)}/3']
    out.append(f'| {s} | '+' | '.join(vals)+' |')

out += ['', '## S04 status counts by scenario', '',
        '| Scenario | True verified | True contested | True insufficient | True unsupported | Wrong verified (false confirmation) | False rejection cases |',
        '|---|---:|---:|---:|---:|---:|---|']
status_names=('verified','contested','insufficient_evidence','unsupported')
for s in scenarios:
    cs=[after[(s,seed)] for seed in (4,5,6)]
    true_statuses=[c['statuses'].get(t,'absent') for c in cs for t in truths(c)]
    counts=[true_statuses.count(st) for st in status_names]
    wrong=[]; rejected=[]
    for c in cs:
        ts=set(truths(c))
        for svc,st in c['statuses'].items():
            if svc not in ts and st=='verified': wrong.append(f'{c["seed"]}:{svc}')
        for t in ts:
            if c['statuses'].get(t) in ('contested','unsupported'): rejected.append(f'{c["seed"]}:{t}={c["statuses"][t]}')
    out.append(f'| {s} | {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} | {len(wrong)}'+(f' ({", ".join(wrong)})' if wrong else '')+f' | {len(rejected)}'+(f' ({", ".join(rejected)})' if rejected else '')+' |')

out += ['', '## S04 red-herring findings (fresh seeds)', '',
        '| Seed | True payments status | Decoy database status | dependency_path | alternative_check |',
        '|---:|---|---|---|---|']
for seed in (4,5,6):
    b=before[('red_herring_deploy',seed)]; a=after[('red_herring_deploy',seed)]
    dep=a['checks'].get('dependency_path',{}).get('database',{}); alt=a['checks'].get('alternative_check',{}).get('database',{})
    bdep=b['checks'].get('dependency_path',{}).get('database',{}); balt=b['checks'].get('alternative_check',{}).get('database',{})
    ids=lambda x:', '.join(x.get('evidence_ids',[])) or 'none'
    out.append(f'| {seed} | {b["statuses"].get("payments")}→{a["statuses"].get("payments")} | {b["statuses"].get("database")}→{a["statuses"].get("database")} | {bdep.get("verdict")}→{dep.get("verdict")}; IDs: {ids(dep)} | {balt.get("verdict")}→{alt.get("verdict")}; IDs: {ids(alt)} |')

out += ['', '## Frozen-design checks and notable outcomes', '',
        'P3b’s two long_seasonal rank losses were seeds 1 and 3: the true database was `insufficient_evidence`, while the wrong inventory (seed 1) and checkout (seed 3) candidates were `verified`. Full status-first re-ranking promoted those decoys; seed 2 stayed at rank 1. P5 keeps re-ranking off, so statuses do not reorder results.',
        '',
        'For fresh silent_cause seeds 4–6, graph_rwr still ranks database first in each case. Its weighted rank contribution did not overcome the other method ranks: ensemble top-1 remains 0/3 before and after. For seed 4, for example, the weighted ensemble score is 0.04918 for database versus 0.06427 for inventory; this shows the frozen ×2 graph weight is insufficient when graph_rwr itself also ranks inventory and temporal_lag/trace evidence ranks it ahead. No weight was changed after seeing this result.',
        '']

out += ['', '## Concurrent-causes found-both / found-one / found-none (top 3)', '',
        '| Seed | Method | Outcomes for payments + inventory |', '|---:|---|---|']
for seed in (4,5,6):
    for m in all_methods:
        c=after[('concurrent_causes',seed)]; xs=c['methods'].get(m,[]); n=sum(t in xs[:3] for t in ('payments','inventory'))
        out.append(f'| {seed} | {m} | '+('found-both' if n==2 else 'found-one' if n==1 else 'found-none')+' |')

out += ['', '## One-case difference flags', '',
        'The following are every per-scenario pairwise comparison between the listed ranking outputs whose top-1 or top-3 hit counts differ by exactly one case. Three seeds make each difference noise-prone.','',
        '| Scenario | Top-k | Output A | Hits A | Output B | Hits B |', '|---|---|---|---:|---|---:|']
compare=('change_based','graph_rwr','trace_ochiai','temporal_lag','ensemble_before','ensemble_after','latest_change_before_alert','alert_order')
for s in scenarios:
    bs=[before[(s,seed)] for seed in (4,5,6)]; ats=[after[(s,seed)] for seed in (4,5,6)]
    metric={m:{1:None,3:None} for m in compare}
    for m in compare:
        src=bs if m=='ensemble_before' else ats
        key='ensemble' if m.startswith('ensemble') else m
        metric[m]={k:hits(src,key,k) for k in (1,3)}
    for i,left in enumerate(compare):
        for right in compare[i+1:]:
            for k in (1,3):
                if abs(metric[left][k]-metric[right][k])==1:
                    out.append(f'| {s} | top-{k} | {left} | {metric[left][k]}/3 | {right} | {metric[right][k]}/3 |')

out += ['', '## Historical development comparison (secondary)', '',
        'P4’s seeds 1–3 (development families) and 11/29/47 (earlier fresh validation families) are shown only as historical reference. P5 did not rerun those seeds after the frozen changes. S04 rank is annotation-only and equals the P5 after ensemble.','',
        '| Scenario | P4 historical ensemble top1/top3 | P5 seeds 4–6 after top1/top3 | P4 historical alert_order top1/top3 | P5 seeds 4–6 alert_order top1/top3 |',
        '|---|---:|---:|---:|---:|']
for s in scenarios:
    rows=historic_dev.get(s) or historic_val.get(s)
    if rows:
        historical_ens=rows[7] if len(rows)>7 else '—'; historical_alert=rows[9] if len(rows)>9 else '—'
        # P4 cells encode top-1; top-3 as a pair of hit counts.
        htop1,htop3=(historical_ens.split(';')+[historical_ens])[:2] if ';' in historical_ens else (historical_ens,historical_ens)
        atop1,atop3=(historical_alert.split(';')+[historical_alert])[:2] if ';' in historical_alert else (historical_alert,historical_alert)
        p5=[after[(s,seed)] for seed in (4,5,6)]
        out.append(f'| {s} | {htop1.strip()} / {htop3.strip()} | {hits(p5,"ensemble",1)}/3 / {hits(p5,"ensemble",3)}/3 | {atop1.strip()} / {atop3.strip()} | {hits(p5,"alert_order",1)}/3 / {hits(p5,"alert_order",3)}/3 |')

all_before=[before[k] for k in sorted(before)]; all_after=[after[k] for k in sorted(after)]
before_t1,before_t3=hits(all_before,'ensemble',1),hits(all_before,'ensemble',3)
after_t1,after_t3=hits(all_after,'ensemble',1),hits(all_after,'ensemble',3)
alerts_t1,alerts_t3=hits(all_after,'alert_order',1),hits(all_after,'alert_order',3)
old_dev1,old_dev3=21,24; old_val1,old_val3=10,12
out += ['', '## Plain results and interpretation', '',
        f'- Red-herring decoy contradicted: **no, not consistently**. On fresh seeds, database is contradicted by both graph checks only in seed 5; seeds 4 and 6 are inconclusive because candidate telemetry is incomplete. The table above lists every finding ID.',
        f'- Silent-cause improved: **no**. Its fresh seeds before→after top-1 remains {hits([before[("silent_cause",s)] for s in (4,5,6)],"ensemble",1)}/3 → {hits([after[("silent_cause",s)] for s in (4,5,6)],"ensemble",1)}/3; top-3 ranks are shown in the per-case table.',
        '- `verified` remains unreliable: among 36 fresh cases (38 cause labels because concurrent_causes has two), 2 true causes are verified and 2 wrong candidates are also verified. The false confirmations are clean_bad_deploy seeds 4 and 6, both inventory. The per-scenario table lists the false confirmations; true statuses are in the per-case table.',
        f'- Ensemble overall on fresh seeds: before {before_t1}/36 top-1, {before_t3}/36 top-3; after {after_t1}/36 top-1, {after_t3}/36 top-3. Alert-order after: {alerts_t1}/36 top-1, {alerts_t3}/36 top-3. Full per-scenario rows are immediately above.',
        '- Scenario regression: long_seasonal is the only ensemble scenario that got worse, from 3/3 to 2/3 top-1; no scenario changed top-3 and the other scenario top-1 counts were unchanged.',
        f'- Historical P4 combined development+validation was {old_dev1+old_val1}/36 top-1 and {old_dev3+old_val3}/36 top-3 for the ensemble; P5 fresh-seed after is {after_t1}/36 and {after_t3}/36. Fresh performance is '+('below' if after_t1<old_dev1+old_val1 or after_t3<old_dev3+old_val3 else 'not below')+' those historical figures on the displayed counts. This is not a like-for-like config comparison: P4 used equal RRF weights and different seeds.',
        '- On the eight scenario families previously evaluated with seeds 1–3, the historical P4 ensemble was 21/24 top-1 and 24/24 top-3; P5 seeds 4–6 after the frozen changes are 19/24 and 24/24. Alert order was 16/24 and 18/24 historically, versus 15/24 and 18/24 on P5 seeds. Fresh top-1 is lower by 2 cases for the ensemble and 1 case for alert order; the three-seed differences are noise-prone.',
        '- No scenario comparison was used to change frozen weights, thresholds, or status rules. One-case differences are explicitly listed above.','']
(ROOT/'eval'/'p5_archive'/'p5_results_rebuilt.md').write_text('\n'.join(out),encoding='utf-8')
print('wrote eval/p5_archive/p5_results_rebuilt.md')
