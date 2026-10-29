# Project Status: Inquest Prototype & Interactive Demo (P12)

## P12: Demo Build Status

| Part | Description | Status | Commit Hash |
|---|---|---|---|
| Part 1 | API & Demo Cache (FastAPI, 8 precomputed cases, security, rate limit, reveal) | done | `7ba7a44` |
| Part 2 | Frontend (Hero with --u scaling, brand copy, /demo, /results, /limitations) | done | `19701c6` |
| Part 3 | Tests (API tests, security, Playwright E2E, smoke & load test) | done | `9884394` |
| Part 4 | Docker & Deploy (multi-stage Dockerfile, docker-compose, CI, deploy configs) | done | `26319cc` |
| Part 5 | Final Documentation, Verification & Tag (v1.1-demo) | done | [pending] |

---

## Test Suite Execution Summary

- **Total Test Cases:** 105 passed, 0 failed.
  - **Existing Simulator & Pipeline Suite:** 84 passed (`simulator/tests/`, `inquest/tests/`).
  - **API, Security & Load Suite (`tests_api/test_api.py`):** 16 passed (health, families, stats sync, results/limitations, allow-list rejection, seed range rejection, path-traversal & injection prevention, 1MB body limit, 429 rate limit with Retry-After, security headers & strict CSP, HTTP basic auth protection, reveal only after run, cached vs live ranking consistency, 60s timeout handling, wording lint, 20 concurrent request load test).
  - **Playwright E2E Acceptance Suite (`tests_api/test_playwright.py`):** 5 passed (1440×900 desktop hero acceptance check by bounding boxes, 390×844 mobile responsive reflow with working menu button, prefers-reduced-motion still fallback and animation disablement, interactive demo flow end-to-end including Reveal, keyboard tab navigation and WCAG contrast check).
- **Diagnostics (`inquest doctor`):** All checks OK (plugin registry, adapter registry, candidate methods, verification methods, configuration, filesystem paths, smoke stage, vault chain integrity across 3 checked vaults).

---

## Visual Demo Screenshots

All visual verification screenshots have been saved to `docs/screenshots/`:
1. `docs/screenshots/hero_desktop_1440x900.png` — Desktop hero canvas at 1440×900 with bounding box verification.
2. `docs/screenshots/hero_mobile_390x844.png` — Mobile single-column reflow at 390×844 with dropdown navigation.
3. `docs/screenshots/hero_reduced_motion.png` — Static poster fallback under `prefers-reduced-motion: reduce`.
4. `docs/screenshots/demo_flow_reveal.png` — Interactive investigation runner output with ground truth reveal match.

---

## Assumptions & Architectural Decisions

1. **Architecture & Truth Boundary:** Demo API is implemented in `demo/api.py` and static frontend in `demo/static/` to strictly protect the `inquest/` package from any simulator imports, paths, or truth leakage. The `POST /api/reveal/{run_id}` route is the single isolated path that reads ground truth data for validation.
2. **Precomputed Demo Cache:** 8 canonical demo cases (`clean_bad_deploy`, `coincident_restart`, `red_herring_deploy`, `shared_dependency`, `missing_telemetry` seed 73, `late_alerting_cause`, `silent_cause` seed 72 top-1 wrong miss, `concurrent_causes`) are precomputed in `demo/cache/precomputed.json` for immediate (<10ms) responses in the interactive demo. Live runs dynamically execute the S00–S05 pipeline within a 60s timeout and a concurrency limit of 2.
3. **Fonts & Assets:** Self-hosted OFL DM Sans and Inter Latin subset font files are placed in `demo/static/fonts/` with SIL Open Font License (OFL 1.1) accompanied by clean system font fallbacks. Hero artwork loop (MP4) and still poster (WebP) total 1.24 MB and are committed to `demo/static/assets/`, with remote URLs and CSS gradient fallbacks.
4. **Security Defaults:** CORS is disabled. CSP allows only `'self'` and the media host (`https://d2ol7oe51mr4n9.cloudfront.net`). In-memory sliding-window IP rate limiting returns 429 after 120 req/min (configurable for tests). Request payload limit is 1 MB (returns 413). Optional HTTP Basic Auth is supported via `DEMO_BASIC_AUTH_USERNAME` and `DEMO_BASIC_AUTH_PASSWORD`.
5. **Docker Availability on Host:** The host operating system (Windows) does not have the `docker` binary or Docker Desktop daemon installed. Local container smoke testing was therefore skipped, and complete deployment configurations (`Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `render.yaml`, `fly.toml`, `docs/DEPLOY.md`) were generated and verified.

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
- **Interactive Web Demo Application & Static UI (P12):**
  - Standalone FastAPI server with strict security, rate limiting, and truth isolation.
  - Strata AI landing hero with `--u` unit scaling (2048×1455 design canvas), Web Animations API entrance sequence, glass data cards, and responsive single-column mobile reflow.
  - Interactive `/demo` runner with 8 precomputed canonical cases, live execution, top-3 candidates table, evidence timeline, unknowns, and ground truth reveal.
  - Benchmark results page (`/results`) and limitations page (`/limitations`) with synthetic data disclaimers.
- **Automated Deploy Configurations:**
  - Multi-stage Dockerfile with non-root user and healthcheck.
  - GitHub Actions CI workflow running lint, doctor, test suite, and container image build.
  - Ready-to-use Render and Fly.io configurations.

---

## 2. What Is Not Built

- **Real-Data Benchmark Evaluation:** `data/real/` is absent from the repository; Inquest has **not been evaluated on real incident data**. No synthetic or simulated real data was fabricated.
- **Real-Time Streaming Ingestion:** Currently operates as an offline or post-incident batch pipeline; streaming message queues (Kafka, Kinesis) are not supported.
- **Automated Graph Topology Recovery:** The pipeline expects a declared or inferred dependency graph; dynamic topology discovery from uninstrumented network traffic is not implemented.
- **S04 Re-Ranking:** S04 verification heuristics are annotation-only due to low recall (15.4% in P7) and vulnerability to shared-ancestry decoys; automated candidate re-ranking by verification checks is not enabled.
- **Operationally Calibrated Probabilities:** Parametric logistic regression clustered all probabilities in `[0.9, 1.0]`, failing to provide reliable uncertainty estimates.
