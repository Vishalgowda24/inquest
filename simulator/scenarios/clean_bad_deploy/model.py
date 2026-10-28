"""Deterministic, load-sensitive microservice scenario."""

from __future__ import annotations

import random
import math
import hmac
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from simulator.contracts import ChangeEvent, DependencyEdge, LogEvent, MetricPoint, ScenarioManifest, Span
from simulator.contracts.schemas import TimeRange

START = datetime(2025, 1, 15, 12, 0, tzinfo=timezone.utc)
SALT_PATH = Path(__file__).resolve().parents[2] / "sim_truth" / ".scenario_id_salt"
SERVICES = ("checkout", "payments", "inventory", "database")
DEPENDENCIES = (("checkout", "payments"), ("checkout", "inventory"), ("payments", "database"), ("inventory", "database"))
UNITS = {"request_rate": "requests/second", "latency_ms": "ms", "error_rate": "ratio", "cpu_percent": "percent", "memory_mb": "MB"}
CLOCK_SKEW_MS = {"checkout": 800, "payments": -450, "inventory": 1200, "database": -1500}


@dataclass(frozen=True)
class ServiceState:
    latency_ms: float
    error_rate: float
    cpu_percent: float
    memory_mb: float
    request_rate: float


@dataclass(frozen=True)
class Dataset:
    manifest: ScenarioManifest
    metrics: tuple[MetricPoint, ...]
    spans: tuple[Span, ...]
    logs: tuple[LogEvent, ...]
    events: tuple[ChangeEvent, ...]
    dependencies: tuple[DependencyEdge, ...]
    truth: dict[str, object]


def _timestamp(step: int, skew_ms: int = 0) -> datetime:
    return START + timedelta(hours=step, milliseconds=skew_ms)


def _stable_id(kind: str, seed: int, *parts: object) -> str:
    return f"{kind}-{seed}-" + "-".join(str(part) for part in parts)


def _service_states(minute: int, rng: random.Random, fault_intensity: float, history: list[dict[str, ServiceState]], *, fault_service: str = "database", fault_start: int = 10, fault_end: int | None = None, fault_threshold: float = 42.0, additional_faults: tuple[tuple[str, int, int | None, float, float], ...] = ()) -> dict[str, ServiceState]:
    phase = 2.0 * 3.141592653589793 * minute / 24.0
    traffic = 0.82 + 0.18 * (0.5 + 0.5 * math.sin(phase))
    load = {"checkout": 38 * traffic, "payments": 31 * traffic, "inventory": 18 * traffic, "database": 74 * traffic}
    downstream: dict[str, ServiceState] = {}
    for service in _dependency_order():
        rate = load[service] * (0.72 if service == "database" else 1.0)
        own_sat = max(0.0, rate - (66 if service == "database" else 90))
        fault_active = service == fault_service and minute >= fault_start and (fault_end is None or minute < fault_end)
        fault_sat = max(0.0, rate - fault_threshold) * (fault_intensity if fault_active else 0.0)
        for extra_service, extra_start, extra_end, extra_intensity, extra_threshold in additional_faults:
            active = service == extra_service and minute >= extra_start and (extra_end is None or minute < extra_end)
            if active:
                fault_sat += max(0.0, rate - extra_threshold) * extra_intensity
        dep_states = [history[minute - 1][name] if minute > 0 else downstream[name] for caller, name in DEPENDENCIES if caller == service]
        latency = 18 + rate * (0.16 if service == "database" else 0.07) + own_sat * 1.8 + fault_sat * 3.2
        latency += sum(dep.latency_ms * 0.55 for dep in dep_states) + rng.uniform(-1.8, 1.8)
        local_error = min(0.65, 0.002 + own_sat * 0.004 + fault_sat * 0.012)
        propagated = 1.0
        for dep in dep_states:
            propagated *= 1.0 - dep.error_rate
        error = min(0.95, 1.0 - (1.0 - local_error) * propagated)
        cpu = min(99.0, 22 + rate * 0.48 + own_sat * 0.45 + fault_sat * 0.9 + rng.uniform(-2, 2))
        mem = 260 + rate * 1.2 + fault_sat * 1.6 + rng.uniform(-4, 4)
        downstream[service] = ServiceState(max(1.0, latency), error, cpu, mem, rate)
    return downstream


def _dependency_order() -> list[str]:
    """Derive callee-before-caller order from the declared graph."""
    remaining = set(SERVICES)
    ordered: list[str] = []
    while remaining:
        ready = sorted(service for service in remaining if all(callee in ordered for caller, callee in DEPENDENCIES if caller == service))
        if not ready:
            raise ValueError("dependency graph contains a cycle")
        ordered.extend(ready)
        remaining.difference_update(ready)
    return ordered


