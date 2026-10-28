"""Simulator-to-canonical-ingest and signal processing acceptance tests."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

import pytest

from inquest.contracts import Report
from inquest.core.builtins import default_registry
from inquest.core.config import InquestConfig
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner
from inquest.core.signals import analyze_signals
from inquest.stages.s00_ingest.adapters import CanonicalJsonAdapter
from simulator.core.export import write_export
from simulator.scenarios.clean_bad_deploy.model import START, generate
from simulator.scenarios.long_seasonal import generate as generate_long


def _export(seed: int, tmp_path: Path) -> Path:
    data = generate(seed)
    folder = tmp_path / data.manifest.scenario_id / "export"
    write_export(data, folder, tmp_path / "sim_truth" / f"seed_{seed}.truth.json")
    return folder


def test_canonical_adapter_ingests_simulator_export_with_diagnostics(tmp_path: Path) -> None:
    folder = _export(1, tmp_path)
    adapter = CanonicalJsonAdapter()
    assert adapter.detect(folder)
    bundle = adapter.load(folder)
    assert bundle.manifest.source == "synthetic"
    assert bundle.manifest.scenario_id == folder.parent.name
    assert bundle.diagnostics.accepted_counts["metrics"] == 380
    assert bundle.diagnostics.rejected_counts["metrics"] == 0
    assert any("clock uncertainty" in warning for warning in bundle.diagnostics.warnings)
    assert any("coverage gap" in warning.lower() for warning in bundle.diagnostics.warnings)
    assert bundle.metrics[0].source_metadata["file"] == "metrics.json"


def test_bad_canonical_record_is_quarantined_with_file_and_record_index(tmp_path: Path) -> None:
    folder = _export(1, tmp_path)
    metrics_path = folder / "metrics" / "metrics.json"
    records = json.loads(metrics_path.read_text(encoding="utf-8"))
    records[0]["schema_version"] = "9.0"
    metrics_path.write_text(json.dumps(records, sort_keys=True, indent=2), encoding="utf-8")
    bundle = CanonicalJsonAdapter().load(folder)
    assert bundle.diagnostics.accepted_counts["metrics"] == 379
    assert bundle.diagnostics.rejected_counts["metrics"] == 1
    issue = bundle.diagnostics.quarantined[0]
    assert issue.record_index == 1
    assert str(metrics_path) == issue.file_path
    assert "schema_version" in issue.error


def test_three_seeds_recover_dependency_onset_order_with_uncertainty(tmp_path: Path) -> None:
    expected_offsets = {"database": -1500, "payments": -450, "inventory": 1200, "checkout": 800}
    for seed in (1, 2, 3):
        analysis = analyze_signals(CanonicalJsonAdapter().load(_export(seed, tmp_path / str(seed))))
        onsets = {item.service: item for item in analysis.onsets if item.metric == "latency_ms"}
        assert {"database", "payments", "inventory", "checkout"} <= onsets.keys()
        expected_steps = {"database": 10, "payments": 11, "inventory": 11, "checkout": 12}
        ordered = [onsets[name] for name in ("database", "payments", "inventory", "checkout")]
        assert onsets["database"].onset_time < min(onsets["payments"].onset_time, onsets["inventory"].onset_time)
        assert max(onsets["payments"].onset_time, onsets["inventory"].onset_time) < onsets["checkout"].onset_time
        for service, onset in zip(("database", "payments", "inventory", "checkout"), ordered):
            expected = START + timedelta(hours=expected_steps[service], milliseconds=expected_offsets[service])
            delta_ms = abs((onset.onset_time - expected).total_seconds() * 1000)
            tolerance_ms = max(60 * 60 * 1000, onset.timestamp_uncertainty_ms)
            assert delta_ms <= tolerance_ms
            assert onset.confidence >= 0.5


def test_full_ingest_vault_signal_pipeline_emits_source_report_and_artifacts(tmp_path: Path) -> None:
    folder = _export(1, tmp_path)
    config = InquestConfig(global_seed=1, log_level="INFO", data_inbox=tmp_path / "inbox", runs_dir=tmp_path / "runs", csv_mapping_path=Path("config/csv_mapping.yaml"), simulation_clock="2025-01-15T12:00:00Z", stages={"smoke": True, "s00_ingest": True, "s01_vault": True, "s02_signals": True})
    context = RunContext(run_id="run_integration", scenario_id=folder.parent.name, runs_dir=config.runs_dir, clock=config.simulation_clock, config=config)
    report = StageRunner(default_registry(config)).run(context, ["s00_ingest", "s01_vault", "s02_signals"], {"folder": str(folder)})
    validated = Report.model_validate_json((config.runs_dir / "run_integration" / "report.json").read_text(encoding="utf-8"))
    assert validated.source == "synthetic"
    assert validated.synthetic
    assert [item.stage for item in report.stages] == ["s00_ingest", "s01_vault", "s02_signals"]
    assert (config.runs_dir / "run_integration" / "vault" / "chain.jsonl").exists()
    for index, stage in enumerate(("s00_ingest", "s01_vault", "s02_signals")):
        stage_path = config.runs_dir / "run_integration" / f"{index:02d}_{stage}"
        assert {"input.json", "output.json", "log.jsonl", "status.json"} <= {path.name for path in stage_path.iterdir()}


def test_clean_scenario_signal_output_matches_golden_file(tmp_path: Path) -> None:
    analysis = analyze_signals(CanonicalJsonAdapter().load(_export(1, tmp_path)))
    actual = json.dumps(analysis.model_dump(mode="json"), sort_keys=True, indent=2) + "\n"
    golden = Path(__file__).parent / "golden" / "clean_bad_deploy_signals.json"
    assert actual == golden.read_text(encoding="utf-8")


def test_long_scenario_enables_seasonal_normalization_when_coverage_allows(tmp_path: Path) -> None:
    dataset = generate_long(2)
    folder = tmp_path / dataset.manifest.scenario_id / "export"
    write_export(dataset, folder, tmp_path / "sim_truth" / "long.truth.json")
    bundle = CanonicalJsonAdapter().load(folder)
    analysis = analyze_signals(bundle)
    points = [item for item in bundle.metrics if item.service == "database" and item.metric == "latency_ms"]
    from inquest.core.signals import _normalized_values

    _, seasonal = _normalized_values(points)
    assert seasonal
    assert not any("Seasonal normalization not applied" in warning for warning in analysis.warnings)
