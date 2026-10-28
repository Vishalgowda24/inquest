"""P2 scenario semantics, opacity, and generated variants."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from simulator.core.export import write_export
from simulator.scenarios.coincident_restart import generate as coincident_restart
from simulator.scenarios.red_herring_deploy import generate as red_herring_deploy
from simulator.scenarios.shared_dependency import generate as shared_dependency
from simulator.scenarios.missing_telemetry import generate as missing_telemetry
from simulator.scenarios.long_seasonal import generate as long_seasonal
from simulator.scenarios.late_alerting_cause import generate as late_alerting_cause
from simulator.scenarios.silent_cause import generate as silent_cause

SCENARIOS = (coincident_restart, red_herring_deploy, shared_dependency, missing_telemetry, long_seasonal, late_alerting_cause, silent_cause)
DEFAULT_SCENARIOS = ("clean_bad_deploy", "coincident_restart", "red_herring_deploy", "shared_dependency", "missing_telemetry", "long_seasonal", "late_alerting_cause", "silent_cause")


def test_default_scenario_registry_excludes_reserved_holdout() -> None:
    from simulator.cli import SCENARIOS as registered

    names = tuple(registered)
    assert names[:len(DEFAULT_SCENARIOS)] == DEFAULT_SCENARIOS
    assert {"concurrent_causes", "noisy_alerts", "partial_graph", "red_herring_hard"} <= set(names)
    assert "holdout" not in names


def _metric(dataset, service: str, metric: str, step: int) -> float:
    point = next(item for item in dataset.metrics if item.service == service and item.metric == metric and int(item.id.split("-")[2]) == step)
    return point.value


@pytest.mark.parametrize("generator", SCENARIOS)
def test_each_new_scenario_has_three_seeded_opaque_exports_without_truth_labels(tmp_path: Path, generator) -> None:
    ids = set()
    for seed in (1, 2, 3):
        dataset = generator(seed)
        ids.add(dataset.manifest.scenario_id)
        assert dataset.manifest.scenario_id.startswith("scn_")
        assert dataset.manifest.seed == seed
        export = tmp_path / dataset.manifest.scenario_id / f"seed_{seed}" / "export"
        write_export(dataset, export, tmp_path / "sim_truth" / f"{seed}.truth.json")
        exported_text = "\n".join(path.read_text(encoding="utf-8") for path in export.rglob("*") if path.is_file())
        assert dataset.truth["scenario_name"] not in exported_text
        assert "injected_fault" not in exported_text
    assert len(ids) == 3


def test_coincident_restart_config_change_degrades_then_restart_recovers() -> None:
    dataset = coincident_restart(1)
    events = {(item.kind, item.service, item.timestamp) for item in dataset.events}
    assert any(kind == "configuration_change" and service == "database" for kind, service, _ in events)
    assert any(kind == "restart" and service == "database" for kind, service, _ in events)
    before = _metric(dataset, "database", "latency_ms", 9)
    during = _metric(dataset, "database", "latency_ms", 12)
    after = _metric(dataset, "database", "latency_ms", 17)
    assert during > before * 1.5
    assert after < during * 0.75


def test_red_herring_is_unrelated_to_faulted_service() -> None:
    dataset = red_herring_deploy(1)
    deploy = next(event for event in dataset.events if event.kind == "deployment")
    cause = next(event for event in dataset.events if event.kind == "configuration_change")
    assert deploy.service == "inventory" and cause.timestamp < deploy.timestamp
    assert cause.service == "payments"
    assert _metric(dataset, "payments", "latency_ms", 9) > _metric(dataset, "payments", "latency_ms", 8) * 1.5


def test_shared_dependency_degrades_callers_without_any_change_event() -> None:
    dataset = shared_dependency(1)
    assert dataset.events == ()
    for service in ("database", "payments", "inventory", "checkout"):
        assert _metric(dataset, service, "latency_ms", 12) > _metric(dataset, service, "latency_ms", 9)


def test_missing_telemetry_has_absent_service_traces_and_long_metric_gap() -> None:
    dataset = missing_telemetry(1)
    assert not any(span.service == "inventory" for span in dataset.spans)
    observed = {int(item.id.split("-")[2]) for item in dataset.metrics if item.service == "checkout" and item.metric == "latency_ms"}
    assert set(range(7, 14)).isdisjoint(observed)


def test_long_seasonal_scenario_covers_at_least_two_days() -> None:
    dataset = long_seasonal(1)
    assert (dataset.manifest.time_range.end - dataset.manifest.time_range.start) >= timedelta(hours=48)
    assert len([item for item in dataset.metrics if item.service == "database" and item.metric == "latency_ms"]) >= 48


def test_harder_alert_order_confounders_hide_or_delay_cause_alerts(tmp_path: Path) -> None:
    from inquest.core.signals import analyze_signals
    from inquest.stages.s00_ingest.adapters import CanonicalJsonAdapter

    for seed in (1, 2, 3):
        late = late_alerting_cause(seed)
        late_folder = tmp_path / "late" / str(seed) / late.manifest.scenario_id / "export"
        write_export(late, late_folder, tmp_path / "sim_truth" / "late" / f"{seed}.json")
        late_analysis = analyze_signals(CanonicalJsonAdapter().load(late_folder))
        late_onsets = {item.service: item for item in late_analysis.onsets if item.metric == "latency_ms"}
        assert late_onsets["payments"].onset_time < late_onsets["database"].onset_time
        assert late_onsets["checkout"].onset_time < late_onsets["database"].onset_time
        assert late_analysis.service_order[0] != "database"

        silent = silent_cause(seed)
        silent_folder = tmp_path / "silent" / str(seed) / silent.manifest.scenario_id / "export"
        write_export(silent, silent_folder, tmp_path / "sim_truth" / "silent" / f"{seed}.json")
        silent_analysis = analyze_signals(CanonicalJsonAdapter().load(silent_folder))
        assert not any(item.service == "database" for item in silent_analysis.onsets)
        assert "database" not in silent_analysis.service_order
        assert silent_analysis.service_order
