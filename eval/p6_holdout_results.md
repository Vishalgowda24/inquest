# P6 One-Time Holdout Results

Frozen configuration: equal-weight RRF, fusion abstention on, S04 annotation only (re-rank off). Seeds 7–9 across all existing scenario families. Each case was run once.

| Scenario | Seed | True cause(s) | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble | s04_annotation | latest_change_before_alert | alert_order | True-cause S04 statuses | Wrong-candidate verified |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| clean_bad_deploy | 7 | database | database:1 | database:1 | database:2 | database:2 | database:1 | database:1 | database:1 | database:1 | database:contested | none |
| clean_bad_deploy | 8 | database | database:1 | database:1 | database:1 | database:2 | database:1 | database:1 | database:1 | database:1 | database:insufficient_evidence | none |
| clean_bad_deploy | 9 | database | database:1 | database:1 | database:3 | database:2 | database:1 | database:1 | database:1 | database:1 | database:verified | none |
| coincident_restart | 7 | database | database:1 | database:1 | database:2 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | none |
| coincident_restart | 8 | database | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:insufficient_evidence | none |
| coincident_restart | 9 | database | database:1 | database:1 | database:2 | database:2 | database:1 | database:1 | database:1 | database:1 | database:contested | none |
| red_herring_deploy | 7 | payments | payments:1 | payments:2 | payments:1 | payments:1 | payments:1 | payments:1 | payments:— | payments:1 | payments:insufficient_evidence | none |
| red_herring_deploy | 8 | payments | payments:1 | payments:2 | payments:— | payments:1 | payments:2 | payments:2 | payments:— | payments:1 | payments:contested | none |
| red_herring_deploy | 9 | payments | payments:1 | payments:1 | payments:2 | payments:1 | payments:1 | payments:1 | payments:— | payments:1 | payments:insufficient_evidence | none |
| shared_dependency | 7 | database | database:— | database:1 | database:2 | database:2 | database:2 | database:2 | database:— | database:1 | database:insufficient_evidence | none |
| shared_dependency | 8 | database | database:— | database:1 | database:2 | database:2 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | none |
| shared_dependency | 9 | database | database:— | database:1 | database:2 | database:2 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | none |
| missing_telemetry | 7 | database | database:1 | database:1 | database:2 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | none |
| missing_telemetry | 8 | database | database:1 | database:1 | database:— | database:1 | database:1 | database:1 | database:1 | database:1 | database:insufficient_evidence | none |
| missing_telemetry | 9 | database | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | none |
| long_seasonal | 7 | database | database:— | database:1 | database:2 | database:1 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | none |
| long_seasonal | 8 | database | database:— | database:1 | database:1 | database:1 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | none |
| long_seasonal | 9 | database | database:— | database:2 | database:2 | database:2 | database:1 | database:1 | database:— | database:2 | database:insufficient_evidence | none |
| late_alerting_cause | 7 | database | database:— | database:1 | database:2 | database:3 | database:2 | database:2 | database:— | database:4 | database:unsupported | none |
| late_alerting_cause | 8 | database | database:— | database:1 | database:1 | database:3 | database:1 | database:1 | database:— | database:3 | database:insufficient_evidence | none |
| late_alerting_cause | 9 | database | database:— | database:1 | database:3 | database:3 | database:2 | database:2 | database:— | database:4 | database:unsupported | none |
| silent_cause | 7 | database | database:— | database:1 | database:2 | database:— | database:2 | database:2 | database:— | database:— | database:insufficient_evidence | none |
| silent_cause | 8 | database | database:— | database:1 | database:1 | database:— | database:2 | database:2 | database:— | database:— | database:insufficient_evidence | none |
| silent_cause | 9 | database | database:— | database:1 | database:3 | database:— | database:3 | database:3 | database:— | database:— | database:insufficient_evidence | none |
| concurrent_causes | 7 | payments, inventory | payments:1, inventory:— | payments:1, inventory:4 | payments:2, inventory:4 | payments:1, inventory:2 | payments:1, inventory:3 | payments:1, inventory:3 | payments:1, inventory:— | payments:1, inventory:— | payments:insufficient_evidence, inventory:insufficient_evidence | none |
| concurrent_causes | 8 | payments, inventory | payments:1, inventory:2 | payments:2, inventory:4 | payments:—, inventory:2 | payments:1, inventory:2 | payments:2, inventory:1 | payments:2, inventory:1 | payments:—, inventory:1 | payments:1, inventory:4 | payments:insufficient_evidence, inventory:contested | none |
| concurrent_causes | 9 | payments, inventory | payments:1, inventory:2 | payments:1, inventory:4 | payments:2, inventory:— | payments:1, inventory:2 | payments:1, inventory:2 | payments:1, inventory:2 | payments:—, inventory:1 | payments:1, inventory:— | payments:insufficient_evidence, inventory:insufficient_evidence | none |
| noisy_alerts | 7 | database | database:— | database:1 | database:2 | database:2 | database:2 | database:2 | database:— | database:1 | database:insufficient_evidence | none |
| noisy_alerts | 8 | database | database:— | database:1 | database:2 | database:2 | database:1 | database:1 | database:— | database:3 | database:insufficient_evidence | none |
| noisy_alerts | 9 | database | database:— | database:1 | database:3 | database:2 | database:2 | database:2 | database:— | database:3 | database:insufficient_evidence | none |
| partial_graph | 7 | database | database:— | database:1 | database:2 | database:3 | database:2 | database:2 | database:— | database:1 | database:insufficient_evidence | none |
| partial_graph | 8 | database | database:— | database:1 | database:2 | database:2 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | none |
| partial_graph | 9 | database | database:— | database:1 | database:3 | database:3 | database:2 | database:2 | database:— | database:1 | database:insufficient_evidence | none |
| red_herring_hard | 7 | payments | payments:1 | payments:2 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:insufficient_evidence | none |
| red_herring_hard | 8 | payments | payments:1 | payments:2 | payments:— | payments:1 | payments:2 | payments:2 | payments:1 | payments:1 | payments:contested | none |
| red_herring_hard | 9 | payments | payments:1 | payments:1 | payments:2 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:insufficient_evidence | none |

