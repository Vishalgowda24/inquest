"""Plausible service alerts emitted in a balanced order unrelated to causality."""
from __future__ import annotations

import random

from simulator.contracts import LogEvent
from simulator.scenarios.clean_bad_deploy.model import SERVICES, _timestamp
from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="unordered_plausible_alerts", fault_service="database", fault_start=10,
    fault_intensity=1.4, fault_threshold=42,
    description="All services emit plausible threshold alerts with report delays independent of causal propagation.",
)


def generate(seed: int):
    data = build(SPEC, seed)
    rng = random.Random(seed ^ 0xBADC0DE)
    cause_position = ((seed - 32) % len(SERVICES)) + 1
    other_services = [service for service in SERVICES if service != "database"]
    rng.shuffle(other_services)
    order = other_services[:cause_position - 1] + ["database"] + other_services[cause_position - 1:]
    # Reports arrive in independent, close-in-time windows after the fault begins.
    schedule = {service: 10 + index for index, service in enumerate(order)}
    alerts = tuple(LogEvent(
        id=f"alert-{seed}-{index}", timestamp=_timestamp(schedule[service]), service=service,
        level="WARN", message="synthetic threshold alert routed",
        attributes={"alert_emission": True}, timestamp_uncertainty_ms=0,
    ) for index, service in enumerate(order, start=1))
    logs = tuple(sorted((*data.logs, *alerts), key=lambda item: (item.timestamp, item.id)))
    truth = {**data.truth, "alert_schedule": schedule, "cause_alert_position": cause_position,
             "alert_order_independent_of_causality": True,
             "spurious_alert_services": other_services}
    manifest = data.manifest.model_copy(update={"record_counts": {**data.manifest.record_counts, "logs": len(logs)}})
    return data.__class__(manifest, data.metrics, data.spans, logs, data.events, data.dependencies, truth)
