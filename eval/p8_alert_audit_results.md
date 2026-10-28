# P8 Simulator Difficulty Audit (no method changes)

P8 analysis commit: `b9fcb2a55e83bacf265600dad5c81a6b1fa4fe59`  
Frozen config SHA-256: `269dbb3f9de3d45edb777fa5bf70c289feb1ec56f40f722a5607fc253b7c90d7`  
P8 new-family cases: 40 (two families × seeds 32–51).

No method, weight, threshold, status rule, or config was changed. P6 seeds 7–9 were read from their saved artifacts only; they were not rerun.

## Part A: P6 vs P7 simulator/config audit

The family implementation for noisy_alerts and partial_graph is unchanged since `6138071bb7242f96d568d529f08d7180a10bca90`. P6's seed materializer was committed in `8f31d05e079de945e8ab0c83e336b83532e1843d`; P7's seed materializer was committed in `74646e85d7b90a8c4c0db1ddbc1a1fb5fc39fc08`. P6 analysis used commit `2e094d8c8d29a695564065cd84a13361fe37b7f7`; P7 used `77b469dfc8cfa203caf97f74c9298439652619d5`. Both used config SHA-256 `269dbb3f9de3d45edb777fa5bf70c289feb1ec56f40f722a5607fc253b7c90d7`. There is no diff in `inquest/` or `config.yaml` between those analysis commits.

Both generators used the same scenario parameters: database fault starts at step 10, intensity 1.4, threshold 42, 20 steps. noisy_alerts emits one alert per service at seeded random steps 5–15, with three healthy-service alerts (75% false-alert share); partial_graph omits only payments→database (one dropped edge). Candidate count is four in every audited case.

| Family | Block | Cause position in alert_order | Alert noise rate | Dropped edges | Candidate count |
|---|---|---|---|---|---|
| noisy_alerts | P6 seeds 7–9 | 1:1, 3:2 | 3/4 | {0: 3} | {4: 3} |
| noisy_alerts | P7 fresh block | 1:5, 2:8, 3:4, 4:3 | 3/4 | {0: 20} | {4: 20} |
| partial_graph | P6 seeds 7–9 | 1:3 | n/a | {1: 3} | {4: 3} |
| partial_graph | P7 fresh block | 1:20 | n/a | {1: 20} | {4: 20} |

Additional noisy-alert timing detail: database alerts arrived at steps [8, 7, 6] in P6 (all 3 before the step-10 fault onset), versus 12/20 before onset in P7. P6 therefore sampled an unusually early cause-alert realization, although P7 also contains many pre-onset alerts and its ensemble still ranked the cause first in all 20 cases.


### P6 per-case ranks and failures

A method is a top-1 failure when the cause rank is not 1; ranks shown include all S03 methods, ensemble, and alert_order.

| Family | Seed | Cause | Cause alert position | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble | alert_order |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| noisy_alerts | 7 | database | 1 | — | 1 | 2 | 2 | 2 | 1 |
| noisy_alerts | 8 | database | 3 | — | 1 | 2 | 2 | 1 | 3 |
| noisy_alerts | 9 | database | 3 | — | 1 | 3 | 2 | 2 | 3 |
| partial_graph | 7 | database | 1 | — | 1 | 2 | 3 | 2 | 1 |
| partial_graph | 8 | database | 1 | — | 1 | 2 | 2 | 1 | 1 |
| partial_graph | 9 | database | 1 | — | 1 | 3 | 3 | 2 | 1 |

Classification: **seed-specific data/rank-fusion edge cases; no different generator, config, or structural scenario parameter was found.** For noisy_alerts, P6 had alert-order positions 1, 3, 3 and P7 spans positions 1–4; both blocks had the same 75% spurious-alert rate. For partial_graph, both blocks dropped exactly one edge and had four candidates, with the cause first in alert_order throughout. In P6, graph_rwr ranked the cause first in all six cases, but in four cases trace/temporal decoys pushed the ensemble cause to rank 2. This implies the P6 1/3 result is a noisy three-seed estimate, not evidence of a systematic generator/config discrepancy.

