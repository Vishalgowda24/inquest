# Simulator export schemas

P0 freezes export format version **1.0**. JSON uses UTF-8, sorted object keys, two-space indentation for JSON files, and one compact JSON object per line for JSONL. Every record has `schema_version: "1.0"`; unsupported versions fail validation. Record IDs are stable within one seed's export and derived from seed, source, and record position. Exported scenario IDs are opaque hashes.

## Export tree

```text
scenario_export/
├── manifest.json
├── metrics/metrics.json
├── traces/spans.json
├── logs/events.jsonl
├── events.json
└── dependency_graph.json
```

`sim run --scenario <registered_scenario> --seed N` writes to `simulator/exports/<scenario_id>/seed_N/export/`, unless `--output` is supplied. The separate truth artifact is written under `simulator/sim_truth/<scenario_name>/seed_N.truth.json`; it is never copied into the export folder. Scenario IDs are salted HMAC values keyed by scenario and seed.

The default registered scenarios are `clean_bad_deploy`, `coincident_restart`, `red_herring_deploy`, `shared_dependency`, `missing_telemetry`, `long_seasonal`, `late_alerting_cause`, and `silent_cause`. Each was exercised with seeds 1–3. `long_seasonal` generates 72 hourly observations; `missing_telemetry` omits all inventory spans and a long checkout metric interval; `late_alerting_cause` masks its fault-service metrics for five windows; `silent_cause` has no database metric stream while its fault propagates to callers. The reserved `scenarios/holdout/` directory is excluded from the simulator registry and the default evaluator.

## Timestamp conventions

All timestamps are ISO 8601 UTC strings ending in `Z`. Simulation starts at a fixed configured instant. Metric samples are one simulated hour apart across a 20-hour observation window. Event timestamps represent source clocks: a service's configured clock skew is applied to its emitted event time. `timestamp_uncertainty_ms` states the absolute skew bound known to the simulator. The manifest time range describes simulation time before source skew. No timestamp is derived from machine wall-clock time.

## Records

- **MetricPoint**: `schema_version`, stable `id`, `timestamp`, `service`, `metric`, numeric `value`, `unit`, `dimensions`, and `timestamp_uncertainty_ms`. Metric names are `request_rate`, `latency_ms`, `error_rate`, `cpu_percent`, and `memory_mb`; units are requests/second, milliseconds, ratio, percent, and megabytes respectively. Values are sampled once per simulated hour; dropped service windows are omitted instead of imputed.
- **Span**: `schema_version`, `trace_id`, `span_id`, optional `parent_span_id`, `service`, `operation`, `start_time`, `duration_ms`, `status`, optional `attributes`, and `timestamp_uncertainty_ms`. Parent spans identify the caller span; root spans omit parent IDs. Timestamps use the emitting service's source clock.
- **LogEvent**: `schema_version`, `id`, `timestamp`, `service`, `level`, `message`, optional `trace_id`, `attributes`, and `timestamp_uncertainty_ms`. Logs include seeded background noise and fault-related observations.
- **ChangeEvent**: `schema_version`, `id`, `kind` (`deployment`, `configuration_change`, or `restart`), `timestamp`, `service`, `change_id`, `details`, and uncertainty. P0 emits one injected deployment and an unrelated deployment.
- **DependencyEdge**: `schema_version`, `id`, `caller`, and `callee`. The direction means the caller invokes the callee. It is declared simulator topology, not discovered causality.
- **ScenarioManifest**: `schema_version`, `scenario_id`, `seed`, `source`, `synthetic`, `time_range` (`start`, `end`), sorted `services`, `record_counts`, and sorted `files`. `synthetic` is always true for this simulator.

## Simulation model

The four services are `checkout`, `payments`, `inventory`, and `database`. Checkout calls payments and inventory; both call database. Traffic has a deterministic 24-hour seasonal component. At each hourly step, base latency/error/CPU/memory are functions of load, seeded jitter is added, and downstream latency/error contributes to each caller. Scenario variants adjust fault service, fault interval, changes, observation length, or telemetry availability while using the same generated service dynamics. Scenario names and injected fault descriptions are stored only in truth files and are not readable by an Inquest runtime.
