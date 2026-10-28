"""Reciprocal-rank fusion across independently generated candidate lists."""

from __future__ import annotations

from collections import Counter

from inquest.contracts import Candidate, CandidateMethodResult


def rank_aggregate(
    results: list[CandidateMethodResult], *, rank_constant: int = 60,
    abstain_without_evidence: bool = True,
    method_weights: dict[str, float] | None = None,
    variant: str = "v0",
) -> tuple[list[Candidate], float, dict[str, dict[str, str]]]:
    if variant not in {"v0", "v1", "v2", "v3", "v4"}:
        raise ValueError(f"Unknown fusion variant: {variant}")
    if variant != "v0":
        return _rank_variant(
            results, variant=variant, rank_constant=rank_constant,
            abstain_without_evidence=abstain_without_evidence,
        )
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


def _rank_variant(
    results: list[CandidateMethodResult], *, variant: str, rank_constant: int,
    abstain_without_evidence: bool,
) -> tuple[list[Candidate], float, dict[str, dict[str, str]]]:
    active = [result for result in results if result.status != "DISABLED"]
    method_candidates: dict[str, list[Candidate]] = {}
    abstentions: dict[str, dict[str, str]] = {}
    universe: set[str] = set()
    for result in active:
        best: dict[str, Candidate] = {}
        for item in result.candidates:
            if abstain_without_evidence and not item.evidence_ids:
                continue
            target = (item.service or item.target) if item.target_type == "change" else item.target
            if target not in best or item.score > best[target].score:
                best[target] = item
        method_candidates[result.method] = sorted(best.values(), key=lambda item: (-item.score, item.target))
        universe.update(best)
    abstentions = {target: {} for target in sorted(universe)}
    for result in active:
        present = {
            (item.service or item.target) if item.target_type == "change" else item.target
            for item in method_candidates[result.method]
        }
        for target in universe - present:
            had_candidate = any(
                ((item.service or item.target) if item.target_type == "change" else item.target) == target
                for item in result.candidates
            )
            abstentions.setdefault(target, {})[result.method] = "no_evidence" if had_candidate else "no_candidate"

    if variant == "v4":
        graph = method_candidates.get("graph_rwr", [])
        output = [Candidate(
            id=f"fusion_v4:{item.target}", target=item.target, target_type="service", service=item.target,
            method="fusion_v4", score=item.score, rationale="Graph RWR reference ranking",
            evidence_ids=item.evidence_ids, method_scores={"graph_rwr": item.score},
        ) for item in graph]
        return output, 0.0, abstentions

    weights: dict[str, float] = {name: 1.0 for name, items in method_candidates.items() if items}
    margins: dict[str, float] = {}
    if variant == "v3":
        for name, items in method_candidates.items():
            if len(items) >= 2:
                margins[name] = max(0.0, items[0].score - items[1].score)
            else:
                margins[name] = 0.0
        total_margin = sum(margins.values())
        if total_margin > 0.0:
            weights = {name: (margins[name] / total_margin) for name in method_candidates if margins[name] > 0.0}
        else:
            weights = {name: 1.0 / len([items for items in method_candidates.values() if items])
                       for name, items in method_candidates.items() if items}

    fused: dict[str, dict[str, object]] = {}
    for name, items in method_candidates.items():
        if name not in weights:
            continue
        n = len(items)
        lo = min((item.score for item in items), default=0.0)
        hi = max((item.score for item in items), default=0.0)
        for position, item in enumerate(items, start=1):
            target = (item.service or item.target) if item.target_type == "change" else item.target
            entry = fused.setdefault(target, {"score": 0.0, "evidence": set(), "method_scores": {}, "methods": set()})
            if variant in {"v1", "v3"}:
                contribution = (len(universe) - position) if variant == "v1" else weights[name] / (rank_constant + position)
            elif variant == "v2":
                contribution = 1.0 if n == 1 or hi == lo else (item.score - lo) / (hi - lo)
            else:
                raise ValueError(f"Unsupported fusion variant: {variant}")
            entry["score"] += contribution
            entry["evidence"].update(item.evidence_ids)
            entry["method_scores"][name] = item.score
            entry["methods"].add(name)
    output = []
    for target, entry in fused.items():
        method_names = sorted(entry["methods"])
        output.append(Candidate(
            id=f"fusion_{variant}:{target}", target=target, target_type="service", service=target,
            method=f"fusion_{variant}", score=entry["score"],
            rationale=f"{variant.upper()} rank aggregation from {', '.join(method_names)}",
            evidence_ids=sorted(entry["evidence"]), method_scores=entry["method_scores"],
        ))
    output.sort(key=lambda item: (-item.score, item.target))
    top_targets = [items[0].target for items in method_candidates.values() if items]
    if variant == "v3":
        top_targets = [method_candidates[name][0].target for name in weights if method_candidates.get(name)]
    disagreement = 0.0
    if len(top_targets) > 1:
        counts = Counter(top_targets)
        disagreement = 1.0 - max(counts.values()) / len(top_targets)
    if not abstain_without_evidence:
        abstentions = {}
    return output, disagreement, abstentions
