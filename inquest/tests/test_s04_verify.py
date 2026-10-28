from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

from inquest.contracts import Candidate, CandidateAnalysis, Evidence, StageInput
from inquest.core.config import InquestConfig
from inquest.core.context import RunContext
from inquest.core.vault import append_evidence, verify_chain
from inquest.stages.s04_verify.methods.alternative_check import AlternativeCheckMethod
from inquest.stages.s04_verify.methods.dependency_path import DependencyPathMethod
from inquest.stages.s04_verify.methods.registry import default_method_registry
from inquest.stages.s04_verify.methods.recovery_check import RecoveryCheckMethod
from inquest.stages.s04_verify.methods.temporal_consistency import TemporalConsistencyMethod
from inquest.stages.s04_verify.stage import VerifyStage


def _candidate(target, score, evidence):
    return Candidate(id=f"candidate:{target}",target=target,target_type="service",service=target,method="ensemble",score=score,rationale="test candidate",evidence_ids=evidence,method_scores={"graph_rwr":score/2})


def test_pipeline_emits_status_preserves_s03_and_tests_vault_provenance(tmp_path):
    now=datetime(2025,1,1,tzinfo=timezone.utc)
    vault_path=tmp_path/"runs"/"verify"/"vault"/"chain.jsonl"
    ev=[Evidence(id="m-db",source="test",timestamp=now,timestamp_uncertainty_ms=0,payload={"service":"database","metric":"latency","value":20}),Evidence(id="edge-db-pay",source="test",timestamp=None,timestamp_uncertainty_ms=0,payload={"caller":"payments","callee":"database"}),Evidence(id="change-db",source="test",timestamp=now,timestamp_uncertainty_ms=0,payload={"service":"database","kind":"configuration_change"})]
    append_evidence(vault_path,ev)
    assert verify_chain(vault_path).valid
    analysis=CandidateAnalysis(candidates=[_candidate("checkout",0.9,["m-db"]),_candidate("database",0.8,["m-db","edge-db-pay","change-db"])],disagreement=0.25)
    context={"onsets":[{"service":"payments","metric":"latency","onset_time":now.isoformat(),"timestamp_uncertainty_ms":0,"baseline_median":10,"baseline_mad":2},{"service":"database","metric":"latency","onset_time":(now+timedelta(hours=1)).isoformat(),"timestamp_uncertainty_ms":0,"baseline_median":10,"baseline_mad":2}],"dependencies":[{"caller":"payments","callee":"database"}],"coverage_gaps":[],"changes":[{"id":"change-db","service":"database","kind":"configuration_change","timestamp":now.isoformat(),"timestamp_uncertainty_ms":0}],"metrics":[]}
    config=InquestConfig(global_seed=1,log_level="INFO",data_inbox=tmp_path/"inbox",runs_dir=tmp_path/"runs",csv_mapping_path=Path("config/csv_mapping.yaml"),simulation_clock=now,stages={"s04_verify":True},verification_methods={"vault_evidence":True,"dependency_path":True,"temporal_consistency":True,"recovery_check":False,"alternative_check":False},verification_rerank=True)
    ctx=RunContext(run_id="verify",scenario_id="scn_000000000001",runs_dir=config.runs_dir,clock=now,config=config)
    result=VerifyStage().run(ctx,StageInput(stage="s04_verify",payload={"previous_output":{"analysis":analysis.model_dump(mode="json"),"verification_context":context,"source":"synthetic","synthetic":True}}))
    data=result.output["analysis"]
    assert result.status.value=="OK"
    assert data["reranking_enabled"] is True
    assert [x["candidate_id"] for x in data["original_order"]]==["candidate:checkout","candidate:database"]
    assert [x["candidate_id"] for x in data["reranked_order"]]==["candidate:database","candidate:checkout"]
    assert [x["status"] for x in data["original_order"]]==["unsupported","verified"]
    for decision in data["original_order"]:
        source=next(x for x in analysis.candidates if x.id==decision["candidate_id"])
        assert decision["s03_rank"] in (1,2)
        assert decision["s03_score"]==source.score
        assert decision["method_scores"]==source.method_scores
        assert decision["s03_disagreement"]==analysis.disagreement
    assert data["original_order"][1]["status"]=="verified"
    ids={x.id for x in ev}
    assert all(set(f["evidence_ids"])<=ids for fs in data["per_method"].values() for f in fs)
    assert all(set(d["evidence_ids"])<=ids for d in data["decisions"])


