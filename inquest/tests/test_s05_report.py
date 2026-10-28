"""S05 report contracts, determinism, coverage abstention, and model integrity."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from inquest.contracts import Evidence, StageInput
from inquest.core.artifacts import write_json
from inquest.core.config import load_config
from inquest.core.context import RunContext
from inquest.core.vault import append_evidence, read_vault_ids
from inquest.stages.s05_report.confidence import FEATURE_NAMES
from inquest.stages.s05_report.stage import ReportStage


def _model(path:Path, intercept:float=2.0)->str:
    value={"version":"confidence_logistic_v1","feature_names":list(FEATURE_NAMES),"mean":[0.0]*8,"scale":[1.0]*8,
           "coefficients":[0.0]*8,"intercept":intercept,"margin_baseline":{"mean":0.0,"scale":1.0,"coefficient":0.0,"intercept":0.0}}
    data=(json.dumps(value,sort_keys=True,indent=2)+"\n").encode()
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _fixture(tmp_path:Path, *, gap:bool=False, disabled:bool=False, bad_hash:bool=False, enable_calibrated:bool=False):
    run_id="s05-test"
    run_dir=tmp_path/run_id
    run_dir.mkdir(parents=True)
    when="2025-01-01T00:00:00+00:00"
    ids=["manifest:scn_000000000001","metric-db","metric-payments","edge-db-payments","change-db","alert-payments"]
    append_evidence(run_dir/"vault"/"chain.jsonl",[Evidence(id=item,source="test",timestamp=None,timestamp_uncertainty_ms=0,payload={}) for item in ids])
    manifest={"scenario_id":"scn_000000000001","source":"synthetic","synthetic":True}
    metric_db={"id":"metric-db","timestamp":when,"service":"database","metric":"latency_ms","value":80,"unit":"ms"}
    metric_pay={"id":"metric-payments","timestamp":"2025-01-01T01:00:00+00:00","service":"payments","metric":"latency_ms","value":60,"unit":"ms"}
    change={"id":"change-db","kind":"restart","timestamp":"2025-01-01T00:30:00+00:00","service":"database","change_id":"restart-1"}
    alert={"id":"alert-payments","timestamp":"2025-01-01T01:30:00+00:00","service":"payments","level":"WARN","attributes":{"alert_emission":True}}
    bundle={"manifest":manifest,"metrics":[metric_db,metric_pay],"logs":[alert],"changes":[change]}
    s00={"source":"synthetic","synthetic":True,"bundle":bundle}
    s02={"bundle":bundle,"analysis":{"detector":"cusum","onsets":[{"service":"database","metric":"latency_ms","onset_time":when,"confidence":.9}],
        "coverage_gaps":[{"service":"database","metric":"error_rate","missing_windows":2}] if gap else [],
        "warnings":["Seasonal normalization not applied: fewer than two complete daily cycles"]}}
    db_candidate={"id":"fusion_v3:database","target":"database","target_type":"service","service":"database","method":"fusion_v3","score":.8,"rationale":"test","evidence_ids":["metric-db","edge-db-payments"],"method_scores":{"graph_rwr":.8,"trace_ochiai":.5}}
    pay_candidate={"id":"fusion_v3:payments","target":"payments","target_type":"service","service":"payments","method":"fusion_v3","score":.5,"rationale":"test","evidence_ids":["metric-payments"],"method_scores":{"trace_ochiai":.4}}
    method_results=[{"method":"graph_rwr","status":"OK","candidates":[db_candidate,pay_candidate]},
        {"method":"trace_ochiai","status":"OK","candidates":[pay_candidate,db_candidate]},
        {"method":"temporal_lag","status":"OK","candidates":[db_candidate,pay_candidate]},
        {"method":"change_based","status":"DISABLED" if disabled else "DEGRADED","candidates":[],"note":"test"}]
    s03={"analysis":{"candidates":[db_candidate,pay_candidate],"method_results":method_results,"disabled_methods":["change_based"] if disabled else [],
        "disagreement":.25,"abstentions":{"database":{"change_based":"no_candidate"}},"verification_context":{"telemetry_gaps":["database"] if gap else [],"coverage_gaps":[]}}}
    finding={"candidate_id":"fusion_v3:payments","target":"payments","verdict":"contradicts","effect_size":.7,"rationale":"The candidate onset follows the symptom.","evidence_ids":["edge-db-payments","metric-payments"]}
    s04={"analysis":{"decisions":[{"target":"database","status":"contested"},{"target":"payments","status":"insufficient_evidence"}],
        "per_method":{"dependency_path":[finding]},"disabled_methods":["alternative_check"] if disabled else [],
        "method_results":[{"method":"alternative_check","status":"DISABLED" if disabled else "OK"}]}}
    for stage,data in (("s00_ingest",s00),("s02_signals",s02),("s03_candidates",s03),("s04_verify",s04)):
        write_json(run_dir/f"00_{stage}"/"output.json",{"output":data})
    model_path=tmp_path/"confidence.json"
    digest=_model(model_path)
    config=load_config(Path("config.yaml")).model_copy(update={"confidence_model_path":model_path,"confidence_model_sha256":"0"*64 if bad_hash else digest,"unvalidated_calibrated_confidence":enable_calibrated or bad_hash})
    ctx=RunContext(run_id=run_id,scenario_id="scn_000000000001",runs_dir=tmp_path,clock=datetime(2025,1,1,tzinfo=timezone.utc),config=config)
    return ctx,run_dir,ids


def test_s05_report_citations_determinism_and_wording(tmp_path):
    ctx,run_dir,ids=_fixture(tmp_path)
    stage=ReportStage()
    first=stage.run(ctx,StageInput(stage="s05_report",payload={}))
    report_json=(run_dir/"05_s05_report"/"report.json").read_bytes()
    report_md=(run_dir/"05_s05_report"/"report.md").read_bytes()
    second=stage.run(ctx,StageInput(stage="s05_report",payload={}))
    assert first.status.value=="OK" and second.status.value=="OK"
    assert (run_dir/"05_s05_report"/"report.json").read_bytes()==report_json
    assert (run_dir/"05_s05_report"/"report.md").read_bytes()==report_md
    record=json.loads(report_json)
    vault_ids=read_vault_ids(run_dir/"vault"/"chain.jsonl")
    def collect(value):
        if isinstance(value,dict): return set(value.get("evidence_ids",[]))|set().union(*(collect(child) for child in value.values()))
        if isinstance(value,list): return set().union(*(collect(child) for child in value)) if value else set()
        return set()
    assert collect(record) <= vault_ids
    lines=[line for line in report_md.decode().splitlines() if line.strip() and not line.startswith("#")]
    assert all("[evidence_ids:" in line for line in lines)
    assert not re.search(r"caused by|proves|root cause is",report_md.decode(),flags=re.IGNORECASE)
    assert "Most likely consistent with" in report_md.decode()
    assert "Evidence is from synthetic scenarios only." in report_md.decode()


def test_s05_coverage_gap_forces_insufficient_evidence_and_unknown(tmp_path):
    ctx,run_dir,_=_fixture(tmp_path,gap=True)
    result=ReportStage().run(ctx,StageInput(stage="s05_report",payload={}))
    report=json.loads((run_dir/"05_s05_report"/"report.json").read_text())
    assert result.status.value=="OK"
    assert report["headline"]["confidence"]["level"]=="insufficient_evidence"
    assert report["headline"]["confidence"]["telemetry_gap"] is True
    assert any("coverage gap" in item["text"].lower() for item in report["unknowns"])


def test_s05_disabled_method_and_check_are_reported_as_unknowns(tmp_path):
    ctx,run_dir,_=_fixture(tmp_path,disabled=True)
    ReportStage().run(ctx,StageInput(stage="s05_report",payload={}))
    report=json.loads((run_dir/"05_s05_report"/"report.json").read_text())
    texts=[item["text"] for item in report["unknowns"]]
    assert any("S03 method change_based was disabled" in text for text in texts)
    assert any("S04 check alternative_check was disabled" in text for text in texts)


def test_s05_confidence_model_hash_mismatch_fails_loudly(tmp_path):
    ctx,_,_=_fixture(tmp_path,bad_hash=True)
    with pytest.raises(ValueError,match="SHA-256 mismatch"):
        ReportStage().run(ctx,StageInput(stage="s05_report",payload={}))


def test_confidence_model_hash_is_stable_across_windows_line_endings(tmp_path):
    model_path=tmp_path/"confidence-crlf.json"
    expected=_model(model_path)
    model_path.write_bytes(model_path.read_bytes().replace(b"\n",b"\r\n"))
    from inquest.stages.s05_report.confidence import load_model
    _,actual=load_model(model_path,expected)
    assert actual==expected


def test_s05_default_report_has_no_numeric_probability(tmp_path):
    ctx,run_dir,_ = _fixture(tmp_path, enable_calibrated=False)
    ReportStage().run(ctx, StageInput(stage="s05_report", payload={}))
    report_json = json.loads((run_dir / "05_s05_report" / "report.json").read_text(encoding="utf-8"))
    report_md = (run_dir / "05_s05_report" / "report.md").read_text(encoding="utf-8")
    conf = report_json["headline"]["confidence"]
    assert conf["unvalidated_calibrated_probability"] is None
    assert "probability" not in conf
    assert re.search(r"\bprobability\b", report_md.split("## Ranked candidates")[0]) is None


def test_s05_calibrated_flag_enables_unvalidated_probability(tmp_path):
    ctx,run_dir,_ = _fixture(tmp_path, enable_calibrated=True)
    ReportStage().run(ctx, StageInput(stage="s05_report", payload={}))
    report_json = json.loads((run_dir / "05_s05_report" / "report.json").read_text(encoding="utf-8"))
    report_md = (run_dir / "05_s05_report" / "report.md").read_text(encoding="utf-8")
    conf = report_json["headline"]["confidence"]
    assert conf["unvalidated_calibrated_probability"] is not None
    assert "unvalidated probability" in report_md