## Part B: composition-adjusted P7 comparison

Intervals are crossed family-and-seed cluster-bootstrap 95% percentile intervals (20,000 replicates; deterministic seed 80808). Each bootstrap weight is the product of independently resampled family and seed cluster multiplicities. silent_cause has one family, so its family dimension is necessarily degenerate; the interval is effectively seed-cluster-only.

| Group | Cases | Ensemble top-1 | Ensemble 95% CI | alert_order top-1 | alert_order 95% CI | Paired difference | Paired 95% CI |
|---|---:|---:|---:|---:|---:|---:|---:|
| designed_or_seasonal | 60 | 54/60 (0.900) | [0.683, 1.000] | 18/60 (0.300) | [0.000, 0.633] | +0.600 | [+0.350, +0.839] |
| other_nine | 180 | 156/180 (0.867) | [0.638, 1.000] | 160/180 (0.889) | [0.661, 1.000] | -0.022 | [-0.067, +0.000] |
| silent_cause_only | 20 | 0/20 (0.000) | [0.000, 0.000] | 0/20 (0.000) | [0.000, 0.000] | +0.000 | [+0.000, +0.000] |

Plain statement: the overall +0.133 top-1 paired difference depends on the family mix. The three designed-or-seasonal families contribute +0.600/case, while the other nine contribute -0.022/case. At those observed group rates, the ensemble/alert_order mix breaks even when the designed-or-seasonal families make up 3.6% of cases; the P7 mix was 25%. This is composition arithmetic, not an intrinsic, scenario-independent advantage.

## Part C1: alert-order difficulty by family

Position is the true cause's position in the alert_order baseline. When explicit alert-emission events exist, this is their emission order; otherwise the frozen baseline falls back to signal onset order. Candidate counts are S03 ensemble candidates per case.

| Scenario | Cause positions in alert_order (cause labels) | Cases with any cause first | Candidate count distribution |
|---|---|---:|---|
| clean_bad_deploy | 1:20 | 20/20 (1.000) | 4 candidates:20 |
| coincident_restart | 1:20 | 20/20 (1.000) | 4 candidates:20 |
| red_herring_deploy | 1:20 | 20/20 (1.000) | 4 candidates:20 |
| shared_dependency | 1:20 | 20/20 (1.000) | 4 candidates:20 |
| missing_telemetry | 1:20 | 20/20 (1.000) | 4 candidates:20 |
| long_seasonal | 1:13, 2:6, 3:1 | 13/20 (0.650) | 4 candidates:20 |
| late_alerting_cause | 3:3, 4:16, absent:1 | 0/20 (0.000) | 4 candidates:20 |
| silent_cause | absent:20 | 0/20 (0.000) | 4 candidates:20 |
| concurrent_causes | 1:20, 3:6, 4:11, absent:3 | 20/20 (1.000) | 4 candidates:20 |
| noisy_alerts | 1:5, 2:8, 3:4, 4:3 | 5/20 (0.250) | 4 candidates:20 |
| partial_graph | 1:20 | 20/20 (1.000) | 4 candidates:20 |
| red_herring_hard | 1:20 | 20/20 (1.000) | 4 candidates:20 |
| cause_alerts_2_4 | 2:7, 3:7, 4:6 | 0/20 (0.000) | 4 candidates:20 |
| unordered_plausible_alerts | 1:5, 2:5, 3:5, 4:5 | 5/20 (0.250) | 4 candidates:20 |

## Part C2–C3: new-family top-1/top-3 and case results

| New family | Cases | Ensemble top-1 | Ensemble top-3 | alert_order top-1 | alert_order top-3 | Outcome |
|---|---:|---:|---:|---:|---:|---|
| cause_alerts_2_4 | 20 | 20/20 | 20/20 | 0/20 | 14/20 | ensemble beats alert_order at top-1 |
| unordered_plausible_alerts | 20 | 20/20 | 20/20 | 5/20 | 15/20 | ensemble beats alert_order at top-1 |

### New-family per-case rankings