def test_reversed_dependency_direction_and_negative_case():
    cause=_candidate("database",0.9,[]); unrelated=_candidate("checkout",0.8,[])
    vault={"edge-1":{"payload":{"caller":"payments","callee":"database"}}}
    context={"onsets":[{"service":"payments"}],"coverage_gaps":[]}
    method=DependencyPathMethod()
    findings=method.run([cause,unrelated],context,vault)
    assert findings[0].verdict=="supports" and findings[0].evidence_ids==["edge-1"]
    assert findings[1].verdict=="contradicts" and findings[1].effect_size==0
    reverse_negative=method.run([_candidate("payments",0.5,[])],{"onsets":[{"service":"database"}],"coverage_gaps":[]},vault)[0]
    assert reverse_negative.verdict=="contradicts"


def test_shared_ancestry_path_is_not_sufficient_support_for_incomplete_topology():
    database=_candidate("database",0.9,[]); payments=_candidate("payments",0.8,[])
    vault={"e1":{"payload":{"caller":"payments","callee":"database"}},"e2":{"payload":{"caller":"inventory","callee":"database"}}}
    context={"onsets":[{"service":"payments"}],"dependency_graph_complete":True}
    findings=DependencyPathMethod().run([database,payments],context,vault)
    assert findings[0].verdict=="inconclusive"
    partial=DependencyPathMethod().run([database,payments],{**context,"dependency_graph_complete":False},vault)
    assert all(item.verdict=="inconclusive" for item in partial)


def test_absent_service_windows_are_inconclusive_for_signal_checks():
    candidate=_candidate("inventory",0.5,[])
    context={"onsets":[{"service":"payments","onset_time":"2025-01-01T00:00:00+00:00"}],"coverage_gaps":[{"service":"inventory"}]}
    vault={"edge":{"payload":{"caller":"payments","callee":"inventory"}}}
    for method in (DependencyPathMethod(),TemporalConsistencyMethod(),AlternativeCheckMethod(),RecoveryCheckMethod()):
        result=method.run([candidate],context,vault)
        assert all(item.verdict=="inconclusive" for item in result)


def test_finding_contract_has_effect_rationale_and_lowercase_verdict():
    findings=DependencyPathMethod().run([_candidate("db",0.2,[])],{}, {})
    item=findings[0].model_dump()
    assert item["verdict"] in {"supports","contradicts","inconclusive"}
    assert 0<=item["effect_size"]<=1 and item["rationale"] and isinstance(item["evidence_ids"],list)


def test_verification_rerank_defaults_off():
    now=datetime(2025,1,1,tzinfo=timezone.utc)
    cfg=InquestConfig(global_seed=1,log_level="INFO",data_inbox=Path("inbox"),runs_dir=Path("runs"),csv_mapping_path=Path("mapping.yaml"),simulation_clock=now,stages={})
    assert cfg.verification_rerank is False


def test_vault_integrity_failure_marks_candidates_unsupported(tmp_path):
    now=datetime(2025,1,1,tzinfo=timezone.utc)
    vault_path=tmp_path/"runs"/"bad"/"vault"/"chain.jsonl"
    append_evidence(vault_path,[Evidence(id="x",source="test",timestamp=now,timestamp_uncertainty_ms=0,payload={"x":1})])
    vault_path.write_text(vault_path.read_text().replace('"x":1','"x":2'),encoding="utf-8")
    cfg=InquestConfig(global_seed=1,log_level="INFO",data_inbox=tmp_path/"inbox",runs_dir=tmp_path/"runs",csv_mapping_path=Path("mapping.yaml"),simulation_clock=now,stages={"s04_verify":True})
    ctx=RunContext(run_id="bad",scenario_id="scn_000000000001",runs_dir=cfg.runs_dir,clock=now,config=cfg)
    analysis=CandidateAnalysis(candidates=[_candidate("database",1,["x"])],disagreement=0)
    result=VerifyStage().run(ctx,StageInput(stage="s04_verify",payload={"previous_output":{"analysis":analysis.model_dump(mode="json")}}))
    assert result.status.value=="FAILED"
    assert result.output["analysis"]["decisions"][0]["status"]=="unsupported"


