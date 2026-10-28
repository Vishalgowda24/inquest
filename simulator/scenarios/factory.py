"""Parameter-driven scenario factory; all telemetry remains generative."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from simulator.contracts import ChangeEvent, DependencyEdge, ScenarioManifest
from simulator.contracts.schemas import TimeRange
from simulator.scenarios.clean_bad_deploy.model import (
    Dataset, SERVICES, START, _make_logs, _make_metrics, _make_spans, _scenario_id, _timestamp,
)


@dataclass(frozen=True)
class ScenarioSpec:
    key: str
    fault_service: str = "database"
    fault_start: int = 10
    fault_end: int | None = None
    fault_intensity: float = 1.35
    fault_threshold: float = 42.0
    additional_faults: tuple[tuple[str, int, int | None, float, float], ...] = ()
    fault_metric_visibility_delay: int = 0
    hide_fault_metrics: bool = False
    suppress_metric_services: frozenset[str] = frozenset()
    steps: int = 20
    changes: tuple[tuple[str, str, int, str], ...] = ()
    missing_windows: dict[str, set[int]] = field(default_factory=dict)
    no_trace_services: frozenset[str] = frozenset()
    description: str = ""


def generate(spec: ScenarioSpec, seed: int) -> Dataset:
    if seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    if spec.steps < 5:
        raise ValueError("scenario must contain at least five hourly steps")
    if spec.fault_service not in SERVICES:
        raise ValueError(f"unknown fault service {spec.fault_service!r}")
    if spec.fault_start < 0 or (spec.fault_end is not None and spec.fault_end <= spec.fault_start):
        raise ValueError("invalid fault interval")

    scenario_id = _scenario_id(seed, spec.key)
    rng = random.Random(seed)
    metrics, states = _make_metrics(
        seed, rng, spec.fault_intensity, steps=spec.steps, scenario_id=scenario_id,
        fault_service=spec.fault_service, fault_start=spec.fault_start,
        fault_end=spec.fault_end, fault_threshold=spec.fault_threshold,
        missing_windows=spec.missing_windows, additional_faults=spec.additional_faults,
    )
    if spec.fault_metric_visibility_delay or spec.hide_fault_metrics:
        # The system state still propagates through the call graph. This
        # counterfactual telemetry masking models delayed or silent alerting.
        baseline_metrics, _ = _make_metrics(
            seed, random.Random(seed), 0.0, steps=spec.steps, scenario_id=scenario_id,
            fault_service=spec.fault_service, fault_start=spec.fault_start,
            fault_end=spec.fault_end, fault_threshold=spec.fault_threshold,
            missing_windows=spec.missing_windows, additional_faults=spec.additional_faults,
        )
        baseline_by_id = {point.id: point.value for point in baseline_metrics}
        visible_from = spec.steps if spec.hide_fault_metrics else spec.fault_start + spec.fault_metric_visibility_delay
        metrics = [
            point.model_copy(update={"value": baseline_by_id[point.id]})
            if point.service == spec.fault_service and spec.fault_start <= int(point.id.split("-")[2]) < visible_from
            else point
            for point in metrics
        ]
    if spec.suppress_metric_services:
        metrics = [point for point in metrics if point.service not in spec.suppress_metric_services]
    spans = _make_spans(seed, rng, states, spec.no_trace_services)
    logs = _make_logs(seed, rng, states)
    events = [
        ChangeEvent(
            id=f"change-{seed}-{index}", kind=kind, timestamp=_timestamp(step), service=service,
            change_id=change_id, details={"change_id": change_id}, timestamp_uncertainty_ms=0,
        )
        for index, (kind, service, step, change_id) in enumerate(spec.changes, start=1)
    ]
    dependency_pairs = (("checkout", "payments"), ("checkout", "inventory"), ("payments", "database"), ("inventory", "database"))
    if spec.key == "partial_graph":
        dependency_pairs = tuple(edge for edge in dependency_pairs if edge != ("payments", "database"))
    dependencies = [DependencyEdge(id=f"dependency-{caller}-{callee}", caller=caller, callee=callee) for caller, callee in dependency_pairs]
    files = ["metrics/metrics.json", "traces/spans.json", "logs/events.jsonl", "events.json", "dependency_graph.json"]
    manifest = ScenarioManifest(
        scenario_id=scenario_id, seed=seed,
        time_range=TimeRange(start=START, end=_timestamp(spec.steps - 1)),
        services=list(SERVICES),
        record_counts={"metrics": len(metrics), "spans": len(spans), "logs": len(logs), "events": len(events), "dependencies": len(dependencies)},
        files=files, dependency_graph_complete=spec.key != "partial_graph",
    )
    truth = {
        "scenario_name": spec.key,
        "scenario_id": scenario_id,
        "seed": seed,
        "description": spec.description,
        "injected_fault": ({"service": spec.fault_service, "start_step": spec.fault_start, "end_step": spec.fault_end, "intensity": spec.fault_intensity, "threshold": spec.fault_threshold} if not spec.additional_faults else [{"service": spec.fault_service, "start_step": spec.fault_start, "end_step": spec.fault_end, "intensity": spec.fault_intensity, "threshold": spec.fault_threshold}, *[{"service": s, "start_step": start, "end_step": end, "intensity": intensity, "threshold": threshold} for s,start,end,intensity,threshold in spec.additional_faults]]),
        "observability": {"fault_metric_visibility_delay_steps": spec.fault_metric_visibility_delay, "fault_metrics_suppressed_after_start": spec.hide_fault_metrics},
        "changes": [{"kind": kind, "service": service, "step": step, "change_id": change_id} for kind, service, step, change_id in spec.changes],
        "telemetry_omissions": {"metric_windows": {service: sorted(windows) for service, windows in spec.missing_windows.items()}, "metric_services_absent": sorted(spec.suppress_metric_services), "traces_missing_for": sorted(spec.no_trace_services)},
        "omitted_dependency_edges": ["payments->database"] if spec.key == "partial_graph" else [],
    }
    return Dataset(manifest, tuple(metrics), tuple(spans), tuple(logs), tuple(events), tuple(dependencies), truth)
