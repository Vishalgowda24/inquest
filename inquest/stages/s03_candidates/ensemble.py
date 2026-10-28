"""Reciprocal-rank fusion across independently generated candidate lists."""

from __future__ import annotations

from collections import Counter

from inquest.contracts import Candidate, CandidateMethodResult


def rank_aggregate(
    results: list[CandidateMethodResult], *, rank_constant: int = 60,
    abstain_without_evidence: bool = True,
    method_weights: dict[str, float] | None = None,
) -> tuple[list[Candidate], float, dict[str, dict[str, str]]]:
    universe = {((item.service or item.target) if item.target_type == "change" else item.target) for result in results for item in result.candidates}
    abstentions: dict[str, dict[str, str]] = {target: {} for target in sorted(universe)}
    active = [item for item in results if item.status != "DISABLED"]
    if not active:
        return [], 0.0, abstentions
    fused: dict[str, dict[str, object]] = {}
    top_targets: list[str] = []
    for method_result in active:
        candidates = method_result.candidates
        if abstain_without_evidence:
            candidates = [item for item in candidates if item.evidence_ids]
        ranked = sorted(candidates, key=lambda item: (-item.score, item.target_type, item.target))
        if not ranked:
            for target in universe:
                abstentions.setdefault(target, {})[method_result.method] = "no_evidence" if any((item.service or item.target if item.target_type == "change" else item.target) == target for item in method_result.candidates) else "no_candidate"
            continue
        canonical = lambda item: item.service or item.target if item.target_type == "change" else item.target
        top_targets.append(canonical(ranked[0]))
        present = {canonical(item) for item in ranked}
        for target in universe - present:
            candidate_exists = any((item.service or item.target if item.target_type == "change" else item.target) == target for item in method_result.candidates)
            abstentions.setdefault(target, {})[method_result.method] = "no_evidence" if candidate_exists else "no_candidate"
        for rank, item in enumerate(ranked, start=1):
            target = canonical(item)
            entry = fused.setdefault(target, {"rrf": 0.0, "scores": {}, "evidence": set(), "methods": set()})
            weight = (method_weights or {}).get(method_result.method, 1.0)
            entry["rrf"] += weight / (rank_constant + rank)
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
            rationale=f"Weighted reciprocal-rank fusion; ranked by {', '.join(methods)}",
            evidence_ids=sorted(entry["evidence"]), method_scores=entry["scores"],
        ))
    if not abstain_without_evidence:
        abstentions = {}
    output.sort(key=lambda item: (-item.score, item.target))
    return output, disagreement, abstentions
