# Inquest Real Incident Data Specification

This document defines the canonical directory layout and file format for ingesting external, real-world incident evidence into Inquest via `inquest ingest-real <dir>`.

---

## 1. Directory Structure

Each incident must be provided in an isolated folder with the following files and subdirectories:

```text
incident_folder/
├── metrics/                 # Time series metrics (CSV or JSON, or metrics.json / metrics.csv)
│   ├── api.csv
│   └── database.json
├── events/                  # Operational events: deploy, config, restart (or events.json / events.csv)
│   └── events.json
├── alerts/                  # Alert firing records (or alerts.json / alerts.csv)
│   └── alerts.json
├── dependency_graph.json    # Service call graph edges (caller -> callee)
├── traces/                  # (Optional) Distributed span records (or traces.json / spans.json)
│   └── spans.json
└── labels.json              # (Optional, evaluation only) Incident window and true root cause
```

---

## 2. File Specifications

### 2.1 Metrics (`metrics/`, `metrics.json`, or `metrics.csv`)
Metric points report regular or irregular time series measurements per service.

**Required Fields:**
- `timestamp`: ISO-8601 UTC timestamp string (e.g., `"2026-03-15T14:30:00Z"`).
- `service`: Name of the emitting microservice (e.g., `"checkout"`, `"payments"`).
- `metric`: Metric name (e.g., `"latency_ms"`, `"error_rate"`, `"cpu_percent"`, `"memory_mb"`).
- `value`: Numeric measurement (float or integer).
- `unit`: Measurement unit (e.g., `"ms"`, `"percent"`, `"count"`, `"mb"`).

**JSON Format Example:**
```json
[
  {
    "timestamp": "2026-03-15T14:30:00Z",
    "service": "database",
    "metric": "latency_ms",
    "value": 245.5,
    "unit": "ms"
  }
]
```

**CSV Format Example:**
```csv
timestamp,service,metric,value,unit
2026-03-15T14:30:00Z,database,latency_ms,245.5,ms
```

---

### 2.2 Events (`events/`, `events.json`, or `events.csv`)
Operational change events that occurred prior to or during the incident window.

**Required Fields:**
- `timestamp`: ISO-8601 UTC timestamp string.
- `service`: Targeted microservice name.
- `kind`: Event classification: `"deploy"`, `"config"`, or `"restart"`.
- `change_id`: (Optional) Unique change identifier (e.g., `"deploy-v2.4.1"`).
- `description`: (Optional) Human-readable event description.

**JSON Format Example:**
```json
[
  {
    "timestamp": "2026-03-15T14:15:00Z",
    "service": "database",
    "kind": "deploy",
    "change_id": "deploy-db-v12",
    "description": "PostgreSQL minor version update"
  }
]
```

---

### 2.3 Alerts (`alerts/`, `alerts.json`, or `alerts.csv`)
Alert notification events dispatched by monitoring or alerting systems.

**Required Fields:**
- `timestamp`: ISO-8601 UTC timestamp string when the alert fired.
- `service`: Microservice associated with the alert.
- `level`: (Optional) Severity level: `"INFO"`, `"WARN"`, `"ERROR"`, or `"CRITICAL"` (defaults to `"WARN"`).
- `message`: (Optional) Alert title or description.

**JSON Format Example:**
```json
[
  {
    "timestamp": "2026-03-15T14:32:00Z",
    "service": "payments",
    "level": "ERROR",
    "message": "High HTTP 500 error rate on /charge endpoint"
  }
]
```

---

### 2.4 Dependency Graph (`dependency_graph.json` or `topology.json`)
The directed runtime call graph between microservices.

**Required Format:**
Array of edge objects with `caller` and `callee` keys:
```json
[
  {"caller": "frontend", "callee": "checkout"},
  {"caller": "checkout", "callee": "payments"},
  {"caller": "checkout", "callee": "inventory"},
  {"caller": "payments", "callee": "database"}
]
```
*(Also accepted: a wrapper object `{"edges": [...]}`.)*

---

### 2.5 Optional Traces (`traces/`, `traces.json`, or `spans.json`)
Distributed request trace spans used for causal trace analysis (e.g., Ochiai anomaly localization).

**Format:**
```json
[
  {
    "trace_id": "trace-98213",
    "span_id": "span-01",
    "service": "checkout",
    "name": "HTTP POST /checkout",
    "start_time": "2026-03-15T14:31:00.100Z",
    "end_time": "2026-03-15T14:31:00.650Z",
    "error": false
  }
]
```

---

### 2.6 Evaluation Labels (`labels.json` — Evaluation Only)
Optional labels provided solely for offline retrospective benchmark evaluation.

> [!IMPORTANT]
> **Strict Isolation:** `labels.json` is never read by the Inquest diagnostic pipeline (S00–S05). Inquest never writes real incident data to `sim_truth/`, and diagnostic stages operate strictly blind to evaluation labels.

**Format:**
```json
{
  "true_cause": ["database"],
  "incident_window": {
    "start": "2026-03-15T14:00:00Z",
    "end": "2026-03-15T15:00:00Z"
  }
}
```

---

## 3. CLI Command

Ingest and investigate a real incident folder end-to-end:

```bash
inquest ingest-real path/to/incident/
```

This command:
1. Validates all required files and field schemas, emitting clear validation errors if malformed or missing.
2. Ingests all metrics, events, alerts, and topology into Inquest's verified evidence vault (`vault/chain.jsonl`).
3. Executes stages S00 through S05 deterministically (`s00_ingest`, `s01_vault`, `s02_signals`, `s03_candidates`, `s04_verify`, `s05_report`).
4. Generates a structured JSON report (`report.json`) and Markdown investigation brief (`report.md`) citing tamper-evident vault evidence IDs.
