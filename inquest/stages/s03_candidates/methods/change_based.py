"""Candidate ranking from temporally relevant and service-relevant changes."""

from __future__ import annotations

from collections import defaultdict, deque
from math import exp

from inquest.contracts import CanonicalBundle, SignalAnalysis
from .common import candidate, result


class ChangeBasedMethod:
    name = "change_based"

    def run(self, bundle: CanonicalBundle, signals: SignalAnalysis, vault_ids: set[str]):
        if not signals.onsets:
            return result(self.name, [], "No signal onset is available to define the change window")
        earliest = min(onset.onset_time for onset in signals.onsets)
        onset_by_service = {}
        for onset in signals.onsets:
            onset_by_service[onset.service] = min(onset_by_service.get(onset.service, onset.onset_time), onset.onset_time)
        graph: dict[str, set[str]] = defaultdict(set)
        for edge in bundle.dependencies:
            graph[edge.caller].add(edge.callee)
        symptomatic = {service for service, time in onset_by_service.items() if (time - earliest).total_seconds() <= 2 * 3600}

        def relevance(changed_service: str) -> float:
            if changed_service in symptomatic:
                return 1.0
            queue = deque([(service, 0) for service in symptomatic])
            seen = set(symptomatic)
            while queue:
                service, depth = queue.popleft()
                if depth >= 4:
                    continue
                for dependency in graph.get(service, set()):
                    if dependency == changed_service:
                        return 0.5 / (depth + 1)
                    if dependency not in seen:
                        seen.add(dependency)
                        queue.append((dependency, depth + 1))
            return 0.15

        output = []
        for event in bundle.changes:
            delta_hours = (earliest - event.timestamp).total_seconds() / 3600
            uncertainty_hours = max((item.timestamp_uncertainty_ms for item in signals.onsets), default=0) / 3_600_000
            if delta_hours < -uncertainty_hours or delta_hours > 12:
                continue
            proximity = exp(-abs(delta_hours) / 6)
            service_score = relevance(event.service)
            score = proximity * service_score
            item = candidate(self.name, event.change_id, "change", score, f"{event.kind} on {event.service} was {abs(delta_hours):.1f}h from earliest onset; service relevance={service_score:.2f}", [event.id], service=event.service)
            if item:
                output.append(item)
        output.sort(key=lambda item: (-item.score, item.target))
        return result(self.name, output, None if output else "No recorded change falls within 12 hours before the onset window")
