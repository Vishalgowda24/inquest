"""Onset-seeded random walk over the reversed dependency graph."""

from __future__ import annotations

import networkx as nx

from inquest.contracts import CanonicalBundle, SignalAnalysis
from .common import candidate, evidence_for_service, result


class GraphRwrMethod:
    name = "graph_rwr"

    def run(self, bundle: CanonicalBundle, signals: SignalAnalysis, vault_ids: set[str]):
        if not signals.onsets or not bundle.dependencies:
            return result(self.name, [], "Onsets or dependency edges are unavailable")
        earliest = min(item.onset_time for item in signals.onsets)
        graph = nx.DiGraph()
        graph.add_nodes_from(bundle.manifest.services)
        # Reverse the effect direction (callee -> caller): walk from symptoms
        # back down the declared caller-to-callee topology toward shared causes.
        graph.add_edges_from((edge.caller, edge.callee) for edge in bundle.dependencies)
        seeds: dict[str, float] = {}
        for onset in signals.onsets:
            age_hours = max(0.0, (onset.onset_time - earliest).total_seconds() / 3600)
            seeds[onset.service] = max(seeds.get(onset.service, 0.0), onset.confidence / (1.0 + age_hours))
        total = sum(seeds.values())
        if total <= 0:
            return result(self.name, [], "Onset scores are empty")
        personalization = {service: seeds.get(service, 0.0) / total for service in graph.nodes}
        scores = nx.pagerank(graph, alpha=0.8, personalization=personalization, max_iter=100, tol=1e-10)
        candidates = []
        for service, score in sorted(scores.items(), key=lambda pair: (-pair[1], pair[0])):
            onset_count = sum(item.service == service for item in signals.onsets)
            refs = evidence_for_service(bundle, service, vault_ids)
            item = candidate(self.name, service, "service", score, f"Reversed-graph random walk seeded by {onset_count} onset(s); score={score:.3f}", refs, service=service)
            if item:
                candidates.append(item)
        return result(self.name, candidates, None if candidates else "No graph candidates have vault-backed evidence")
