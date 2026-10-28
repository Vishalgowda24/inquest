# P4 design fixes and fresh-scenario validation

Part B thresholds/design were committed before evaluation. Part C specifications and simulator implementation were committed before S03/S04 ran. Holdout was not run.

## Part A reconciliation

- P3b top-1 arithmetic: S03 21/24; S04 19/24. `red_herring_deploy` loses 3, `silent_cause` gains 3, and `long_seasonal` loses 2: 21 - 3 + 3 - 2 = 19.
- True-cause rank regressions in the reported P3b table: red_herring_deploy seeds 1,2,3 payments 1→3; long_seasonal seed 1 database 1→2; long_seasonal seed 3 database 1→2. The P3b report attributes false verification to graph checks, but retained artifacts disagree: alternative_check is disabled and database status is insufficient_evidence in red-herring seed 1. The provenance gap is documented in DECISIONS.md.
- P3b per-check contribution table and all five check-ablation tables are preserved in `eval/p3b_results.md` C6-C7; its C6 omits the last two rows in the visible markdown. P4 repair audit must treat those counts cautiously until the raw artifact mismatch is resolved.
- Red-herring saved dependency-path IDs: seed 1 `metric-1-13-database-cpu_percent`, `metric-1-15-database-request_rate`; seed 2 `metric-2-15-database-request_rate`, `metric-2-18-database-cpu_percent`; seed 3 `metric-3-15-database-request_rate`. Retained runs list `alternative_check` as disabled, so no alternative-check IDs can be cited. The graph had a recorded shared path and symptom telemetry; the logic weakness is treating path existence as sufficient causal support, not absence of graph data.

## Scope and summary

Development: 24 cases (the eight previously seen scenarios, seeds 1-3). Fresh validation: 12 cases (four new scenarios, seeds 11, 29, 47). Holdout: not run.

| Dataset | Method | Top-1 | Top-3 |
|---|---|---:|---:|
| development | change_based | 12/24 | 12/24 |
| development | graph_rwr | 19/24 | 24/24 |
| development | trace_ochiai | 10/24 | 23/24 |
| development | temporal_lag | 15/24 | 21/24 |
| development | ensemble_before | 21/24 | 24/24 |
| development | ensemble_after | 21/24 | 24/24 |
| development | s04_annotation | 21/24 | 24/24 |
| development | latest_change_before_alert | 9/24 | 9/24 |
| development | alert_order | 16/24 | 18/24 |
| validation | change_based | 6/12 | 6/12 |
| validation | graph_rwr | 7/12 | 12/12 |
| validation | trace_ochiai | 6/12 | 8/12 |
| validation | temporal_lag | 8/12 | 12/12 |
| validation | ensemble_before | 10/12 | 12/12 |
| validation | ensemble_after | 10/12 | 12/12 |
| validation | s04_annotation | 10/12 | 12/12 |
| validation | latest_change_before_alert | 6/12 | 6/12 |
| validation | alert_order | 9/12 | 11/12 |
## Development details

### Per-scenario top-1/top-3 hits (3 seeds per scenario)

| Scenario | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble before abstention | ensemble after abstention | S04 annotation | latest_change_before_alert | alert_order |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | 0/3; 2/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| red_herring_deploy | 3/3; 3/3 | 0/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| shared_dependency | 0/3; 0/3 | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| long_seasonal | 0/3; 0/3 | 1/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 1/3; 3/3 |
| late_alerting_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |
| silent_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 0/3; 3/3 | 0/3; 3/3 | 0/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |

### Per-case rankings, statuses, and evidence checks

| Scenario | Seed | True cause(s) | change_based ranks | graph_rwr ranks | trace_ochiai ranks | temporal_lag ranks | ensemble before | ensemble after | S04 annotation | latest change | alert order | true status | other candidate statuses | per-cause check verdict/effect/evidence | rank movement before→after |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clean_bad_deploy | 1 | database | database:1 | database:1 | database:2 | database:2 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | inventory:contested, payments:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| clean_bad_deploy | 2 | database | database:1 | database:1 | database:2 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | inventory:contested, payments:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| clean_bad_deploy | 3 | database | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | inventory:insufficient_evidence, payments:insufficient_evidence, checkout:unsupported | database: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| coincident_restart | 1 | database | database:1 | database:1 | database:4 | database:2 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | payments:insufficient_evidence, inventory:unsupported, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=supports(0.9309431829893701); alternative_check=supports(1.0) | database:1→1 |
| coincident_restart | 2 | database | database:1 | database:1 | database:2 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | inventory:unsupported, payments:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=supports(0.9671861326610658); alternative_check=supports(1.0) | database:1→1 |
| coincident_restart | 3 | database | database:1 | database:1 | database:2 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | inventory:insufficient_evidence, payments:insufficient_evidence, checkout:unsupported | database: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=supports(0.9737539799292733); alternative_check=supports(1.0) | database:1→1 |
| red_herring_deploy | 1 | payments | payments:1 | payments:2 | payments:3 | payments:1 | payments:1 | payments:1 | payments:1 | payments:— | payments:1 | payments:insufficient_evidence | inventory:contested, database:insufficient_evidence, checkout:insufficient_evidence | payments: dependency_path=inconclusive(0.0); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=inconclusive(0.0) | payments:1→1 |
| red_herring_deploy | 2 | payments | payments:1 | payments:2 | payments:2 | payments:1 | payments:1 | payments:1 | payments:1 | payments:— | payments:1 | payments:insufficient_evidence | inventory:contested, database:insufficient_evidence, checkout:insufficient_evidence | payments: dependency_path=inconclusive(0.0); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=inconclusive(0.0) | payments:1→1 |
| red_herring_deploy | 3 | payments | payments:1 | payments:2 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:— | payments:1 | payments:insufficient_evidence | database:insufficient_evidence, checkout:unsupported, inventory:insufficient_evidence | payments: dependency_path=inconclusive(0.0); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=inconclusive(0.0) | payments:1→1 |
| shared_dependency | 1 | database | database:— | database:1 | database:1 | database:2 | database:1 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | payments:insufficient_evidence, inventory:unsupported, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| shared_dependency | 2 | database | database:— | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | inventory:unsupported, payments:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| shared_dependency | 3 | database | database:— | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | inventory:insufficient_evidence, payments:insufficient_evidence, checkout:unsupported | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| missing_telemetry | 1 | database | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | payments:insufficient_evidence, checkout:insufficient_evidence, inventory:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| missing_telemetry | 2 | database | database:1 | database:1 | database:3 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | payments:insufficient_evidence, checkout:insufficient_evidence, inventory:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| missing_telemetry | 3 | database | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:1 | database:verified | payments:insufficient_evidence, checkout:insufficient_evidence, inventory:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| long_seasonal | 1 | database | database:— | database:2 | database:1 | database:1 | database:1 | database:1 | database:1 | database:— | database:2 | database:insufficient_evidence | inventory:insufficient_evidence, payments:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.0); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=inconclusive(0.0) | database:1→1 |
| long_seasonal | 2 | database | database:— | database:2 | database:3 | database:1 | database:1 | database:1 | database:1 | database:— | database:2 | database:contested | inventory:insufficient_evidence, payments:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=contradicts(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| long_seasonal | 3 | database | database:— | database:1 | database:3 | database:1 | database:1 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | inventory:insufficient_evidence, payments:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.0); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=inconclusive(0.0) | database:1→1 |
| late_alerting_cause | 1 | database | database:— | database:1 | database:2 | database:3 | database:1 | database:1 | database:1 | database:— | database:4 | database:contested | inventory:unsupported, payments:contested, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| late_alerting_cause | 2 | database | database:— | database:1 | database:2 | database:3 | database:1 | database:1 | database:1 | database:— | database:4 | database:insufficient_evidence | inventory:unsupported, payments:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| late_alerting_cause | 3 | database | database:— | database:1 | database:1 | database:3 | database:1 | database:1 | database:1 | database:— | database:4 | database:insufficient_evidence | inventory:insufficient_evidence, payments:insufficient_evidence, checkout:unsupported | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| silent_cause | 1 | database | database:— | database:1 | database:2 | database:— | database:3 | database:3 | database:3 | database:— | database:— | database:insufficient_evidence | inventory:unsupported, payments:contested, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.6666666666666666); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:3→3 |
| silent_cause | 2 | database | database:— | database:1 | database:2 | database:— | database:3 | database:3 | database:3 | database:— | database:— | database:insufficient_evidence | inventory:unsupported, payments:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.6666666666666666); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:3→3 |
| silent_cause | 3 | database | database:— | database:1 | database:1 | database:— | database:3 | database:3 | database:3 | database:— | database:— | database:insufficient_evidence | inventory:insufficient_evidence, payments:insufficient_evidence, checkout:unsupported | database: dependency_path=inconclusive(0.6666666666666666); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:3→3 |

