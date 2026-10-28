"""CSV adapter column mapping, quarantine, and provenance tests."""

from __future__ import annotations

from pathlib import Path

from inquest.stages.s00_ingest.adapters import CsvGenericAdapter


def test_csv_mapping_normalizes_valid_rows_and_quarantines_bad_row(tmp_path: Path) -> None:
    mapping = tmp_path / "mapping.yaml"
    mapping.write_text("metric:\n  id: id\n  timestamp: time\n  service: component\n  metric: name\n  value: value\n  unit: unit\n", encoding="utf-8")
    source = tmp_path / "telemetry.csv"
    source.write_text("id,time,component,name,value,unit\nrow-1,2025-01-01T00:00:00Z,api,latency_ms,12.5,ms\nrow-2,not-a-time,api,latency_ms,bad,ms\n", encoding="utf-8")
    adapter = CsvGenericAdapter(mapping)
    assert adapter.detect(source)
    bundle = adapter.load(source)
    assert bundle.manifest.source == "real"
    assert bundle.manifest.synthetic is False
    assert len(bundle.metrics) == 1
    assert bundle.metrics[0].source == source.name
    assert bundle.diagnostics.accepted_counts["metrics"] == 1
    assert bundle.diagnostics.rejected_counts["metrics"] == 1
    assert bundle.diagnostics.quarantined[0].record_index == 3
    assert str(source) in bundle.diagnostics.quarantined[0].file_path


def test_csv_adapter_fails_with_context_when_mapping_column_is_missing(tmp_path: Path) -> None:
    mapping = tmp_path / "mapping.yaml"
    mapping.write_text("metric:\n  timestamp: time\n  service: service\n  metric: metric\n  value: value\n  unit: unit\n", encoding="utf-8")
    source = tmp_path / "telemetry.csv"
    source.write_text("time,service,metric,value,unit\n", encoding="utf-8")
    try:
        CsvGenericAdapter(mapping).load(source)
    except Exception as exc:
        assert str(source) in str(exc)
    else:
        raise AssertionError("missing mapped column should fail with input path")