| Family | Seed | Opaque ID | Cause | Cause alert position | change_based rank | graph_rwr rank | trace_ochiai rank | temporal_lag rank | Ensemble rank | alert_order rank | latest_change rank | Candidate count | Run ID |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| cause_alerts_2_4 | 32 | scn_a057d712ff18 | database | 2 | — | 1 | 2 | 1 | 1 | 2 | — | 4 | p8_c495ef8e1ed12c50f3 |
| cause_alerts_2_4 | 33 | scn_1008b8e1c172 | database | 3 | — | 1 | 3 | 1 | 1 | 3 | — | 4 | p8_32979606f2b44de267 |
| cause_alerts_2_4 | 34 | scn_d45a597a5bd5 | database | 4 | — | 1 | 3 | 1 | 1 | 4 | — | 4 | p8_554925eb59c8cf1126 |
| cause_alerts_2_4 | 35 | scn_2a1e8a69f10e | database | 2 | — | 1 | 1 | 1 | 1 | 2 | — | 4 | p8_15ae8bd0d2c474c799 |
| cause_alerts_2_4 | 36 | scn_138a6a808513 | database | 3 | — | 1 | 3 | 1 | 1 | 3 | — | 4 | p8_5aaa33de6d7f97ec03 |
| cause_alerts_2_4 | 37 | scn_7d81b34cd255 | database | 4 | — | 1 | 2 | 1 | 1 | 4 | — | 4 | p8_f1bfab5c62427d3fcb |
| cause_alerts_2_4 | 38 | scn_c0fa11df2555 | database | 2 | — | 1 | 1 | 1 | 1 | 2 | — | 4 | p8_c0a661b8f81c83cb5f |
| cause_alerts_2_4 | 39 | scn_2ce0cfbadeba | database | 3 | — | 1 | 3 | 1 | 1 | 3 | — | 4 | p8_aed78bc593fd7d8c0e |
| cause_alerts_2_4 | 40 | scn_c7097eb2ca8b | database | 4 | — | 1 | 2 | 1 | 1 | 4 | — | 4 | p8_06301007078f545759 |
| cause_alerts_2_4 | 41 | scn_81010de7eff6 | database | 2 | — | 1 | 1 | 1 | 1 | 2 | — | 4 | p8_dce112f458ca4bb744 |
| cause_alerts_2_4 | 42 | scn_603e494a4ad9 | database | 3 | — | 1 | 2 | 2 | 1 | 3 | — | 4 | p8_03998523e697b9f11f |
| cause_alerts_2_4 | 43 | scn_e2df7d9e6344 | database | 4 | — | 1 | 1 | 1 | 1 | 4 | — | 4 | p8_d1904fa0da562fa9c0 |
| cause_alerts_2_4 | 44 | scn_cbff7b9867fb | database | 2 | — | 1 | 1 | 1 | 1 | 2 | — | 4 | p8_923337759e8dfec28c |
| cause_alerts_2_4 | 45 | scn_b2eea87aa9ce | database | 3 | — | 1 | 3 | 1 | 1 | 3 | — | 4 | p8_103b4c50748b1ae3b7 |
| cause_alerts_2_4 | 46 | scn_a02c12d7e4bd | database | 4 | — | 1 | 1 | 1 | 1 | 4 | — | 4 | p8_3e83284c167ac5fca0 |
| cause_alerts_2_4 | 47 | scn_6f79618e43cf | database | 2 | — | 1 | 1 | 3 | 1 | 2 | — | 4 | p8_8503fdaf8756ac3fe9 |
| cause_alerts_2_4 | 48 | scn_a0e2a66de8e5 | database | 3 | — | 1 | 3 | 2 | 1 | 3 | — | 4 | p8_5cb46e6a99b57319cc |
| cause_alerts_2_4 | 49 | scn_8da7fa72be94 | database | 4 | — | 1 | 1 | 1 | 1 | 4 | — | 4 | p8_ecf95b6a8a14793d4d |
| cause_alerts_2_4 | 50 | scn_ac4b46681219 | database | 2 | — | 1 | 2 | 1 | 1 | 2 | — | 4 | p8_3f9f8b6d24d838d4f2 |
| cause_alerts_2_4 | 51 | scn_747795089373 | database | 3 | — | 1 | 2 | 2 | 1 | 3 | — | 4 | p8_6d6ca339311842c854 |
| unordered_plausible_alerts | 32 | scn_0df3cc5262e1 | database | 1 | — | 1 | 2 | 1 | 1 | 1 | — | 4 | p8_adbb3659e8882933f0 |
| unordered_plausible_alerts | 33 | scn_5634a06916e7 | database | 2 | — | 1 | 3 | 1 | 1 | 2 | — | 4 | p8_d6e3001d9cf6de38e3 |
| unordered_plausible_alerts | 34 | scn_efc65728ac40 | database | 3 | — | 1 | 3 | 1 | 1 | 3 | — | 4 | p8_917ef0b77327156a0a |
| unordered_plausible_alerts | 35 | scn_c08da503a9fb | database | 4 | — | 1 | 1 | 1 | 1 | 4 | — | 4 | p8_2a403b885fcc1f631a |
| unordered_plausible_alerts | 36 | scn_fdeca0e9ff60 | database | 1 | — | 1 | 3 | 1 | 1 | 1 | — | 4 | p8_88b33745653c044771 |
| unordered_plausible_alerts | 37 | scn_03590bf5b899 | database | 2 | — | 1 | 2 | 1 | 1 | 2 | — | 4 | p8_63a0cbd53e41b6b559 |
| unordered_plausible_alerts | 38 | scn_4faf3c240281 | database | 3 | — | 1 | 1 | 1 | 1 | 3 | — | 4 | p8_70baca288cf924c811 |
| unordered_plausible_alerts | 39 | scn_e30ddb0816b0 | database | 4 | — | 1 | 3 | 1 | 1 | 4 | — | 4 | p8_d61d9fd16bda2e98ce |
| unordered_plausible_alerts | 40 | scn_32fec5662de6 | database | 1 | — | 1 | 2 | 1 | 1 | 1 | — | 4 | p8_da39e7f61c18fe1124 |
| unordered_plausible_alerts | 41 | scn_8b49e2e24366 | database | 2 | — | 1 | 1 | 1 | 1 | 2 | — | 4 | p8_80fa7b6b4fd1336699 |
| unordered_plausible_alerts | 42 | scn_14b0612ee963 | database | 3 | — | 1 | 2 | 2 | 1 | 3 | — | 4 | p8_5a3fa1e3153a52ca32 |
| unordered_plausible_alerts | 43 | scn_66169d749ab6 | database | 4 | — | 1 | 1 | 1 | 1 | 4 | — | 4 | p8_902baf2c92080dd7dc |
| unordered_plausible_alerts | 44 | scn_75e4cdb85981 | database | 1 | — | 1 | 1 | 1 | 1 | 1 | — | 4 | p8_8fb11206e5cd6daea5 |
| unordered_plausible_alerts | 45 | scn_05d0b7060346 | database | 2 | — | 1 | 3 | 1 | 1 | 2 | — | 4 | p8_d09a1778cc16d91917 |
| unordered_plausible_alerts | 46 | scn_5b6d3e26a7ca | database | 3 | — | 1 | 1 | 1 | 1 | 3 | — | 4 | p8_d857411293fbdf13cd |
| unordered_plausible_alerts | 47 | scn_46406737dc4b | database | 4 | — | 1 | 1 | 3 | 1 | 4 | — | 4 | p8_38071da41105073c63 |
| unordered_plausible_alerts | 48 | scn_5291b054f904 | database | 1 | — | 1 | 3 | 2 | 1 | 1 | — | 4 | p8_96c53febbf2a04b86f |
| unordered_plausible_alerts | 49 | scn_3d727ccb47be | database | 2 | — | 1 | 1 | 1 | 1 | 2 | — | 4 | p8_629c774d8394f609a0 |
| unordered_plausible_alerts | 50 | scn_0d5feb65b2df | database | 3 | — | 1 | 2 | 1 | 1 | 3 | — | 4 | p8_44ae17f9d8b5934d90 |
| unordered_plausible_alerts | 51 | scn_b6c6c0f74311 | database | 4 | — | 1 | 2 | 2 | 1 | 4 | — | 4 | p8_d539e827fc8136ac08 |

