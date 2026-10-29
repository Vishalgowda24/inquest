# Project Status: Inquest Prototype & Interactive Demo (P12)

## P12: Demo Build Status

| Part | Description | Status | Commit Hash |
|---|---|---|---|
| Part 1 | API & Demo Cache (FastAPI, 8 precomputed cases, security, rate limit, reveal) | done | [pending] |
| Part 2 | Frontend (Hero with --u scaling, brand copy, /demo, /results, /limitations) | in progress | - |
| Part 3 | Tests (API tests, security, Playwright E2E, smoke & load test) | not started | - |
| Part 4 | Docker & Deploy (multi-stage Dockerfile, docker-compose, CI, deploy configs) | not started | - |
| Part 5 | Final Documentation, Verification & Tag (v1.1-demo) | not started | - |

---

## Assumptions (P12)

1. **Architecture & Truth Boundary:** Demo API is implemented in `demo/api.py` and static frontend in `demo/static/` to strictly protect the `inquest/` package from any simulator imports, paths, or truth leakage. The `POST /api/reveal/{run_id}` route is the single isolated path that reads ground truth data for validation.
2. **Precomputed Demo Cache:** 8 canonical demo cases (`clean_bad_deploy`, `coincident_restart`, `red_herring_deploy`, `shared_dependency`, `missing_telemetry` seed 73, `late_alerting_cause`, `silent_cause` seed 72 top-1 wrong miss, `concurrent_causes`) are precomputed in `demo/cache/precomputed.json` for immediate (<10ms) responses in the interactive demo. Live runs dynamically execute the S00–S05 pipeline within a 60s timeout and a concurrency limit of 2.
3. **Fonts & Assets:** Self-hosted OFL DM Sans and Inter Latin subset font files are placed in `demo/static/fonts/` with SIL Open Font License (OFL 1.1) accompanied by clean system font fallbacks. Hero artwork loop (MP4) and still poster (WebP) total 1.24 MB and are committed to `demo/static/assets/`, with remote URLs and CSS gradient fallbacks.
4. **Security Defaults:** CORS is disabled. CSP allows only `'self'` and the media host (`https://d2ol7oe51mr4n9.cloudfront.net`). In-memory sliding-window IP rate limiting returns 429 after 120 req/min (configurable for tests). Request payload limit is 1 MB (returns 413). Optional HTTP Basic Auth is supported via `DEMO_BASIC_AUTH_USERNAME` and `DEMO_BASIC_AUTH_PASSWORD`.

---

## P11 Prototype Checkpoint Status (v1.0-prototype)

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
