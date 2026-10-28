# P5 fresh-seed results

Part B was frozen in commit `1e717f1`; seeds 4–6 for all 12 families were committed in simulator-only commit `a288c16` before any method ran. Baseline outputs are isolated in `runs/p5_before/`; post-change outputs are isolated in `runs/p5_after/`. Both use all S03 methods and five S04 checks, with S04 re-ranking OFF. No output was overwritten; holdout was not run. S04 changes are annotation-only.

P5 weight: graph_rwr contribution ×2.0; others ×1.0; RRF constant 60. Frozen S04 change: temporal downstream candidate checks. The values were not altered after Part B.

## Per-case method orders, statuses, and baselines

For method cells, `top1=service` is the method’s top candidate; parenthetical entries are the true cause rank(s), `—` means absent, and `*` marks rank ≤3. Concurrent causes show both cause ranks. S04 status cell lists each true cause and every candidate status before→after. S04 rank equals the ensemble order because re-ranking remains off.

| Scenario | Seed | True cause(s) | Before S03 methods (top1; true ranks) | After S03 methods (top1; true ranks) | S04 statuses true/decoys before→after | Latest-change / alert-order baseline (top1; true ranks) |
|---|---:|---|---|---|---|---|
| clean_bad_deploy | 4 | database | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory verified→verified, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: database (database:1*)<br>alert_order: database (database:1*) |
| clean_bad_deploy | 5 | database | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: verified→verified; decoys: checkout unsupported→unsupported, inventory insufficient_evidence→insufficient_evidence, payments unsupported→unsupported | latest_change_before_alert: database (database:1*)<br>alert_order: database (database:1*) |
| clean_bad_deploy | 6 | database | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory verified→verified, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: database (database:1*)<br>alert_order: database (database:1*) |
| coincident_restart | 4 | database | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: database (database:1*)<br>alert_order: database (database:1*) |
| coincident_restart | 5 | database | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: verified→verified; decoys: checkout unsupported→unsupported, inventory insufficient_evidence→insufficient_evidence, payments unsupported→unsupported | latest_change_before_alert: database (database:1*)<br>alert_order: database (database:1*) |
| coincident_restart | 6 | database | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: database (database:1*)<br>alert_order: database (database:1*) |
| concurrent_causes | 4 | payments, inventory | change_based: payments (payments:1*, inventory:—)<br>graph_rwr: payments (payments:1*, inventory:4)<br>trace_ochiai: checkout (payments:2*, inventory:—)<br>temporal_lag: payments (payments:1*, inventory:2*)<br>ensemble: payments (payments:1*, inventory:4) | change_based: payments (payments:1*, inventory:—)<br>graph_rwr: payments (payments:1*, inventory:4)<br>trace_ochiai: checkout (payments:2*, inventory:—)<br>temporal_lag: payments (payments:1*, inventory:2*)<br>ensemble: payments (payments:1*, inventory:4) | payments: insufficient_evidence→insufficient_evidence; inventory: verified→contested; decoys: checkout insufficient_evidence→insufficient_evidence, database insufficient_evidence→insufficient_evidence | latest_change_before_alert: payments (payments:1*, inventory:—)<br>alert_order: payments (payments:1*, inventory:3*) |
| concurrent_causes | 5 | payments, inventory | change_based: payments (payments:1*, inventory:—)<br>graph_rwr: database (payments:2*, inventory:4)<br>trace_ochiai: checkout (payments:2*, inventory:3*)<br>temporal_lag: payments (payments:1*, inventory:3*)<br>ensemble: payments (payments:1*, inventory:2*) | change_based: payments (payments:1*, inventory:—)<br>graph_rwr: database (payments:2*, inventory:4)<br>trace_ochiai: checkout (payments:2*, inventory:3*)<br>temporal_lag: payments (payments:1*, inventory:3*)<br>ensemble: payments (payments:1*, inventory:2*) | payments: contested→insufficient_evidence; inventory: insufficient_evidence→insufficient_evidence; decoys: checkout unsupported→unsupported, database insufficient_evidence→unsupported | latest_change_before_alert: payments (payments:1*, inventory:—)<br>alert_order: payments (payments:1*, inventory:3*) |
| concurrent_causes | 6 | payments, inventory | change_based: payments (payments:1*, inventory:2*)<br>graph_rwr: payments (payments:1*, inventory:4)<br>trace_ochiai: payments (payments:1*, inventory:—)<br>temporal_lag: payments (payments:1*, inventory:3*)<br>ensemble: payments (payments:1*, inventory:3*) | change_based: payments (payments:1*, inventory:2*)<br>graph_rwr: payments (payments:1*, inventory:4)<br>trace_ochiai: payments (payments:1*, inventory:—)<br>temporal_lag: payments (payments:1*, inventory:3*)<br>ensemble: payments (payments:1*, inventory:3*) | payments: insufficient_evidence→insufficient_evidence; inventory: verified→contested; decoys: checkout insufficient_evidence→insufficient_evidence, database insufficient_evidence→insufficient_evidence | latest_change_before_alert: inventory (payments:—, inventory:1*)<br>alert_order: payments (payments:1*, inventory:3*) |
| late_alerting_cause | 4 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:3*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:3*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: payments (database:—) |
| late_alerting_cause | 5 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:3*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:3*)<br>ensemble: database (database:1*) | database: insufficient_evidence→unsupported; decoys: checkout unsupported→unsupported, inventory insufficient_evidence→insufficient_evidence, payments unsupported→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: payments (database:4) |
| late_alerting_cause | 6 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: inventory (database:—)<br>ensemble: payments (database:2*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: inventory (database:—)<br>ensemble: payments (database:2*) | database: contested→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory contested→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: payments (database:4) |
| long_seasonal | 4 | database | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:2*)<br>ensemble: database (database:1*) | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:2*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: database (database:1*)<br>alert_order: database (database:1*) |
| long_seasonal | 5 | database | change_based: — (database:—)<br>graph_rwr: inventory (database:2*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: inventory (database:2*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: inventory (database:2*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: inventory (database:2*) |
| long_seasonal | 6 | database | change_based: — (database:—)<br>graph_rwr: inventory (database:2*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: inventory (database:2*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: inventory (database:2*) |
| missing_telemetry | 4 | database | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:3*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:3*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: database (database:1*)<br>alert_order: database (database:1*) |
| missing_telemetry | 5 | database | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: verified→contested; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments unsupported→unsupported | latest_change_before_alert: database (database:1*)<br>alert_order: checkout (database:2*) |
| missing_telemetry | 6 | database | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: database (database:1*)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: database (database:1*)<br>alert_order: database (database:1*) |
| noisy_alerts | 4 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: database (database:1*) |
| noisy_alerts | 5 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout unsupported→unsupported, inventory insufficient_evidence→insufficient_evidence, payments unsupported→unsupported | latest_change_before_alert: — (database:—)<br>alert_order: database (database:1*) |
| noisy_alerts | 6 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: database (database:1*) |
| partial_graph | 4 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: database (database:1*) |
| partial_graph | 5 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:3*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:3*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout unsupported→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments unsupported→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: database (database:1*) |
| partial_graph | 6 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: database (database:1*) |
| red_herring_deploy | 4 | payments | change_based: payments (payments:1*)<br>graph_rwr: payments (payments:1*)<br>trace_ochiai: checkout (payments:2*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | change_based: payments (payments:1*)<br>graph_rwr: payments (payments:1*)<br>trace_ochiai: checkout (payments:2*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | payments: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, database insufficient_evidence→insufficient_evidence, inventory verified→contested | latest_change_before_alert: inventory (payments:—)<br>alert_order: payments (payments:1*) |
| red_herring_deploy | 5 | payments | change_based: payments (payments:1*)<br>graph_rwr: database (payments:2*)<br>trace_ochiai: checkout (payments:2*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | change_based: payments (payments:1*)<br>graph_rwr: database (payments:2*)<br>trace_ochiai: checkout (payments:2*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | payments: contested→insufficient_evidence; decoys: checkout unsupported→unsupported, database insufficient_evidence→unsupported, inventory insufficient_evidence→insufficient_evidence | latest_change_before_alert: inventory (payments:—)<br>alert_order: payments (payments:1*) |
| red_herring_deploy | 6 | payments | change_based: payments (payments:1*)<br>graph_rwr: payments (payments:1*)<br>trace_ochiai: payments (payments:1*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | change_based: payments (payments:1*)<br>graph_rwr: payments (payments:1*)<br>trace_ochiai: payments (payments:1*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | payments: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, database insufficient_evidence→insufficient_evidence, inventory verified→contested | latest_change_before_alert: inventory (payments:—)<br>alert_order: payments (payments:1*) |
| red_herring_hard | 4 | payments | change_based: payments (payments:1*)<br>graph_rwr: payments (payments:1*)<br>trace_ochiai: checkout (payments:2*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | change_based: payments (payments:1*)<br>graph_rwr: payments (payments:1*)<br>trace_ochiai: checkout (payments:2*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | payments: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, database insufficient_evidence→insufficient_evidence, inventory verified→contested | latest_change_before_alert: payments (payments:1*)<br>alert_order: payments (payments:1*) |
| red_herring_hard | 5 | payments | change_based: payments (payments:1*)<br>graph_rwr: database (payments:2*)<br>trace_ochiai: checkout (payments:2*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | change_based: payments (payments:1*)<br>graph_rwr: database (payments:2*)<br>trace_ochiai: checkout (payments:2*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | payments: contested→insufficient_evidence; decoys: checkout unsupported→unsupported, database insufficient_evidence→unsupported, inventory insufficient_evidence→insufficient_evidence | latest_change_before_alert: payments (payments:1*)<br>alert_order: payments (payments:1*) |
| red_herring_hard | 6 | payments | change_based: payments (payments:1*)<br>graph_rwr: payments (payments:1*)<br>trace_ochiai: payments (payments:1*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | change_based: payments (payments:1*)<br>graph_rwr: payments (payments:1*)<br>trace_ochiai: payments (payments:1*)<br>temporal_lag: payments (payments:1*)<br>ensemble: payments (payments:1*) | payments: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, database insufficient_evidence→insufficient_evidence, inventory verified→contested | latest_change_before_alert: payments (payments:1*)<br>alert_order: payments (payments:1*) |
| shared_dependency | 4 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: database (database:1*) |
| shared_dependency | 5 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout unsupported→unsupported, inventory insufficient_evidence→insufficient_evidence, payments unsupported→unsupported | latest_change_before_alert: — (database:—)<br>alert_order: database (database:1*) |
| shared_dependency | 6 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: database (database:1*)<br>ensemble: database (database:1*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory insufficient_evidence→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: database (database:1*) |
| silent_cause | 4 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:—)<br>ensemble: inventory (database:3*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:—)<br>ensemble: inventory (database:3*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory unsupported→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: payments (database:—) |
| silent_cause | 5 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:—)<br>ensemble: inventory (database:3*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: database (database:1*)<br>temporal_lag: inventory (database:—)<br>ensemble: inventory (database:3*) | database: insufficient_evidence→insufficient_evidence; decoys: checkout unsupported→unsupported, inventory insufficient_evidence→insufficient_evidence, payments unsupported→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: payments (database:—) |
| silent_cause | 6 | database | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: inventory (database:—)<br>ensemble: payments (database:2*) | change_based: — (database:—)<br>graph_rwr: database (database:1*)<br>trace_ochiai: checkout (database:2*)<br>temporal_lag: inventory (database:—)<br>ensemble: payments (database:2*) | database: contested→insufficient_evidence; decoys: checkout insufficient_evidence→insufficient_evidence, inventory unsupported→insufficient_evidence, payments insufficient_evidence→insufficient_evidence | latest_change_before_alert: — (database:—)<br>alert_order: payments (database:—) |

## Per-scenario top-1/top-3 hits (3 seeds)

| Scenario | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble before | ensemble after | latest change | alert order |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean_bad_deploy | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| coincident_restart | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| concurrent_causes | 3/3; 3/3 → 3/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 1/3; 3/3 → 1/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| late_alerting_cause | 0/3; 0/3 → 0/3; 0/3 | 3/3; 3/3 → 3/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 0/3; 2/3 → 0/3; 2/3 | 2/3; 3/3 → 2/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |
| long_seasonal | 1/3; 1/3 → 1/3; 1/3 | 1/3; 3/3 → 1/3; 3/3 | 1/3; 3/3 → 1/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 3/3; 3/3 → 2/3; 3/3 | 1/3; 1/3 | 1/3; 3/3 |
| missing_telemetry | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 1/3; 3/3 → 1/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 |
| noisy_alerts | 0/3; 0/3 → 0/3; 0/3 | 3/3; 3/3 → 3/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| partial_graph | 0/3; 0/3 → 0/3; 0/3 | 3/3; 3/3 → 3/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| red_herring_deploy | 3/3; 3/3 → 3/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 1/3; 3/3 → 1/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| red_herring_hard | 3/3; 3/3 → 3/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 1/3; 3/3 → 1/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| shared_dependency | 0/3; 0/3 → 0/3; 0/3 | 3/3; 3/3 → 3/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 3/3; 3/3 → 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| silent_cause | 0/3; 0/3 → 0/3; 0/3 | 3/3; 3/3 → 3/3; 3/3 | 2/3; 3/3 → 2/3; 3/3 | 0/3; 0/3 → 0/3; 0/3 | 0/3; 3/3 → 0/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |

## S04 status counts by scenario

| Scenario | True verified | True contested | True insufficient | True unsupported | Wrong verified (false confirmation) | False rejection cases |
|---|---:|---:|---:|---:|---:|---|
| clean_bad_deploy | 1 | 0 | 2 | 0 | 2 (4:inventory, 6:inventory) | 0 |
| coincident_restart | 1 | 0 | 2 | 0 | 0 | 0 |
| concurrent_causes | 0 | 2 | 4 | 0 | 0 | 2 (4:inventory=contested, 6:inventory=contested) |
| late_alerting_cause | 0 | 0 | 2 | 1 | 0 | 1 (5:database=unsupported) |
| long_seasonal | 0 | 0 | 3 | 0 | 0 | 0 |
| missing_telemetry | 0 | 1 | 2 | 0 | 0 | 1 (5:database=contested) |
| noisy_alerts | 0 | 0 | 3 | 0 | 0 | 0 |
| partial_graph | 0 | 0 | 3 | 0 | 0 | 0 |
| red_herring_deploy | 0 | 0 | 3 | 0 | 0 | 0 |
| red_herring_hard | 0 | 0 | 3 | 0 | 0 | 0 |
| shared_dependency | 0 | 0 | 3 | 0 | 0 | 0 |
| silent_cause | 0 | 0 | 3 | 0 | 0 | 0 |

## S04 red-herring findings (fresh seeds)

| Seed | True payments status | Decoy database status | dependency_path | alternative_check |
|---:|---|---|---|---|
| 4 | insufficient_evidence→insufficient_evidence | insufficient_evidence→insufficient_evidence | inconclusive→inconclusive; IDs: dependency-checkout-inventory, dependency-checkout-payments, dependency-inventory-database, dependency-payments-database, metric-4-10-checkout-latency_ms, metric-4-15-inventory-request_rate, metric-4-15-payments-request_rate, metric-4-8-payments-cpu_percent, metric-4-9-payments-latency_ms | inconclusive→inconclusive; IDs: none |
| 5 | contested→insufficient_evidence | insufficient_evidence→unsupported | inconclusive→contradicts; IDs: dependency-checkout-inventory, dependency-checkout-payments, dependency-inventory-database, dependency-payments-database, metric-5-10-checkout-latency_ms, metric-5-14-inventory-request_rate, metric-5-15-checkout-request_rate, metric-5-15-database-request_rate, metric-5-15-payments-request_rate, metric-5-9-payments-latency_ms | supports→contradicts; IDs: dependency-checkout-inventory, dependency-checkout-payments, dependency-inventory-database, dependency-payments-database, metric-5-10-checkout-latency_ms, metric-5-14-inventory-request_rate, metric-5-15-checkout-request_rate, metric-5-15-database-request_rate, metric-5-15-payments-request_rate, metric-5-9-payments-latency_ms |
| 6 | insufficient_evidence→insufficient_evidence | insufficient_evidence→insufficient_evidence | inconclusive→inconclusive; IDs: dependency-checkout-inventory, dependency-checkout-payments, dependency-inventory-database, dependency-payments-database, metric-6-10-checkout-latency_ms, metric-6-12-checkout-request_rate, metric-6-15-inventory-request_rate, metric-6-9-payments-cpu_percent, metric-6-9-payments-latency_ms | inconclusive→inconclusive; IDs: none |

## Frozen-design checks and notable outcomes

P3b’s two long_seasonal rank losses were seeds 1 and 3: the true database was `insufficient_evidence`, while the wrong inventory (seed 1) and checkout (seed 3) candidates were `verified`. Full status-first re-ranking promoted those decoys; seed 2 stayed at rank 1. P5 keeps re-ranking off, so statuses do not reorder results.

For fresh silent_cause seeds 4–6, graph_rwr still ranks database first in each case. Its weighted rank contribution did not overcome the other method ranks: ensemble top-1 remains 0/3 before and after. For seed 4, for example, the weighted ensemble score is 0.04918 for database versus 0.06427 for inventory; this shows the frozen ×2 graph weight is insufficient when graph_rwr itself also ranks inventory and temporal_lag/trace evidence ranks it ahead. No weight was changed after seeing this result.


## Concurrent-causes found-both / found-one / found-none (top 3)

| Seed | Method | Outcomes for payments + inventory |
|---:|---|---|
| 4 | change_based | found-one |
| 4 | graph_rwr | found-one |
| 4 | trace_ochiai | found-one |
| 4 | temporal_lag | found-both |
| 4 | ensemble | found-one |
| 4 | latest_change_before_alert | found-one |
| 4 | alert_order | found-both |
| 5 | change_based | found-one |
| 5 | graph_rwr | found-one |
| 5 | trace_ochiai | found-both |
| 5 | temporal_lag | found-both |
| 5 | ensemble | found-both |
| 5 | latest_change_before_alert | found-one |
| 5 | alert_order | found-both |
| 6 | change_based | found-both |
| 6 | graph_rwr | found-one |
| 6 | trace_ochiai | found-one |
| 6 | temporal_lag | found-both |
| 6 | ensemble | found-both |
| 6 | latest_change_before_alert | found-one |
| 6 | alert_order | found-both |

## One-case difference flags

The following are every per-scenario pairwise comparison between the listed ranking outputs whose top-1 or top-3 hit counts differ by exactly one case. Three seeds make each difference noise-prone.

| Scenario | Top-k | Output A | Hits A | Output B | Hits B |
|---|---|---|---:|---|---:|
| clean_bad_deploy | top-1 | change_based | 3/3 | trace_ochiai | 2/3 |
| clean_bad_deploy | top-1 | graph_rwr | 3/3 | trace_ochiai | 2/3 |
| clean_bad_deploy | top-1 | trace_ochiai | 2/3 | temporal_lag | 3/3 |
| clean_bad_deploy | top-1 | trace_ochiai | 2/3 | ensemble_before | 3/3 |
| clean_bad_deploy | top-1 | trace_ochiai | 2/3 | ensemble_after | 3/3 |
| clean_bad_deploy | top-1 | trace_ochiai | 2/3 | latest_change_before_alert | 3/3 |
| clean_bad_deploy | top-1 | trace_ochiai | 2/3 | alert_order | 3/3 |
| coincident_restart | top-1 | change_based | 3/3 | trace_ochiai | 2/3 |
| coincident_restart | top-1 | graph_rwr | 3/3 | trace_ochiai | 2/3 |
| coincident_restart | top-1 | trace_ochiai | 2/3 | temporal_lag | 3/3 |
| coincident_restart | top-1 | trace_ochiai | 2/3 | ensemble_before | 3/3 |
| coincident_restart | top-1 | trace_ochiai | 2/3 | ensemble_after | 3/3 |
| coincident_restart | top-1 | trace_ochiai | 2/3 | latest_change_before_alert | 3/3 |
| coincident_restart | top-1 | trace_ochiai | 2/3 | alert_order | 3/3 |
| concurrent_causes | top-1 | change_based | 3/3 | graph_rwr | 2/3 |
| concurrent_causes | top-1 | graph_rwr | 2/3 | trace_ochiai | 1/3 |
| concurrent_causes | top-1 | graph_rwr | 2/3 | temporal_lag | 3/3 |
| concurrent_causes | top-1 | graph_rwr | 2/3 | ensemble_before | 3/3 |
| concurrent_causes | top-1 | graph_rwr | 2/3 | ensemble_after | 3/3 |
| concurrent_causes | top-1 | graph_rwr | 2/3 | latest_change_before_alert | 3/3 |
| concurrent_causes | top-1 | graph_rwr | 2/3 | alert_order | 3/3 |
| late_alerting_cause | top-1 | graph_rwr | 3/3 | trace_ochiai | 2/3 |
| late_alerting_cause | top-3 | graph_rwr | 3/3 | temporal_lag | 2/3 |
| late_alerting_cause | top-1 | graph_rwr | 3/3 | ensemble_before | 2/3 |
| late_alerting_cause | top-1 | graph_rwr | 3/3 | ensemble_after | 2/3 |
| late_alerting_cause | top-3 | trace_ochiai | 3/3 | temporal_lag | 2/3 |
| late_alerting_cause | top-3 | temporal_lag | 2/3 | ensemble_before | 3/3 |
| late_alerting_cause | top-3 | temporal_lag | 2/3 | ensemble_after | 3/3 |
| long_seasonal | top-1 | change_based | 1/3 | temporal_lag | 2/3 |
| long_seasonal | top-1 | change_based | 1/3 | ensemble_after | 2/3 |
| long_seasonal | top-1 | graph_rwr | 1/3 | temporal_lag | 2/3 |
| long_seasonal | top-1 | graph_rwr | 1/3 | ensemble_after | 2/3 |
| long_seasonal | top-1 | trace_ochiai | 1/3 | temporal_lag | 2/3 |
| long_seasonal | top-1 | trace_ochiai | 1/3 | ensemble_after | 2/3 |
| long_seasonal | top-1 | temporal_lag | 2/3 | ensemble_before | 3/3 |
| long_seasonal | top-1 | temporal_lag | 2/3 | latest_change_before_alert | 1/3 |
| long_seasonal | top-1 | temporal_lag | 2/3 | alert_order | 1/3 |
| long_seasonal | top-1 | ensemble_before | 3/3 | ensemble_after | 2/3 |
| long_seasonal | top-1 | ensemble_after | 2/3 | latest_change_before_alert | 1/3 |
| long_seasonal | top-1 | ensemble_after | 2/3 | alert_order | 1/3 |
| missing_telemetry | top-1 | change_based | 3/3 | alert_order | 2/3 |
| missing_telemetry | top-1 | graph_rwr | 3/3 | alert_order | 2/3 |
| missing_telemetry | top-1 | trace_ochiai | 1/3 | alert_order | 2/3 |
| missing_telemetry | top-1 | temporal_lag | 3/3 | alert_order | 2/3 |
| missing_telemetry | top-1 | ensemble_before | 3/3 | alert_order | 2/3 |
| missing_telemetry | top-1 | ensemble_after | 3/3 | alert_order | 2/3 |
| missing_telemetry | top-1 | latest_change_before_alert | 3/3 | alert_order | 2/3 |
| noisy_alerts | top-1 | graph_rwr | 3/3 | trace_ochiai | 2/3 |
| noisy_alerts | top-1 | trace_ochiai | 2/3 | temporal_lag | 3/3 |
| noisy_alerts | top-1 | trace_ochiai | 2/3 | ensemble_before | 3/3 |
| noisy_alerts | top-1 | trace_ochiai | 2/3 | ensemble_after | 3/3 |
| noisy_alerts | top-1 | trace_ochiai | 2/3 | alert_order | 3/3 |
| partial_graph | top-1 | graph_rwr | 3/3 | trace_ochiai | 2/3 |
| partial_graph | top-1 | graph_rwr | 3/3 | temporal_lag | 2/3 |
| partial_graph | top-1 | trace_ochiai | 2/3 | ensemble_before | 3/3 |
| partial_graph | top-1 | trace_ochiai | 2/3 | ensemble_after | 3/3 |
| partial_graph | top-1 | trace_ochiai | 2/3 | alert_order | 3/3 |
| partial_graph | top-1 | temporal_lag | 2/3 | ensemble_before | 3/3 |
| partial_graph | top-1 | temporal_lag | 2/3 | ensemble_after | 3/3 |
| partial_graph | top-1 | temporal_lag | 2/3 | alert_order | 3/3 |
| red_herring_deploy | top-1 | change_based | 3/3 | graph_rwr | 2/3 |
| red_herring_deploy | top-1 | graph_rwr | 2/3 | trace_ochiai | 1/3 |
| red_herring_deploy | top-1 | graph_rwr | 2/3 | temporal_lag | 3/3 |
| red_herring_deploy | top-1 | graph_rwr | 2/3 | ensemble_before | 3/3 |
| red_herring_deploy | top-1 | graph_rwr | 2/3 | ensemble_after | 3/3 |
| red_herring_deploy | top-1 | graph_rwr | 2/3 | alert_order | 3/3 |
| red_herring_deploy | top-1 | trace_ochiai | 1/3 | latest_change_before_alert | 0/3 |
| red_herring_hard | top-1 | change_based | 3/3 | graph_rwr | 2/3 |
| red_herring_hard | top-1 | graph_rwr | 2/3 | trace_ochiai | 1/3 |
| red_herring_hard | top-1 | graph_rwr | 2/3 | temporal_lag | 3/3 |
| red_herring_hard | top-1 | graph_rwr | 2/3 | ensemble_before | 3/3 |
| red_herring_hard | top-1 | graph_rwr | 2/3 | ensemble_after | 3/3 |
| red_herring_hard | top-1 | graph_rwr | 2/3 | latest_change_before_alert | 3/3 |
| red_herring_hard | top-1 | graph_rwr | 2/3 | alert_order | 3/3 |
| shared_dependency | top-1 | graph_rwr | 3/3 | trace_ochiai | 2/3 |
| shared_dependency | top-1 | trace_ochiai | 2/3 | temporal_lag | 3/3 |
| shared_dependency | top-1 | trace_ochiai | 2/3 | ensemble_before | 3/3 |
| shared_dependency | top-1 | trace_ochiai | 2/3 | ensemble_after | 3/3 |
| shared_dependency | top-1 | trace_ochiai | 2/3 | alert_order | 3/3 |
| silent_cause | top-1 | graph_rwr | 3/3 | trace_ochiai | 2/3 |

## Historical development comparison (secondary)

P4’s seeds 1–3 (development families) and 11/29/47 (earlier fresh validation families) are shown only as historical reference. P5 did not rerun those seeds after the frozen changes. S04 rank is annotation-only and equals the P5 after ensemble.

| Scenario | P4 historical ensemble top1/top3 | P5 seeds 4–6 after top1/top3 | P4 historical alert_order top1/top3 | P5 seeds 4–6 alert_order top1/top3 |
|---|---:|---:|---:|---:|
| clean_bad_deploy | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 |
| coincident_restart | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 |
| concurrent_causes | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 |
| late_alerting_cause | 3/3 / 3/3 | 2/3 / 3/3 | 0/3 / 0/3 | 0/3 / 0/3 |
| long_seasonal | 3/3 / 3/3 | 2/3 / 3/3 | 1/3 / 3/3 | 1/3 / 3/3 |
| missing_telemetry | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 | 2/3 / 3/3 |
| noisy_alerts | 2/3 / 3/3 | 3/3 / 3/3 | 0/3 / 2/3 | 3/3 / 3/3 |
| partial_graph | 2/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 |
| red_herring_deploy | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 |
| red_herring_hard | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 |
| shared_dependency | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 | 3/3 / 3/3 |
| silent_cause | 0/3 / 3/3 | 0/3 / 3/3 | 0/3 / 0/3 | 0/3 / 0/3 |

## Plain results and interpretation

- Red-herring decoy contradicted: **no, not consistently**. On fresh seeds, database is contradicted by both graph checks only in seed 5; seeds 4 and 6 are inconclusive because candidate telemetry is incomplete. The table above lists every finding ID.
- Silent-cause improved: **no**. Its fresh seeds before→after top-1 remains 0/3 → 0/3; top-3 ranks are shown in the per-case table.
- `verified` remains unreliable: among 36 fresh cases (38 cause labels because concurrent_causes has two), 2 true causes are verified and 2 wrong candidates are also verified. The false confirmations are clean_bad_deploy seeds 4 and 6, both inventory. The per-scenario table lists the false confirmations; true statuses are in the per-case table.
- Ensemble overall on fresh seeds: before 32/36 top-1, 36/36 top-3; after 31/36 top-1, 36/36 top-3. Alert-order after: 27/36 top-1, 30/36 top-3. Full per-scenario rows are immediately above.
- Scenario regression: long_seasonal is the only ensemble scenario that got worse, from 3/3 to 2/3 top-1; no scenario changed top-3 and the other scenario top-1 counts were unchanged.
- Historical P4 combined development+validation was 31/36 top-1 and 36/36 top-3 for the ensemble; P5 fresh-seed after is 31/36 and 36/36. Fresh performance is not below those historical figures on the displayed counts. This is not a like-for-like config comparison: P4 used equal RRF weights and different seeds.
- On the eight scenario families previously evaluated with seeds 1–3, the historical P4 ensemble was 21/24 top-1 and 24/24 top-3; P5 seeds 4–6 after the frozen changes are 19/24 and 24/24. Alert order was 16/24 and 18/24 historically, versus 15/24 and 18/24 on P5 seeds. Fresh top-1 is lower by 2 cases for the ensemble and 1 case for alert order; the three-seed differences are noise-prone.
- No scenario comparison was used to change frozen weights, thresholds, or status rules. One-case differences are explicitly listed above.
