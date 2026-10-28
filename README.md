# Inquest

Inquest is an evidence-driven incident investigation pipeline with an isolated synthetic telemetry simulator. P0 established the simulator and failure-resilient stage runner. P1 adds S00 ingestion, S01 append-only evidence vault, and S02 robust signal onset analysis. P2 adds scenario variants and S03 candidate methods with an ensemble.

## Environment

Python 3.11 or 3.12 is supported. Exact dependency versions are pinned in `requirements.txt`. On Windows, run `./setup.ps1` to check dependencies, run pytest, and run `inquest doctor`. The setup uses the workspace package cache when its exact pinned versions are present; otherwise it installs pinned requirements into that cache. In the supplied environment Python 3.11 is absent, Python 3.12.14 is used, and network access is unavailable, so setup reuses the packages already provisioned in `work/python-packages`.

## Commands

```powershell
./setup.ps1
python -m simulator.cli list
python -m simulator.cli run --scenario clean_bad_deploy --seed 1
python -m simulator.cli run --scenario red_herring_deploy --seed 1
python -m inquest.cli doctor
python -m inquest.cli validate simulator/exports/<scn_id>/seed_1/export
python -m inquest.cli ingest simulator/exports/<scn_id>/seed_1/export
python -m inquest.cli explain --run <run_id>
python -m inquest.cli rerun --run <run_id> --stage s03_candidates
python eval/run_p2.py
python -m pytest --basetemp work/pytest-run-temp
```

`validate` is a dry run and writes no run or vault files. `ingest` accepts a simulator canonical JSON export or a mapped CSV file/folder and runs S00–S03. CSV column names are declared in `config/csv_mapping.yaml`. Per-stage artifacts and the final report are saved under `runs/<run_id>/`; malformed rows are saved in `quarantine/rejected.jsonl` with file and record indexes. Candidate methods are independently toggleable in `config.yaml` under `candidate_methods`.

## Architecture and data boundary

- `simulator/` generates deterministic telemetry for `clean_bad_deploy`, `coincident_restart`, `red_herring_deploy`, `shared_dependency`, `missing_telemetry`, `long_seasonal`, `late_alerting_cause`, and `silent_cause`. `simulator/sim_truth/` stores scenario names, fault descriptions, and the random scenario-ID salt.
- Telemetry exports expose only salted opaque `scn_<12 hex>` identifiers. An export contains no scenario name or fault type.
- `inquest/contracts/` contains strict Pydantic v2 models. `inquest/core/` provides the stage interface and registry, isolated runner, atomic artifacts, structured logs, config, vault, and signal logic.
- `inquest/stages/s00_ingest/`, `s01_vault/`, `s02_signals/`, and `s03_candidates/` implement adapter ingestion, evidence persistence, onset analysis, and independent change/graph/trace/temporal methods plus reciprocal-rank fusion. Stages use shared contracts and core services; candidate methods do not import each other.
- Reports always carry `ScenarioManifest.source` (`synthetic`, `otel`, or `real`). Stage exceptions become `FAILED` results while a validated final report is still written.

The default evaluator runs three seeds for every non-holdout scenario. Reserved scenarios under `simulator/scenarios/holdout/` are not registered or evaluated. See `eval/p2_results.md` for the per-scenario table and individual predictions.

See `SIM_SCHEMA.md`, `DATA_NOTES.md`, `DECISIONS.md`, `RUNBOOK.md`, and `P0_SIMULATION_SUMMARY.md` for details and verified observations.