Run IDs and per-stage status:

| Scenario | Seed | Opaque ID | Run ID | Stage statuses |
|---|---:|---|---|---|
| clean_bad_deploy | 7 | scn_0f4d4e90db53 | p6_a3a70c6cf2609903 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| clean_bad_deploy | 8 | scn_532045d2fdce | p6_c0942fd1db37b7f1 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| clean_bad_deploy | 9 | scn_773ba9eefec3 | p6_878ffa1793b46d4e | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| coincident_restart | 7 | scn_bc39d193f5c7 | p6_427743fad11ebe03 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| coincident_restart | 8 | scn_03a1b679aad6 | p6_c1582efdb954d0c3 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| coincident_restart | 9 | scn_33c1d8757d6f | p6_073efaedb7d45bfc | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| red_herring_deploy | 7 | scn_fc6611a55477 | p6_a80329d27a8aa797 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| red_herring_deploy | 8 | scn_7c79cc97a6b1 | p6_01dedeea30186d2a | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| red_herring_deploy | 9 | scn_99d5b4ea27dc | p6_4fdc53268ea85346 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| shared_dependency | 7 | scn_95a0c05e690b | p6_9113af91cac6ef4c | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| shared_dependency | 8 | scn_b6923a2a4d34 | p6_2866f72544f22941 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| shared_dependency | 9 | scn_22d7175037eb | p6_8cb2c10c16dbbdee | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| missing_telemetry | 7 | scn_121bc40d1764 | p6_f7ddf1cd73bc7fc9 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| missing_telemetry | 8 | scn_d5ecf45b0cc0 | p6_6dbe82ca3474b6ae | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| missing_telemetry | 9 | scn_54d0e71557f4 | p6_1f92f99906c1a755 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| long_seasonal | 7 | scn_dc8206c59054 | p6_9faf516af52f5cb4 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| long_seasonal | 8 | scn_592dfb6e94dc | p6_08fce0b3fa3a0dba | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| long_seasonal | 9 | scn_32ffaf5f5647 | p6_6455f7d356a4475c | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| late_alerting_cause | 7 | scn_9fd75b1f75a5 | p6_d9756ccc5916afa6 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| late_alerting_cause | 8 | scn_6e955589b782 | p6_3dd3493e0dc600c2 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| late_alerting_cause | 9 | scn_f6f69882f5ba | p6_8330f6c5d9f3c434 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| silent_cause | 7 | scn_34177bfa2809 | p6_3225b4e8a17694e3 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| silent_cause | 8 | scn_bba5b40c73e9 | p6_08cffbb46cd4f85c | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| silent_cause | 9 | scn_4b80e283fcbe | p6_52434988519b0738 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| concurrent_causes | 7 | scn_685317ef1844 | p6_135f3c43217da749 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| concurrent_causes | 8 | scn_77e0a06b9021 | p6_e39ee278ca84ef92 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| concurrent_causes | 9 | scn_a892622063fb | p6_dbe5067ed5f77e6d | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| noisy_alerts | 7 | scn_7fef645b444c | p6_5196e2fc75743b7a | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| noisy_alerts | 8 | scn_646a010a856b | p6_6758d86d45f07cf0 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| noisy_alerts | 9 | scn_75fbcf9816ff | p6_8526866c99e4aa66 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| partial_graph | 7 | scn_9e3d5b0f5ad5 | p6_9de77a3e9420fce2 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| partial_graph | 8 | scn_70e79484c6af | p6_f9582bc9db4ba9bc | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| partial_graph | 9 | scn_69b62891adcc | p6_df9ed91bc80c212b | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=DEGRADED, s04_verify=OK |
| red_herring_hard | 7 | scn_b8eb5ec0936d | p6_5fd654f3272b29ba | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| red_herring_hard | 8 | scn_717325a13182 | p6_fc11732a1d685903 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
| red_herring_hard | 9 | scn_f6105c36cf89 | p6_7fa8f66dd98a1162 | s00_ingest=DEGRADED, s01_vault=OK, s02_signals=DEGRADED, s03_candidates=OK, s04_verify=OK |