### S04 false rejection and false confirmation

| Scenario | False rejections (true cause contested/unsupported) | False confirmations (wrong candidate verified) |
|---|---|---|
| clean_bad_deploy | 0: none | 0: none |
| coincident_restart | 0: none | 0: none |
| red_herring_deploy | 0: none | 0: none |
| shared_dependency | 0: none | 0: none |
| missing_telemetry | 0: none | 0: none |
| long_seasonal | 1: seed 2 database=contested (temporal_consistency:change-2-1,metric-2-50-database-latency_ms) | 0: none |
| late_alerting_cause | 1: seed 1 database=contested (equal-score contest) | 0: none |
| silent_cause | 0: none | 0: none |

### S04 status counts

| Scenario | All candidates V/C/I/U | True causes V/C/I/U per seed | Affected missing-telemetry services and outcomes |
|---|---|---|---|
| clean_bad_deploy | 3/2/6/1 | 1:database=verified; 2:database=verified; 3:database=verified | none recorded |
| coincident_restart | 3/0/6/3 | 1:database=verified; 2:database=verified; 3:database=verified | none recorded |
| red_herring_deploy | 0/2/9/1 | 1:payments=insufficient_evidence; 2:payments=insufficient_evidence; 3:payments=insufficient_evidence | none recorded |
| shared_dependency | 0/0/9/3 | 1:database=insufficient_evidence; 2:database=insufficient_evidence; 3:database=insufficient_evidence | none recorded |
| missing_telemetry | 3/0/9/0 | 1:database=verified; 2:database=verified; 3:database=verified | seed 1 checkout=insufficient_evidence, contradicts=False; seed 1 inventory=insufficient_evidence, contradicts=False; seed 2 checkout=insufficient_evidence, contradicts=False; seed 2 inventory=insufficient_evidence, contradicts=False; seed 3 checkout=insufficient_evidence, contradicts=False; seed 3 inventory=insufficient_evidence, contradicts=False |
| long_seasonal | 0/1/11/0 | 1:database=insufficient_evidence; 2:database=contested; 3:database=insufficient_evidence | none recorded |
| late_alerting_cause | 0/2/7/3 | 1:database=contested; 2:database=insufficient_evidence; 3:database=insufficient_evidence | none recorded |
| silent_cause | 0/1/8/3 | 1:database=insufficient_evidence; 2:database=insufficient_evidence; 3:database=insufficient_evidence | seed 1 database=insufficient_evidence, contradicts=False; seed 2 database=insufficient_evidence, contradicts=False; seed 3 database=insufficient_evidence, contradicts=False |

### Per-check contribution (supports/contradicts/inconclusive; true cause vs decoys)

| Scenario | Check | True S/C/I | Decoy S/C/I | Discriminating? |
|---|---|---:|---:|---|
| clean_bad_deploy | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| clean_bad_deploy | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| clean_bad_deploy | temporal_consistency | 3/0/0 | 2/0/7 | yes; distributions differ |
| clean_bad_deploy | recovery_check | 0/0/3 | 0/0/9 | yes; distributions differ |
| clean_bad_deploy | alternative_check | 3/0/0 | 0/3/6 | yes; distributions differ |
| coincident_restart | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| coincident_restart | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| coincident_restart | temporal_consistency | 3/0/0 | 0/0/9 | yes; distributions differ |
| coincident_restart | recovery_check | 3/0/0 | 0/0/9 | yes; distributions differ |
| coincident_restart | alternative_check | 3/0/0 | 0/3/6 | yes; distributions differ |
| red_herring_deploy | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| red_herring_deploy | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| red_herring_deploy | temporal_consistency | 0/0/3 | 2/0/7 | yes; distributions differ |
| red_herring_deploy | recovery_check | 0/0/3 | 0/0/9 | yes; distributions differ |
| red_herring_deploy | alternative_check | 0/0/3 | 3/3/3 | yes; distributions differ |
| shared_dependency | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| shared_dependency | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| shared_dependency | temporal_consistency | 0/0/3 | 0/0/9 | yes; distributions differ |
| shared_dependency | recovery_check | 0/0/3 | 0/0/9 | yes; distributions differ |
| shared_dependency | alternative_check | 3/0/0 | 0/3/6 | yes; distributions differ |
| missing_telemetry | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| missing_telemetry | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| missing_telemetry | temporal_consistency | 3/0/0 | 0/0/9 | yes; distributions differ |
| missing_telemetry | recovery_check | 0/0/3 | 0/0/9 | yes; distributions differ |
| missing_telemetry | alternative_check | 3/0/0 | 0/0/9 | yes; distributions differ |
| long_seasonal | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| long_seasonal | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| long_seasonal | temporal_consistency | 0/1/2 | 0/0/9 | yes; distributions differ |
| long_seasonal | recovery_check | 0/0/3 | 0/0/9 | yes; distributions differ |
| long_seasonal | alternative_check | 1/0/2 | 2/0/7 | yes; distributions differ |
| late_alerting_cause | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| late_alerting_cause | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| late_alerting_cause | temporal_consistency | 0/0/3 | 0/0/9 | yes; distributions differ |
| late_alerting_cause | recovery_check | 0/0/3 | 0/0/9 | yes; distributions differ |
| late_alerting_cause | alternative_check | 3/0/0 | 0/3/6 | yes; distributions differ |
| silent_cause | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| silent_cause | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| silent_cause | temporal_consistency | 0/0/3 | 0/0/9 | yes; distributions differ |
| silent_cause | recovery_check | 0/0/3 | 0/0/9 | yes; distributions differ |
| silent_cause | alternative_check | 3/0/0 | 0/3/6 | yes; distributions differ |

