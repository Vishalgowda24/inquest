"""Registry-based canonical JSON and mapped CSV adapters."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from inquest.contracts import CanonicalBundle, ChangeEvent, DependencyEdge, IngestDiagnostics, LogEvent, MetricPoint, QuarantinedRecord, ScenarioManifest, Span
from inquest.core.errors import IngestError

T = TypeVar("T", bound=BaseModel)
RecordSchema = type[T]


class IngestAdapter(Protocol):
    name: str

    def detect(self, path: Path) -> bool: ...

    def load(self, path: Path) -> CanonicalBundle: ...


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: list[IngestAdapter] = []

    def register(self, adapter: IngestAdapter) -> None:
        if any(item.name == adapter.name for item in self._adapters):
            raise IngestError(f"Adapter already registered: {adapter.name}")
        self._adapters.append(adapter)

    def select(self, path: Path) -> IngestAdapter:
        matches = [adapter for adapter in self._adapters if adapter.detect(path)]
        if len(matches) != 1:
            names = ", ".join(adapter.name for adapter in matches) or "none"
            raise IngestError(f"Expected exactly one adapter for {path}; detected: {names}", input_path=str(path))
        return matches[0]

    def load(self, path: Path) -> CanonicalBundle:
        return self.select(path).load(path)

    def names(self) -> tuple[str, ...]:
        return tuple(adapter.name for adapter in self._adapters)


def _validate_record(path: Path, index: int, raw: object, schema: RecordSchema[T]) -> tuple[T | None, QuarantinedRecord | None]:
    if not isinstance(raw, dict):
        item = QuarantinedRecord(file_path=str(path), record_index=index, error="record must be a JSON object", raw_record={"raw_value": raw})
        return None, item
    values = dict(raw)
    values.setdefault("source", path.name)
    values.setdefault("source_metadata", {"file": path.name, "record_index": index, "original": raw})
    try:
        return schema.model_validate(values), None
    except ValidationError as exc:
        issue = QuarantinedRecord(file_path=str(path), record_index=index, error=str(exc), raw_record=raw)
        return None, issue


def _read_json_records(path: Path) -> list[tuple[int, object]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IngestError(f"Cannot read JSON records: {exc}", stage="s00_ingest", input_path=str(path)) from exc
    values = value if isinstance(value, list) else [value]
    return list(enumerate(values, start=1))


def _read_jsonl_records(path: Path) -> tuple[list[tuple[int, object]], list[QuarantinedRecord]]:
    records: list[tuple[int, object]] = []
    rejected: list[QuarantinedRecord] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise IngestError(f"Cannot read JSONL records: {exc}", stage="s00_ingest", input_path=str(path)) from exc
    for index, line in enumerate(lines, start=1):
        try:
            records.append((index, json.loads(line)))
        except json.JSONDecodeError as exc:
            rejected.append(QuarantinedRecord(file_path=str(path), record_index=index, error=str(exc), raw_record={"raw_line": line}))
    return records, rejected


class CanonicalJsonAdapter(IngestAdapter):
    name = "canonical_json"
    _tables: tuple[tuple[str, str, RecordSchema[BaseModel]], ...] = (
        ("metrics/metrics.json", "metrics", MetricPoint),
        ("traces/spans.json", "spans", Span),
        ("logs/events.jsonl", "logs", LogEvent),
        ("events.json", "changes", ChangeEvent),
        ("dependency_graph.json", "dependencies", DependencyEdge),
    )

    def detect(self, path: Path) -> bool:
        return path.is_dir() and (path / "manifest.json").is_file()

    def load(self, path: Path) -> CanonicalBundle:
        manifest = self._load_manifest(path / "manifest.json")
        rows, counts, issues, files, warnings = self._load_tables(path, manifest)
        warnings.extend(self._reference_warnings(manifest, rows))
        warnings.extend(self._clock_warnings(rows))
        warnings.extend(self._coverage_warnings(manifest, rows["metrics"]))
        warnings.extend(_observed_gap_warnings(rows["metrics"]))
        diagnostics = IngestDiagnostics(accepted_counts=counts[0], rejected_counts=counts[1], warnings=warnings, quarantined=issues, input_files=files)
        return CanonicalBundle(manifest=manifest, metrics=rows["metrics"], spans=rows["spans"], logs=rows["logs"], changes=rows["changes"], dependencies=rows["dependencies"], diagnostics=diagnostics)

    def _load_manifest(self, path: Path) -> ScenarioManifest:
        try:
            return ScenarioManifest.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValidationError, ValueError) as exc:
            raise IngestError(f"Invalid or unsupported manifest schema at {path}: {exc}", stage="s00_ingest", input_path=str(path)) from exc

    def _load_tables(self, root: Path, manifest: ScenarioManifest) -> tuple[dict[str, list], tuple[dict[str, int], dict[str, int]], list[QuarantinedRecord], list[str], list[str]]:
        rows: dict[str, list] = {key: [] for _, key, _ in self._tables}
        accepted: dict[str, int] = {}
        rejected: dict[str, int] = {}
        issues: list[QuarantinedRecord] = []
        files: list[str] = ["manifest.json"]
        warnings: list[str] = []
        declared = set(manifest.files)
        for relative, key, schema in self._tables:
            path = root / relative
            if relative not in declared or not path.exists():
                accepted[key] = 0
                rejected[key] = 0
                warnings.append(f"Missing optional source file: {relative}")
                continue
            parsed, parse_issues = self._records(path, relative.endswith(".jsonl"))
            files.append(relative)
            issues.extend(parse_issues)
            accepted[key] = 0
            rejected[key] = len(parse_issues)
            for index, raw in parsed:
                record, issue = _validate_record(path, index, raw, schema)
                if issue is not None:
                    issues.append(issue)
                    rejected[key] += 1
                else:
                    rows[key].append(record)
                    accepted[key] += 1
        return rows, (accepted, rejected), issues, files, warnings

    def _records(self, path: Path, jsonl: bool) -> tuple[list[tuple[int, object]], list[QuarantinedRecord]]:
        if jsonl:
            return _read_jsonl_records(path)
        return _read_json_records(path), []

    def _reference_warnings(self, manifest: ScenarioManifest, rows: dict[str, list]) -> list[str]:
        known = set(manifest.services)
        observed = {record.service for group in ("metrics", "spans", "logs", "changes") for record in rows[group] if record.service}
        unknown = sorted(observed - known)
        warnings = [f"Unknown service reference: {name}" for name in unknown]
        unknown_edges = sorted({name for edge in rows["dependencies"] for name in (edge.caller, edge.callee) if name not in known})
        warnings.extend(f"Unknown dependency service reference: {name}" for name in unknown_edges)
        return warnings

    def _clock_warnings(self, rows: dict[str, list]) -> list[str]:
        records = [record for group in rows.values() for record in group if getattr(record, "timestamp_uncertainty_ms", 0) > 0]
        return [f"Source clock uncertainty present on {len(records)} records; event ordering may be uncertain"] if records else []

    def _coverage_warnings(self, manifest: ScenarioManifest, metrics: list[MetricPoint]) -> list[str]:
        if not metrics:
            return ["No metric records available for signal processing"]
        expected = (manifest.time_range.end - manifest.time_range.start).total_seconds()
        warnings: list[str] = []
        groups: dict[tuple[str, str], int] = {}
        period_by_metric: dict[tuple[str, str], int] = {}
        for point in metrics:
            key = (point.service, point.metric)
            groups[key] = groups.get(key, 0) + 1
            period_by_metric[key] = int(point.dimensions.get("window_minutes", "0")) * 60
        for key, count in sorted(groups.items()):
            period = period_by_metric[key]
            required = int(expected // period) + 1 if period > 0 else count
            if count < required:
                warnings.append(f"Telemetry coverage gap for {key[0]}/{key[1]}: {required - count} expected windows missing")
        return warnings


class CsvGenericAdapter(IngestAdapter):
    name = "csv_generic"
    required_fields = ("timestamp", "service", "metric", "value", "unit")

    def __init__(self, mapping_path: Path) -> None:
        try:
            raw = yaml.safe_load(mapping_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise IngestError(f"Cannot load CSV column mapping {mapping_path}: {exc}", input_path=str(mapping_path)) from exc
        self.mapping = raw.get("metric", {}) if isinstance(raw, dict) else {}
        missing = [field for field in self.required_fields if field not in self.mapping]
        if missing:
            raise IngestError(f"CSV mapping is missing required fields: {', '.join(missing)}", input_path=str(mapping_path))

    def detect(self, path: Path) -> bool:
        return path.is_file() and path.suffix.lower() == ".csv" or path.is_dir() and len(list(path.glob("*.csv"))) == 1

    def load(self, path: Path) -> CanonicalBundle:
        file_path = path if path.is_file() else next(path.glob("*.csv"))
        records, rejected = self._load_rows(file_path)
        if not records:
            raise IngestError(f"No valid metric rows in {file_path}; rejected {len(rejected)}", stage="s00_ingest", input_path=str(file_path))
        manifest = self._manifest(file_path, records)
        warnings = [f"Rejected {len(rejected)} malformed CSV rows"] if rejected else []
        warnings.extend(CanonicalJsonAdapter()._clock_warnings({"metrics": records}))
        warnings.extend(_observed_gap_warnings(records))
        diagnostics = IngestDiagnostics(accepted_counts={"metrics": len(records)}, rejected_counts={"metrics": len(rejected)}, warnings=warnings, quarantined=rejected, input_files=[file_path.name])
        return CanonicalBundle(manifest=manifest, metrics=records, diagnostics=diagnostics)

    def _load_rows(self, path: Path) -> tuple[list[MetricPoint], list[QuarantinedRecord]]:
        accepted: list[MetricPoint] = []
        rejected: list[QuarantinedRecord] = []
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as source:
                reader = csv.DictReader(source)
                self._validate_columns(path, reader.fieldnames or [])
                for row_index, row in enumerate(reader, start=2):
                    metric, issue = self._metric_row(path, row_index, row)
                    if issue:
                        rejected.append(issue)
                    elif metric:
                        accepted.append(metric)
        except OSError as exc:
            raise IngestError(f"Cannot read CSV: {exc}", stage="s00_ingest", input_path=str(path)) from exc
        return accepted, rejected

    def _validate_columns(self, path: Path, columns: list[str]) -> None:
        missing = [self.mapping[field] for field in self.required_fields if self.mapping[field] not in columns]
        if missing:
            raise IngestError(f"CSV is missing mapped columns: {', '.join(missing)}", stage="s00_ingest", input_path=str(path))

    def _metric_row(self, path: Path, row_index: int, row: dict[str, str | None]) -> tuple[MetricPoint | None, QuarantinedRecord | None]:
        normalized = {field: row.get(column) for field, column in self.mapping.items()}
        normalized["timestamp"] = normalized.get("timestamp")
        normalized["value"] = normalized.get("value")
        digest = hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()[:16]
        normalized.update({"id": normalized.get("id") or f"csv-{digest}-{row_index}", "timestamp_uncertainty_ms": 0, "source": path.name, "source_metadata": {"file": path.name, "row": row_index, "original": row}})
        try:
            return MetricPoint.model_validate(normalized), None
        except ValidationError as exc:
            return None, QuarantinedRecord(file_path=str(path), record_index=row_index, error=str(exc), raw_record={key: value or "" for key, value in row.items()})

    def _manifest(self, path: Path, records: list[MetricPoint]) -> ScenarioManifest:
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        timestamps = [item.timestamp for item in records]
        return ScenarioManifest(scenario_id=f"scn_{content_hash}", seed=0, source="real", synthetic=False, time_range={"start": min(timestamps), "end": max(timestamps)}, services=sorted({item.service for item in records}), record_counts={"metrics": len(records)}, files=[path.name], source_metadata={"adapter": self.name})


def default_adapter_registry(mapping_path: Path) -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register(CanonicalJsonAdapter())
    registry.register(CsvGenericAdapter(mapping_path))
    return registry


def _observed_gap_warnings(metrics: list[MetricPoint]) -> list[str]:
    groups: dict[tuple[str, str], list[datetime]] = {}
    for point in metrics:
        groups.setdefault((point.service, point.metric), []).append(point.timestamp)
    warnings: list[str] = []
    for (service, metric), timestamps in sorted(groups.items()):
        timestamps.sort()
        intervals = [(right - left).total_seconds() for left, right in zip(timestamps, timestamps[1:])]
        positive = [interval for interval in intervals if interval > 0]
        if len(positive) < 2:
            continue
        typical = sorted(positive)[len(positive) // 2]
        missing = sum(max(0, round(interval / typical) - 1) for interval in positive if interval >= 1.5 * typical)
        if missing:
            warnings.append(f"Observed coverage gap for {service}/{metric}: {missing} windows missing between samples")
    return warnings
