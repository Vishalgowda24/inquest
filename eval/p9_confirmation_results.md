# P9 One-Time Confirmation (seeds 52–71)

Commit: `049259238cd0008db441c7e56737eed3e892f16f`  
V0 config SHA-256: `fca28db7efe3c969a3a28bb6ae6ea114228bc1621e8846c36f6287460267ccb0`; output `runs\p9_confirmation_v0_fca28db7`  
V3 config SHA-256: `02b68a016441cfcc869f5b7a8f1535c112cd55a704bc6ffdcf2345ec3b8f9362`; output `runs\p9_confirmation_v3_02b68a01`  
Cases: 280 (14 families × 20 seeds). This is the only P9 confirmation run; no variants were re-selected afterward. Bootstrap intervals use 20,000 crossed family/seed cluster replicates, RNG seed 90909, and 95% percentile bounds.

## Per-family top-1/top-3

| Family | Cases | V0 top-1/top-3 | V3 top-1/top-3 | alert_order top-1/top-3 | latest_change top-1/top-3 |
|---|---:|---:|---:|---:|---:|
| cause_alerts_2_4 | 20 | 16/20 (20/20) | 18/20 (18/20) | 0/20 (13/20) | 0/20 (0/20) |
| clean_bad_deploy | 20 | 17/20 (20/20) | 19/20 (19/20) | 20/20 (20/20) | 18/20 (18/20) |
| coincident_restart | 20 | 19/20 (20/20) | 18/20 (18/20) | 20/20 (20/20) | 18/20 (18/20) |
| concurrent_causes | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| late_alerting_cause | 20 | 11/20 (20/20) | 18/20 (19/20) | 0/20 (4/20) | 0/20 (0/20) |
| long_seasonal | 20 | 20/20 (20/20) | 19/20 (20/20) | 13/20 (20/20) | 13/20 (13/20) |
| missing_telemetry | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| noisy_alerts | 20 | 16/20 (20/20) | 18/20 (18/20) | 3/20 (17/20) | 0/20 (0/20) |
| partial_graph | 20 | 16/20 (20/20) | 18/20 (18/20) | 20/20 (20/20) | 0/20 (0/20) |
| red_herring_deploy | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 0/20 (0/20) |
| red_herring_hard | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| shared_dependency | 20 | 17/20 (20/20) | 19/20 (19/20) | 20/20 (20/20) | 0/20 (0/20) |
| silent_cause | 20 | 1/20 (16/20) | 6/20 (17/20) | 0/20 (0/20) | 0/20 (0/20) |
| unordered_plausible_alerts | 20 | 16/20 (20/20) | 18/20 (18/20) | 5/20 (15/20) | 0/20 (0/20) |

## Paired top-1 differences (two-way family × seed cluster bootstrap)

| Comparison | Paired difference | 95% percentile interval |
|---|---:|---:|
| V3 − V0 | +0.079 | [+0.004, +0.175] |
| V3 − alert_order | +0.250 | [+0.050, +0.471] |

Plain result: on confirmation, V3 outperforms V0 at top-1 by +0.079/case; the interval excludes zero. Against alert_order, V3's paired difference is +0.250, interval [+0.050, +0.471].

The complete per-case rankings and both config hashes are in `p9_confirmation_cases.json`.