### Per-check ablation and fusion abstention on/off

| Scenario | Fusion OFF top1/top3 | Fusion ON top1/top3 | Abstention effect | Check disabled | S04 order top1/top3 | True verified | Wrong verified | Check effect on status |
|---|---:|---:|---|---|---:|---:|---:|---|
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | no top-k change | vault_evidence | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/2/6/1; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | no top-k change | dependency_path | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/2/6/1; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | no top-k change | temporal_consistency | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/9/3; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | no top-k change | recovery_check | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/2/6/1; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | no top-k change | alternative_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/12/0; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | no top-k change | vault_evidence | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/0/6/3; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | no top-k change | dependency_path | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/0/6/3; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | no top-k change | temporal_consistency | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/0/6/3; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | no top-k change | recovery_check | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/0/6/3; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | no top-k change | alternative_check | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/0/9/0; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| red_herring_deploy | 3/3; 3/3 | 3/3; 3/3 | no top-k change | vault_evidence | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/9/1; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| red_herring_deploy | 3/3; 3/3 | 3/3; 3/3 | no top-k change | dependency_path | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/9/1; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| red_herring_deploy | 3/3; 3/3 | 3/3; 3/3 | no top-k change | temporal_consistency | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/9/3; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| red_herring_deploy | 3/3; 3/3 | 3/3; 3/3 | no top-k change | recovery_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/9/1; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| red_herring_deploy | 3/3; 3/3 | 3/3; 3/3 | no top-k change | alternative_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/12/0; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| shared_dependency | 3/3; 3/3 | 3/3; 3/3 | no top-k change | vault_evidence | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/9/3; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| shared_dependency | 3/3; 3/3 | 3/3; 3/3 | no top-k change | dependency_path | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/9/3; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| shared_dependency | 3/3; 3/3 | 3/3; 3/3 | no top-k change | temporal_consistency | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/9/3; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| shared_dependency | 3/3; 3/3 | 3/3; 3/3 | no top-k change | recovery_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/9/3; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| shared_dependency | 3/3; 3/3 | 3/3; 3/3 | no top-k change | alternative_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/12/0; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | no top-k change | vault_evidence | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/0/9/0; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | no top-k change | dependency_path | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/0/9/0; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | no top-k change | temporal_consistency | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/12/0; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | no top-k change | recovery_check | 3/3; 3/3 | 3 | 0 | all V/C/I/U=3/0/9/0; true V/C/I/U=3/0/0/0; annotation order unchanged. |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | no top-k change | alternative_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/12/0; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| long_seasonal | 3/3; 3/3 | 3/3; 3/3 | no top-k change | vault_evidence | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/1/11/0; true V/C/I/U=0/1/2/0; annotation order unchanged. |
| long_seasonal | 3/3; 3/3 | 3/3; 3/3 | no top-k change | dependency_path | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/1/11/0; true V/C/I/U=0/1/2/0; annotation order unchanged. |
| long_seasonal | 3/3; 3/3 | 3/3; 3/3 | no top-k change | temporal_consistency | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/12/0; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| long_seasonal | 3/3; 3/3 | 3/3; 3/3 | no top-k change | recovery_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/1/11/0; true V/C/I/U=0/1/2/0; annotation order unchanged. |
| long_seasonal | 3/3; 3/3 | 3/3; 3/3 | no top-k change | alternative_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/11/1; true V/C/I/U=0/0/2/1; annotation order unchanged. |
| late_alerting_cause | 3/3; 3/3 | 3/3; 3/3 | no top-k change | vault_evidence | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/7/3; true V/C/I/U=0/1/2/0; annotation order unchanged. |
| late_alerting_cause | 3/3; 3/3 | 3/3; 3/3 | no top-k change | dependency_path | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/7/3; true V/C/I/U=0/1/2/0; annotation order unchanged. |
| late_alerting_cause | 3/3; 3/3 | 3/3; 3/3 | no top-k change | temporal_consistency | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/7/3; true V/C/I/U=0/1/2/0; annotation order unchanged. |
| late_alerting_cause | 3/3; 3/3 | 3/3; 3/3 | no top-k change | recovery_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/7/3; true V/C/I/U=0/1/2/0; annotation order unchanged. |
| late_alerting_cause | 3/3; 3/3 | 3/3; 3/3 | no top-k change | alternative_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/3/9/0; true V/C/I/U=0/1/2/0; annotation order unchanged. |
| silent_cause | 0/3; 3/3 | 0/3; 3/3 | no top-k change | vault_evidence | 0/3; 3/3 | 0 | 0 | all V/C/I/U=0/1/8/3; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| silent_cause | 0/3; 3/3 | 0/3; 3/3 | no top-k change | dependency_path | 0/3; 3/3 | 0 | 0 | all V/C/I/U=0/1/8/3; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| silent_cause | 0/3; 3/3 | 0/3; 3/3 | no top-k change | temporal_consistency | 0/3; 3/3 | 0 | 0 | all V/C/I/U=0/1/8/3; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| silent_cause | 0/3; 3/3 | 0/3; 3/3 | no top-k change | recovery_check | 0/3; 3/3 | 0 | 0 | all V/C/I/U=0/1/8/3; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| silent_cause | 0/3; 3/3 | 0/3; 3/3 | no top-k change | alternative_check | 0/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/10/0; true V/C/I/U=0/0/3/0; annotation order unchanged. |