def _make_metrics(seed: int, rng: random.Random, fault_intensity: float, *, steps: int = 20, scenario_id: str | None = None, fault_service: str = "database", fault_start: int = 10, fault_end: int | None = None, fault_threshold: float = 42.0, missing_windows: dict[str, set[int]] | None = None, additional_faults: tuple[tuple[str, int, int | None, float, float], ...] = ()) -> tuple[list[MetricPoint], list[dict[str, ServiceState]]]:
    metrics: list[MetricPoint] = []
    all_states: list[dict[str, ServiceState]] = []
    scenario_id = scenario_id or _scenario_id(seed)
    missing_windows = missing_windows or {}
    for minute in range(steps):
        states = _service_states(minute, rng, fault_intensity, all_states, fault_service=fault_service, fault_start=fault_start, fault_end=fault_end, fault_threshold=fault_threshold, additional_faults=additional_faults)
        all_states.append(states)
        for service in SERVICES:
            state = states[service]
            if rng.random() < 0.035 or minute in missing_windows.get(service, set()):
                continue
            for metric in ("request_rate", "latency_ms", "error_rate", "cpu_percent", "memory_mb"):
                metrics.append(MetricPoint(
                    id=_stable_id("metric", seed, minute, service, metric),
                    timestamp=_timestamp(minute, CLOCK_SKEW_MS[service]), service=service, metric=metric,
                    value=round(getattr(state, {"request_rate": "request_rate", "latency_ms": "latency_ms", "error_rate": "error_rate", "cpu_percent": "cpu_percent", "memory_mb": "memory_mb"}[metric]), 4),
                    unit=UNITS[metric], dimensions={"scenario_id": scenario_id, "window_minutes": "60"},
                    timestamp_uncertainty_ms=abs(CLOCK_SKEW_MS[service]),
                ))
    return metrics, all_states


def _append_trace_tree(spans: list[Span], seed: int, trace_id: str, step: int, service: str, parent: str | None, path: tuple[str, ...], states: dict[str, ServiceState], rng: random.Random, no_trace_services: frozenset[str] = frozenset()) -> None:
    span_id = _stable_id("span", seed, step, *path)
    state = states[service]
    if service not in no_trace_services:
        spans.append(Span(
        trace_id=trace_id, span_id=span_id, parent_span_id=parent, service=service,
        operation="request" if parent is None else "call", start_time=_timestamp(step, CLOCK_SKEW_MS[service]),
        duration_ms=round(state.latency_ms, 4), status="ERROR" if rng.random() < state.error_rate else "OK",
        attributes={"scenario_step": step, "synthetic": True}, timestamp_uncertainty_ms=abs(CLOCK_SKEW_MS[service]),
        ))
    for caller, callee in DEPENDENCIES:
        if caller == service:
            _append_trace_tree(spans, seed, trace_id, step, callee, span_id, (*path, callee), states, rng, no_trace_services)


def _make_spans(seed: int, rng: random.Random, states_by_minute: list[dict[str, ServiceState]], no_trace_services: frozenset[str] = frozenset()) -> list[Span]:
    spans: list[Span] = []
    for minute, states in enumerate(states_by_minute):
        for request in range(3):
            trace = _stable_id("trace", seed, minute, request)
            _append_trace_tree(spans, seed, trace, minute, "checkout", None, (str(request), "checkout"), states, rng, no_trace_services)
    return spans


def _make_logs(seed: int, rng: random.Random, states_by_minute: list[dict[str, ServiceState]]) -> list[LogEvent]:
    logs: list[LogEvent] = []
    for minute, states in enumerate(states_by_minute):
        for service in SERVICES:
            failed = states[service].error_rate > 0.12
            noisy = rng.random() < 0.15
            if failed or noisy:
                level = "ERROR" if failed else "INFO"
                message = "request failed while dependency latency elevated" if failed else "periodic health check completed"
                skew = CLOCK_SKEW_MS[service]
                logs.append(LogEvent(
                    id=_stable_id("log", seed, minute, service), timestamp=_timestamp(minute, skew), service=service,
                    level=level, message=message, attributes={"scenario_step": minute, "synthetic": True},
                    timestamp_uncertainty_ms=abs(skew),
                ))
    return logs


def _scenario_id(seed: int, scenario_key: str = "clean_bad_deploy") -> str:
    salt = SALT_PATH.read_bytes()
    digest = hmac.digest(salt, f"{scenario_key}:{seed}:sim-v1".encode(), "sha256").hex()[:12]
    return f"scn_{digest}"


def generate(seed: int, fault_intensity: float = 1.35) -> Dataset:
    """Generate one complete, reproducible scenario for a nonnegative seed."""
    if seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    if fault_intensity < 0:
        raise ValueError("fault_intensity must be nonnegative")
    rng = random.Random(seed)
    metrics, states = _make_metrics(seed, rng, fault_intensity)
    spans = _make_spans(seed, rng, states)
    logs = _make_logs(seed, rng, states)
    events = [
        ChangeEvent(id="change-1", kind="deployment", timestamp=_timestamp(10), service="database", change_id="release-db-2", details={"version": "release-2"}, timestamp_uncertainty_ms=0),
        ChangeEvent(id="change-2", kind="deployment", timestamp=_timestamp(7), service="inventory", change_id="release-inventory-4", details={"version": "release-4"}, timestamp_uncertainty_ms=0),
    ]
    dependencies = [DependencyEdge(id=f"dependency-{caller}-{callee}", caller=caller, callee=callee) for caller, callee in DEPENDENCIES]
    file_list = ["metrics/metrics.json", "traces/spans.json", "logs/events.jsonl", "events.json", "dependency_graph.json"]
    manifest = ScenarioManifest(
        scenario_id=_scenario_id(seed), seed=seed,
        time_range=TimeRange(start=START, end=_timestamp(19)), services=list(SERVICES),
        record_counts={"metrics": len(metrics), "spans": len(spans), "logs": len(logs), "events": len(events), "dependencies": len(dependencies)},
        files=file_list,
    )
    truth = {"scenario_name": "clean_bad_deploy", "scenario_id": _scenario_id(seed), "seed": seed, "injected_fault": {"kind": "database_saturation_after_deployment", "service": "database", "change_id": "release-db-2", "step": 10, "intensity": fault_intensity}}
    return Dataset(manifest, tuple(metrics), tuple(spans), tuple(logs), tuple(events), tuple(dependencies), truth)
