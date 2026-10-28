"""P0 simulator contract, determinism, propagation, and isolation tests."""

from __future__ import annotations

import json
import hashlib
from datetime import timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from simulator.contracts import ChangeEvent, DependencyEdge, LogEvent, MetricPoint, ScenarioManifest, Span
from simulator.core.export import write_export
from simulator.scenarios.clean_bad_deploy.model import START, generate


def test_seed_reproduces_identical_records() -> None:
    first, second = generate(7), generate(7)
    assert first.manifest.model_dump(mode="json") == second.manifest.model_dump(mode="json")
    assert [item.model_dump(mode="json") for item in first.metrics] == [item.model_dump(mode="json") for item in second.metrics]
    assert [item.model_dump(mode="json") for item in first.spans] == [item.model_dump(mode="json") for item in second.spans]
    assert first.truth == second.truth


def test_generated_records_validate_and_manifest_is_synthetic() -> None:
    data = generate(1)
    assert data.manifest.synthetic is True
    assert data.manifest.scenario_id.startswith("scn_")
    unsalted = hashlib.sha256(f"clean_bad_deploy:1:sim-v1".encode()).hexdigest()[:12]
    assert data.manifest.scenario_id != f"scn_{unsalted}"
    assert set(data.manifest.services) == {"checkout", "payments", "inventory", "database"}
    for record, schema in (
        *((record, MetricPoint) for record in data.metrics),
        *((record, Span) for record in data.spans),
        *((record, LogEvent) for record in data.logs),
        *((record, ChangeEvent) for record in data.events),
        *((record, DependencyEdge) for record in data.dependencies),
    ):
        schema.model_validate(record.model_dump())
    ScenarioManifest.model_validate(data.manifest.model_dump())
    assert data.manifest.record_counts["metrics"] == len(data.metrics)


def test_rejects_unknown_schema_version_and_naive_timestamp() -> None:
    record = generate(1).metrics[0].model_dump(mode="json")
    with pytest.raises(ValidationError):
        MetricPoint.model_validate({**record, "schema_version": "2.0"})
    with pytest.raises(ValidationError):
        MetricPoint.model_validate({**record, "timestamp": "2025-01-15T12:00:00"})


def test_export_and_truth_are_separate_and_export_id_is_opaque(tmp_path: Path) -> None:
    data = generate(1)
    export = tmp_path / data.manifest.scenario_id / "export"
    truth = tmp_path / "sim_truth" / "scenario.truth.json"
    write_export(data, export, truth)
    repeat_export = tmp_path / data.manifest.scenario_id / "repeat"
    repeat_truth = tmp_path / "repeat_truth" / "scenario.truth.json"
    write_export(generate(1), repeat_export, repeat_truth)
    for path in export.rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (repeat_export / path.relative_to(export)).read_bytes()
    assert truth.read_bytes() == repeat_truth.read_bytes()
    assert (export / "manifest.json").is_file()
    assert truth.is_file()
    export_text = "\n".join(path.read_text(encoding="utf-8") for path in export.rglob("*") if path.is_file())
    assert "clean_bad_deploy" not in export_text
    assert "injected_fault" not in export_text
    assert "database_saturation" not in export_text
    assert "synthetic_fault" not in export_text
    ScenarioManifest.model_validate(json.loads((export / "manifest.json").read_text(encoding="utf-8")))
    for record in json.loads((export / "metrics" / "metrics.json").read_text(encoding="utf-8")):
        MetricPoint.model_validate(record)
    for record in json.loads((export / "traces" / "spans.json").read_text(encoding="utf-8")):
        Span.model_validate(record)
    for line in (export / "logs" / "events.jsonl").read_text(encoding="utf-8").splitlines():
        LogEvent.model_validate_json(line)
    for record in json.loads((export / "events.json").read_text(encoding="utf-8")):
        ChangeEvent.model_validate(record)
    for record in json.loads((export / "dependency_graph.json").read_text(encoding="utf-8")):
        DependencyEdge.model_validate(record)


def test_inquest_runtime_cannot_read_scenario_names_or_truth() -> None:
    inquest = Path(__file__).resolve().parents[2] / "inquest"
    scenario_name = "clean" + "_bad" + "_deploy"
    truth_file = "truth" + ".json"
    truth_dir = "sim" + "_truth"
    assert inquest.exists()
    for source in inquest.rglob("*.py"):
        if "eval" in source.parts:
            continue
        content = source.read_text(encoding="utf-8")
        assert scenario_name not in content, source
        assert truth_file not in content, source
        assert truth_dir not in content, source
        assert "from simulator" not in content, source
        assert "import simulator" not in content, source


def test_fault_parameter_changes_downstream_metrics_via_call_graph() -> None:
    baseline = generate(11, fault_intensity=0.0)
    injected = generate(11, fault_intensity=1.8)
    by_id_base = {metric.id: metric for metric in baseline.metrics}
    by_id_fault = {metric.id: metric for metric in injected.metrics}
    for service in ("database", "payments", "checkout"):
        differences = [
            by_id_fault[item_id].value - metric.value
            for item_id, metric in by_id_base.items()
            if metric.service == service and metric.metric == "latency_ms" and item_id in by_id_fault
            and int(item_id.split("-")[2]) >= 11
        ]
        assert differences and sum(differences) / len(differences) > 0


def test_latency_summary_has_seasonality_jitter_skew_and_dropped_windows() -> None:
    data = generate(1)
    checkout = [item for item in data.metrics if item.service == "checkout" and item.metric == "latency_ms"]
    assert len(checkout) < 20
    values = [item.value for item in checkout]
    assert len(set(values)) > 10
    offsets = [round((item.timestamp - (START + timedelta(hours=int(item.id.split("-")[2])))).total_seconds() * 1000) for item in checkout]
    assert set(offsets) == {800}
    steps = [int(item.id.split("-")[2]) for item in checkout]
    early = [item.value for step, item in zip(steps, checkout) if step < 5]
    daytime_peak = [item.value for step, item in zip(steps, checkout) if 5 <= step < 10]
    assert sum(daytime_peak) / len(daytime_peak) > sum(early) / len(early)


def test_truth_labels_do_not_appear_in_any_workspace_export_file(tmp_path: Path) -> None:
    data = generate(1)
    export = tmp_path / data.manifest.scenario_id / "export"
    write_export(data, export, tmp_path / "sim_truth" / "seed_1.truth.json")
    roots = [Path(__file__).resolve().parents[1], export.parent.parent]
    files = {path for root in roots if root.exists() for path in root.rglob("*") if path.is_file() and "export" in path.parts}
    forbidden = ("clean_bad_deploy", "database_saturation_after_deployment", "injected_fault")
    for path in files:
        content = path.read_text(encoding="utf-8")
        assert not any(term in content for term in forbidden), path