### One-case comparison flags

Every pair of ranking methods whose per-scenario top-1 or top-3 hit count differs by exactly one case is listed.

| Scenario | Metric | Method A | Hits A | Method B | Hits B |
|---|---|---|---:|---|---:|
| clean_bad_deploy | top-1 | change_based | 3/3 | temporal_lag | 2/3 |
| clean_bad_deploy | top-1 | graph_rwr | 3/3 | temporal_lag | 2/3 |
| clean_bad_deploy | top-1 | trace_ochiai | 1/3 | temporal_lag | 2/3 |
| clean_bad_deploy | top-1 | temporal_lag | 2/3 | ensemble_before | 3/3 |
| clean_bad_deploy | top-1 | temporal_lag | 2/3 | ensemble_after | 3/3 |
| clean_bad_deploy | top-1 | temporal_lag | 2/3 | s04_annotation | 3/3 |
| clean_bad_deploy | top-1 | temporal_lag | 2/3 | latest_change_before_alert | 3/3 |
| clean_bad_deploy | top-1 | temporal_lag | 2/3 | alert_order | 3/3 |
| coincident_restart | top-1 | change_based | 3/3 | temporal_lag | 2/3 |
| coincident_restart | top-1 | graph_rwr | 3/3 | temporal_lag | 2/3 |
| coincident_restart | top-1 | temporal_lag | 2/3 | ensemble_before | 3/3 |
| coincident_restart | top-1 | temporal_lag | 2/3 | ensemble_after | 3/3 |
| coincident_restart | top-1 | temporal_lag | 2/3 | s04_annotation | 3/3 |
| coincident_restart | top-1 | temporal_lag | 2/3 | latest_change_before_alert | 3/3 |
| coincident_restart | top-1 | temporal_lag | 2/3 | alert_order | 3/3 |
| coincident_restart | top-3 | change_based | 3/3 | trace_ochiai | 2/3 |
| coincident_restart | top-3 | graph_rwr | 3/3 | trace_ochiai | 2/3 |
| coincident_restart | top-3 | trace_ochiai | 2/3 | temporal_lag | 3/3 |
| coincident_restart | top-3 | trace_ochiai | 2/3 | ensemble_before | 3/3 |
| coincident_restart | top-3 | trace_ochiai | 2/3 | ensemble_after | 3/3 |
| coincident_restart | top-3 | trace_ochiai | 2/3 | s04_annotation | 3/3 |
| coincident_restart | top-3 | trace_ochiai | 2/3 | latest_change_before_alert | 3/3 |
| coincident_restart | top-3 | trace_ochiai | 2/3 | alert_order | 3/3 |
| red_herring_deploy | top-1 | graph_rwr | 0/3 | trace_ochiai | 1/3 |
| red_herring_deploy | top-1 | trace_ochiai | 1/3 | latest_change_before_alert | 0/3 |
| shared_dependency | top-1 | graph_rwr | 3/3 | temporal_lag | 2/3 |
| shared_dependency | top-1 | trace_ochiai | 3/3 | temporal_lag | 2/3 |
| shared_dependency | top-1 | temporal_lag | 2/3 | ensemble_before | 3/3 |
| shared_dependency | top-1 | temporal_lag | 2/3 | ensemble_after | 3/3 |
| shared_dependency | top-1 | temporal_lag | 2/3 | s04_annotation | 3/3 |
| shared_dependency | top-1 | temporal_lag | 2/3 | alert_order | 3/3 |
| missing_telemetry | top-1 | change_based | 3/3 | trace_ochiai | 2/3 |
| missing_telemetry | top-1 | graph_rwr | 3/3 | trace_ochiai | 2/3 |
| missing_telemetry | top-1 | trace_ochiai | 2/3 | temporal_lag | 3/3 |
| missing_telemetry | top-1 | trace_ochiai | 2/3 | ensemble_before | 3/3 |
| missing_telemetry | top-1 | trace_ochiai | 2/3 | ensemble_after | 3/3 |
| missing_telemetry | top-1 | trace_ochiai | 2/3 | s04_annotation | 3/3 |
| missing_telemetry | top-1 | trace_ochiai | 2/3 | latest_change_before_alert | 3/3 |
| missing_telemetry | top-1 | trace_ochiai | 2/3 | alert_order | 3/3 |
| long_seasonal | top-1 | change_based | 0/3 | graph_rwr | 1/3 |
| long_seasonal | top-1 | change_based | 0/3 | trace_ochiai | 1/3 |
| long_seasonal | top-1 | change_based | 0/3 | alert_order | 1/3 |
| long_seasonal | top-1 | graph_rwr | 1/3 | latest_change_before_alert | 0/3 |
| long_seasonal | top-1 | trace_ochiai | 1/3 | latest_change_before_alert | 0/3 |
| long_seasonal | top-1 | latest_change_before_alert | 0/3 | alert_order | 1/3 |
| late_alerting_cause | top-1 | change_based | 0/3 | trace_ochiai | 1/3 |
| late_alerting_cause | top-1 | trace_ochiai | 1/3 | temporal_lag | 0/3 |
| late_alerting_cause | top-1 | trace_ochiai | 1/3 | latest_change_before_alert | 0/3 |
| late_alerting_cause | top-1 | trace_ochiai | 1/3 | alert_order | 0/3 |
| silent_cause | top-1 | change_based | 0/3 | trace_ochiai | 1/3 |
| silent_cause | top-1 | trace_ochiai | 1/3 | temporal_lag | 0/3 |
| silent_cause | top-1 | trace_ochiai | 1/3 | ensemble_before | 0/3 |
| silent_cause | top-1 | trace_ochiai | 1/3 | ensemble_after | 0/3 |
| silent_cause | top-1 | trace_ochiai | 1/3 | s04_annotation | 0/3 |
| silent_cause | top-1 | trace_ochiai | 1/3 | latest_change_before_alert | 0/3 |
| silent_cause | top-1 | trace_ochiai | 1/3 | alert_order | 0/3 |
## Fresh validation details

### Per-scenario top-1/top-3 hits (3 seeds per scenario)

| Scenario | change_based | graph_rwr | trace_ochiai | temporal_lag | ensemble before abstention | ensemble after abstention | S04 annotation | latest_change_before_alert | alert_order |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| concurrent_causes | 3/3; 3/3 | 0/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| noisy_alerts | 0/3; 0/3 | 3/3; 3/3 | 1/3; 1/3 | 1/3; 3/3 | 2/3; 3/3 | 2/3; 3/3 | 2/3; 3/3 | 0/3; 0/3 | 0/3; 2/3 |
| partial_graph | 0/3; 0/3 | 3/3; 3/3 | 1/3; 1/3 | 1/3; 3/3 | 2/3; 3/3 | 2/3; 3/3 | 2/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| red_herring_hard | 3/3; 3/3 | 1/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |

### Per-case rankings, statuses, and evidence checks

| Scenario | Seed | True cause(s) | change_based ranks | graph_rwr ranks | trace_ochiai ranks | temporal_lag ranks | ensemble before | ensemble after | S04 annotation | latest change | alert order | true status | other candidate statuses | per-cause check verdict/effect/evidence | rank movement before→after |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| concurrent_causes | 11 | payments, inventory | payments:1, inventory:2 | payments:2, inventory:3 | payments:1, inventory:— | payments:1, inventory:2 | payments:1, inventory:2 | payments:1, inventory:2 | payments:1, inventory:2 | payments:—, inventory:1 | payments:1, inventory:3 | payments:insufficient_evidence, inventory:insufficient_evidence | database:insufficient_evidence, checkout:insufficient_evidence | payments: dependency_path=inconclusive(0.0); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=inconclusive(0.0)<br>inventory: dependency_path=inconclusive(0.0); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=inconclusive(0.0) | payments:1→1, inventory:2→2 |
| concurrent_causes | 29 | payments, inventory | payments:1, inventory:— | payments:2, inventory:4 | payments:1, inventory:3 | payments:1, inventory:2 | payments:1, inventory:2 | payments:1, inventory:2 | payments:1, inventory:2 | payments:1, inventory:— | payments:1, inventory:4 | payments:contested, inventory:insufficient_evidence | database:insufficient_evidence, checkout:insufficient_evidence | payments: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=inconclusive(0.0); alternative_check=contradicts(1.0)<br>inventory: dependency_path=inconclusive(0.0); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=inconclusive(0.0) | payments:1→1, inventory:2→2 |
| concurrent_causes | 47 | payments, inventory | payments:1, inventory:2 | payments:2, inventory:4 | payments:2, inventory:— | payments:1, inventory:2 | payments:1, inventory:2 | payments:1, inventory:2 | payments:1, inventory:2 | payments:—, inventory:1 | payments:1, inventory:4 | payments:contested, inventory:insufficient_evidence | checkout:contested, database:contested | payments: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=inconclusive(0.0); alternative_check=contradicts(1.0)<br>inventory: dependency_path=inconclusive(0.0); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=inconclusive(0.0) | payments:1→1, inventory:2→2 |
| noisy_alerts | 11 | database | database:— | database:1 | database:4 | database:1 | database:1 | database:1 | database:1 | database:— | database:3 | database:insufficient_evidence | payments:insufficient_evidence, inventory:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| noisy_alerts | 29 | database | database:— | database:1 | database:4 | database:2 | database:2 | database:2 | database:2 | database:— | database:2 | database:insufficient_evidence | payments:unsupported, inventory:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:2→2 |
| noisy_alerts | 47 | database | database:— | database:1 | database:1 | database:3 | database:1 | database:1 | database:1 | database:— | database:4 | database:insufficient_evidence | inventory:insufficient_evidence, payments:unsupported, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(1.0) | database:1→1 |
| partial_graph | 11 | database | database:— | database:1 | database:4 | database:1 | database:1 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | payments:insufficient_evidence, inventory:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(0.75) | database:1→1 |
| partial_graph | 29 | database | database:— | database:1 | database:4 | database:2 | database:2 | database:2 | database:2 | database:— | database:1 | database:insufficient_evidence | payments:unsupported, inventory:insufficient_evidence, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(0.75) | database:2→2 |
| partial_graph | 47 | database | database:— | database:1 | database:1 | database:3 | database:1 | database:1 | database:1 | database:— | database:1 | database:insufficient_evidence | inventory:insufficient_evidence, payments:unsupported, checkout:insufficient_evidence | database: dependency_path=inconclusive(0.25); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=supports(0.75) | database:1→1 |
| red_herring_hard | 11 | payments | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:insufficient_evidence | inventory:insufficient_evidence, checkout:contested, database:contested | payments: dependency_path=inconclusive(0.0); temporal_consistency=inconclusive(0.0); recovery_check=inconclusive(0.0); alternative_check=inconclusive(0.0) | payments:1→1 |
| red_herring_hard | 29 | payments | payments:1 | payments:2 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:contested | inventory:insufficient_evidence, database:insufficient_evidence, checkout:insufficient_evidence | payments: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=inconclusive(0.0); alternative_check=contradicts(1.0) | payments:1→1 |
| red_herring_hard | 47 | payments | payments:1 | payments:2 | payments:2 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:1 | payments:contested | inventory:insufficient_evidence, database:insufficient_evidence, checkout:insufficient_evidence | payments: dependency_path=inconclusive(0.25); temporal_consistency=supports(1.0); recovery_check=inconclusive(0.0); alternative_check=contradicts(1.0) | payments:1→1 |

### S04 false rejection and false confirmation

| Scenario | False rejections (true cause contested/unsupported) | False confirmations (wrong candidate verified) |
|---|---|---|
| concurrent_causes | 2: seed 29 payments=contested (alternative_check:dependency-checkout-payments,metric-29-13-checkout-request_rate,metric-29-15-payments-request_rate,metric-29-8-payments-latency_ms,metric-29-9-checkout-latency_ms); seed 47 payments=contested (alternative_check:dependency-checkout-payments,metric-47-10-checkout-latency_ms,metric-47-15-payments-request_rate,metric-47-8-payments-cpu_percent,metric-47-8-payments-latency_ms) | 0: none |
| noisy_alerts | 0: none | 0: none |
| partial_graph | 0: none | 0: none |
| red_herring_hard | 2: seed 29 payments=contested (alternative_check:dependency-checkout-payments,metric-29-10-checkout-latency_ms,metric-29-13-checkout-request_rate,metric-29-15-payments-request_rate,metric-29-9-payments-latency_ms); seed 47 payments=contested (alternative_check:dependency-checkout-payments,metric-47-10-checkout-latency_ms,metric-47-15-payments-request_rate,metric-47-9-payments-cpu_percent,metric-47-9-payments-latency_ms) | 0: none |

### S04 status counts