## Part D1: silent_cause method ranks and diagnosis

| Seed | change_based | graph_rwr | trace_ochiai | temporal_lag | Ensemble | alert_order | Method top-1 candidates (change/graph/trace/lag) |
|---:|---:|---:|---:|---:|---:|---:|---|
| 10 | — | 1 | 1 | — | 3 | — | —, database, database, inventory |
| 11 | — | 1 | 4 | — | 3 | — | —, database, payments, payments |
| 12 | — | 1 | 2 | — | 3 | — | —, database, checkout, payments |
| 13 | — | 1 | 2 | — | 3 | — | —, database, checkout, inventory |
| 14 | — | 1 | 1 | — | 3 | — | —, database, database, payments |
| 15 | — | 1 | 1 | — | 3 | — | —, database, database, inventory |
| 16 | — | 1 | 2 | — | 3 | — | —, database, checkout, payments |
| 17 | — | 1 | 1 | — | 3 | — | —, database, database, payments |
| 18 | — | 1 | 2 | — | 3 | — | —, database, checkout, payments |
| 19 | — | 2 | 2 | — | 4 | — | —, payments, checkout, inventory |
| 20 | — | 1 | 2 | — | 3 | — | —, database, checkout, payments |
| 21 | — | 1 | 2 | — | 3 | — | —, database, checkout, inventory |
| 22 | — | 1 | 4 | — | 3 | — | —, database, inventory, payments |
| 23 | — | 1 | 1 | — | 3 | — | —, database, database, inventory |
| 24 | — | 1 | 2 | — | 3 | — | —, database, inventory, inventory |
| 25 | — | 1 | 1 | — | 3 | — | —, database, database, payments |
| 26 | — | 1 | 2 | — | 2 | — | —, database, payments, payments |
| 27 | — | 1 | 3 | — | 3 | — | —, database, checkout, inventory |
| 28 | — | 1 | 1 | — | 3 | — | —, database, database, inventory |
| 29 | — | 1 | 4 | — | 4 | — | —, database, checkout, payments |

