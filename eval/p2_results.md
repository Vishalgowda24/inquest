# Candidate evaluation after P3 hardening

Default evaluation includes 8 non-holdout scenarios x 3 seeds = 24 cases. `simulator/scenarios/holdout/` is not registered, imported, or evaluated.

## Per-scenario top-1 / top-3 hits and ensemble lead (seed hits)

| Scenario | Seeds | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble | latest_change_before_alert | alert_order | Ensemble lead (cases) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| clean_bad_deploy | 3 | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | single +0; baseline +0 [FLAG: lead <= 1 case] |
| coincident_restart | 3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 2/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | single +0; baseline +0 [FLAG: lead <= 1 case] |
| red_herring_deploy | 3 | 3/3; 3/3 | 0/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 | single +0; baseline +0 [FLAG: lead <= 1 case] |
| shared_dependency | 3 | 0/3; 0/3 | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 | single +0; baseline +0 [FLAG: lead <= 1 case] |
| missing_telemetry | 3 | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | single +0; baseline +0 [FLAG: lead <= 1 case] |
| long_seasonal | 3 | 0/3; 0/3 | 1/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 1/3; 3/3 | single +0; baseline +2 [FLAG: lead <= 1 case] |
| late_alerting_cause | 3 | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 | single +0; baseline +3 [FLAG: lead <= 1 case] |
| silent_cause | 3 | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 0/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 | single -3; baseline +0 [FLAG: lead <= 1 case] |

Each method cell is `top-1 hits; top-3 hits`. Lead is ensemble top-1 cases minus the best single-method and best-baseline top-1 counts. Any lead of one case or less is flagged. Overall percentages are included only after the per-scenario table.

## Overall top-1 / top-3

| Method | Hits / cases (rate) top-1 / top-3 |
|---|---:|
| change_based | 12/24 (50%) / 12/24 (50%) |
| graph_rwr | 19/24 (79%) / 24/24 (100%) |
| trace_ochiai | 10/24 (42%) / 23/24 (96%) |
| temporal_lag | 15/24 (62%) / 21/24 (88%) |
| ensemble | 21/24 (88%) / 24/24 (100%) |
| latest_change_before_alert | 9/24 (38%) / 9/24 (38%) |
| alert_order | 16/24 (67%) / 18/24 (75%) |

## Per-case top-1 predictions ([MISS] identifies misses)

| Scenario / seed | Truth service | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble | latest_change_before_alert | alert_order | Ensemble true rank | Top-score margin |
|---|---|---|---|---|---|---|---|---|---:|---:|
| clean_bad_deploy / 1 | database | database [OK] | database [OK] | inventory [MISS] | payments [MISS] | database [OK] | database [OK] | database [OK] | 1 | 0.00078 |
| clean_bad_deploy / 2 | database | database [OK] | database [OK] | checkout [MISS] | database [OK] | database [OK] | database [OK] | database [OK] | 1 | 0.00131 |
| clean_bad_deploy / 3 | database | database [OK] | database [OK] | database [OK] | database [OK] | database [OK] | database [OK] | database [OK] | 1 | 0.00157 |
| coincident_restart / 1 | database | database [OK] | database [OK] | inventory [MISS] | payments [MISS] | database [OK] | database [OK] | database [OK] | 1 | 0.01589 |
| coincident_restart / 2 | database | database [OK] | database [OK] | checkout [MISS] | database [OK] | database [OK] | database [OK] | database [OK] | 1 | 0.01743 |
| coincident_restart / 3 | database | database [OK] | database [OK] | checkout [MISS] | database [OK] | database [OK] | database [OK] | database [OK] | 1 | 0.01743 |
| red_herring_deploy / 1 | payments | payments [OK] | database [MISS] | checkout [MISS] | payments [OK] | payments [OK] | inventory [MISS] | payments [OK] | 1 | 0.00103 |
| red_herring_deploy / 2 | payments | payments [OK] | database [MISS] | checkout [MISS] | payments [OK] | payments [OK] | inventory [MISS] | payments [OK] | 1 | 0.01742 |
| red_herring_deploy / 3 | payments | payments [OK] | database [MISS] | payments [OK] | payments [OK] | payments [OK] | inventory [MISS] | payments [OK] | 1 | 0.03279 |
| shared_dependency / 1 | database | — [MISS] | database [OK] | database [OK] | payments [MISS] | database [OK] | — [MISS] | database [OK] | 1 | 0.00052 |
| shared_dependency / 2 | database | — [MISS] | database [OK] | database [OK] | database [OK] | database [OK] | — [MISS] | database [OK] | 1 | 0.00131 |
| shared_dependency / 3 | database | — [MISS] | database [OK] | database [OK] | database [OK] | database [OK] | — [MISS] | database [OK] | 1 | 0.00131 |
| missing_telemetry / 1 | database | database [OK] | database [OK] | database [OK] | database [OK] | database [OK] | database [OK] | database [OK] | 1 | 0.01744 |
| missing_telemetry / 2 | database | database [OK] | database [OK] | checkout [MISS] | database [OK] | database [OK] | database [OK] | database [OK] | 1 | 0.01692 |
| missing_telemetry / 3 | database | database [OK] | database [OK] | database [OK] | database [OK] | database [OK] | database [OK] | database [OK] | 1 | 0.03332 |
| long_seasonal / 1 | database | — [MISS] | checkout [MISS] | database [OK] | database [OK] | database [OK] | — [MISS] | checkout [MISS] | 1 | 0.00104 |
| long_seasonal / 2 | database | — [MISS] | checkout [MISS] | checkout [MISS] | database [OK] | database [OK] | — [MISS] | checkout [MISS] | 1 | 0.00052 |
| long_seasonal / 3 | database | — [MISS] | database [OK] | checkout [MISS] | database [OK] | database [OK] | — [MISS] | database [OK] | 1 | 0.00053 |
| late_alerting_cause / 1 | database | — [MISS] | database [OK] | inventory [MISS] | payments [MISS] | database [OK] | — [MISS] | payments [MISS] | 1 | 0.00000 |
| late_alerting_cause / 2 | database | — [MISS] | database [OK] | checkout [MISS] | inventory [MISS] | database [OK] | — [MISS] | checkout [MISS] | 1 | 0.00026 |
| late_alerting_cause / 3 | database | — [MISS] | database [OK] | database [OK] | inventory [MISS] | database [OK] | — [MISS] | payments [MISS] | 1 | 0.00052 |
| silent_cause / 1 | database | — [MISS] | database [OK] | inventory [MISS] | payments [MISS] | inventory [MISS] | — [MISS] | payments [MISS] | 3 | 0.00000 |
| silent_cause / 2 | database | — [MISS] | database [OK] | checkout [MISS] | inventory [MISS] | inventory [MISS] | — [MISS] | checkout [MISS] | 3 | 0.00026 |
| silent_cause / 3 | database | — [MISS] | database [OK] | database [OK] | inventory [MISS] | inventory [MISS] | — [MISS] | payments [MISS] | 3 | 0.00026 |

Evaluation uses truth only from `simulator/sim_truth/`; Inquest stages receive only opaque IDs and exported telemetry. No holdout data is read or used for tuning.
