# Runbook

## Setup and checks

Run `./setup.ps1` on Windows. It verifies the pinned dependencies, runs the full pytest suite, then runs `inquest doctor`. This workspace uses Python 3.12.14 because Python 3.11 is not installed. Managed network access to PyPI is unavailable, so the setup reuses exact pinned packages already present in `work/python-packages`. The available bundled Python also lacks a working `ensurepip`; the setup avoids venv bootstrap by using the workspace-local dependency cache.

For manual checks, set `PYTHONPATH` to `work/python-packages` and `TEMP`/`TMP` to `work/tmp`, then run:

```powershell
python -m pytest --basetemp work/pytest-run-temp
python -m inquest.cli doctor --config config.yaml
```

## CLI workflow

1. Create a simulator export: `python -m simulator.cli run --scenario clean_bad_deploy --seed 1`.
2. Run `python -m inquest.cli validate <export-folder>` to inspect it without writes.
3. Run `python -m inquest.cli ingest <export-folder>` to validate, quarantine malformed rows, append evidence to the vault, and analyze signals.
4. Read the report with `python -m inquest.cli explain --run <run_id>`; stage artifacts live in `runs/<run_id>/<NN>_<stage>/`.
5. Recompute one stage from saved input with `python -m inquest.cli rerun --run <run_id> --stage s03_candidates`.

The simulator registry includes `coincident_restart`, `red_herring_deploy`, `shared_dependency`, `missing_telemetry`, `long_seasonal`, `late_alerting_cause`, and `silent_cause`. It exports opaque IDs and writes truth only under `simulator/sim_truth/<scenario>/`. The long scenario spans 72 hourly points so S02 can normalize seasonality after checking coverage; the late and silent scenarios make alert order misleading by delaying or removing cause-service metrics.

S03 runs through `inquest ingest` after S02. Its independent methods are enabled or disabled in `config.yaml` under `candidate_methods`. The default evaluation command is `python eval/run_p2.py`; it runs seeds 1–3 across the explicit non-holdout registry, saves per-scenario hits and per-case ensemble rank/margin to `eval/p2_results.md`, and reads truth only from `simulator/sim_truth/`. The reserved `simulator/scenarios/holdout/` folder is not registered or evaluated.

`validate` reports accepted/rejected row counts, context-rich quarantines, clock uncertainty, missing services, and coverage gaps. Missing windows are never imputed. CSV mappings are configured in `config/csv_mapping.yaml`.

## Integrity and failure handling

The vault is append-only JSONL with a SHA-256 chain. `inquest doctor` verifies every `runs/*/vault/chain.jsonl` and returns nonzero for tampering. Stage exceptions are isolated into `FAILED` statuses; the runner still writes a schema-valid final report and passes typed missing-input information to downstream stages.

## Signal interpretation

S02 uses a robust median/MAD baseline, CUSUM by default, and ruptures PELT when the optional library is available. Onsets are ordered by estimated onset time. Reported timestamp uncertainty includes source clock uncertainty and observed missing-window intervals. Seasonality normalization is applied only when at least two complete daily cycles are available; the simulator's 20-hour observation period does not meet this threshold, so the report explicitly notes that normalization was skipped.
