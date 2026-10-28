"""Tests for the real incident data adapter and CLI ingest-real command."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from typer.testing import CliRunner

from inquest.cli import app
from inquest.core.errors import IngestError
from inquest.core.vault import read_vault_ids, verify_chain
from inquest.stages.s00_ingest.adapters import RealIncidentAdapter


runner = CliRunner()


def _create_minimal_incident(folder: Path, *, omit: str | None = None, malformed: str | None = None) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    when = "2026-03-15T14:00:00Z"
    when_onset = "2026-03-15T14:10:00Z"

    if omit != "metrics":
        m_val = "bad_numeric_value" if malformed == "metric_val" else 150.0
        metrics = [
            {"timestamp": when, "service": "db_service", "metric": "latency_ms", "value": 20.0, "unit": "ms"},
            {"timestamp": when_onset, "service": "db_service", "metric": "latency_ms", "value": m_val, "unit": "ms"},
            {"timestamp": when, "service": "pay_service", "metric": "latency_ms", "value": 15.0, "unit": "ms"},
            {"timestamp": when_onset, "service": "pay_service", "metric": "latency_ms", "value": 110.0, "unit": "ms"},
        ]
        if malformed == "metric_json":
            (folder / "metrics.json").write_text("{bad json: true", encoding="utf-8")
        else:
            (folder / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")

    if omit != "events":
        events = [
            {"timestamp": when, "service": "db_service", "kind": "deploy", "change_id": "dep-1", "description": "db update"}
        ]
        (folder / "events.json").write_text(json.dumps(events), encoding="utf-8")

    if omit != "alerts":
        alerts = [
            {"timestamp": when_onset, "service": "pay_service", "level": "ERROR", "message": "High error rate"}
        ]
        (folder / "alerts.json").write_text(json.dumps(alerts), encoding="utf-8")

    if omit != "dependency_graph":
        if malformed == "graph_json":
            (folder / "dependency_graph.json").write_text("[bad json", encoding="utf-8")
        elif malformed == "graph_edge":
            (folder / "dependency_graph.json").write_text(json.dumps([{"caller": "only_caller"}]), encoding="utf-8")
        else:
            graph = [
                {"caller": "pay_service", "callee": "db_service"}
            ]
            (folder / "dependency_graph.json").write_text(json.dumps(graph), encoding="utf-8")

    # Offline evaluation labels (must be strictly ignored by pipeline)
    eval_labels = {
        "evaluation_cause": ["db_service"],
        "incident_window": {"start": when, "end": "2026-03-15T15:00:00Z"},
    }
    (folder / "labels.json").write_text(json.dumps(eval_labels), encoding="utf-8")


def test_real_data_missing_files_validation(tmp_path: Path) -> None:
    adapter = RealIncidentAdapter()

    # Missing metrics
    p1 = tmp_path / "missing_metrics"
    _create_minimal_incident(p1, omit="metrics")
    with pytest.raises(IngestError, match="Missing required metrics"):
        adapter.validate(p1)

    # Missing events
    p2 = tmp_path / "missing_events"
    _create_minimal_incident(p2, omit="events")
    with pytest.raises(IngestError, match="Missing required events"):
        adapter.validate(p2)

    # Missing alerts
    p3 = tmp_path / "missing_alerts"
    _create_minimal_incident(p3, omit="alerts")
    with pytest.raises(IngestError, match="Missing required alerts"):
        adapter.validate(p3)

    # Missing dependency graph
    p4 = tmp_path / "missing_graph"
    _create_minimal_incident(p4, omit="dependency_graph")
    with pytest.raises(IngestError, match="Missing required dependency graph"):
        adapter.validate(p4)


def test_real_data_malformed_input_validation(tmp_path: Path) -> None:
    adapter = RealIncidentAdapter()

    # Non-existent path
    with pytest.raises(IngestError, match="not an accessible directory"):
        adapter.validate(tmp_path / "non_existent")

    # Malformed metric JSON
    p1 = tmp_path / "bad_metric_json"
    _create_minimal_incident(p1, malformed="metric_json")
    with pytest.raises(IngestError, match="Malformed JSON in metrics file"):
        adapter.validate(p1)

    # Malformed metric value (non-numeric)
    p2 = tmp_path / "bad_metric_val"
    _create_minimal_incident(p2, malformed="metric_val")
    with pytest.raises(IngestError, match="non-numeric value"):
        adapter.validate(p2)

    # Malformed dependency graph JSON
    p3 = tmp_path / "bad_graph_json"
    _create_minimal_incident(p3, malformed="graph_json")
    with pytest.raises(IngestError, match="Malformed JSON in dependency graph"):
        adapter.validate(p3)

    # Malformed dependency edge
    p4 = tmp_path / "bad_graph_edge"
    _create_minimal_incident(p4, malformed="graph_edge")
    with pytest.raises(IngestError, match="required keys 'caller' and 'callee'"):
        adapter.validate(p4)


def test_real_data_ingest_real_cli_runs_s00_to_s05(tmp_path: Path) -> None:
    incident_dir = tmp_path / "sample_incident"
    _create_minimal_incident(incident_dir)

    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    config_file = tmp_path / "config.yaml"
    config_file.write_text(Path("config.yaml").read_text(encoding="utf-8").replace("runs_dir: runs", f"runs_dir: {runs_dir.as_posix()}"), encoding="utf-8")

    result = runner.invoke(app, ["ingest-real", str(incident_dir), "--config", str(config_file)])
    assert result.exit_code == 0, result.output
    assert "Inquest real incident report" in result.output

    # Verify run artifacts
    run_folders = list(runs_dir.glob("real_*"))
    assert len(run_folders) == 1
    run_dir = run_folders[0]

    # Verify vault chain
    chain_file = run_dir / "vault" / "chain.jsonl"
    assert chain_file.is_file()
    chain_status = verify_chain(chain_file)
    assert chain_status.valid is True
    vault_ids = read_vault_ids(chain_file)
    assert len(vault_ids) > 0

    # Verify report artifacts
    report_json_path = run_dir / "05_s05_report" / "report.json"
    report_md_path = run_dir / "05_s05_report" / "report.md"
    assert report_json_path.is_file()
    assert report_md_path.is_file()

    report_data = json.loads(report_json_path.read_text(encoding="utf-8"))
    assert report_data["source"] == "real"
    assert report_data["synthetic"] is False
    assert report_data["headline"]["confidence"]["level"] in ("standard", "review_recommended", "insufficient_evidence")
    assert report_data["headline"]["confidence"]["unvalidated_calibrated_probability"] is None

    # Check evidence citations are in vault
    def collect_evidence_ids(val):
        if isinstance(val, dict):
            found = set(val.get("evidence_ids", []))
            for v in val.values():
                found.update(collect_evidence_ids(v))
            return found
        if isinstance(val, list):
            found = set()
            for item in val:
                found.update(collect_evidence_ids(item))
            return found
        return set()

    cited_ids = collect_evidence_ids(report_data)
    assert cited_ids <= vault_ids

    # Verify report.md content
    report_md = report_md_path.read_text(encoding="utf-8")
    assert "Source: real. Synthetic: false." in report_md
    assert "Most likely consistent with" in report_md
    assert "Evidence is from synthetic scenarios only." in report_md
