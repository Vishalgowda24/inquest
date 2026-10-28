"""Shared candidate construction helpers, without method-specific logic."""

from __future__ import annotations

import hashlib

from inquest.contracts import Candidate, CandidateMethodResult, CanonicalBundle


def evidence_for_service(bundle: CanonicalBundle, service: str, vault_ids: set[str]) -> list[str]:
    ids = [point.id for point in bundle.metrics if point.service == service]
    ids.extend(f"span:{span.trace_id}:{span.span_id}" for span in bundle.spans if span.service == service)
    ids.extend(event.id for event in bundle.changes if event.service == service)
    return sorted(set(ids) & vault_ids)


def candidate(method: str, target: str, target_type: str, score: float, rationale: str, evidence_ids: list[str], *, service: str | None = None) -> Candidate | None:
    cited = sorted(set(evidence_ids))
    if not cited:
        return None
    stable = hashlib.sha256(f"{method}|{target_type}|{target}".encode()).hexdigest()[:12]
    return Candidate(id=f"cand_{stable}", target=target, target_type=target_type, service=service, method=method, score=max(0.0, float(score)), rationale=rationale[:240], evidence_ids=cited)


def result(method: str, candidates: list[Candidate], note: str | None = None, *, degraded: bool = False) -> CandidateMethodResult:
    return CandidateMethodResult(method=method, status="DEGRADED" if degraded or not candidates else "OK", candidates=candidates, note=note)
