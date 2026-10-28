"""Lagged latency correlation restricted to declared dependency edges."""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from inquest.contracts import CanonicalBundle, SignalAnalysis
from .common import candidate, result


class TemporalLagMethod:
    name = "temporal_lag"

    def run(self, bundle: CanonicalBundle, signals: SignalAnalysis, vault_ids: set[str]):
        del signals
        metrics = defaultdict(dict)
        for point in bundle.metrics:
            if point.metric == "latency_ms":
                hour = round((point.timestamp - bundle.manifest.time_range.start).total_seconds() / 3600)
                metrics[point.service][hour] = (point.value, point.id)
        if not bundle.dependencies:
            return result(self.name, [], "No declared dependency edges", degraded=True)
        best: dict[str, tuple[float, str, list[str]]] = {}
        for edge in bundle.dependencies:
            caller = metrics.get(edge.caller, {})
            callee = metrics.get(edge.callee, {})
            best_edge: tuple[float, int, list[str]] | None = None
            # Test small causal delays: callee signal at t precedes caller at t + lag.
            for lag in range(0, 4):
                pairs = [(callee[t][0], caller[t + lag][0], [callee[t][1], caller[t + lag][1]]) for t in callee if t + lag in caller]
                if len(pairs) < 5:
                    continue
                x = np.asarray([pair[0] for pair in pairs], dtype=float)
                y = np.asarray([pair[1] for pair in pairs], dtype=float)
                if float(np.std(x)) == 0 or float(np.std(y)) == 0:
                    continue
                effect = float(np.corrcoef(x, y)[0, 1])
                if best_edge is None or effect > best_edge[0]:
                    ids = sorted({identifier for pair in pairs for identifier in pair[2]})
                    best_edge = (effect, lag, ids)
            if best_edge is None or best_edge[0] <= 0:
                continue
            effect, lag, refs = best_edge
            previous = best.get(edge.callee)
            if previous is None or effect > previous[0]:
                best[edge.callee] = (effect, edge.caller, refs)
        candidates = []
        for service, (effect, caller, refs) in sorted(best.items(), key=lambda item: (-item[1][0], item[0])):
            ids = sorted(set(refs) & vault_ids)
            item = candidate(self.name, service, "service", effect, f"Latency effect r={effect:.3f} on declared edge {caller} -> {service}; lagged association, not a p-value", ids, service=service)
            if item:
                candidates.append(item)
        return result(self.name, candidates, None if candidates else "Insufficient aligned latency windows on dependency edges", degraded=not bool(candidates))