| Scenario | All candidates V/C/I/U | True causes V/C/I/U per seed | Affected missing-telemetry services and outcomes |
|---|---|---|---|
| concurrent_causes | 0/4/8/0 | 11:payments=insufficient_evidence,inventory=insufficient_evidence; 29:payments=contested,inventory=insufficient_evidence; 47:payments=contested,inventory=insufficient_evidence | none recorded |
| noisy_alerts | 0/0/10/2 | 11:database=insufficient_evidence; 29:database=insufficient_evidence; 47:database=insufficient_evidence | none recorded |
| partial_graph | 0/0/10/2 | 11:database=insufficient_evidence; 29:database=insufficient_evidence; 47:database=insufficient_evidence | none recorded |
| red_herring_hard | 0/4/8/0 | 11:payments=insufficient_evidence; 29:payments=contested; 47:payments=contested | none recorded |

### Per-check contribution (supports/contradicts/inconclusive; true cause vs decoys)

| Scenario | Check | True S/C/I | Decoy S/C/I | Discriminating? |
|---|---|---:|---:|---|
| concurrent_causes | vault_evidence | 6/0/0 | 6/0/0 | no; identical verdict counts |
| concurrent_causes | dependency_path | 0/0/6 | 0/0/6 | no; identical verdict counts |
| concurrent_causes | temporal_consistency | 2/0/4 | 0/0/6 | yes; distributions differ |
| concurrent_causes | recovery_check | 0/0/6 | 0/0/6 | no; identical verdict counts |
| concurrent_causes | alternative_check | 0/2/4 | 3/0/3 | yes; distributions differ |
| noisy_alerts | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| noisy_alerts | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| noisy_alerts | temporal_consistency | 0/0/3 | 0/0/9 | yes; distributions differ |
| noisy_alerts | recovery_check | 0/0/3 | 0/0/9 | yes; distributions differ |
| noisy_alerts | alternative_check | 3/0/0 | 0/2/7 | yes; distributions differ |
| partial_graph | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| partial_graph | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| partial_graph | temporal_consistency | 0/0/3 | 0/0/9 | yes; distributions differ |
| partial_graph | recovery_check | 0/0/3 | 0/0/9 | yes; distributions differ |
| partial_graph | alternative_check | 3/0/0 | 0/2/7 | yes; distributions differ |
| red_herring_hard | vault_evidence | 3/0/0 | 9/0/0 | yes; distributions differ |
| red_herring_hard | dependency_path | 0/0/3 | 0/0/9 | yes; distributions differ |
| red_herring_hard | temporal_consistency | 2/0/1 | 0/0/9 | yes; distributions differ |
| red_herring_hard | recovery_check | 0/0/3 | 0/0/9 | yes; distributions differ |
| red_herring_hard | alternative_check | 0/2/1 | 3/0/6 | yes; distributions differ |

### Per-check ablation and fusion abstention on/off

| Scenario | Fusion OFF top1/top3 | Fusion ON top1/top3 | Abstention effect | Check disabled | S04 order top1/top3 | True verified | Wrong verified | Check effect on status |
|---|---:|---:|---|---|---:|---:|---:|---|
| concurrent_causes | 3/3; 3/3 | 3/3; 3/3 | no top-k change | vault_evidence | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/4/8/0; true V/C/I/U=0/2/4/0; annotation order unchanged. |
| concurrent_causes | 3/3; 3/3 | 3/3; 3/3 | no top-k change | dependency_path | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/4/8/0; true V/C/I/U=0/2/4/0; annotation order unchanged. |
| concurrent_causes | 3/3; 3/3 | 3/3; 3/3 | no top-k change | temporal_consistency | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/8/2; true V/C/I/U=0/0/4/2; annotation order unchanged. |
| concurrent_causes | 3/3; 3/3 | 3/3; 3/3 | no top-k change | recovery_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/4/8/0; true V/C/I/U=0/2/4/0; annotation order unchanged. |
| concurrent_causes | 3/3; 3/3 | 3/3; 3/3 | no top-k change | alternative_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/10/0; true V/C/I/U=0/0/6/0; annotation order unchanged. |
| noisy_alerts | 2/3; 3/3 | 2/3; 3/3 | no top-k change | vault_evidence | 2/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/10/2; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| noisy_alerts | 2/3; 3/3 | 2/3; 3/3 | no top-k change | dependency_path | 2/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/10/2; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| noisy_alerts | 2/3; 3/3 | 2/3; 3/3 | no top-k change | temporal_consistency | 2/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/10/2; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| noisy_alerts | 2/3; 3/3 | 2/3; 3/3 | no top-k change | recovery_check | 2/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/10/2; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| noisy_alerts | 2/3; 3/3 | 2/3; 3/3 | no top-k change | alternative_check | 2/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/12/0; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| partial_graph | 2/3; 3/3 | 2/3; 3/3 | no top-k change | vault_evidence | 2/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/10/2; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| partial_graph | 2/3; 3/3 | 2/3; 3/3 | no top-k change | dependency_path | 2/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/10/2; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| partial_graph | 2/3; 3/3 | 2/3; 3/3 | no top-k change | temporal_consistency | 2/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/10/2; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| partial_graph | 2/3; 3/3 | 2/3; 3/3 | no top-k change | recovery_check | 2/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/10/2; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| partial_graph | 2/3; 3/3 | 2/3; 3/3 | no top-k change | alternative_check | 2/3; 3/3 | 0 | 0 | all V/C/I/U=0/0/12/0; true V/C/I/U=0/0/3/0; annotation order unchanged. |
| red_herring_hard | 3/3; 3/3 | 3/3; 3/3 | no top-k change | vault_evidence | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/4/8/0; true V/C/I/U=0/2/1/0; annotation order unchanged. |
| red_herring_hard | 3/3; 3/3 | 3/3; 3/3 | no top-k change | dependency_path | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/4/8/0; true V/C/I/U=0/2/1/0; annotation order unchanged. |
| red_herring_hard | 3/3; 3/3 | 3/3; 3/3 | no top-k change | temporal_consistency | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/8/2; true V/C/I/U=0/0/1/2; annotation order unchanged. |
| red_herring_hard | 3/3; 3/3 | 3/3; 3/3 | no top-k change | recovery_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/4/8/0; true V/C/I/U=0/2/1/0; annotation order unchanged. |
| red_herring_hard | 3/3; 3/3 | 3/3; 3/3 | no top-k change | alternative_check | 3/3; 3/3 | 0 | 0 | all V/C/I/U=0/2/10/0; true V/C/I/U=0/0/3/0; annotation order unchanged. |

### Concurrent causes: per-case found-both / found-one / found-none among top 3

