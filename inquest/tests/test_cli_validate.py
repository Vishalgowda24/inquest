"""CLI validation remains a read-only dry run."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from inquest.cli import app


def test_validate_does_not_create_runs_or_vault_files(tmp_path: Path) -> None:
    mapping = tmp_path / "mapping.yaml"
    mapping.write_text("metric:\n  timestamp: time\n  service: service\n  metric: metric\n  value: value\n  unit: unit\n", encoding="utf-8")
    config = tmp_path / "config.yaml"
    config.write_text(f"global_seed: 1\nlog_level: INFO\ndata_inbox: {tmp_path / 'inbox'}\nruns_dir: {tmp_path / 'runs'}\ncsv_mapping_path: {mapping}\nsimulation_clock: '2025-01-01T00:00:00Z'\nstages:\n  smoke: true\n", encoding="utf-8")
    source = tmp_path / "input.csv"
    source.write_text("time,service,metric,value,unit\n2025-01-01T00:00:00Z,api,latency_ms,4.5,ms\n", encoding="utf-8")
    result = CliRunner().invoke(app, ["validate", str(source), "--config", str(config)])
    assert result.exit_code == 0, result.output
    assert "source=real" in result.output
    assert not (tmp_path / "runs").exists()
    assert not (tmp_path / "inbox").exists()
