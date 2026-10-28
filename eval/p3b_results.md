# P3b S04 evaluation

Scope: 8 non-holdout scenarios x 3 seeds = 24 cases. Holdout was not run. Spec frozen in DECISIONS.md before this run. Frozen-spec commit: `59cade35196252bf5fa2549aa4f7b27e9e55106a`; pre-rerun bug-log commit: `49d7fd0e6f6d047964f6768b841b2a0de58654eb`.

## C1. True cause vs decoys (per case)

| Scenario | Seed | True cause | S03 true rank | S04 status | Other top-3 candidates/status | True-cause check verdicts |
|---|---:|---|---:|---|---|---|
| clean_bad_deploy | 1 | database | 1 | verified | inventory: contested, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=supports(1.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| clean_bad_deploy | 2 | database | 1 | verified | inventory: contested, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=supports(1.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| clean_bad_deploy | 3 | database | 1 | verified | inventory: insufficient_evidence, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=supports(1.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| coincident_restart | 1 | database | 1 | verified | payments: insufficient_evidence, inventory: contested | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=supports(1.00); recovery_check=supports(0.93); alternative_check=supports(1.00) |
| coincident_restart | 2 | database | 1 | verified | inventory: contested, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=supports(1.00); recovery_check=supports(0.97); alternative_check=supports(1.00) |
| coincident_restart | 3 | database | 1 | verified | inventory: insufficient_evidence, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=supports(1.00); recovery_check=supports(0.97); alternative_check=supports(1.00) |
| red_herring_deploy | 1 | payments | 1 | insufficient_evidence | inventory: contested, database: verified | vault_evidence=supports(1.00); dependency_path=inconclusive(0.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=inconclusive(0.00) |
| red_herring_deploy | 2 | payments | 1 | insufficient_evidence | inventory: contested, database: verified | vault_evidence=supports(1.00); dependency_path=inconclusive(0.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=inconclusive(0.00) |
| red_herring_deploy | 3 | payments | 1 | insufficient_evidence | database: verified, checkout: contested | vault_evidence=supports(1.00); dependency_path=inconclusive(0.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=inconclusive(0.00) |
| shared_dependency | 1 | database | 1 | verified | payments: insufficient_evidence, inventory: contested | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| shared_dependency | 2 | database | 1 | verified | inventory: contested, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| shared_dependency | 3 | database | 1 | verified | inventory: insufficient_evidence, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| missing_telemetry | 1 | database | 1 | verified | payments: insufficient_evidence, checkout: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=supports(1.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| missing_telemetry | 2 | database | 1 | verified | payments: insufficient_evidence, checkout: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=supports(1.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| missing_telemetry | 3 | database | 1 | verified | payments: insufficient_evidence, checkout: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=supports(1.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| long_seasonal | 1 | database | 1 | insufficient_evidence | inventory: verified, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=inconclusive(0.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=inconclusive(0.00) |
| long_seasonal | 2 | database | 1 | contested | inventory: insufficient_evidence, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=contradicts(0.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| long_seasonal | 3 | database | 1 | insufficient_evidence | inventory: insufficient_evidence, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=inconclusive(0.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=inconclusive(0.00) |
| late_alerting_cause | 1 | database | 1 | contested | inventory: contested, payments: contested | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| late_alerting_cause | 2 | database | 1 | verified | inventory: contested, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| late_alerting_cause | 3 | database | 1 | verified | inventory: insufficient_evidence, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| silent_cause | 1 | database | 3 | verified | inventory: contested, payments: contested | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| silent_cause | 2 | database | 3 | verified | inventory: contested, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |
| silent_cause | 3 | database | 3 | verified | inventory: insufficient_evidence, payments: insufficient_evidence | vault_evidence=supports(1.00); dependency_path=supports(1.00); temporal_consistency=inconclusive(0.00); recovery_check=inconclusive(0.00); alternative_check=supports(1.00) |

## C2. False rejection (true cause contested or unsupported)

| Scenario | Count / 3 | Case details (seed: status; contradicting checks and evidence IDs) |
|---|---:|---|
| clean_bad_deploy | 0/3 | none |
| coincident_restart | 0/3 | none |
| red_herring_deploy | 0/3 | none |
| shared_dependency | 0/3 | none |
| missing_telemetry | 0/3 | none |
| long_seasonal | 1/3 | seed 2: contested; temporal_consistency=['change-2-1', 'metric-2-50-database-latency_ms'] |
| late_alerting_cause | 1/3 | seed 1: contested; equally scored candidate(s): inventory, payments |
| silent_cause | 0/3 | none |

## C3. False confirmation (wrong candidate marked verified)

| Scenario | Count | Case details (seed: candidate; supporting checks and rationale) |
|---|---:|---|
| clean_bad_deploy | 0 | none |
| coincident_restart | 0 | none |
| red_herring_deploy | 3 | seed 1: database; dependency_path: Candidate lies on a recorded upstream dependency path to a symptomatic service.; alternative_check: No competing candidate explains as many symptomatic services through the recorded graph.; seed 2: database; dependency_path: Candidate lies on a recorded upstream dependency path to a symptomatic service.; alternative_check: No competing candidate explains as many symptomatic services through the recorded graph.; seed 3: database; dependency_path: Candidate lies on a recorded upstream dependency path to a symptomatic service.; alternative_check: No competing candidate explains as many symptomatic services through the recorded graph. |
| shared_dependency | 0 | none |
| missing_telemetry | 0 | none |
| long_seasonal | 2 | seed 1: inventory; dependency_path: Candidate lies on a recorded upstream dependency path to a symptomatic service.; alternative_check: No competing candidate explains as many symptomatic services through the recorded graph.; seed 3: checkout; dependency_path: Candidate lies on a recorded upstream dependency path to a symptomatic service.; alternative_check: No competing candidate explains as many symptomatic services through the recorded graph. |
| late_alerting_cause | 0 | none |
| silent_cause | 0 | none |

## C4. Status distribution (candidate counts; true-cause status)

| Scenario | All candidates V/C/I/U | True cause status seeds 1/2/3 | Missing-coverage service status by seed (expected insufficient_evidence) | Missing-coverage candidates contradicted by any check? |
|---|---|---|---|---|
| clean_bad_deploy | 3/3/6/0 | verified, verified, verified | seed 1: checkout=insufficient_evidence, payments=insufficient_evidence; seed 2: checkout=insufficient_evidence, payments=insufficient_evidence; seed 3: inventory=insufficient_evidence, payments=insufficient_evidence | none |
| coincident_restart | 3/3/6/0 | verified, verified, verified | seed 1: checkout=insufficient_evidence, payments=insufficient_evidence; seed 2: checkout=insufficient_evidence, payments=insufficient_evidence; seed 3: inventory=insufficient_evidence, payments=insufficient_evidence | none |
| red_herring_deploy | 3/3/6/0 | insufficient_evidence, insufficient_evidence, insufficient_evidence | seed 1: checkout=insufficient_evidence, payments=insufficient_evidence; seed 2: checkout=insufficient_evidence, payments=insufficient_evidence; seed 3: inventory=insufficient_evidence, payments=insufficient_evidence | none |
| shared_dependency | 3/3/6/0 | verified, verified, verified | seed 1: checkout=insufficient_evidence, payments=insufficient_evidence; seed 2: checkout=insufficient_evidence, payments=insufficient_evidence; seed 3: inventory=insufficient_evidence, payments=insufficient_evidence | none |
| missing_telemetry | 3/0/9/0 | verified, verified, verified | seed 1: checkout=insufficient_evidence, inventory=insufficient_evidence, payments=insufficient_evidence; seed 2: checkout=insufficient_evidence, inventory=insufficient_evidence, payments=insufficient_evidence; seed 3: checkout=insufficient_evidence, inventory=insufficient_evidence, payments=insufficient_evidence | none |
| long_seasonal | 2/1/9/0 | insufficient_evidence, contested, insufficient_evidence | seed 1: checkout=insufficient_evidence, database=insufficient_evidence, payments=insufficient_evidence; seed 2: checkout=insufficient_evidence, inventory=insufficient_evidence, payments=insufficient_evidence; seed 3: database=insufficient_evidence, inventory=insufficient_evidence, payments=insufficient_evidence | none |
| late_alerting_cause | 2/5/5/0 | contested, verified, verified | seed 1: checkout=insufficient_evidence, payments=contested; seed 2: checkout=insufficient_evidence, payments=insufficient_evidence; seed 3: inventory=insufficient_evidence, payments=insufficient_evidence | none |
| silent_cause | 3/4/5/0 | verified, verified, verified | seed 1: checkout=insufficient_evidence, payments=contested; seed 2: checkout=insufficient_evidence, payments=insufficient_evidence; seed 3: inventory=insufficient_evidence, payments=insufficient_evidence | none |

## C5. Per-scenario top-1/top-3 hits (seed hits)

| Scenario | change | graph | Ochiai | lag | S03 ensemble | S04 reranked | latest change | alert order | One-case comparisons |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| clean_bad_deploy | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | change_based/temporal_lag, graph_rwr/temporal_lag, trace_ochiai/temporal_lag, temporal_lag/ensemble, temporal_lag/s04_reranked, temporal_lag/latest_change_before_alert, temporal_lag/alert_order |
| coincident_restart | 3/3; 3/3 | 3/3; 3/3 | 0/3; 2/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | change_based/trace_ochiai, change_based/temporal_lag, graph_rwr/trace_ochiai, graph_rwr/temporal_lag, trace_ochiai/temporal_lag, trace_ochiai/ensemble, trace_ochiai/s04_reranked, trace_ochiai/latest_change_before_alert, trace_ochiai/alert_order, temporal_lag/ensemble, temporal_lag/s04_reranked, temporal_lag/latest_change_before_alert, temporal_lag/alert_order |
| red_herring_deploy | 3/3; 3/3 | 0/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 | graph_rwr/trace_ochiai, trace_ochiai/s04_reranked, trace_ochiai/latest_change_before_alert |
| shared_dependency | 0/3; 0/3 | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 3/3; 3/3 | graph_rwr/temporal_lag, trace_ochiai/temporal_lag, temporal_lag/ensemble, temporal_lag/s04_reranked, temporal_lag/alert_order |
| missing_telemetry | 3/3; 3/3 | 3/3; 3/3 | 2/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | change_based/trace_ochiai, graph_rwr/trace_ochiai, trace_ochiai/temporal_lag, trace_ochiai/ensemble, trace_ochiai/s04_reranked, trace_ochiai/latest_change_before_alert, trace_ochiai/alert_order |
| long_seasonal | 0/3; 0/3 | 1/3; 3/3 | 1/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 1/3; 3/3 | change_based/graph_rwr, change_based/trace_ochiai, change_based/s04_reranked, change_based/alert_order, graph_rwr/latest_change_before_alert, trace_ochiai/latest_change_before_alert, s04_reranked/latest_change_before_alert, latest_change_before_alert/alert_order |
| late_alerting_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 3/3 | 3/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 | change_based/trace_ochiai, trace_ochiai/temporal_lag, trace_ochiai/latest_change_before_alert, trace_ochiai/alert_order |
| silent_cause | 0/3; 0/3 | 3/3; 3/3 | 1/3; 3/3 | 0/3; 0/3 | 0/3; 3/3 | 3/3; 3/3 | 0/3; 0/3 | 0/3; 0/3 | change_based/trace_ochiai, trace_ochiai/temporal_lag, trace_ochiai/ensemble, trace_ochiai/latest_change_before_alert, trace_ochiai/alert_order |

### C5 per-case true-cause rank movement

| Scenario | Seed | S03 rank | S04 rank | Movement |
|---|---:|---:|---:|---|
| clean_bad_deploy | 1 | 1 | 1 | +0 (same) |
| clean_bad_deploy | 2 | 1 | 1 | +0 (same) |
| clean_bad_deploy | 3 | 1 | 1 | +0 (same) |
| coincident_restart | 1 | 1 | 1 | +0 (same) |
| coincident_restart | 2 | 1 | 1 | +0 (same) |
| coincident_restart | 3 | 1 | 1 | +0 (same) |
| red_herring_deploy | 1 | 1 | 3 | +2 (worse) |
| red_herring_deploy | 2 | 1 | 3 | +2 (worse) |
| red_herring_deploy | 3 | 1 | 3 | +2 (worse) |
| shared_dependency | 1 | 1 | 1 | +0 (same) |
| shared_dependency | 2 | 1 | 1 | +0 (same) |
| shared_dependency | 3 | 1 | 1 | +0 (same) |
| missing_telemetry | 1 | 1 | 1 | +0 (same) |
| missing_telemetry | 2 | 1 | 1 | +0 (same) |
| missing_telemetry | 3 | 1 | 1 | +0 (same) |
| long_seasonal | 1 | 1 | 2 | +1 (worse) |
| long_seasonal | 2 | 1 | 1 | +0 (same) |
| long_seasonal | 3 | 1 | 2 | +1 (worse) |
| late_alerting_cause | 1 | 1 | 1 | +0 (same) |
| late_alerting_cause | 2 | 1 | 1 | +0 (same) |
| late_alerting_cause | 3 | 1 | 1 | +0 (same) |
| silent_cause | 1 | 3 | 1 | -2 (better) |
| silent_cause | 2 | 3 | 1 | -2 (better) |
| silent_cause | 3 | 3 | 1 | -2 (better) |

## C6. Per-check contribution (true cause vs decoys)

| Check | True supports/contradicts/inconclusive | Decoys supports/contradicts/inconclusive | Discrimination note |
|---|---:|---:|---|
| vault_evidence | 24/0/0 | 72/0/0 | not discriminating: same normalized verdict distribution |
| dependency_path | 19/0/5 | 23/0/49 | normalized verdict distributions differ |
| temporal_consistency | 9/1/14 | 4/0/68 | normalized verdict distributions differ |
| recovery_check | 3/0/21 | 0/0/72 | normalized verdict distributions differ |
| alternative_check | 19/0/5 | 5/18/49 | normalized verdict distributions differ |

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

## D. Required plain statements

- S04 separated true causes from decoys in 17/24 true-cause cases marked verified and 5 wrong candidates falsely verified; case-level evidence is in C1–C3.
- Re-ranking mixed over the S03 ensemble overall: top-1 21/24 -> 19/24; top-3 24/24 -> 24/24.
- red_herring_deploy: S03 ensemble top-1/top-3 (3, 3); S04 reranked (0, 3); alert_order (3, 3) (hits out of 3). S03 ensemble ties alert_order on top-1; S04 trails alert_order on top-1.
- shared_dependency: S03 ensemble top-1/top-3 (3, 3); S04 reranked (3, 3); alert_order (3, 3) (hits out of 3). S03 ensemble ties alert_order on top-1; S04 ties alert_order on top-1.
- late_alerting_cause: S03 ensemble top-1/top-3 (3, 3); S04 reranked (3, 3); alert_order (0, 0) (hits out of 3). S03 ensemble beats alert_order on top-1; S04 beats alert_order on top-1.
- silent_cause: S03 ensemble top-1/top-3 (0, 3); S04 reranked (3, 3); alert_order (0, 0) (hits out of 3). S03 ensemble ties alert_order on top-1; S04 beats alert_order on top-1.
- Failed cases and check/method outcomes are listed in C1–C3 and per-case rank movement in C5.
- Threshold/spec clarifications after the initial Part A draft: recovery coverage was made 3 pre-action plus 3 post-action windows, and its effect formula was made explicit before evaluation; rationale is recorded in DECISIONS.md. No values changed after the frozen-spec commit.

## E. Decision proposals only (nothing applied)

- Silent-cause fusion miss: propose abstaining methods contribute no rank for candidates without their evidence. Expected to reduce rank dilution where methods lack coverage; could harm cases where a method's sparse-but-valid evidence is useful. Not implemented.
- Simulator gaps for P4 consideration: alerting noise, partial dependency graphs, multiple concurrent causes, and delayed or missing change records. Not built.
- Holdout recommendation: reserve a single end-of-phase run after P4 freezes; it provides an untouched final check, but this is a proposal only. Holdout was not run.

## F. Completion checklist

| Item | Result |
|---|---|
| Frozen Part A spec committed before eval | See commit recorded with this report |
| Per-candidate status vocabulary | yes |
| Rerank toggle default OFF; both orders emitted | yes |
| recovery_check and alternative_check | implemented generically; no simulator-specific logic |
| S04 tests outside simulator/; no simulator imports | yes |
| Direction regression including reversed-edge negative case | yes |
| Missing telemetry yields inconclusive | yes; no check contradicted a coverage-gap candidate in C4 |
| S04 evidence IDs validated against vault | yes; stage contract and test |
| pytest and inquest doctor | see gate report |
| Holdout not run | yes |
| P4 not started | yes |

### Status snapshots per case

| Scenario | Seed | Stage statuses S00/S01/S02/S03/S04 | Candidate counts |
|---|---:|---|---:|
| clean_bad_deploy | 1 | DEGRADED / OK / DEGRADED / OK / OK | 4 |
| clean_bad_deploy | 2 | DEGRADED / OK / DEGRADED / OK / OK | 4 |
| clean_bad_deploy | 3 | DEGRADED / OK / DEGRADED / OK / OK | 4 |
| coincident_restart | 1 | DEGRADED / OK / DEGRADED / OK / OK | 4 |
| coincident_restart | 2 | DEGRADED / OK / DEGRADED / OK / OK | 4 |
| coincident_restart | 3 | DEGRADED / OK / DEGRADED / OK / OK | 4 |
| red_herring_deploy | 1 | DEGRADED / OK / DEGRADED / OK / OK | 4 |
| red_herring_deploy | 2 | DEGRADED / OK / DEGRADED / OK / OK | 4 |
| red_herring_deploy | 3 | DEGRADED / OK / DEGRADED / OK / OK | 4 |
| shared_dependency | 1 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| shared_dependency | 2 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| shared_dependency | 3 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| missing_telemetry | 1 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| missing_telemetry | 2 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| missing_telemetry | 3 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| long_seasonal | 1 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| long_seasonal | 2 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| long_seasonal | 3 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| late_alerting_cause | 1 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| late_alerting_cause | 2 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| late_alerting_cause | 3 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| silent_cause | 1 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| silent_cause | 2 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
| silent_cause | 3 | DEGRADED / OK / DEGRADED / DEGRADED / OK | 4 |
