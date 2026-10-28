# P9 Development Fusion Evaluation

Evaluation code commit: `f05e86085e941e41557db2b0d2a9244385d51c09`  
Cases: 388 across 14 families; seed range in source records: 1–51. All saved truth-confirmed cases available at evaluation time are included.

No S03 method, evidence rule, threshold, or status rule was changed. Variant formula and selection rule were committed before evaluation in `DECISIONS.md`.

## Full per-family table (top-1 / top-3)

| Family | Cases | CHANGE_BASED top-1/top-3 | GRAPH_RWR top-1/top-3 | TRACE_OCHIAI top-1/top-3 | TEMPORAL_LAG top-1/top-3 | V0 top-1/top-3 | V1 top-1/top-3 | V2 top-1/top-3 | V3 top-1/top-3 | V4 top-1/top-3 | LATEST_CHANGE_BEFORE_ALERT top-1/top-3 | ALERT_ORDER top-1/top-3 |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| cause_alerts_2_4 | 20 | 0/20 (0/20) | 20/20 (20/20) | 8/20 (20/20) | 16/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 0/20 (0/20) | 0/20 (14/20) |
| clean_bad_deploy | 29 | 28/29 (28/29) | 29/29 (29/29) | 11/29 (26/29) | 17/29 (29/29) | 28/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 28/29 (28/29) | 29/29 (29/29) |
| coincident_restart | 29 | 28/29 (28/29) | 29/29 (29/29) | 9/29 (25/29) | 19/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 28/29 (28/29) | 29/29 (29/29) |
| concurrent_causes | 29 | 29/29 (29/29) | 8/29 (29/29) | 10/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 8/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| late_alerting_cause | 29 | 0/29 (0/29) | 29/29 (29/29) | 11/29 (26/29) | 0/29 (27/29) | 20/29 (29/29) | 21/29 (29/29) | 12/29 (27/29) | 28/29 (29/29) | 29/29 (29/29) | 0/29 (0/29) | 0/29 (4/29) |
| long_seasonal | 29 | 7/29 (7/29) | 17/29 (29/29) | 9/29 (29/29) | 25/29 (29/29) | 29/29 (29/29) | 27/29 (29/29) | 28/29 (29/29) | 23/29 (29/29) | 17/29 (29/29) | 7/29 (7/29) | 17/29 (29/29) |
| missing_telemetry | 29 | 28/29 (28/29) | 29/29 (29/29) | 11/29 (28/29) | 24/29 (29/29) | 28/29 (29/29) | 28/29 (29/29) | 28/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 28/29 (28/29) | 28/29 (29/29) |
| noisy_alerts | 29 | 0/29 (0/29) | 29/29 (29/29) | 11/29 (27/29) | 15/29 (29/29) | 26/29 (29/29) | 26/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 0/29 (0/29) | 8/29 (25/29) |
| partial_graph | 29 | 0/29 (0/29) | 29/29 (29/29) | 11/29 (27/29) | 12/29 (29/29) | 25/29 (29/29) | 25/29 (29/29) | 23/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 0/29 (0/29) | 29/29 (29/29) |
| red_herring_deploy | 29 | 29/29 (29/29) | 10/29 (29/29) | 12/29 (27/29) | 29/29 (29/29) | 28/29 (29/29) | 28/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 10/29 (29/29) | 0/29 (0/29) | 29/29 (29/29) |
| red_herring_hard | 29 | 29/29 (29/29) | 10/29 (29/29) | 11/29 (27/29) | 29/29 (29/29) | 28/29 (29/29) | 28/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 10/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| shared_dependency | 29 | 0/29 (0/29) | 29/29 (29/29) | 13/29 (27/29) | 16/29 (29/29) | 27/29 (29/29) | 27/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 0/29 (0/29) | 29/29 (29/29) |
| silent_cause | 29 | 0/29 (0/29) | 28/29 (29/29) | 11/29 (26/29) | 0/29 (0/29) | 0/29 (27/29) | 17/29 (28/29) | 14/29 (29/29) | 11/29 (29/29) | 28/29 (29/29) | 0/29 (0/29) | 0/29 (0/29) |
| unordered_plausible_alerts | 20 | 0/20 (0/20) | 20/20 (20/20) | 8/20 (20/20) | 16/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 0/20 (0/20) | 5/20 (15/20) |

## Family-equal selection calculation

| Variant | Family-equal top-1 | Aggregate top-3 | red_herring_deploy top-1 (seeds 10–29) | shared_dependency top-1 (seeds 10–29) | Eligible |
|---|---:|---:|---:|---:|---|
| V0 | 0.8744 | 386/388 | 20/20 | 19/20 | yes |
| V1 | 0.9163 | 387/388 | 20/20 | 19/20 | yes |
| V2 | 0.9015 | 386/388 | 20/20 | 20/20 | yes |
| V3 | 0.9384 | 388/388 | 20/20 | 20/20 | yes |
| V4 | 0.8227 | 388/388 | 7/20 | 20/20 | no |

Selection under frozen rule: **V3**. Highest eligible family-equal top-1 is 0.9384; V0 is 0.8744; improvement is +0.0640. Minimum required gain is 0.0200. No confirmation data has been read or generated at this point.

## V0 misses where graph_rwr ranks a true cause first

