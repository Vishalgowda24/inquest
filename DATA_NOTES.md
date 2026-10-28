# Data and environment notes

## Workspace and runtime (2026-10-28)

The supplied project workspace began empty. The deliverable now contains the simulator and Inquest P0/P1 implementation. Python 3.12.14 is the available bundled interpreter; Python 3.11 is not installed. The runtime package directory is not writable, so exact pinned packages are available in the workspace-local `work/python-packages` cache. Network access to PyPI was unavailable during this task. The bundled Python's `ensurepip` bootstrap failed, so `setup.ps1` uses the package cache directly and runs pytest plus `inquest doctor`.

## Generated telemetry

Seed 1 exports 380 metric points, 300 graph-derived spans, log events, two change events, four dependency edges, and a synthetic manifest. Seeded missing windows are omitted, not imputed. Each timestamp carries source clock uncertainty. The seed-1 pipeline warns about clock uncertainty and coverage gaps for checkout and payments; it quarantines zero of 708 evidence records.

## P1 findings

- `validate` and `ingest` accept canonical JSON exports; a registry-selected CSV adapter uses `config/csv_mapping.yaml`.
- The current seed-1 ingest accepts 714 records (380 metrics, 300 spans, 28 logs, 2 changes, 4 dependencies), rejects none, and records clock/coverage warnings.
- The vault chain validates under doctor. Repeated chain generation for identical evidence is deterministic, and tampering is detected by item ID.
- CUSUM detects the propagated latency onset order database -> payments -> checkout on seeds 1, 2, and 3 within timestamp uncertainty. Seed 2's missing checkout sample widens uncertainty to cover the later observed point.
- A 20-hour dataset does not span two full 24-hour cycles. Signal seasonal adjustment therefore stays off and is explicitly noted; baseline uses robust median/MAD.
- Fault intensity changes database and downstream metrics through the call graph. There are no hand-authored per-service output series.

## P2 findings

- New scenarios and seeds 1–3 are registered for default evaluation; holdout is reserved and excluded.
- `long_seasonal` generates 72 hourly observations and passes the two-cycle seasonal-normalization gate for the database latency series. Shorter clean scenarios skip seasonal correction.
- The missing-telemetry scenario has no inventory spans and omits checkout metric windows 7–13. Trace Ochiai returns `DEGRADED` with the missing service called out while the other methods still rank candidates.
- Evaluation covers six non-holdout scenarios x three seeds. The detailed scenario table and per-case misses are in `eval/p2_results.md`. RRF ensemble top-1/top-3 is 18/18; latest-change baseline is 9/18 and alert-order baseline is 16/18. These are synthetic evaluation results, not a production accuracy estimate.
- The trace Ochiai implementation was weak on this generated data: top-1 was 0/18 and top-3 was 6/18. It often ranked checkout first because failing traces commonly include errors across multiple nodes; no holdout tuning was performed.
- The change-based method missed all shared-dependency cases because those scenarios intentionally contain no changes. Graph RWR's top-1 missed all three red-herring cases, though the true service remained in its top three. This demonstrates why the ensemble and explicit baselines are reported separately.

## P3 hardening results

- Trace Ochiai's previous zero top-1 and clean top-3 result came from unsorted output: it returned candidates in manifest order. Correct score sorting restores 3/3 clean top-3; no score values or thresholds changed.
- The new late-alerting case has the cause's metric onset after callers on all three seeds. The silent-cause case has no database metric series and no database signal onset; callers still show propagated metrics anomalies.
- Expanded evaluation is eight scenarios x three seeds. The detailed output includes ensemble true rank, top-score margin, seed counts, and flags small ensemble leads. See `eval/p2_results.md`; no holdout data was run.
- Current gates: 48 pytest tests passed and `inquest doctor` reported all registries and existing vault chains healthy.