| Seed | Method | Found state | Cause ranks |
|---:|---|---|---|
| 11 | ensemble_before | found-both | payments:1, inventory:2 |
| 11 | ensemble_after | found-both | payments:1, inventory:2 |
| 11 | s04_annotation | found-both | payments:1, inventory:2 |
| 11 | latest_change_before_alert | found-one | payments:—, inventory:1 |
| 11 | alert_order | found-both | payments:1, inventory:3 |
| 29 | ensemble_before | found-both | payments:1, inventory:2 |
| 29 | ensemble_after | found-both | payments:1, inventory:2 |
| 29 | s04_annotation | found-both | payments:1, inventory:2 |
| 29 | latest_change_before_alert | found-one | payments:1, inventory:— |
| 29 | alert_order | found-one | payments:1, inventory:4 |
| 47 | ensemble_before | found-both | payments:1, inventory:2 |
| 47 | ensemble_after | found-both | payments:1, inventory:2 |
| 47 | s04_annotation | found-both | payments:1, inventory:2 |
| 47 | latest_change_before_alert | found-one | payments:—, inventory:1 |
| 47 | alert_order | found-one | payments:1, inventory:4 |

### One-case comparison flags

Every pair of ranking methods whose per-scenario top-1 or top-3 hit count differs by exactly one case is listed.

| Scenario | Metric | Method A | Hits A | Method B | Hits B |
|---|---|---|---:|---|---:|
| concurrent_causes | top-1 | change_based | 3/3 | trace_ochiai | 2/3 |
| concurrent_causes | top-1 | trace_ochiai | 2/3 | temporal_lag | 3/3 |
| concurrent_causes | top-1 | trace_ochiai | 2/3 | ensemble_before | 3/3 |
| concurrent_causes | top-1 | trace_ochiai | 2/3 | ensemble_after | 3/3 |
| concurrent_causes | top-1 | trace_ochiai | 2/3 | s04_annotation | 3/3 |
| concurrent_causes | top-1 | trace_ochiai | 2/3 | latest_change_before_alert | 3/3 |
| concurrent_causes | top-1 | trace_ochiai | 2/3 | alert_order | 3/3 |
| noisy_alerts | top-1 | change_based | 0/3 | trace_ochiai | 1/3 |
| noisy_alerts | top-1 | change_based | 0/3 | temporal_lag | 1/3 |
| noisy_alerts | top-1 | graph_rwr | 3/3 | ensemble_before | 2/3 |
| noisy_alerts | top-1 | graph_rwr | 3/3 | ensemble_after | 2/3 |
| noisy_alerts | top-1 | graph_rwr | 3/3 | s04_annotation | 2/3 |
| noisy_alerts | top-1 | trace_ochiai | 1/3 | ensemble_before | 2/3 |
| noisy_alerts | top-1 | trace_ochiai | 1/3 | ensemble_after | 2/3 |
| noisy_alerts | top-1 | trace_ochiai | 1/3 | s04_annotation | 2/3 |
| noisy_alerts | top-1 | trace_ochiai | 1/3 | latest_change_before_alert | 0/3 |
| noisy_alerts | top-1 | trace_ochiai | 1/3 | alert_order | 0/3 |
| noisy_alerts | top-1 | temporal_lag | 1/3 | ensemble_before | 2/3 |
| noisy_alerts | top-1 | temporal_lag | 1/3 | ensemble_after | 2/3 |
| noisy_alerts | top-1 | temporal_lag | 1/3 | s04_annotation | 2/3 |
| noisy_alerts | top-1 | temporal_lag | 1/3 | latest_change_before_alert | 0/3 |
| noisy_alerts | top-1 | temporal_lag | 1/3 | alert_order | 0/3 |
| noisy_alerts | top-3 | change_based | 0/3 | trace_ochiai | 1/3 |
| noisy_alerts | top-3 | graph_rwr | 3/3 | alert_order | 2/3 |
| noisy_alerts | top-3 | trace_ochiai | 1/3 | latest_change_before_alert | 0/3 |
| noisy_alerts | top-3 | trace_ochiai | 1/3 | alert_order | 2/3 |
| noisy_alerts | top-3 | temporal_lag | 3/3 | alert_order | 2/3 |
| noisy_alerts | top-3 | ensemble_before | 3/3 | alert_order | 2/3 |
| noisy_alerts | top-3 | ensemble_after | 3/3 | alert_order | 2/3 |
| noisy_alerts | top-3 | s04_annotation | 3/3 | alert_order | 2/3 |
| partial_graph | top-1 | change_based | 0/3 | trace_ochiai | 1/3 |
| partial_graph | top-1 | change_based | 0/3 | temporal_lag | 1/3 |
| partial_graph | top-1 | graph_rwr | 3/3 | ensemble_before | 2/3 |
| partial_graph | top-1 | graph_rwr | 3/3 | ensemble_after | 2/3 |
| partial_graph | top-1 | graph_rwr | 3/3 | s04_annotation | 2/3 |
| partial_graph | top-1 | trace_ochiai | 1/3 | ensemble_before | 2/3 |
| partial_graph | top-1 | trace_ochiai | 1/3 | ensemble_after | 2/3 |
| partial_graph | top-1 | trace_ochiai | 1/3 | s04_annotation | 2/3 |
| partial_graph | top-1 | trace_ochiai | 1/3 | latest_change_before_alert | 0/3 |
| partial_graph | top-1 | temporal_lag | 1/3 | ensemble_before | 2/3 |
| partial_graph | top-1 | temporal_lag | 1/3 | ensemble_after | 2/3 |
| partial_graph | top-1 | temporal_lag | 1/3 | s04_annotation | 2/3 |
| partial_graph | top-1 | temporal_lag | 1/3 | latest_change_before_alert | 0/3 |
| partial_graph | top-1 | ensemble_before | 2/3 | alert_order | 3/3 |
| partial_graph | top-1 | ensemble_after | 2/3 | alert_order | 3/3 |
| partial_graph | top-1 | s04_annotation | 2/3 | alert_order | 3/3 |
| partial_graph | top-3 | change_based | 0/3 | trace_ochiai | 1/3 |
| partial_graph | top-3 | trace_ochiai | 1/3 | latest_change_before_alert | 0/3 |
| red_herring_hard | top-1 | change_based | 3/3 | trace_ochiai | 2/3 |
| red_herring_hard | top-1 | graph_rwr | 1/3 | trace_ochiai | 2/3 |
| red_herring_hard | top-1 | trace_ochiai | 2/3 | temporal_lag | 3/3 |
| red_herring_hard | top-1 | trace_ochiai | 2/3 | ensemble_before | 3/3 |
| red_herring_hard | top-1 | trace_ochiai | 2/3 | ensemble_after | 3/3 |
| red_herring_hard | top-1 | trace_ochiai | 2/3 | s04_annotation | 3/3 |
| red_herring_hard | top-1 | trace_ochiai | 2/3 | latest_change_before_alert | 3/3 |
| red_herring_hard | top-1 | trace_ochiai | 2/3 | alert_order | 3/3 |

