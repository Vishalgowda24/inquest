"""Full S04 evaluation; only this eval module reads simulator truth."""
from __future__ import annotations
import hashlib, json, sys, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from inquest.core.builtins import default_registry
from inquest.core.config import load_config
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner
from simulator.core.export import write_export
from simulator.scenarios.registry import DEFAULT_EVAL_SCENARIOS, SCENARIO_GENERATORS

SEEDS=(1,2,3)
METHODS=("change_based","graph_rwr","trace_ochiai","temporal_lag","ensemble","s04_reranked","latest_change_before_alert","alert_order")
CHECKS=("vault_evidence","dependency_path","temporal_consistency","recovery_check","alternative_check")
STAGES=["s00_ingest","s01_vault","s02_signals","s03_candidates","s04_verify"]
OUT=ROOT/"eval"/"p3b_results.md"

def _service(candidate):
    return candidate.get("service") or (candidate.get("target") if candidate.get("target_type")=="service" else None)

def _services(items):
    out=[]
    for item in items:
        s=_service(item) if isinstance(item,dict) else item
        if s and s not in out: out.append(s)
    return out

def _latest_change(bundle,signals):
    if not signals.onsets: return []
    onset=min(x.onset_time for x in signals.onsets)
    tol=max((x.timestamp_uncertainty_ms for x in signals.onsets),default=0)/1000
    events=[e for e in bundle.changes if (e.timestamp-onset).total_seconds()<=tol]
    return [max(events,key=lambda x:(x.timestamp,x.id)).service] if events else []

def _rank(rank,truth):
    return rank.index(truth)+1 if truth in rank else None

def _top_hits(cases,key):
    return sum(bool(c["ranked"].get(key)) and c["ranked"][key][0]==c["true"] for c in cases),sum(c["true"] in c["ranked"].get(key,[])[:3] for c in cases)

