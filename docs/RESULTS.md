# Inquest Benchmark Results (V3 Default)

This document records the complete, frozen evaluation results for Inquest's default pipeline (V3 per-case score-margin weighted RRF) across all 948 synthetic scenario cases spanning seeds 1 through 91.

No pipeline parameters, method weights, thresholds, or status rules were tuned or modified on these evaluations.

---

## 1. Problem-Family Performance Across All Seed Blocks (n=948)

Evaluated across the 14 registered problem families and all three seed blocks:
- **Development Block** (seeds 1–51, including holdout seeds 7–9): 388 cases
- **Confirmation Block** (seeds 52–71): 280 cases
- **Calibration Block** (seeds 72–91): 280 cases

| Family | n | Ensemble (V3) top-1/top-3 | V0 top-1/top-3 | graph_rwr top-1/top-3 | alert_order top-1/top-3 | latest_change top-1/top-3 | V3 vs V0 top-1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| cause_alerts_2_4 | 60 | 57/60 (58/60) | 55/60 (60/60) | 60/60 (60/60) | 0/60 (40/60) | 0/60 (0/60) | +2 (better) |
| clean_bad_deploy | 69 | 68/69 (68/69) | 62/69 (69/69) | 69/69 (69/69) | 68/69 (69/69) | 64/69 (64/69) | +6 (better) |
| **coincident_restart** | 69 | 65/69 (66/69) | 67/69 (69/69) | 69/69 (69/69) | 68/69 (69/69) | 64/69 (64/69) | **-2 (worse)** |
| concurrent_causes | 69 | 69/69 (69/69) | 69/69 (69/69) | 16/69 (69/69) | 69/69 (69/69) | 69/69 (69/69) | = |
| **late_alerting_cause** | 69 | 65/69 (68/69) | 45/69 (68/69) | 69/69 (69/69) | 3/69 (13/69) | 0/69 (0/69) | +20 (better) |
| **long_seasonal** | 69 | 57/69 (69/69) | 69/69 (69/69) | 43/69 (69/69) | 40/69 (69/69) | 27/69 (27/69) | **-12 (worse)** |
| missing_telemetry | 69 | 69/69 (69/69) | 68/69 (69/69) | 69/69 (69/69) | 68/69 (69/69) | 68/69 (69/69) | +1 (better) |
| noisy_alerts | 69 | 66/69 (67/69) | 61/69 (69/69) | 69/69 (69/69) | 15/69 (57/69) | 0/69 (0/69) | +5 (better) |
| partial_graph | 69 | 66/69 (67/69) | 60/69 (69/69) | 69/69 (69/69) | 68/69 (69/69) | 0/69 (0/69) | +6 (better) |
| **red_herring_deploy** | 69 | 69/69 (69/69) | 68/69 (69/69) | 14/69 (69/69) | 68/69 (69/69) | 0/69 (0/69) | +1 (better) |
| red_herring_hard | 69 | 69/69 (69/69) | 68/69 (69/69) | 14/69 (69/69) | 68/69 (69/69) | 69/69 (69/69) | +1 (better) |
| shared_dependency | 69 | 67/69 (68/69) | 63/69 (69/69) | 69/69 (69/69) | 68/69 (69/69) | 0/69 (0/69) | +4 (better) |
| **silent_cause** | 69 | 24/69 (65/69) | 1/69 (59/69) | 66/69 (69/69) | 0/69 (0/69) | 0/69 (0/69) | +23 (better) |
| unordered_plausible_alerts | 60 | 57/60 (58/60) | 55/60 (60/60) | 60/60 (60/60) | 15/60 (45/60) | 0/60 (0/60) | +2 (better) |
| **Total** | **948** | **868/948 (930/948)** | **811/948 (937/948)** | **756/948 (948/948)** | **618/948 (776/948)** | **361/948 (361/948)** | **+57** |

### Highlights and Key Observations

1. **`silent_cause` remains a known failure:** Although V3 improves markedly over V0 (24/69 vs 1/69 top-1), it still misses 45 out of 69 cases (65.2% miss rate at top-1). The graph random-walk method alone (`graph_rwr`) achieves 66/69 top-1, but when fused with other methods lacking signal, its candidate is diluted.
2. **`late_alerting_cause` demonstrates fusion advantage:** V3 scores 65/69 top-1 (94.2%) vs V0's 45/69 (65.2%) and `alert_order`'s 3/69 (4.3%). Causal metrics correctly identify the root cause before alerts trigger.
3. **`red_herring_deploy` demonstrates multi-modal robustness:** V3 achieves 69/69 top-1 (100.0%) and top-3, resisting the decoy deployment. By contrast, topological `graph_rwr` alone drops to 14/69 (20.3%) because it lacks change-event awareness.
4. **Families where V3 is worse than V0:**
   - **`long_seasonal`:** V3 drops from 69/69 to 57/69 (-12 top-1 hits). Unresolved diurnal cycle variations lead some methods to output high but misleading score margins, which V3 amplifies over equal-weight fusion.
   - **`coincident_restart`:** V3 drops from 67/69 to 65/69 (-2 top-1 hits). Non-causal restarts occasionally receive high change-based confidence scores.

