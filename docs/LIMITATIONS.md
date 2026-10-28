# Limitations and pre-real-data risks

## What was tested

All evidence is synthetic. The simulator covers 12 scenario families and uses three seeds per family in each evaluated seed block. P6 used seeds 7–9: 36 cases total. `concurrent_causes` has two injected causes in each of its three cases, so the holdout contains **39 cause labels**, not 38. This corrects the arithmetic in the P6 Part A note: 36 cases plus three additional second-cause labels equals 39. The same correction applies to P5's 36 cases on seeds 4–6. Earlier reports' `2/38` verified-recall denominator is therefore a bookkeeping error; the numerator remains two, and the corrected denominator is 39.

The P6 holdout is a fresh-seed evaluation of already-known scenario families, not a holdout of unseen scenario designs. It was run once. The complete per-case table is in `eval/p6_holdout_results.md`, with machine-readable case results in `eval/p6_holdout_cases.json` and artifacts under `runs/p6_holdout_equal_rrf/`.

On seeds 1–3 in the eight development families, the ensemble had 21/24 top-1 and 24/24 top-3 case hits; `alert_order` had 16/24 and 18/24. On seeds 4–6 across 12 families under the equal-weight configuration, the ensemble had 32/36 and 36/36, while `alert_order` had 27/36 and 30/36. On P6 seeds 7–9, the ensemble had 24/36 and 36/36; `alert_order` had 27/36 and 31/36. Thus P6 ensemble top-1 was materially below the prior seed blocks, while top-3 remained complete. On this holdout, the ensemble did **not** beat `alert_order` at top-1 (24 vs 27 cases); it did beat it at top-3 (36 vs 31). These small seed blocks do not establish production accuracy.

S04 remained annotation-only and exactly preserved the S03 order. Four of 39 true-cause labels were marked `verified`; no wrong candidate was marked `verified` in this holdout. This low coverage does not make `verified` a dependable positive confirmation. `concurrent_causes` had all three cases with both true causes in the ensemble's top three; no case had only one or neither in that top-three set.

## Known failures and baseline behavior

- `silent_cause` remains a top-1 miss for all three P6 seeds; its true cause was ranked second or third. Methods without an event or trace signal can still contribute no useful candidate, and equal-weight rank fusion can bury the graph method's signal.
- Thin telemetry leaves S04 with many `insufficient_evidence` outcomes; a shared path can look plausible without establishing causality.
- `long_seasonal` can still challenge ranking and seasonal normalization. The P6 ensemble recovered all three top-1 cases here, but previous seed blocks had misses, so this is not a resolved general case.
- `alert_order` is a strong synthetic baseline. It matched the ensemble's top-1 in multiple families and beat it overall on the P6 holdout by three cases. Its advantage can depend on simulator alert timing and should not be mistaken for general causal evidence.

## Reproduction and retained artifacts

The P6 table can be regenerated from the frozen case record without running any method again:

```powershell
$env:PYTHONPATH = (Resolve-Path work/python-packages).Path
$py = 'C:\Users\LOQ\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py eval/render_saved_p6.py
```

The one-time holdout runner is `eval/run_p6_holdout.py`; it refuses to run if its output/report already exists. **Do not use it to repeat P6.** Each frozen configuration's artifacts are under its own `runs/` subdirectory. Historical tables remain in `eval/p2_results.md`, `eval/p3b_results.md`, `eval/p4_results.md`, and `eval/p5_results.md`.

There is not currently a single end-to-end command that regenerates every historical P2–P5 table from seeds: P2–P4 retain evaluator scripts, but P5's evaluator helpers were kept under ignored `work/`, and the historical per-case intermediate records were not all retained in tracked `eval/` files. The committed Markdown reports are the record for those phases. Recreating all those tables from scratch would require restoring and validating the missing P5 evaluator and isolated output roots; this was not attempted after the P6 holdout. P6 itself is reproducible as a report from its saved case JSON, while the holdout analysis remains single-run.

## Top three risks before real incident data

1. **Synthetic-to-real shift.** The simulator's service topology, fault mechanics, telemetry quality, and alert behavior may not match an organization's systems.
2. **Incomplete or misleading evidence.** Missing traces, metric gaps, clock skew, and shared dependencies can suppress a true cause or make decoys look causal; S04's low verified coverage shows this directly.
3. **Ranking and alert-process bias.** The ensemble misses silent causes at top-1, and the synthetic alert-order baseline is strong. Real alert routing, suppression, and collection delays could change both rankings and apparent baseline performance.

## P9 frozen fusion results

The entire evidence base is synthetic. P9's 388-case development set covers all currently generated scenarios for seeds 1–51 across 14 families; family sample sizes vary (20 or 29 cases), and P4–P7 fresh and P6 holdout blocks are nested within that development set. P9 added one balanced 20-seed confirmation block (280 cases). These results do not establish real-incident performance.

The advantage of rank fusion depends on scenario mix. In P7, equal-weight RRF's overall +0.133 paired top-1 difference over `alert_order` came from a +0.600 difference on late-alerting, noisy-alert, and long-seasonal families combined with −0.022 on the other nine. Under the preregistered P9 family-equal development rule, V3 was selected (0.9384 vs V0 0.8744). In the one confirmation block, V3 exceeded V0 by 0.079 top-1/case (two-way family×seed cluster-bootstrap 95% interval [+0.004, +0.175]) and exceeded `alert_order` by 0.250 (interval [+0.050, +0.471]). This is one synthetic confirmation block, not independent real-world validation.

`silent_cause` remains a weakness: V3 found the cause top-1 in 11/29 development cases and 6/20 confirmation cases, so it still missed most confirmation cases. V0 found it top-1 in 1/20 confirmation cases. The P7 S04 true-cause `verified` count was only 40/260; treat `verified` as a low-recall annotation, not as a reliable positive confirmation.

The simulator's alert process favors early cause alerts in several families. In P6 noisy-alert seeds the true-cause alert preceded fault onset in 3/3 cases; in P7 it did so in 12/20. `alert_order` is consequently a strong baseline in many families, while it fails by design on silent and late causes. These timing assumptions are simulator properties and may not reflect operational alert routing or delivery.

## P10 S05 confidence report

S05 is deterministic and reads only saved S00–S04 outputs plus the verified vault. Its logistic confidence model was fitted on synthetic seeds 1–51 and was evaluated once on fresh seeds 72–91 (280 cases); seeds 52–71 (280 cases) are a secondary check. Holdout seeds 7–9 were not rerun. The complete per-family and per-confidence-level tables are in `eval/p10_evaluation_results_final.md`.

On fresh seeds 72–91, top-1 accuracy was 254/280 (90.7%). Calibrated Brier was 0.0831 versus 0.0850 for both the constant and margin-only baselines, but calibrated ECE was 0.0289 versus 0.0284 for both baselines. This is mixed and small; it does not establish reliable calibration. All probabilities landed in the 0.9–1.0 bin, and the model produced no medium or low confidence cases. It marked 95/280 (33.9%) as `insufficient_evidence`; 17 cases (6.1%) were high-confidence wrong. In `silent_cause`, 9/16 high-confidence reports were wrong and mean confidence was 0.924 against 35% top-1 accuracy. `late_alerting_cause` also had one high-confidence miss. The red-herring family had no misses in this block.

Withholding low and insufficient-evidence cases retained 185/280 (66.1%) at 90.8% accuracy, only 0.1 percentage point above the 90.7% unfiltered accuracy. This is not a meaningful demonstrated selective-accuracy gain. The report's confidence labels and probabilities remain synthetic-only and should not be used as operationally calibrated probabilities.
