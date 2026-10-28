"""Spectrum-based failing-versus-healthy trace service localization."""

from __future__ import annotations

from collections import defaultdict
from math import sqrt

from inquest.contracts import CanonicalBundle, SignalAnalysis
from .common import candidate, result


class TraceOchiaiMethod:
    name = "trace_ochiai"

    def run(self, bundle: CanonicalBundle, signals: SignalAnalysis, vault_ids: set[str]):
        del signals
        if not bundle.spans:
            return result(self.name, [], "No trace spans were ingested", degraded=True)
        trace_services: dict[str, set[str]] = defaultdict(set)
        failing_services: dict[str, set[str]] = defaultdict(set)
        for span in bundle.spans:
            trace_services[span.trace_id].add(span.service)
            if span.status == "ERROR":
                failing_services[span.trace_id].add(span.service)
        failed = set(failing_services)
        healthy = set(trace_services) - failed
        if not failed or not healthy:
            return result(self.name, [], "Both failing and healthy traces are required for Ochiai comparison", degraded=True)
        candidates = []
        for service in bundle.manifest.services:
            failed_count = sum(service in failing_services[trace] for trace in failed)
            healthy_count = sum(service in trace_services[trace] for trace in healthy)
            denominator = sqrt(len(failed) * (failed_count + healthy_count))
            if not denominator:
                continue
            score = failed_count / denominator
            ids = [f"span:{span.trace_id}:{span.span_id}" for span in bundle.spans if span.service == service and span.status == "ERROR"]
            ids = sorted(set(ids) & vault_ids)
            item = candidate(self.name, service, "service", score, f"Ochiai={score:.3f} from {failed_count} failing and {healthy_count} healthy traces", ids, service=service)
            if item:
                candidates.append(item)
        missing = sorted(set(bundle.manifest.services) - {span.service for span in bundle.spans})
        note = f"No spans for services: {', '.join(missing)}" if missing else None
        # Candidate order is semantic: downstream rank consumers use list order.
        candidates.sort(key=lambda item: (-item.score, item.target))
        return result(self.name, candidates, note, degraded=bool(missing))