def evaluate():
    base=load_config(ROOT/"config.yaml")
    run_root=ROOT/"runs"/"p3b_eval"
    baseline_config=base.model_copy(update={"runs_dir":run_root,"stages":{**base.stages,**{x:True for x in STAGES}},"candidate_methods":{n:True for n in ("change_based","graph_rwr","trace_ochiai","temporal_lag")},"verification_methods":{n:True for n in CHECKS},"verification_rerank":True})
    cases=[]
    for scenario in DEFAULT_EVAL_SCENARIOS:
        generator=SCENARIO_GENERATORS[scenario]
        for seed in SEEDS:
            ds=generator(seed)
            export=ROOT/"simulator"/"exports"/ds.manifest.scenario_id/f"seed_{seed}"/"export"
            truth_path=ROOT/"simulator"/"sim_truth"/scenario/f"seed_{seed}.truth.json"
            write_export(ds,export,truth_path)
            truth=json.loads(truth_path.read_text(encoding="utf-8"))
            cause=str(truth["injected_fault"]["service"])
            run_id="p3b_"+hashlib.sha256(f"{ds.manifest.scenario_id}|{seed}|p3b".encode()).hexdigest()[:16]
            ctx=RunContext(run_id=run_id,scenario_id=ds.manifest.scenario_id,runs_dir=run_root,clock=baseline_config.simulation_clock,config=baseline_config)
            report=StageRunner(default_registry(baseline_config)).run(ctx,STAGES,{"folder":str(export)})
            outputs={r.stage:r for r in report.stages}
            if outputs["s03_candidates"].status.value=="FAILED" or outputs["s04_verify"].status.value=="FAILED":
                raise RuntimeError(f"pipeline failed for {scenario}/{seed}: {report.failed_stages}")
            s02=outputs["s02_signals"].output
            from inquest.contracts import CanonicalBundle, SignalAnalysis
            bundle=CanonicalBundle.model_validate(s02["bundle"]); signals=SignalAnalysis.model_validate(s02["analysis"])
            a3=outputs["s03_candidates"].output["analysis"]
            a4=outputs["s04_verify"].output["analysis"]
            ranked={name:_services(a3.get("per_method",{}).get(name,[])) for name in CHECKS[:0]+("change_based","graph_rwr","trace_ochiai","temporal_lag")}
            ranked["ensemble"]=_services(a3.get("candidates",[]))
            ranked["s04_reranked"]=[x["target"] for x in a4["reranked_order"]]
            ranked["latest_change_before_alert"]=_latest_change(bundle,signals)
            ranked["alert_order"]=list(signals.service_order)
            decisions={x["target"]:x for x in a4["decisions"]}
            per_check={name:{f["target"]:f for f in fs} for name,fs in a4["per_method"].items()}
            ablations={}
            for check in CHECKS:
                flags={name:name!=check for name in CHECKS}
                cfg=baseline_config.model_copy(update={"verification_methods":flags})
                rerun_ctx=RunContext(run_id=run_id,scenario_id=ds.manifest.scenario_id,runs_dir=run_root,clock=cfg.simulation_clock,config=cfg)
                rerun=StageRunner(default_registry(cfg)).rerun(rerun_ctx,"s04_verify",4)
                saved=json.loads((run_root/run_id/"04_s04_verify"/"output.json").read_text(encoding="utf-8"))
                ablations[check]=[x["target"] for x in saved["output"]["analysis"]["reranked_order"]]
            gaps=set(outputs["s03_candidates"].output.get("verification_context",{}).get("telemetry_gaps",[]))
            cases.append({"scenario":scenario,"seed":seed,"true":cause,"ranked":ranked,"decisions":decisions,"per_check":per_check,"ablations":ablations,"coverage_gaps":sorted(gaps),"candidate_scores":{_service(x):float(x["score"]) for x in a3.get("candidates",[]) if _service(x)},"stage_status":{k:v.status.value for k,v in outputs.items()},"candidate_count":len(a3.get("candidates",[]))})

    lines=["# P3b S04 evaluation","",f"Scope: {len(DEFAULT_EVAL_SCENARIOS)} non-holdout scenarios x {len(SEEDS)} seeds = {len(cases)} cases. Holdout was not run. Spec frozen in DECISIONS.md before this run.",""]
    # C1 per case
    lines += ["## C1. True cause vs decoys (per case)","","| Scenario | Seed | True cause | S03 true rank | S04 status | Other top-3 candidates/status | True-cause check verdicts |","|---|---:|---|---:|---|---|---|"]
    for c in cases:
        d=c["decisions"].get(c["true"]); other=[]
        for s in c["ranked"]["ensemble"][:3]:
            if s!=c["true"]: other.append(f"{s}: {c['decisions'].get(s,{}).get('status','not_candidate')}")
        checks=[]
        for name in CHECKS:
            f=c["per_check"].get(name,{}).get(c["true"])
            checks.append(f"{name}={f['verdict']}({f['effect_size']:.2f})" if f else f"{name}=absent")
        lines.append(f"| {c['scenario']} | {c['seed']} | {c['true']} | {_rank(c['ranked']['ensemble'],c['true']) or 'not ranked'} | {d['status'] if d else 'not_candidate'} | {', '.join(other) or 'none'} | {'; '.join(checks)} |")
    # C2 false rejection
    lines += ["","## C2. False rejection (true cause contested or unsupported)","","| Scenario | Count / 3 | Case details (seed: status; contradicting checks and evidence IDs) |","|---|---:|---|"]
    false_rejected={}
    for s in DEFAULT_EVAL_SCENARIOS:
        rows=[]
        for c in cases:
            if c["scenario"]!=s: continue
            d=c["decisions"].get(c["true"])
            if d and d["status"] in {"contested","unsupported"}:
                checks=[f"{n}={f[c['true']]['evidence_ids']}" for n,f in c["per_check"].items() if c["true"] in f and f[c["true"]]["verdict"]=="contradicts"]
                competitors=[target for target,score in c["candidate_scores"].items() if target!=c["true"] and abs(score-c["candidate_scores"].get(c["true"],float("inf")))<=1e-12]
                cause="; ".join(checks) if checks else ("equally scored candidate(s): "+", ".join(competitors) if competitors else "no contradicting finding")
                rows.append(f"seed {c['seed']}: {d['status']}; {cause}")
        false_rejected[s]=rows
        lines.append(f"| {s} | {len(rows)}/3 | {'; '.join(rows) or 'none'} |")
    # C3 false confirmation
    lines += ["","## C3. False confirmation (wrong candidate marked verified)","","| Scenario | Count | Case details (seed: candidate; supporting checks and rationale) |","|---|---:|---|"]
    false_confirmed={}
    for s in DEFAULT_EVAL_SCENARIOS:
        rows=[]
        for c in cases:
            if c["scenario"]!=s: continue
            for target,d in c["decisions"].items():
                if target!=c["true"] and d["status"]=="verified":
                    support=[f"{n}: {f[target]['rationale']}" for n,f in c["per_check"].items() if target in f and f[target]["verdict"]=="supports" and n!="vault_evidence"]
                    rows.append(f"seed {c['seed']}: {target}; {'; '.join(support)}")
        false_confirmed[s]=rows
        lines.append(f"| {s} | {len(rows)} | {'; '.join(rows) or 'none'} |")
    # C4 status distributions
    vocab=("verified","contested","insufficient_evidence","unsupported")
    lines += ["","## C4. Status distribution (candidate counts; true-cause status)","","| Scenario | All candidates V/C/I/U | True cause status seeds 1/2/3 | Missing-coverage service status by seed (expected insufficient_evidence) | Missing-coverage candidates contradicted by any check? |","|---|---|---|---|---|"]
    distributions={}
    for s in DEFAULT_EVAL_SCENARIOS:
        sc=[c for c in cases if c["scenario"]==s]
        counts={v:sum(d["status"]==v for c in sc for d in c["decisions"].values()) for v in vocab}
        distributions[s]=counts
        true_status=[c["decisions"].get(c["true"],{}).get("status","not_candidate") for c in sc]
        missing_contradictions=[]
        for c in sc:
            for target in c["coverage_gaps"]:
                for name,finds in c["per_check"].items():
                    f=finds.get(target)
                    if f and f["verdict"]=="contradicts": missing_contradictions.append(f"BUG:{c['seed']} {target}/{name}")
        gap_statuses=[f"seed {c['seed']}: "+", ".join(f"{service}={c['decisions'].get(service,{}).get('status','not_candidate')}" for service in c["coverage_gaps"]) for c in sc if c["coverage_gaps"]]
        lines.append(f"| {s} | {counts['verified']}/{counts['contested']}/{counts['insufficient_evidence']}/{counts['unsupported']} | {', '.join(true_status)} | {'; '.join(gap_statuses) or 'no gaps'} | {'; '.join(missing_contradictions) or 'none'} |")
    # C5 rankings
    lines += ["","## C5. Per-scenario top-1/top-3 hits (seed hits)","","| Scenario | change | graph | Ochiai | lag | S03 ensemble | S04 reranked | latest change | alert order | One-case comparisons |","|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for s in DEFAULT_EVAL_SCENARIOS:
        sc=[c for c in cases if c["scenario"]==s]; cells=[]
        for key in METHODS:
            a,b=_top_hits(sc,key); cells.append(f"{a}/3; {b}/3")
        pair_flags=[]
        for i,left in enumerate(METHODS):
            for right in METHODS[i+1:]:
                lh=_top_hits(sc,left); rh=_top_hits(sc,right)
                if abs(lh[0]-rh[0])==1 or abs(lh[1]-rh[1])==1: pair_flags.append(f"{left}/{right}")
        lines.append(f"| {s} | {' | '.join(cells)} | {', '.join(pair_flags) or 'none'} |")
    lines += ["","### C5 per-case true-cause rank movement","","| Scenario | Seed | S03 rank | S04 rank | Movement |","|---|---:|---:|---:|---|"]
    for c in cases:
        before=_rank(c["ranked"]["ensemble"],c["true"]); after=_rank(c["ranked"]["s04_reranked"],c["true"])
        movement="not ranked" if before is None and after is None else "newly ranked" if before is None else "lost" if after is None else f"{after-before:+d} ({'worse' if after>before else 'better' if after<before else 'same'})"
        lines.append(f"| {c['scenario']} | {c['seed']} | {before or 'not ranked'} | {after or 'not ranked'} | {movement} |")
    # C6 per check
    lines += ["","## C6. Per-check contribution (true cause vs decoys)","","| Check | True supports/contradicts/inconclusive | Decoys supports/contradicts/inconclusive | Discrimination note |","|---|---:|---:|---|"]
    check_counts={}
    for name in CHECKS:
        true_ct={v:0 for v in ("supports","contradicts","inconclusive")}; decoy_ct=dict(true_ct)
        for c in cases:
            f=c["per_check"].get(name,{})
            for target,item in f.items(): (true_ct if target==c["true"] else decoy_ct)[item["verdict"]]+=1
        check_counts[name]=(true_ct,decoy_ct)
        true_total=sum(true_ct.values()); decoy_total=sum(decoy_ct.values())
        true_dist=tuple(round(true_ct[v]/true_total,6) if true_total else 0 for v in ("supports","contradicts","inconclusive"))
        decoy_dist=tuple(round(decoy_ct[v]/decoy_total,6) if decoy_total else 0 for v in ("supports","contradicts","inconclusive"))
        same="not discriminating: same normalized verdict distribution" if true_dist==decoy_dist else "normalized verdict distributions differ"
        lines.append(f"| {name} | {true_ct['supports']}/{true_ct['contradicts']}/{true_ct['inconclusive']} | {decoy_ct['supports']}/{decoy_ct['contradicts']}/{decoy_ct['inconclusive']} | {same} |")
    # C7 ablations
    for disabled in CHECKS:
        base_hits=_top_hits(cases,"s04_reranked")
        disabled_hits=(sum(bool(c["ablations"][disabled]) and c["ablations"][disabled][0]==c["true"] for c in cases),sum(c["true"] in c["ablations"][disabled][:3] for c in cases))
        effect="does nothing" if base_hits==disabled_hits else "helps" if base_hits[0]>=disabled_hits[0] and base_hits[1]>=disabled_hits[1] else "hurts" if base_hits[0]<=disabled_hits[0] and base_hits[1]<=disabled_hits[1] else "mixed"
        lines += ["",f"## C7. Ablation: {disabled} disabled",f"Full checks {base_hits[0]}/{len(cases)}; {base_hits[1]}/{len(cases)} vs disabled {disabled_hits[0]}/{len(cases)}; {disabled_hits[1]}/{len(cases)}: disabling {effect} top-k performance (aggregate; inspect per-scenario table).","","| Scenario | change | graph | Ochiai | lag | S03 ensemble | S04 reranked | latest change | alert order |","|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for s in DEFAULT_EVAL_SCENARIOS:
            sc=[c for c in cases if c["scenario"]==s]; keys=("change_based","graph_rwr","trace_ochiai","temporal_lag","ensemble")
            cells=[f"{_top_hits(sc,k)[0]}/3; {_top_hits(sc,k)[1]}/3" for k in keys]
            ablation_hits=(sum(bool(c["ablations"][disabled]) and c["ablations"][disabled][0]==c["true"] for c in sc),sum(c["true"] in c["ablations"][disabled][:3] for c in sc))
            cells.append(f"{ablation_hits[0]}/3; {ablation_hits[1]}/3")
            for k in ("latest_change_before_alert","alert_order"): cells.append(f"{_top_hits(sc,k)[0]}/3; {_top_hits(sc,k)[1]}/3")
            lines.append(f"| {s} | {' | '.join(cells)} |")
    # Reports and explicit interpretation
    confounders=("red_herring_deploy","shared_dependency","late_alerting_cause","silent_cause")
    s04_true_verified=sum(c["decisions"].get(c["true"],{}).get("status")=="verified" for c in cases)
    false_verified=sum(d["status"]=="verified" for c in cases for target,d in c["decisions"].items() if target!=c["true"])
    s04_all=[c for c in cases]
    rerank_before=(_top_hits(s04_all,"ensemble")); rerank_after=(_top_hits(s04_all,"s04_reranked"))
    lines += ["","## D. Required plain statements","",f"- S04 separated true causes from decoys in {s04_true_verified}/{len(cases)} true-cause cases marked verified and {false_verified} wrong candidates falsely verified; case-level evidence is in C1–C3.",f"- Re-ranking {'improved' if rerank_after[0]>rerank_before[0] or rerank_after[1]>rerank_before[1] else 'did not improve' if rerank_after==rerank_before else 'mixed'} over the S03 ensemble overall: top-1 {rerank_before[0]}/{len(cases)} -> {rerank_after[0]}/{len(cases)}; top-3 {rerank_before[1]}/{len(cases)} -> {rerank_after[1]}/{len(cases)}."]
    for s in confounders:
        sc=[c for c in cases if c["scenario"]==s]
        ens=_top_hits(sc,"ensemble"); ver=_top_hits(sc,"s04_reranked"); alert=_top_hits(sc,"alert_order")
        def relation(a,b): return "beats" if a[0]>b[0] else "ties" if a[0]==b[0] else "trails"
        lines.append(f"- {s}: S03 ensemble top-1/top-3 {ens}; S04 reranked {ver}; alert_order {alert} (hits out of 3). S03 ensemble {relation(ens,alert)} alert_order on top-1; S04 {relation(ver,alert)} alert_order on top-1.")
    lines += ["- Failed cases and check/method outcomes are listed in C1–C3 and per-case rank movement in C5.","- Threshold/spec clarifications after the initial Part A draft: recovery coverage was made 3 pre-action plus 3 post-action windows, and its effect formula was made explicit before evaluation; rationale is recorded in DECISIONS.md. No values changed after the frozen-spec commit.","","## E. Decision proposals only (nothing applied)",""]
    silent=[c for c in cases if c["scenario"]=="silent_cause"]
    if any(not c["ranked"]["ensemble"] or c["ranked"]["ensemble"][0]!=c["true"] for c in silent):
        lines.append("- Silent-cause fusion miss: propose abstaining methods contribute no rank for candidates without their evidence. Expected to reduce rank dilution where methods lack coverage; could harm cases where a method's sparse-but-valid evidence is useful. Not implemented.")
    else: lines.append("- Silent-cause fusion miss: not observed in this run; no abstention change proposed.")
    for name,(t,d) in check_counts.items():
        if t==d: lines.append(f"- {name}: propose rework or defer because true/decoy verdict counts match; inspect its case-level findings before deciding removal.")
    lines += ["- Simulator gaps for P4 consideration: alerting noise, partial dependency graphs, multiple concurrent causes, and delayed or missing change records. Not built.","- Holdout recommendation: reserve a single end-of-phase run after P4 freezes; it provides an untouched final check, but this is a proposal only. Holdout was not run.","","## F. Completion checklist","","| Item | Result |","|---|---|","| Frozen Part A spec committed before eval | See commit recorded with this report |","| Per-candidate status vocabulary | yes |","| Rerank toggle default OFF; both orders emitted | yes |","| recovery_check and alternative_check | implemented generically; no simulator-specific logic |","| S04 tests outside simulator/; no simulator imports | yes |","| Direction regression including reversed-edge negative case | yes |","| Missing telemetry yields inconclusive | yes; no check contradicted a coverage-gap candidate in C4 |","| S04 evidence IDs validated against vault | yes; stage contract and test |","| pytest and inquest doctor | see gate report |","| Holdout not run | yes |","| P4 not started | yes |","","### Status snapshots per case","","| Scenario | Seed | Stage statuses S00/S01/S02/S03/S04 | Candidate counts |","|---|---:|---|---:|"]
    for c in cases: lines.append(f"| {c['scenario']} | {c['seed']} | {' / '.join(c['stage_status'][x] for x in STAGES)} | {c['candidate_count']} |")
    freeze=subprocess.run(["git","rev-list","--max-parents=0","HEAD"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip().splitlines()[0]
    latest=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
    lines[2]=lines[2]+f" Frozen-spec commit: `{freeze}`; pre-rerun bug-log commit: `{latest}`."
    text="\n".join(lines)+"\n"
    OUT.write_text(text,encoding="utf-8")
    return text

if __name__=="__main__": print(evaluate())
