"""Reciprocal-rank fusion across independently generated candidate lists."""

from __future__ import annotations

from collections import Counter, defaultdict

from inquest.contracts import Candidate, CandidateMethodResult


def rank_aggregate(results: list[CandidateMethodResult], *, rank_constant: int = 60) -> tuple[list[Candidate], float]:
    active = [item for item in results if item.status != "DISABLED" and item.candidates]
    if not active:
        return [], 0.0
    fused: dict[str, dict[str, object]] = {}
    top_targets: list[str] = []
    for method_result in active:
        ranked = sorted(method_result.candidates, key=lambda item: (-item.score, item.target_type, item.target))
        canonical = lambda item: item.service or item.target if item.target_type == "change" else item.target
        top_targets.append(canonical(ranked[0]))
        for rank, item in enumerate(ranked, start=1):
            target = canonical(item)
            entry = fused.setdefault(target, {"rrf": 0.0, "scores": {}, "evidence": set(), "methods": set()})
            entry["rrf"] += 1.0 / (rank_constant + rank)
            entry["scores"][method_result.method] = item.score
            entry["evidence"].update(item.evidence_ids)
            entry["methods"].add(method_result.method)
    disagreement = 0.0
    if len(top_targets) > 1:
        counts = Counter(top_targets)
        disagreement = 1.0 - max(counts.values()) / len(top_targets)
    output = []
    for target, entry in fused.items():
        methods = sorted(entry["methods"])
        output.append(Candidate(
            id=f"ensemble:{target}", target=target, target_type="service", service=target,
            method="ensemble", score=entry["rrf"],
            rationale=f"Reciprocal-rank fusion; ranked by {', '.join(methods)}",
            evidence_ids=sorted(entry["evidence"]), method_scores=entry["scores"],
        ))
    output.sort(key=lambda item: (-item.score, item.target))
    return output, disagreement