---

## 2. Results by Seed Block and Family

### Development Block (Seeds 1–51, n=388; includes seeds 7–9)

| Family | n | V3 top-1/top-3 | V0 top-1/top-3 | graph_rwr top-1/top-3 | alert_order top-1/top-3 | latest_change top-1/top-3 |
|---|---:|---:|---:|---:|---:|---:|
| cause_alerts_2_4 | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 0/20 (14/20) | 0/20 (0/20) |
| clean_bad_deploy | 29 | 29/29 (29/29) | 28/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 28/29 (28/29) |
| coincident_restart | 29 | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 28/29 (28/29) |
| concurrent_causes | 29 | 29/29 (29/29) | 29/29 (29/29) | 8/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| late_alerting_cause | 29 | 28/29 (29/29) | 20/29 (29/29) | 29/29 (29/29) | 0/29 (4/29) | 0/29 (0/29) |
| long_seasonal | 29 | 23/29 (29/29) | 29/29 (29/29) | 17/29 (29/29) | 17/29 (29/29) | 7/29 (7/29) |
| missing_telemetry | 29 | 29/29 (29/29) | 28/29 (29/29) | 29/29 (29/29) | 28/29 (29/29) | 28/29 (28/29) |
| noisy_alerts | 29 | 29/29 (29/29) | 26/29 (29/29) | 29/29 (29/29) | 8/29 (25/29) | 0/29 (0/29) |
| partial_graph | 29 | 29/29 (29/29) | 25/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 0/29 (0/29) |
| red_herring_deploy | 29 | 29/29 (29/29) | 28/29 (29/29) | 10/29 (29/29) | 29/29 (29/29) | 0/29 (0/29) |
| red_herring_hard | 29 | 29/29 (29/29) | 28/29 (29/29) | 10/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) |
| shared_dependency | 29 | 29/29 (29/29) | 27/29 (29/29) | 29/29 (29/29) | 29/29 (29/29) | 0/29 (0/29) |
| silent_cause | 29 | 11/29 (29/29) | 0/29 (27/29) | 28/29 (29/29) | 0/29 (0/29) | 0/29 (0/29) |
| unordered_plausible_alerts | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 5/20 (15/20) | 0/20 (0/20) |
| **Total** | **388** | **363/388 (388/388)** | **337/388 (386/388)** | **316/388 (388/388)** | **261/388 (319/388)** | **149/388 (149/388)** |

### Confirmation Block (Seeds 52–71, n=280)

| Family | n | V3 top-1/top-3 | V0 top-1/top-3 | graph_rwr top-1/top-3 | alert_order top-1/top-3 | latest_change top-1/top-3 |
|---|---:|---:|---:|---:|---:|---:|
| cause_alerts_2_4 | 20 | 18/20 (18/20) | 16/20 (20/20) | 20/20 (20/20) | 0/20 (13/20) | 0/20 (0/20) |
| clean_bad_deploy | 20 | 19/20 (19/20) | 17/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 18/20 (18/20) |
| coincident_restart | 20 | 18/20 (18/20) | 19/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 18/20 (18/20) |
| concurrent_causes | 20 | 20/20 (20/20) | 20/20 (20/20) | 6/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| late_alerting_cause | 20 | 18/20 (19/20) | 11/20 (20/20) | 20/20 (20/20) | 0/20 (4/20) | 0/20 (0/20) |
| long_seasonal | 20 | 19/20 (20/20) | 20/20 (20/20) | 13/20 (20/20) | 13/20 (20/20) | 13/20 (13/20) |
| missing_telemetry | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| noisy_alerts | 20 | 18/20 (18/20) | 16/20 (20/20) | 20/20 (20/20) | 3/20 (17/20) | 0/20 (0/20) |
| partial_graph | 20 | 18/20 (18/20) | 16/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 0/20 (0/20) |
| red_herring_deploy | 20 | 20/20 (20/20) | 20/20 (20/20) | 2/20 (20/20) | 20/20 (20/20) | 0/20 (0/20) |
| red_herring_hard | 20 | 20/20 (20/20) | 20/20 (20/20) | 2/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| shared_dependency | 20 | 19/20 (19/20) | 17/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 0/20 (0/20) |
| silent_cause | 20 | 6/20 (17/20) | 1/20 (16/20) | 19/20 (20/20) | 0/20 (0/20) | 0/20 (0/20) |
| unordered_plausible_alerts | 20 | 18/20 (18/20) | 16/20 (20/20) | 20/20 (20/20) | 5/20 (15/20) | 0/20 (0/20) |
| **Total** | **280** | **251/280 (264/280)** | **229/280 (276/280)** | **222/280 (280/280)** | **181/280 (229/280)** | **109/280 (109/280)** |

