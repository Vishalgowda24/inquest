# P4 fresh validation scenario specifications

These are validation-only specifications, written before implementation or method execution. Each scenario will use seeds 11, 29, and 47. Exports use the existing HMAC-salted opaque `scn_<hash>` IDs; readable labels, injected faults, and truth mappings are confined to `simulator/sim_truth/`. The holdout registry and files are not used.

## concurrent_causes

- Inject two independent overlapping local faults, one in `payments` and one in `inventory`; neither fault is a consequence of the other. Their activation intervals overlap for at least six simulated windows, with distinct onset times separated enough to allow each fault's local onset to be identified. The downstream symptom set may overlap through checkout and database.
- Truth contains both root causes. Evaluation is multi-label: report both found, one found, or none found among the ranked candidates; a single top-1 metric is insufficient.
- Risk: shared downstream symptoms and common database edges can make the earlier/stronger fault dominate the second cause.

## noisy_alerts

- Keep a real database fault, but independently randomize alert emission order across affected services and add spurious alerts on healthy services. Preserve original raw metrics and traces; expose alert records as telemetry evidence rather than altering metric onset timestamps.
- Truth labels spurious alerts and retains the true fault. Alert-order baseline should be non-informative by construction, while metric and trace methods retain their normal inputs.
- Risk: noisy alert records could inadvertently leak into non-alert evidence; inputs will distinguish alert evidence from raw metric and trace evidence.

## partial_graph

- Keep a real database fault and normal propagated metrics/traces, but omit a deterministic subset of dependency edges only from the declared graph; data-plane propagation still uses the full graph. Set canonical collection metadata `dependency_graph_complete: false` so missing declared edges are explicit rather than guessed by S04.
- Truth records which declared edges were omitted. No truth labels enter exports.
- Risk: graph-based methods should abstain or lose accuracy when their required edges are absent; methods using observed traces/metrics should still operate.

## red_herring_hard

- Inject a real payments configuration fault, an unrelated inventory deployment inside the onset window, and a database shared-dependency path that makes database a plausible graph decoy for multiple symptomatic services. Database has no local fault. The scenario is designed so change-based and graph-based candidate generation each have a plausible wrong answer.
- Truth separately records the payments fault, unrelated deployment, and database decoy role. The exported event/graph/metric data contains no truth labels.
- Risk: this may expose weak discrimination in change proximity, shared-ancestry graph scoring, and S04 alternative reasoning.

## Reproducibility and isolation requirements

- The three fixed seeds are the entire fresh validation set for each named scenario. IDs use the existing random/salted HMAC mechanism and are not derived from scenario names in exports.
- New exports and truth are generated only after this spec is committed. No S03/S04 method, evaluator, tuning loop, holdout scenario, or truth-aware selection runs until the scenario implementation is committed.
- Validation report must separate these 12 cases from all previously seen development cases and must not tune any method on them.