## Required findings

- Fusion abstention and silent_cause: top-1 changed 0/3 → 0/3 in development. Scenarios with a top-k regression under abstention: none.
- Silent-cause explanation: the database candidate had 6 method/candidate abstentions across the three seeds, but fusion top-k did not change. Legacy RRF already added ranks only for candidates a method emitted, so absent candidates already contributed no worst-rank penalty; this P4 abstention bookkeeping makes that explicit but does not alter this miss.
- noisy_alerts: abstention ensemble top-1/top-3=2/3,3/3; S04 annotation=2/3,3/3; alert_order=0/3,2/3. On top-1 both the ensemble and S04 beat alert_order.
- late_alerting_cause: abstention ensemble top-1/top-3=3/3,3/3; S04 annotation=3/3,3/3; alert_order=0/3,0/3. On top-1 both the ensemble and S04 beat alert_order.
- silent_cause: abstention ensemble top-1/top-3=0/3,3/3; S04 annotation=0/3,3/3; alert_order=0/3,0/3. On top-1 both tie alert_order; neither beats it.
- `verified`: prior P3b report recorded 5 false confirmations. P4 emits 0 wrong-candidate verified decisions and 9 true-cause verified decisions across dev+validation. This is more selective, with lower true-cause coverage; both figures are needed to assess it.
- Development vs validation ensemble-after-abstention: top-1/top-3 21/24,24/24 vs 10/12,12/12 (87.5% vs 83.3% top-1, a 4.2-point decrease; top-3 is unchanged). This is not a large drop in this 12-case validation set; the per-scenario rows show where the difference comes from.
- No tuning or holdout execution occurred. The only post-freeze change before evaluation was the unit-test-discovered integrity-family accounting correction logged in DECISIONS.md.

## Part E: proposals only

- **Holdout:** recommend one final end-of-phase run after the design is frozen and approved. The fresh validation set has only 12 cases; a single untouched run would provide an independent final check. Holdout was not run.
- **P5 candidates:** improve multi-cause status/reporting beyond top-k found-both; make fusion abstention change ranks only where candidate evidence is truly unavailable; strengthen causal evidence for shared-ancestry graph decoys; calibrate noisy-alert and partial-graph handling; add concurrent-fault and missing-change scenarios; improve coverage-aware status confidence. Nothing from this list is implemented in P4.

## P4 completion checklist

| Item | Result |
|---|---|
| Part A P3b reconciliation | yes |
| Part B design frozen and committed before eval | yes (`23decd9`) |
| Part C specs and implementation committed before methods ran | yes (`260f19f`, `6138071`) |
| Validation reported separately from development | yes |
| Holdout not run | yes |
| P5 not started | yes |
| Gates | yes: pytest 66 passed; `inquest doctor` passed |

## Part A appendix: full P3b check counts and check ablations

| Check | True cause S/C/I | Decoys S/C/I |
|---|---:|---:|
| vault_evidence | 24/0/0 | 72/0/0 |
| dependency_path | 19/0/5 | 23/0/49 |
| temporal_consistency | 9/1/14 | 4/0/68 |
| recovery_check | 3/0/21 | 0/0/72 |
| alternative_check | 19/0/5 | 5/18/49 |

All five P3b per-scenario check-ablation tables from the final P3b evaluation follow. The P3b artifact mismatch described in DECISIONS.md applies to their raw-output provenance.

## C7. Ablation: vault_evidence disabled
Full checks 19/24; 24/24 vs disabled 19/24; 24/24: disabling does nothing top-k performance (aggregate; inspect per-scenario table).

| Scenario | change | graph | Ochiai | lag | S03 ensemble | S04 reranked | latest change | alert order |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | 0/3; 2/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| red_herring_deploy | 3/3; 3/3 | 0/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| shared_dependency | 0/3; 0/3 | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| long_seasonal | 0/3; 0/3 | 1/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 1/3; 3/3 |
| late_alerting_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |
| silent_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 0/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |

## C7. Ablation: dependency_path disabled
Full checks 19/24; 24/24 vs disabled 19/24; 24/24: disabling does nothing top-k performance (aggregate; inspect per-scenario table).

| Scenario | change | graph | Ochiai | lag | S03 ensemble | S04 reranked | latest change | alert order |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | 0/3; 2/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| red_herring_deploy | 3/3; 3/3 | 0/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| shared_dependency | 0/3; 0/3 | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| long_seasonal | 0/3; 0/3 | 1/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 1/3; 3/3 |
| late_alerting_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |
| silent_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 0/3; 3/3 | 0/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |

## C7. Ablation: temporal_consistency disabled
Full checks 19/24; 24/24 vs disabled 19/24; 24/24: disabling does nothing top-k performance (aggregate; inspect per-scenario table).

| Scenario | change | graph | Ochiai | lag | S03 ensemble | S04 reranked | latest change | alert order |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | 0/3; 2/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| red_herring_deploy | 3/3; 3/3 | 0/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| shared_dependency | 0/3; 0/3 | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| long_seasonal | 0/3; 0/3 | 1/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 1/3; 3/3 |
| late_alerting_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |
| silent_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 0/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |

## C7. Ablation: recovery_check disabled
Full checks 19/24; 24/24 vs disabled 19/24; 24/24: disabling does nothing top-k performance (aggregate; inspect per-scenario table).

| Scenario | change | graph | Ochiai | lag | S03 ensemble | S04 reranked | latest change | alert order |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | 0/3; 2/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| red_herring_deploy | 3/3; 3/3 | 0/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| shared_dependency | 0/3; 0/3 | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| long_seasonal | 0/3; 0/3 | 1/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 1/3; 3/3 |
| late_alerting_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |
| silent_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 0/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |

## C7. Ablation: alternative_check disabled
Full checks 19/24; 24/24 vs disabled 19/24; 24/24: disabling does nothing top-k performance (aggregate; inspect per-scenario table).

| Scenario | change | graph | Ochiai | lag | S03 ensemble | S04 reranked | latest change | alert order |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | 0/3; 2/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| red_herring_deploy | 3/3; 3/3 | 0/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| shared_dependency | 0/3; 0/3 | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 |
| long_seasonal | 0/3; 0/3 | 1/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 1/3; 3/3 |
| late_alerting_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |
| silent_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 0/3; 3/3 | 0/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 |

