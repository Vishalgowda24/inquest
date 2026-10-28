# Project Status: Inquest Prototype (v1.0-prototype)

## Final Checkpoint Status

| Part | Description | Status | Commit Hash |
|---|---|---|---|
| Part A | Confidence Cleanup & Rule-Based Flags | done | `06bfd06` |
| Part B | S04 Decision & Experimental Status | done | `751eadf` |
| Part C | Problem-Family Performance Tables | done | `7b86d31` |
| Part D | Real-Data Adapter & Verification | done | `62c6924` |
| Part E | Finalization, README, Limitations & Tag | done | `53ffc7d` |

---

## 1. What Is Built

- **Deterministic End-to-End Diagnostic Pipeline (S00–S05):**
  - **S00 Ingest:** Adapter-based ingestion for canonical simulator JSON, mapped CSV, and real-incident directory structures.
  - **S01 Vault:** Cryptographically sealed append-only SHA-256 evidence chain (`vault/chain.jsonl`), guaranteeing tamper detection.
  - **S02 Signals:** Biweight/MAD robust onset detection, service ordering, and missing window coverage analysis with seasonal detrending.
  - **S03 Candidates:** Four independent localization methods (`change_based`, `graph_rwr`, `trace_ochiai`, `temporal_lag`) with evidence-filtered V3 score-margin weighted reciprocal-rank fusion.
  - **S04 Verification:** Vault integrity verification gate (`vault_evidence`) and contradiction heuristics (`dependency_path`, `temporal_consistency`, `recovery_check`, `alternative_check`). S04 re-ranking remains disabled (`verification_rerank: false`), preserving S03 candidate order.
  - **S05 Report:** Fully deterministic JSON (`report.json`) and Markdown (`report.md`) generation with evidence-cited claims, candidate rankings, event timelines, runner-up findings, unknowns, and next check recommendations.
- **Rule-Based Assessment Flag System (Part A):**
  - Removed misleading numeric probabilities from headlines and default JSON output.
  - Replaced with rule-based flags (`standard`, `review_recommended`, `insufficient_evidence`):
    - `standard`: 100.0% top-1 accuracy (47/47 cases) on seeds 72–91.
    - `review_recommended`: Catches 100% of non-telemetry wrong answers (17/17 misses, including all 9 `silent_cause` misses).
    - `insufficient_evidence`: Correctly identifies 100% of top-candidate telemetry gaps (7/7 in `missing_telemetry`).
  - Combined non-standard flags capture 26/26 (100%) of all benchmark misses; zero wrong answers receive `standard`.
  - The parametric calibrated logistic model remains in the repository behind `unvalidated_calibrated_confidence` (default `false`).
- **Real-Data Ingestion Adapter (Part D):**
  - Defined self-contained directory schema in `docs/REAL_DATA.md` for metrics (CSV/JSON), operational events, alerts, dependency graphs, optional traces, and offline `labels.json`.
  - Implemented `inquest ingest-real <dir>` CLI command and `RealIncidentAdapter` with schema validation, clear error messages, and automatic conversion into the vault.
  - Strict isolation: real data never touches `sim_truth/`, and `labels.json` is never read by diagnostic stages.
  - Comprehensive unit and CLI integration tests covering converted examples, malformed records, and missing required files.
- **Reproducible Evaluation Infrastructure:**
  - Evaluated on 948 synthetic cases across 14 scenario families (Development seeds 1–51: n=388, Confirmation seeds 52–71: n=280, Calibration seeds 72–91: n=280).
  - Single-command reproduction script: `python eval/reproduce_all_results.py`.
  - Complete benchmark results recorded in `docs/RESULTS.md` and detailed boundaries documented in `docs/LIMITATIONS.md`.

---

## 2. What Is Not Built

- **Real-Data Benchmark Evaluation:** `data/real/` is absent from the repository; Inquest has **not been evaluated on real incident data**. No synthetic or simulated real data was fabricated.
- **Real-Time Streaming Ingestion:** Currently operates as an offline or post-incident batch pipeline; streaming message queues (Kafka, Kinesis) are not supported.
- **Automated Graph Topology Recovery:** The pipeline expects a declared or inferred dependency graph; dynamic topology discovery from uninstrumented network traffic is not implemented.
- **S04 Re-Ranking:** S04 verification heuristics are annotation-only due to low recall (15.4% in P7) and vulnerability to shared-ancestry decoys; automated candidate re-ranking by verification checks is not enabled.
- **Operationally Calibrated Probabilities:** Parametric logistic regression clustered all probabilities in `[0.9, 1.0]`, failing to provide reliable uncertainty estimates.

---

## 3. Ranked Next Steps

1. **Ingest and Benchmark on Genuine Production Incidents:**
   Gather real post-mortem incident bundles formatted per `docs/REAL_DATA.md` into `data/real/` and benchmark the V3 ensemble against production baseline heuristics.
2. **Resolve the `silent_cause` Bottleneck:**
   `silent_cause` remains the primary top-1 failure mode (only 34.8% top-1 accuracy across 948 cases). Develop specialized silent-failure signals—such as downstream client traffic divergence, missing heartbeat tracking, and synthetic canary probes—to break reliance on alert/change signals.
3. **Refine Seasonal Detrending for Sparse Series:**
   Fix the V3 margin regression on `long_seasonal` (-12 cases vs V0) by improving diurnal baseline estimation when fewer than two complete 24-hour cycles exist.
4. **Develop High-Recall Causal Verification Checks:**
   Re-engineer S04 checks to handle shared-ancestry topologies and increase verified recall beyond 15.4% before considering automated candidate re-ranking.