def test_temporal_check_uses_change_and_onset_timestamps():
    t0=datetime(2025,1,1,tzinfo=timezone.utc)
    candidate=_candidate("database",0.9,[])
    context={"onsets":[{"service":"database","metric":"latency","onset_time":(t0+timedelta(hours=2)).isoformat(),"timestamp_uncertainty_ms":100}],"changes":[{"id":"change-1","service":"database","kind":"configuration_change","timestamp":(t0+timedelta(hours=1)).isoformat(),"timestamp_uncertainty_ms":100}],"coverage_gaps":[],"metrics":[{"id":"onset-1","service":"database","metric":"latency","timestamp":(t0+timedelta(hours=2)).isoformat()}]}
    result=TemporalConsistencyMethod().run([candidate],context,{"change-1":{},"onset-1":{}})[0]
    assert result.verdict=="supports" and set(result.evidence_ids)=={"change-1","onset-1"}


def test_recovery_check_detects_three_post_restart_windows():
    t0=datetime(2025,1,1,tzinfo=timezone.utc)
    onset_time=t0+timedelta(hours=2); action_time=t0+timedelta(hours=5)
    times=[t0+timedelta(hours=h) for h in (3,4,4.5,6,7,8)]
    values=[30,32,31,10.5,10.2,10.3]
    metrics=[{"id":f"latency-{i}","service":"database","metric":"latency","timestamp":t.isoformat(),"value":v} for i,(t,v) in enumerate(zip(times,values))]
    metrics += [{"id":f"cpu-{i}","service":"database","metric":"cpu_percent","timestamp":t.isoformat(),"value":25 if t<action_time else 27} for i,t in enumerate(times)]
    context={"onsets":[{"service":"database","metric":"cpu_percent","onset_time":(t0+timedelta(hours=1)).isoformat(),"baseline_median":20,"baseline_mad":1},{"service":"database","metric":"latency","onset_time":onset_time.isoformat(),"baseline_median":10,"baseline_mad":1}],"changes":[{"id":"restart-1","service":"database","kind":"restart","timestamp":action_time.isoformat()}],"metrics":metrics,"coverage_gaps":[]}
    vault={x["id"]:{} for x in metrics}; vault["restart-1"]={}
    finding=RecoveryCheckMethod().run([_candidate("database",0.9,[])],context,vault)[0]
    assert finding.verdict=="supports" and finding.effect_size>0


def test_alternative_check_identifies_common_dependency_explaining_more_symptoms():
    candidates=[_candidate("database",0.9,[]),_candidate("payments",0.7,[])]
    vault={"e1":{"payload":{"caller":"payments","callee":"database"}},"e2":{"payload":{"caller":"inventory","callee":"database"}}}
    context={"onsets":[{"service":"payments"},{"service":"inventory"}],"coverage_gaps":[]}
    results=AlternativeCheckMethod().run(candidates,context,vault)
    assert results[0].verdict=="supports"
    assert results[1].verdict=="contradicts"
    assert set(results[0].evidence_ids)=={"e1","e2"}


def test_s04_method_modules_do_not_import_each_other():
    root=Path(__file__).resolve().parents[1]/"stages"/"s04_verify"/"methods"
    names=default_method_registry().names()
    for source in root.glob("*.py"):
        if source.stem in {"interface","registry","__init__"}: continue
        text=source.read_text(encoding="utf-8")
        for other in names:
            if other!=source.stem: assert not re.search(rf"(?:from|import)\s+(?:\.\s*)?{re.escape(other)}\b",text)
