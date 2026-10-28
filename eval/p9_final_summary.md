# P9 Final Summary Tables

Selected default: V3 (per-case score-margin weighted RRF). The development block contains all 388 saved cases across seeds 1–51, including the already-seen P6 seeds 7–9. The P4–P7 fresh block is the union of P4 validation, P5 seeds 4–6, and P7 fresh cases (288 unique cases); it is nested within the development block. P6 seeds 7–9 are also shown separately as a nested block. Confirmation is the one-time seeds 52–71 run.

## Development (seeds 1–51; all 388 cases)

| Family | Cases | V0 top-1/top-3 | V3 top-1/top-3 | ALERT_ORDER top-1/top-3 |
|---|---:|---|---|---|
| cause_alerts_2_4 | 20 | 20/20 (20/20) | 20/20 (20/20) | 0/20 (14/20) |
| clean_bad_deploy | 29 | 28/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| coincident_restart | 29 | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| concurrent_causes | 29 | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| late_alerting_cause | 29 | 20/29 (29/29) | 28/29 (29/29) | 0/29 (4/29) |
| long_seasonal | 29 | 29/29 (29/29) | 23/29 (29/29) | 17/29 (29/29) |
| missing_telemetry | 29 | 28/29 (29/29) | 29/29 (29/29) | 28/29 (29/29) |
| noisy_alerts | 29 | 26/29 (29/29) | 29/29 (29/29) | 8/29 (25/29) |
| partial_graph | 29 | 25/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| red_herring_deploy | 29 | 28/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| red_herring_hard | 29 | 28/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| shared_dependency | 29 | 27/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| silent_cause | 29 | 0/29 (27/29) | 11/29 (29/29) | 0/29 (0/29) |
| unordered_plausible_alerts | 20 | 20/20 (20/20) | 20/20 (20/20) | 5/20 (15/20) |

## P4–P7 fresh blocks (unique union)

| Family | Cases | V0 top-1/top-3 | V3 top-1/top-3 | ALERT_ORDER top-1/top-3 |
|---|---:|---|---|---|
| clean_bad_deploy | 23 | 22/23 (23/23) | 23/23 (23/23) | 23/23 (23/23) |
| coincident_restart | 23 | 23/23 (23/23) | 23/23 (23/23) | 23/23 (23/23) |
| concurrent_causes | 26 | 26/26 (26/26) | 26/26 (26/26) | 26/26 (26/26) |
| late_alerting_cause | 23 | 16/23 (23/23) | 22/23 (23/23) | 0/23 (3/23) |
| long_seasonal | 23 | 23/23 (23/23) | 19/23 (23/23) | 14/23 (23/23) |
| missing_telemetry | 23 | 22/23 (23/23) | 23/23 (23/23) | 22/23 (23/23) |
| noisy_alerts | 26 | 25/26 (26/26) | 26/26 (26/26) | 7/26 (22/26) |
| partial_graph | 26 | 24/26 (26/26) | 26/26 (26/26) | 26/26 (26/26) |
| red_herring_deploy | 23 | 23/23 (23/23) | 23/23 (23/23) | 23/23 (23/23) |
| red_herring_hard | 26 | 26/26 (26/26) | 26/26 (26/26) | 26/26 (26/26) |
| shared_dependency | 23 | 22/23 (23/23) | 23/23 (23/23) | 23/23 (23/23) |
| silent_cause | 23 | 0/23 (21/23) | 9/23 (23/23) | 0/23 (0/23) |

## P6 holdout seeds 7–9 (shown separately; already included in development)

| Family | Cases | V0 top-1/top-3 | V3 top-1/top-3 | ALERT_ORDER top-1/top-3 |
|---|---:|---|---|---|
| clean_bad_deploy | 3 | 3/3 (3/3) | 3/3 (3/3) | 3/3 (3/3) |
| coincident_restart | 3 | 3/3 (3/3) | 3/3 (3/3) | 3/3 (3/3) |
| concurrent_causes | 3 | 3/3 (3/3) | 3/3 (3/3) | 3/3 (3/3) |
| late_alerting_cause | 3 | 1/3 (3/3) | 3/3 (3/3) | 0/3 (1/3) |
| long_seasonal | 3 | 3/3 (3/3) | 2/3 (3/3) | 2/3 (3/3) |
| missing_telemetry | 3 | 3/3 (3/3) | 3/3 (3/3) | 3/3 (3/3) |
| noisy_alerts | 3 | 1/3 (3/3) | 3/3 (3/3) | 1/3 (3/3) |
| partial_graph | 3 | 1/3 (3/3) | 3/3 (3/3) | 3/3 (3/3) |
| red_herring_deploy | 3 | 2/3 (3/3) | 3/3 (3/3) | 3/3 (3/3) |
| red_herring_hard | 3 | 2/3 (3/3) | 3/3 (3/3) | 3/3 (3/3) |
| shared_dependency | 3 | 2/3 (3/3) | 3/3 (3/3) | 3/3 (3/3) |
| silent_cause | 3 | 0/3 (3/3) | 1/3 (3/3) | 0/3 (0/3) |

## P9 confirmation seeds 52–71

| Family | Cases | V0 top-1/top-3 | V3 top-1/top-3 | ALERT_ORDER top-1/top-3 |
|---|---:|---|---|---|
| cause_alerts_2_4 | 20 | 16/20 (20/20) | 18/20 (18/20) | 0/20 (13/20) |
| clean_bad_deploy | 20 | 17/20 (20/20) | 19/20 (19/20) | 20/20 (20/20) |
| coincident_restart | 20 | 19/20 (20/20) | 18/20 (18/20) | 20/20 (20/20) |
| concurrent_causes | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| late_alerting_cause | 20 | 11/20 (20/20) | 18/20 (19/20) | 0/20 (4/20) |
| long_seasonal | 20 | 20/20 (20/20) | 19/20 (20/20) | 13/20 (20/20) |
| missing_telemetry | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| noisy_alerts | 20 | 16/20 (20/20) | 18/20 (18/20) | 3/20 (17/20) |
| partial_graph | 20 | 16/20 (20/20) | 18/20 (18/20) | 20/20 (20/20) |
| red_herring_deploy | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| red_herring_hard | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| shared_dependency | 20 | 17/20 (20/20) | 19/20 (19/20) | 20/20 (20/20) |
| silent_cause | 20 | 1/20 (16/20) | 6/20 (17/20) | 0/20 (0/20) |
| unordered_plausible_alerts | 20 | 16/20 (20/20) | 18/20 (18/20) | 5/20 (15/20) |

## Confirmation totals

On 280 cases, V0 top-1=229/280, V3 top-1=251/280, alert_order top-1=181/280. See `p9_confirmation_results.md` for the preregistered two-way family×seed cluster-bootstrap intervals and exact config hashes.
