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




def _parse_real_timestamp(value: str) -> datetime:
    text_val = str(value).strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(text_val)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


class RealIncidentAdapter(IngestAdapter):
    name = "real_incident"

    def detect(self, path: Path) -> bool:
        if not path.is_dir():
            return False
        if (path / "manifest.json").is_file():
            return False
        has_metrics = (path / "metrics.json").exists() or (path / "metrics.csv").exists() or (path / "metrics").is_dir()
        has_graph = (path / "dependency_graph.json").exists() or (path / "dependencies.json").exists() or (path / "topology.json").exists()
        return has_metrics and has_graph

    def validate(self, path: Path) -> None:
        if not path.is_dir():
            raise IngestError(f"Incident path {path} is not an accessible directory", input_path=str(path))

        # 1. Metrics check
        metric_file = None
        if (path / "metrics.json").is_file():
            metric_file = path / "metrics.json"
        elif (path / "metrics.csv").is_file():
            metric_file = path / "metrics.csv"
        elif (path / "metrics").is_dir():
            m_items = [p for p in (path / "metrics").iterdir() if p.suffix.lower() in (".json", ".csv")]
            if not m_items:
                raise IngestError(f"Metrics directory {path / 'metrics'} contains no .json or .csv files", input_path=str(path))
        else:
            raise IngestError(f"Missing required metrics data in {path}: expected metrics.json, metrics.csv, or a populated metrics/ directory", input_path=str(path))

        # 2. Events check
        if (path / "events.json").is_file():
            pass
        elif (path / "events.csv").is_file():
            pass
        elif (path / "events").is_dir():
            e_items = [p for p in (path / "events").iterdir() if p.suffix.lower() in (".json", ".csv")]
            if not e_items:
                raise IngestError(f"Events directory {path / 'events'} contains no .json or .csv files", input_path=str(path))
        else:
            raise IngestError(f"Missing required events data in {path}: expected events.json, events.csv, or events/ directory", input_path=str(path))

        # 3. Alerts check
        if (path / "alerts.json").is_file():
            pass
        elif (path / "alerts.csv").is_file():
            pass
        elif (path / "alerts").is_dir():
            a_items = [p for p in (path / "alerts").iterdir() if p.suffix.lower() in (".json", ".csv")]
            if not a_items:
                raise IngestError(f"Alerts directory {path / 'alerts'} contains no .json or .csv files", input_path=str(path))
        else:
            raise IngestError(f"Missing required alerts data in {path}: expected alerts.json, alerts.csv, or alerts/ directory", input_path=str(path))

        # 4. Dependency graph check
        graph_file = next((path / name for name in ("dependency_graph.json", "dependencies.json", "topology.json") if (path / name).is_file()), None)
        if not graph_file:
            raise IngestError(f"Missing required dependency graph in {path}: expected dependency_graph.json or topology.json", input_path=str(path))

        # Validate graph content
        try:
            raw_graph = json.loads(graph_file.read_text(encoding="utf-8"))
        except Exception as exc:
            raise IngestError(f"Malformed JSON in dependency graph {graph_file}: {exc}", input_path=str(graph_file)) from exc
        edges = raw_graph.get("edges", raw_graph) if isinstance(raw_graph, dict) else raw_graph
        if not isinstance(edges, list) or not edges:
            raise IngestError(f"Dependency graph {graph_file} must contain a non-empty list of edge objects", input_path=str(graph_file))
        for idx, edge in enumerate(edges, start=1):
            if not isinstance(edge, dict) or not edge.get("caller") or not edge.get("callee"):
                raise IngestError(f"Malformed dependency edge #{idx} in {graph_file}: required keys 'caller' and 'callee'", input_path=str(graph_file))

        # Validate metric file content if single file
        if metric_file and metric_file.suffix.lower() == ".json":
            try:
                raw_m = json.loads(metric_file.read_text(encoding="utf-8"))
                if not isinstance(raw_m, list):
                    raise IngestError(f"Malformed metrics JSON in {metric_file}: root must be a list of records", input_path=str(metric_file))
                for idx, item in enumerate(raw_m, start=1):
                    if not isinstance(item, dict):
                        raise IngestError(f"Metric record #{idx} in {metric_file} is not an object", input_path=str(metric_file))
                    for req in ("timestamp", "service", "metric", "value", "unit"):
                        if req not in item:
                            raise IngestError(f"Metric record #{idx} in {metric_file} missing required key '{req}'", input_path=str(metric_file))
                    try:
                        float(item["value"])
                    except (ValueError, TypeError):
                        raise IngestError(f"Metric record #{idx} in {metric_file} has non-numeric value: {item['value']}", input_path=str(metric_file))
                    try:
                        _parse_real_timestamp(str(item["timestamp"]))
                    except Exception as exc:
                        raise IngestError(f"Metric record #{idx} in {metric_file} has unparseable timestamp: {exc}", input_path=str(metric_file))
            except json.JSONDecodeError as exc:
                raise IngestError(f"Malformed JSON in metrics file {metric_file}: {exc}", input_path=str(metric_file)) from exc

    def load(self, path: Path) -> CanonicalBundle:
        self.validate(path)

        accepted_counts = {"metrics": 0, "logs": 0, "changes": 0, "dependencies": 0, "spans": 0}
        rejected_counts = {"metrics": 0, "logs": 0, "changes": 0, "dependencies": 0, "spans": 0}
        quarantined: list[QuarantinedRecord] = []
        input_files: list[str] = []
        warnings: list[str] = []

        all_timestamps: list[datetime] = []
        services: set[str] = set()

        # Load metrics
        metrics: list[MetricPoint] = []
        metric_paths: list[Path] = []
        if (path / "metrics.json").is_file():
            metric_paths.append(path / "metrics.json")
        elif (path / "metrics.csv").is_file():
            metric_paths.append(path / "metrics.csv")
        elif (path / "metrics").is_dir():
            metric_paths.extend(sorted(p for p in (path / "metrics").iterdir() if p.suffix.lower() in (".json", ".csv")))

        for mp in metric_paths:
            input_files.append(str(mp.relative_to(path)))
            if mp.suffix.lower() == ".json":
                items = json.loads(mp.read_text(encoding="utf-8"))
                for idx, raw in enumerate(items, start=1):
                    try:
                        ts = _parse_real_timestamp(raw["timestamp"])
                        all_timestamps.append(ts)
                        svc = str(raw["service"])
                        services.add(svc)
                        pid = str(raw.get("id") or f"metric-{svc}-{raw['metric']}-{len(metrics)}")
                        pt = MetricPoint(
                            id=pid,
                            timestamp=ts,
                            service=svc,
                            metric=str(raw["metric"]),
                            value=float(raw["value"]),
                            unit=str(raw["unit"]),
                            dimensions=dict(raw.get("dimensions", {})),
                            timestamp_uncertainty_ms=int(raw.get("timestamp_uncertainty_ms", 0)),
                            source=mp.name,
                        )
                        metrics.append(pt)
                        accepted_counts["metrics"] += 1
                    except Exception as exc:
                        rejected_counts["metrics"] += 1
                        quarantined.append(QuarantinedRecord(file_path=str(mp), record_index=idx, error=str(exc), raw_record=raw if isinstance(raw, dict) else {"raw": raw}))
            elif mp.suffix.lower() == ".csv":
                with mp.open("r", encoding="utf-8", newline="") as cf:
                    reader = csv.DictReader(cf)
                    for idx, raw in enumerate(reader, start=1):
                        try:
                            ts = _parse_real_timestamp(raw["timestamp"])
                            all_timestamps.append(ts)
                            svc = str(raw["service"])
                            services.add(svc)
                            pid = str(raw.get("id") or f"metric-{svc}-{raw['metric']}-{len(metrics)}")
                            pt = MetricPoint(
                                id=pid,
                                timestamp=ts,
                                service=svc,
                                metric=str(raw["metric"]),
                                value=float(raw["value"]),
                                unit=str(raw["unit"]),
                                dimensions={},
                                timestamp_uncertainty_ms=0,
                                source=mp.name,
                            )
                            metrics.append(pt)
                            accepted_counts["metrics"] += 1
                        except Exception as exc:
                            rejected_counts["metrics"] += 1
                            quarantined.append(QuarantinedRecord(file_path=str(mp), record_index=idx, error=str(exc), raw_record=raw))

        # Load events
        changes: list[ChangeEvent] = []
        event_paths: list[Path] = []
        if (path / "events.json").is_file():
            event_paths.append(path / "events.json")
        elif (path / "events.csv").is_file():
            event_paths.append(path / "events.csv")
        elif (path / "events").is_dir():
            event_paths.extend(sorted(p for p in (path / "events").iterdir() if p.suffix.lower() in (".json", ".csv")))

        for ep in event_paths:
            input_files.append(str(ep.relative_to(path)))
            if ep.suffix.lower() == ".json":
                items = json.loads(ep.read_text(encoding="utf-8"))
                for idx, raw in enumerate(items, start=1):
                    try:
                        ts = _parse_real_timestamp(raw["timestamp"])
                        all_timestamps.append(ts)
                        svc = str(raw["service"])
                        services.add(svc)
                        cid = str(raw.get("id") or f"change-{svc}-{len(changes)}")
                        change = ChangeEvent(
                            id=cid,
                            timestamp=ts,
                            service=svc,
                            kind=str(raw["kind"]),
                            change_id=raw.get("change_id"),
                            description=raw.get("description"),
                            timestamp_uncertainty_ms=int(raw.get("timestamp_uncertainty_ms", 0)),
                            source=ep.name,
                        )
                        changes.append(change)
                        accepted_counts["changes"] += 1
                    except Exception as exc:
                        rejected_counts["changes"] += 1
                        quarantined.append(QuarantinedRecord(file_path=str(ep), record_index=idx, error=str(exc), raw_record=raw if isinstance(raw, dict) else {"raw": raw}))
            elif ep.suffix.lower() == ".csv":
                with ep.open("r", encoding="utf-8", newline="") as cf:
                    reader = csv.DictReader(cf)
                    for idx, raw in enumerate(reader, start=1):
                        try:
                            ts = _parse_real_timestamp(raw["timestamp"])
                            all_timestamps.append(ts)
                            svc = str(raw["service"])
                            services.add(svc)
                            cid = str(raw.get("id") or f"change-{svc}-{len(changes)}")
                            change = ChangeEvent(
                                id=cid,
                                timestamp=ts,
                                service=svc,
                                kind=str(raw["kind"]),
                                change_id=raw.get("change_id"),
                                description=raw.get("description"),
                                timestamp_uncertainty_ms=0,
                                source=ep.name,
                            )
                            changes.append(change)
                            accepted_counts["changes"] += 1
                        except Exception as exc:
                            rejected_counts["changes"] += 1
                            quarantined.append(QuarantinedRecord(file_path=str(ep), record_index=idx, error=str(exc), raw_record=raw))

        # Load alerts
        logs: list[LogEvent] = []
        alert_paths: list[Path] = []
        if (path / "alerts.json").is_file():
            alert_paths.append(path / "alerts.json")
        elif (path / "alerts.csv").is_file():
            alert_paths.append(path / "alerts.csv")
        elif (path / "alerts").is_dir():
            alert_paths.extend(sorted(p for p in (path / "alerts").iterdir() if p.suffix.lower() in (".json", ".csv")))

        for ap in alert_paths:
            input_files.append(str(ap.relative_to(path)))
            if ap.suffix.lower() == ".json":
                items = json.loads(ap.read_text(encoding="utf-8"))
                for idx, raw in enumerate(items, start=1):
                    try:
                        ts = _parse_real_timestamp(raw["timestamp"])
                        all_timestamps.append(ts)
                        svc = str(raw["service"])
                        services.add(svc)
                        lid = str(raw.get("id") or f"alert-{svc}-{len(logs)}")
                        attrs = dict(raw.get("attributes", {}))
                        attrs["alert_emission"] = True
                        if raw.get("message"):
                            attrs["message"] = str(raw["message"])
                        log = LogEvent(
                            id=lid,
                            timestamp=ts,
                            service=svc,
                            level=str(raw.get("level", "WARN")),
                            message=str(raw.get("message") or "Alert fired"),
                            attributes=attrs,
                            timestamp_uncertainty_ms=int(raw.get("timestamp_uncertainty_ms", 0)),
                            source=ap.name,
                        )
                        logs.append(log)
                        accepted_counts["logs"] += 1
                    except Exception as exc:
                        rejected_counts["logs"] += 1
                        quarantined.append(QuarantinedRecord(file_path=str(ap), record_index=idx, error=str(exc), raw_record=raw if isinstance(raw, dict) else {"raw": raw}))
            elif ap.suffix.lower() == ".csv":
                with ap.open("r", encoding="utf-8", newline="") as cf:
                    reader = csv.DictReader(cf)
                    for idx, raw in enumerate(reader, start=1):
                        try:
                            ts = _parse_real_timestamp(raw["timestamp"])
                            all_timestamps.append(ts)
                            svc = str(raw["service"])
                            services.add(svc)
                            lid = str(raw.get("id") or f"alert-{svc}-{len(logs)}")
                            attrs = {"alert_emission": True}
                            if raw.get("message"):
                                attrs["message"] = str(raw["message"])
                            log = LogEvent(
                                id=lid,
                                timestamp=ts,
                                service=svc,
                                level=str(raw.get("level", "WARN")),
                                message=str(raw.get("message") or "Alert fired"),
                                attributes=attrs,
                                timestamp_uncertainty_ms=0,
                                source=ap.name,
                            )
                            logs.append(log)
                            accepted_counts["logs"] += 1
                        except Exception as exc:
                            rejected_counts["logs"] += 1
                            quarantined.append(QuarantinedRecord(file_path=str(ap), record_index=idx, error=str(exc), raw_record=raw))

        # Load dependency graph
        dependencies: list[DependencyEdge] = []
        graph_file = next(path / name for name in ("dependency_graph.json", "dependencies.json", "topology.json") if (path / name).is_file())
        input_files.append(str(graph_file.relative_to(path)))
        raw_graph = json.loads(graph_file.read_text(encoding="utf-8"))
        edges = raw_graph.get("edges", raw_graph) if isinstance(raw_graph, dict) else raw_graph
        for idx, edge in enumerate(edges, start=1):
            caller = str(edge["caller"])
            callee = str(edge["callee"])
            services.add(caller)
            services.add(callee)
            eid = str(edge.get("id") or f"edge-{caller}-{callee}")
            dependencies.append(DependencyEdge(id=eid, caller=caller, callee=callee, source=graph_file.name))
            accepted_counts["dependencies"] += 1

        # Optional traces
        spans: list[Span] = []
        trace_paths: list[Path] = []
        if (path / "traces.json").is_file():
            trace_paths.append(path / "traces.json")
        elif (path / "spans.json").is_file():
            trace_paths.append(path / "spans.json")
        elif (path / "traces").is_dir():
            trace_paths.extend(sorted(p for p in (path / "traces").iterdir() if p.suffix.lower() == ".json"))

        for tp in trace_paths:
            input_files.append(str(tp.relative_to(path)))
            raw_spans = json.loads(tp.read_text(encoding="utf-8"))
            for idx, raw in enumerate(raw_spans, start=1):
                try:
                    s_ts = _parse_real_timestamp(raw["start_time"])
                    e_ts = _parse_real_timestamp(raw["end_time"])
                    all_timestamps.extend([s_ts, e_ts])
                    svc = str(raw["service"])
                    services.add(svc)
                    span = Span(
                        trace_id=str(raw["trace_id"]),
                        span_id=str(raw["span_id"]),
                        service=svc,
                        name=str(raw.get("name", "span")),
                        start_time=s_ts,
                        end_time=e_ts,
                        parent_id=raw.get("parent_id"),
                        error=bool(raw.get("error", False)),
                        attributes=dict(raw.get("attributes", {})),
                        timestamp_uncertainty_ms=int(raw.get("timestamp_uncertainty_ms", 0)),
                        source=tp.name,
                    )
                    spans.append(span)
                    accepted_counts["spans"] += 1
                except Exception as exc:
                    rejected_counts["spans"] += 1
                    quarantined.append(QuarantinedRecord(file_path=str(tp), record_index=idx, error=str(exc), raw_record=raw if isinstance(raw, dict) else {"raw": raw}))

        min_time = min(all_timestamps) if all_timestamps else datetime.now(timezone.utc)
        max_time = max(all_timestamps) if all_timestamps else min_time
        time_range = {"start": min_time, "end": max_time}

        content_seed = f"{path.name}|{len(metrics)}|{len(changes)}|{len(logs)}|{len(dependencies)}"
        content_hash = hashlib.sha256(content_seed.encode("utf-8")).hexdigest()[:12]
        manifest = ScenarioManifest(
            scenario_id=f"scn_{content_hash}",
            seed=0,
            source="real",
            synthetic=False,
            time_range=time_range,
            services=sorted(services),
            record_counts={
                "metrics": len(metrics),
                "spans": len(spans),
                "logs": len(logs),
                "changes": len(changes),
                "dependencies": len(dependencies),
            },
            files=input_files,
            source_metadata={"adapter": self.name, "directory": str(path.resolve())},
        )

        diagnostics = IngestDiagnostics(
            accepted_counts=accepted_counts,
            rejected_counts=rejected_counts,
            warnings=warnings,
            quarantined=quarantined,
            input_files=input_files,
        )

        return CanonicalBundle(
            manifest=manifest,
            metrics=metrics,
            spans=spans,
            logs=logs,
            changes=changes,
            dependencies=dependencies,
            diagnostics=diagnostics,
        )


def default_adapter_registry(mapping_path: Path) -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register(CanonicalJsonAdapter())
    registry.register(CsvGenericAdapter(mapping_path))
    registry.register(RealIncidentAdapter())
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