Mechanism evidence: graph_rwr ranks database first in 19/20 cases; trace_ochiai ranks it first in 7/20 and second in 9/20. change_based ranks database in none, temporal_lag ranks it in none, and temporal_lag's top-1 is payments in 11 and inventory in 9. The ensemble's top-1 is payments in 13 and inventory in 7; database ranks third in 17 cases, fourth in two, and second in one. This is vote mass on decoys despite one strong graph signal, not a configured threshold or tie-break. No fix is applied. Proposal: test an evidence-aware anomaly-only fusion path for candidates supported by graph/metric propagation even without changes or alerts. It could harm shared_dependency and partial_graph, where graph paths and missing edges can favor a shared-ancestry decoy; validate those families on fresh seeds before adoption.

## Part D2: late_alerting_cause misses

| Seed | Cause rank ensemble | change_based | graph_rwr | trace_ochiai | temporal_lag | Ensemble top-1 | alert_order rank |
|---:|---:|---:|---:|---:|---:|---|---:|
| 11 | 3 | — | 1 | 4 | 3 | payments | 4 |
| 22 | 3 | — | 1 | 4 | 3 | inventory | 4 |
| 24 | 3 | — | 1 | 2 | — | inventory | 4 |
| 26 | 2 | — | 1 | 2 | 3 | payments | 4 |
| 27 | 2 | — | 1 | 3 | 3 | payments | 4 |
| 29 | 3 | — | 1 | 4 | 3 | payments | 4 |

There are 6 top-1 misses in P7's 20 late_alerting_cause cases (the six misses referenced in the request). In all six, graph_rwr ranks the cause first, change_based emits no cause, and alert_order puts the cause fourth; trace/temporal rank mass favors callers, leaving the ensemble cause second or third. No changes were applied.
\n