| Family | Seed | Opaque scenario ID | Truth label(s) | V0 rank(s) | graph_rwr rank(s) | V0 top-1 |
|---|---:|---|---|---|---|---|
| clean_bad_deploy | 16 | scn_2501749e962e | database | 2 | 1 | inventory |
| late_alerting_cause | 6 | scn_745c1ff9f1da | database | 2 | 1 | payments |
| late_alerting_cause | 7 | scn_9fd75b1f75a5 | database | 2 | 1 | inventory |
| late_alerting_cause | 9 | scn_f6f69882f5ba | database | 2 | 1 | inventory |
| late_alerting_cause | 11 | scn_ed306dc87e0b | database | 3 | 1 | payments |
| late_alerting_cause | 22 | scn_32b8f30838dd | database | 3 | 1 | inventory |
| late_alerting_cause | 24 | scn_fa51e941bad3 | database | 3 | 1 | inventory |
| late_alerting_cause | 26 | scn_dd1238674241 | database | 2 | 1 | payments |
| late_alerting_cause | 27 | scn_2ae638a85550 | database | 2 | 1 | payments |
| late_alerting_cause | 29 | scn_07fe6c99fa87 | database | 3 | 1 | payments |
| missing_telemetry | 16 | scn_129beb61df4f | database | 2 | 1 | payments |
| noisy_alerts | 7 | scn_7fef645b444c | database | 2 | 1 | inventory |
| noisy_alerts | 9 | scn_75fbcf9816ff | database | 2 | 1 | inventory |
| noisy_alerts | 29 | scn_84901223e50f | database | 2 | 1 | payments |
| partial_graph | 7 | scn_9e3d5b0f5ad5 | database | 2 | 1 | inventory |
| partial_graph | 9 | scn_69b62891adcc | database | 2 | 1 | inventory |
| partial_graph | 22 | scn_3fbe2114255a | database | 2 | 1 | inventory |
| partial_graph | 29 | scn_e07f74ec8550 | database | 2 | 1 | payments |
| shared_dependency | 7 | scn_95a0c05e690b | database | 2 | 1 | inventory |
| shared_dependency | 29 | scn_82680140ad50 | database | 2 | 1 | payments |
| silent_cause | 1 | scn_2ef04d261b74 | database | 3 | 1 | inventory |
| silent_cause | 2 | scn_d5fde7e5c326 | database | 3 | 1 | inventory |
| silent_cause | 3 | scn_a21dc32e9d7d | database | 3 | 1 | inventory |
| silent_cause | 4 | scn_2427a35cbd63 | database | 3 | 1 | inventory |
| silent_cause | 5 | scn_89c6d0e99559 | database | 3 | 1 | inventory |
| silent_cause | 6 | scn_ab694a1cf19f | database | 2 | 1 | payments |
| silent_cause | 7 | scn_34177bfa2809 | database | 2 | 1 | inventory |
| silent_cause | 8 | scn_bba5b40c73e9 | database | 2 | 1 | inventory |
| silent_cause | 9 | scn_4b80e283fcbe | database | 3 | 1 | inventory |
| silent_cause | 10 | scn_87614e5cf448 | database | 3 | 1 | inventory |
| silent_cause | 11 | scn_8de891146952 | database | 3 | 1 | payments |
| silent_cause | 12 | scn_4d1b2137790d | database | 3 | 1 | payments |
| silent_cause | 13 | scn_4d94692f9832 | database | 3 | 1 | inventory |
| silent_cause | 14 | scn_417e9e7d1c53 | database | 3 | 1 | payments |
| silent_cause | 15 | scn_dc4c86521dd9 | database | 3 | 1 | payments |
| silent_cause | 16 | scn_ce300b8c97c8 | database | 3 | 1 | payments |
| silent_cause | 17 | scn_579204c88c0a | database | 3 | 1 | payments |
| silent_cause | 18 | scn_af14dbd18f2e | database | 3 | 1 | inventory |
| silent_cause | 20 | scn_3be75bc2739e | database | 3 | 1 | payments |
| silent_cause | 21 | scn_64361e643ec5 | database | 3 | 1 | inventory |
| silent_cause | 22 | scn_fd57b5d82b32 | database | 3 | 1 | inventory |
| silent_cause | 23 | scn_dec61be61310 | database | 3 | 1 | inventory |
| silent_cause | 24 | scn_9a03bd2e0c13 | database | 3 | 1 | inventory |
| silent_cause | 25 | scn_6abb9a940f3b | database | 3 | 1 | payments |
| silent_cause | 26 | scn_a5be29ce17a7 | database | 2 | 1 | payments |
| silent_cause | 27 | scn_bbd3f385a92d | database | 3 | 1 | payments |
| silent_cause | 28 | scn_6feb764a8958 | database | 3 | 1 | payments |
| silent_cause | 29 | scn_7114e12a4b9d | database | 4 | 1 | payments |

## P6/P7 noisy-alert onset timing

| Block | Cause alert before injected fault | Cases | Ensemble top-1 conditional on before-onset cause alert |
|---|---:|---:|---:|
| P6 seeds 7–9 | 3/3 (1.000) | 3 | 1/3 (0.333) |
| P7 fresh block | 12/20 (0.600) | 20 | 12/12 (1.000) |

The primary P6/P7 baseline ensemble is the saved V0 RRF from each original run; these conditional figures use the matching original ensemble rankings, not a re-evaluated variant.

