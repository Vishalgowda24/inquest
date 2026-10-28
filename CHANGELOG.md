# Changelog

## P3b S04 evaluation and status hardening

- Added per-check lowercase verdict/effect-size findings, candidate statuses, provenance-preserving S03 rank/score fields, and optional verification-based reranking (default off).
- Added recovery and competing-explanation checks; made missing service telemetry inconclusive and kept vault integrity separate from causal support.
- Added `eval/run_p3b.py` and the full per-case, status, re-ranking, ablation, and decision report at `eval/p3b_results.md`. A first run exposed three bugs; fixes and rationale are recorded in `DECISIONS.md`, with its preliminary tables retained separately.
- Final gate: 58 pytest tests passed and `inquest doctor` passed. No holdout or P4 work.

## P3 S04 verification

- Added independently toggleable vault-evidence, dependency-path, and temporal-consistency verification methods, with retained per-method findings, majority decisions, confidence, disagreement, and vault-backed evidence IDs.
- Added S03 verification context, CLI/doctor registration, config switches, and integration checks including reversed dependency-edge traversal.
- Final setup gate: 51 pytest tests passed; `inquest doctor` passed. No holdout evaluation or P4 work.

## P3 hardening on P2 (2026-10-28)

- Diagnosed trace Ochiai's 0/18 top-1 and clean seed's 0/3 top-3 as an unsorted candidate-list bug: checkout appeared first from manifest order despite a lower score. Recorded the root cause before fixing the order; added a minimal hand-built trace regression test.
- Added `late_alerting_cause` and `silent_cause`, each across seeds 1–3, with opaque IDs and truth artifacts isolated in `simulator/sim_truth/`.
- Added an AST/source/fixture leakage contract that blocks simulator imports, truth paths/labels, and truth-field access under the entire Inquest tree.
- Added ensemble true-rank and top-score margin per case, seed counts, and one-case ensemble lead flags to the non-holdout evaluation report.
- Full setup gate passed 48 pytest tests and `inquest doctor`; expanded evaluation covers eight scenarios x three seeds. No holdout run or S03 score tuning was done.

## P2 — scenario coverage and candidate methods (2026-10-28)

- Added five deterministic parameterized scenario variants (three seeds each): restart recovery, red-herring deployment, shared dependency saturation, missing telemetry, and a 72-hour seasonal case. Added a reserved holdout area excluded from registries/default evaluation.
- Extended simulator CLI to generate each registered scenario with opaque salted IDs and truth kept only under `simulator/sim_truth/`.
- Added timestamp-phase seasonal normalization only when two daily cycles and sufficient phase coverage are present.
- Added S03 change proximity/relevance, onset-seeded graph RWR, trace Ochiai, and dependency-restricted lag correlation methods, each individually configurable, plus reciprocal-rank ensemble and disagreement indicator.
- Added contracts/tests for vault-backed candidate evidence, independent method modules, toggles, missing traces, long seasonal coverage, and scenario semantics.
- Added a default evaluation over six non-holdout scenarios x three seeds, including per-scenario top-1/top-3 tables, method baselines, and per-case predictions in `eval/p2_results.md`.
- P2 verification before hardening: 43 pytest tests passed; current total after P3 hardening is 48.

## P1 — S00 ingest, S01 vault, S02 signals (2026-10-28)

- Closed P0 fault-injection, opaque salted-ID/export-leakage, pinned dependency, setup, and doctor requirements.
- Added canonical Pydantic contracts, adapter protocol/registry, simulator canonical JSON adapter, and YAML-mapped generic CSV adapter.
- Added schema validation with file/row context, bad-row quarantine and counts, unknown-reference, source-clock, and coverage warnings; exposed dry-run `validate` and full `ingest` CLI commands.
- Added append-only canonical evidence JSONL with a deterministic SHA-256 chain and item-specific tamper verification. `inquest doctor` now checks each existing chain.
- Added median/MAD signal baselines, optional complete-cycle seasonal normalization, a unified ruptures/CUSUM detector interface, onset confidence/order, uncertainty propagation, and explicit coverage-gap records.
- Added unit/integration/golden tests, three-seed propagation-order checks, vault tamper tests, and CLI dry-run checks.
- `./setup.ps1` passed: 23 pytest tests passed and `inquest doctor` reported config/paths/registries/smoke/vault integrity OK. Python 3.12.14 was used because Python 3.11 and working `ensurepip` were unavailable; the setup used exact pinned workspace packages because PyPI could not be reached.

## P0 — simulator and resilient pipeline skeleton (2026-10-28)

- Added a deterministic four-service simulator, telemetry contracts and exports, separated truth artifacts, typed Inquest contracts, stage runner, artifacts, structured logs, and diagnostic commands.
- Added fault propagation, seasonality, seeded jitter, source clock skew, dropped windows, opaque scenario IDs, and P0 resilience checks.