### Calibration Block (Seeds 72–91, n=280)

| Family | n | V3 top-1/top-3 | V0 top-1/top-3 | graph_rwr top-1/top-3 | alert_order top-1/top-3 | latest_change top-1/top-3 |
|---|---:|---:|---:|---:|---:|---:|
| cause_alerts_2_4 | 20 | 19/20 (20/20) | 19/20 (20/20) | 20/20 (20/20) | 0/20 (13/20) | 0/20 (0/20) |
| clean_bad_deploy | 20 | 20/20 (20/20) | 17/20 (20/20) | 20/20 (20/20) | 19/20 (20/20) | 18/20 (18/20) |
| coincident_restart | 20 | 18/20 (19/20) | 19/20 (20/20) | 20/20 (20/20) | 19/20 (20/20) | 18/20 (18/20) |
| concurrent_causes | 20 | 20/20 (20/20) | 20/20 (20/20) | 2/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| late_alerting_cause | 20 | 19/20 (20/20) | 14/20 (19/20) | 20/20 (20/20) | 3/20 (5/20) | 0/20 (0/20) |
| long_seasonal | 20 | 15/20 (20/20) | 20/20 (20/20) | 13/20 (20/20) | 10/20 (20/20) | 7/20 (7/20) |
| missing_telemetry | 20 | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) | 20/20 (20/20) |
| noisy_alerts | 20 | 19/20 (20/20) | 19/20 (20/20) | 20/20 (20/20) | 4/20 (15/20) | 0/20 (0/20) |
| partial_graph | 20 | 19/20 (20/20) | 19/20 (20/20) | 20/20 (20/20) | 19/20 (20/20) | 0/20 (0/20) |
| red_herring_deploy | 20 | 20/20 (20/20) | 20/20 (20/20) | 2/20 (20/20) | 19/20 (20/20) | 0/20 (0/20) |
| red_herring_hard | 20 | 20/20 (20/20) | 20/20 (20/20) | 2/20 (20/20) | 19/20 (20/20) | 20/20 (20/20) |
| shared_dependency | 20 | 19/20 (20/20) | 19/20 (20/20) | 20/20 (20/20) | 19/20 (20/20) | 0/20 (0/20) |
| silent_cause | 20 | 7/20 (19/20) | 0/20 (16/20) | 19/20 (20/20) | 0/20 (0/20) | 0/20 (0/20) |
| unordered_plausible_alerts | 20 | 19/20 (20/20) | 19/20 (20/20) | 20/20 (20/20) | 5/20 (15/20) | 0/20 (0/20) |
| **Total** | **280** | **254/280 (278/280)** | **245/280 (275/280)** | **218/280 (280/280)** | **176/280 (228/280)** | **103/280 (103/280)** |

---

## 3. Family-Mix Caveat (Ensemble vs `alert_order`)

Across all 948 cases, the ensemble achieves 868 top-1 hits (91.6%) versus `alert_order`'s 618 (65.2%), an aggregate difference of +250 cases (+26.4 percentage points).

However, **this aggregate advantage is entirely dependent on scenario family mix**:
- On the 7 families where alerts fire predictably without deliberate corruption or delay (`clean_bad_deploy`, `coincident_restart`, `missing_telemetry`, `partial_graph`, `red_herring_deploy`, `red_herring_hard`, `shared_dependency`), `alert_order` achieves **476/483 top-1 hits (98.6%)**, essentially matching the ensemble's **477/483 (98.8%)**.
- The ensemble's entire net lead arises from families with designed alert failure modes:
  - `late_alerting_cause` (+62 cases: 65 vs 3)
  - `cause_alerts_2_4` (+57 cases: 57 vs 0)
  - `noisy_alerts` (+51 cases: 66 vs 15)
  - `unordered_plausible_alerts` (+42 cases: 57 vs 15)
  - `silent_cause` (+24 cases: 24 vs 0)

In an environment where alert routing is pristine and early, a simple first-alert heuristic performs almost as well as a full multi-modal pipeline on top-1 cause identification. Inquest's value lies specifically in its resilience against missing, delayed, unordered, or noisy alerts.
