"""Candidate-method regression coverage using canonical in-memory fixtures."""

from datetime import datetime, timedelta, timezone

from inquest.contracts import CanonicalBundle, DependencyEdge, LogEvent, MetricPoint, ScenarioManifest, SignalAnalysis, Span
from inquest.stages.s03_candidates.methods.trace_ochiai import TraceOchiaiMethod
from inquest.stages.s03_candidates.ensemble import rank_aggregate
from inquest.contracts import Candidate, CandidateMethodResult


def test_trace_ochiai_ranks_known_root_from_minimal_failing_trace_set() -> None:
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    services = ["checkout", "payments", "inventory", "database"]
    manifest = ScenarioManifest(
        scenario_id="scn_000000000001", seed=1, source="synthetic", synthetic=True,
        time_range={"start": start, "end": start + timedelta(hours=3)}, services=services,
        record_counts={"metrics": 0, "spans": 16, "logs": 0, "events": 0, "dependencies": 0}, files=[],
    )
    spans = []
    failing_errors = {
        "fail-1": {"database", "payments", "checkout"},
        "fail-2": {"database", "inventory"},
    }
    for trace_index, trace_id in enumerate(("fail-1", "fail-2", "healthy-1", "healthy-2")):
        for service_index, service in enumerate(services):
            is_error = service in failing_errors.get(trace_id, set())
            spans.append(Span(
                trace_id=trace_id, span_id=f"{trace_id}-{service}", parent_span_id=None,
                service=service, operation="request", start_time=start + timedelta(hours=trace_index),
                duration_ms=10.0, status="ERROR" if is_error else "OK",
                timestamp_uncertainty_ms=0,
            ))
    bundle = CanonicalBundle(manifest=manifest, spans=spans, metrics=[], logs=[], changes=[], dependencies=[])
    signal_analysis = SignalAnalysis(detector="cusum", onsets=[], service_order=[], coverage_gaps=[], warnings=[])
    vault_ids = {f"span:{span.trace_id}:{span.span_id}" for span in spans}

    result = TraceOchiaiMethod().run(bundle, signal_analysis, vault_ids)

    assert result.status == "OK"
    assert result.candidates[0].target == "database"
    assert result.candidates[0].score > result.candidates[1].score
    assert all(set(item.evidence_ids) <= vault_ids for item in result.candidates)


def test_fusion_abstains_without_candidate_evidence_and_records_reason():
    useful = Candidate(id="c:a", target="database", target_type="service", service="database", method="m1", score=0.9, rationale="known", evidence_ids=["e1"])
    unsupported = useful.model_copy(update={"id": "c:b", "target": "payments", "service": "payments", "method": "m2", "score": 0.8, "evidence_ids": []})
    results = [CandidateMethodResult(method="m1", status="OK", candidates=[useful]), CandidateMethodResult(method="m2", status="OK", candidates=[unsupported])]
    fused, disagreement, abstentions = rank_aggregate(results)
    assert [item.target for item in fused] == ["database"]
    assert abstentions["payments"]["m2"] == "no_evidence"
    assert "m1" in abstentions["payments"]
    assert disagreement == 0.0


def test_fusion_ablation_without_abstention_preserves_legacy_ranks():
    candidate = Candidate(id="c:a", target="payments", target_type="service", service="payments", method="m", score=1, rationale="no evidence", evidence_ids=[])
    results = [CandidateMethodResult(method="m", status="OK", candidates=[candidate])]
    fused, _, abstentions = rank_aggregate(results, abstain_without_evidence=False)
    assert [item.target for item in fused] == ["payments"]
    assert abstentions == {}


def test_fusion_applies_frozen_graph_rwr_weight_without_changing_raw_scores():
    def c(target, method, score):
        return Candidate(id=f"{method}:{target}",target=target,target_type="service",service=target,method=method,score=score,rationale="test",evidence_ids=[f"ev-{method}-{target}"])
    results=[
        CandidateMethodResult(method="graph_rwr",status="OK",candidates=[c("database","graph_rwr",0.9)]),
        CandidateMethodResult(method="trace_ochiai",status="OK",candidates=[c("inventory","trace_ochiai",0.9),c("database","trace_ochiai",0.8)]),
        CandidateMethodResult(method="temporal_lag",status="OK",candidates=[c("inventory","temporal_lag",0.9),c("payments","temporal_lag",0.8)]),
    ]
    fused,_,_=rank_aggregate(results,method_weights={"graph_rwr":2.0})
    assert [item.target for item in fused][:2]==["database","inventory"]
    db=next(item for item in fused if item.target=="database")
    assert db.method_scores=={"graph_rwr":0.9,"trace_ochiai":0.8}


def test_fusion_variants_use_the_preregistered_formulas():
    def c(target, method, score):
        return Candidate(id=f"{method}:{target}", target=target, target_type="service", service=target,
                         method=method, score=score, rationale="test", evidence_ids=[f"ev-{method}-{target}"])
    results = [
        CandidateMethodResult(method="graph_rwr", status="OK", candidates=[c("db", "graph_rwr", .9), c("api", "graph_rwr", .1)]),
        CandidateMethodResult(method="trace_ochiai", status="OK", candidates=[c("db", "trace_ochiai", .8), c("api", "trace_ochiai", .7)]),
    ]
    borda, _, _ = rank_aggregate(results, variant="v1")
    assert [item.target for item in borda] == ["db", "api"]
    assert [item.score for item in borda] == [2.0, 0.0]

    normalized, _, _ = rank_aggregate(results, variant="v2")
    assert [item.target for item in normalized] == ["db", "api"]
    assert [item.score for item in normalized] == [2.0, 0.0]

    margin_rrf, _, _ = rank_aggregate(results, variant="v3")
    assert [item.target for item in margin_rrf] == ["db", "api"]
    assert all(item.method == "fusion_v3" for item in margin_rrf)

    graph, _, _ = rank_aggregate(results, variant="v4")
    assert [item.target for item in graph] == ["db", "api"]
    assert all(item.method == "fusion_v4" for item in graph)


def test_v3_equal_weights_when_all_method_margins_are_zero():
    def c(target, method, score):
        return Candidate(id=f"{method}:{target}", target=target, target_type="service", service=target,
                         method=method, score=score, rationale="test", evidence_ids=[f"ev-{method}-{target}"])
    results = [
        CandidateMethodResult(method="m1", status="OK", candidates=[c("a", "m1", 1), c("b", "m1", 1)]),
        CandidateMethodResult(method="m2", status="OK", candidates=[c("b", "m2", 1), c("a", "m2", 1)]),
    ]
    fused, _, _ = rank_aggregate(results, variant="v3")
    assert [item.target for item in fused] == ["a", "b"]
