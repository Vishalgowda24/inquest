"""Typer CLI for dry-run validation, ingestion, and P0 diagnostic commands."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import typer

from inquest.contracts import CanonicalBundle, IncidentReport, Report, StageStatus
from inquest.core.artifacts import read_json
from inquest.core.builtins import default_registry
from inquest.core.config import InquestConfig, load_config
from inquest.core.errors import ConfigurationError, InquestError
from inquest.core.context import RunContext
from inquest.core.vault import verify_chain
from inquest.core.runner import StageRunner, make_context
from inquest.stages.s00_ingest.adapters import default_adapter_registry, RealIncidentAdapter
from inquest.stages.s03_candidates.methods.registry import default_method_registry
from inquest.stages.s04_verify.methods.registry import default_method_registry as default_verification_registry
from inquest.core.artifacts import write_json, write_text

app = typer.Typer(no_args_is_help=True, help="Evidence-driven incident investigation CLI")
OPAQUE_ID = re.compile(r"^scn_[a-f0-9]{12}$")


def _clock(config: InquestConfig) -> datetime:
    return config.simulation_clock


def _context(config: InquestConfig, scenario_id: str, run_id: str) -> RunContext:
    return make_context(run_id, scenario_id, config.runs_dir, _clock(config), config)


def _run_id(scenario_id: str, seed: int, stages: list[str]) -> str:
    source = f"{scenario_id}|{seed}|{','.join(stages)}|p2"
    return "run_" + hashlib.sha256(source.encode()).hexdigest()[:16]


def _vault_checks(runs_dir: Path) -> tuple[list[str], list[str]]:
    paths = sorted(runs_dir.glob("*/vault/chain.jsonl"))
    results = [(path, verify_chain(path)) for path in paths]
    failed = [f"{path}: {result.error}" for path, result in results if not result.valid]
    return [str(path) for path in paths], failed


def _load_bundle(folder: Path, settings: InquestConfig) -> CanonicalBundle:
    try:
        return default_adapter_registry(settings.csv_mapping_path).load(folder)
    except InquestError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc


def _ingest_summary(report) -> dict[str, object]:
    stages = [{"stage": item.stage, "status": item.status.value, "error_type": item.error_type} for item in report.stages]
    ingest_result = next((item for item in report.stages if item.stage == "s00_ingest"), None)
    signal_result = next((item for item in report.stages if item.stage == "s02_signals"), None)
    candidate_result = next((item for item in report.stages if item.stage == "s03_candidates"), None)
    verification_result = next((item for item in report.stages if item.stage == "s04_verify"), None)
    ingest_output = ingest_result.output if ingest_result else {}
    signal_output = signal_result.output if signal_result else {}
    analysis = signal_output.get("analysis", {})
    candidate_analysis = candidate_result.output.get("analysis", {}) if candidate_result else {}
    verification_analysis = verification_result.output.get("analysis", {}) if verification_result else {}
    top_candidates = candidate_analysis.get("candidates", [])[:5]
    top_candidates = [{key: item.get(key) for key in ("target", "target_type", "score", "method_scores", "rationale")} for item in top_candidates]
    return {
        "scenario_id": report.scenario_id,
        "source": report.source,
        "synthetic": report.synthetic,
        "run_id": report.run_id,
        "summary": report.summary,
        "stages": stages,
        "accepted_counts": ingest_output.get("accepted_counts", {}),
        "rejected_counts": ingest_output.get("rejected_counts", {}),
        "warnings": ingest_output.get("warnings", []),
        "detector": analysis.get("detector"),
        "onset_count": len(analysis.get("onsets", [])),
        "onset_order": analysis.get("service_order", []),
        "coverage_gap_count": len(analysis.get("coverage_gaps", [])),
        "candidate_count": len(candidate_analysis.get("candidates", [])),
        "candidate_methods": [{"method": item.get("method"), "status": item.get("status")} for item in candidate_analysis.get("method_results", [])],
        "candidate_disagreement": candidate_analysis.get("disagreement", 0.0),
        "top_candidates": top_candidates,
        "verification_decisions": len(verification_analysis.get("decisions", [])),
        "verification_disagreement": verification_analysis.get("disagreement", 0.0),
    }


@app.command()
def doctor(config: Path = typer.Option(Path("config.yaml"), "--config")) -> None:
    """Validate config, paths, registry, and run a smoke plugin."""
    try:
        settings = load_config(config)
        registry = default_registry(settings)
        adapters = default_adapter_registry(settings.csv_mapping_path)
        candidate_methods = default_method_registry()
        verification_methods = default_verification_registry()
        settings.data_inbox.mkdir(parents=True, exist_ok=True)
        settings.runs_dir.mkdir(parents=True, exist_ok=True)
        if not settings.runs_dir.is_dir() or not registry.names():
            raise ConfigurationError("Required paths or plugin registry are unavailable")
        context = _context(settings, "scn_000000000000", "doctor_smoke")
        report = StageRunner(registry).run(context, ["smoke"], {"doctor": True})
        checked_vaults, bad_vaults = _vault_checks(settings.runs_dir)
        vault_status = "FAILED" if bad_vaults else "OK"
        unknown_methods = sorted(set(settings.candidate_methods) - set(candidate_methods.names()))
        unknown_verification_methods = sorted(set(settings.verification_methods) - set(verification_methods.names()))
        typer.echo(json.dumps({"config": "OK", "paths": "OK", "plugin_registry": list(registry.names()), "adapter_registry": list(adapters.names()), "candidate_method_registry": list(candidate_methods.names()), "unknown_candidate_methods": unknown_methods, "verification_method_registry": list(verification_methods.names()), "unknown_verification_methods": unknown_verification_methods, "smoke": report.status.value, "vault_integrity": vault_status, "vaults_checked": len(checked_vaults), "vault_errors": bad_vaults}, sort_keys=True))
        if report.status.value == "FAILED" or bad_vaults or unknown_methods or unknown_verification_methods:
            raise typer.Exit(code=1)
    except (ConfigurationError, InquestError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc


@app.command()
def validate(folder: Path = typer.Argument(...), config: Path = typer.Option(Path("config.yaml"), "--config")) -> None:
    """Validate supported inputs without writing run or vault artifacts."""
    settings = load_config(config)
    bundle = _load_bundle(folder, settings)
    diagnostics = bundle.diagnostics
    typer.echo(f"Inquest validation | source={bundle.manifest.source} | scenario_id={bundle.manifest.scenario_id}")
    typer.echo(json.dumps({"synthetic": bundle.manifest.synthetic, "accepted_counts": diagnostics.accepted_counts, "rejected_counts": diagnostics.rejected_counts, "warnings": diagnostics.warnings, "input_files": diagnostics.input_files, "quarantined": [item.model_dump(mode="json") for item in diagnostics.quarantined]}, sort_keys=True))


@app.command()
def ingest(folder: Path = typer.Argument(...), config: Path = typer.Option(Path("config.yaml"), "--config")) -> None:
    """Ingest evidence, append the vault, and compute robust signal onsets."""
    settings = load_config(config)
    bundle = _load_bundle(folder, settings)
    names = ["s00_ingest", "s01_vault", "s02_signals", "s03_candidates", "s04_verify", "s05_report"]
    run_id = _run_id(bundle.manifest.scenario_id, bundle.manifest.seed, names)
    report = StageRunner(default_registry(settings)).run(_context(settings, bundle.manifest.scenario_id, run_id), names, {"folder": str(folder)})
    ingest_result = next((item for item in report.stages if item.stage == "s00_ingest"), None)
    details = ingest_result.output if ingest_result else {}
    diagnostics = {key: details.get(key) for key in ("accepted_counts", "rejected_counts", "warnings", "adapter")}
    quarantined = details.get("quarantined", [])
    if isinstance(quarantined, list) and quarantined:
        lines = "".join(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n" for item in quarantined)
        write_text(settings.runs_dir / run_id / "quarantine" / "rejected.jsonl", lines)
    write_json(settings.runs_dir / run_id / "ingest_report.json", {"run_id": run_id, "scenario_id": report.scenario_id, "source": report.source, "synthetic": report.synthetic, **diagnostics, "failed_stages": report.failed_stages, "degraded_stages": report.degraded_stages})
    typer.echo(f"Inquest report | source={report.source} | scenario_id={report.scenario_id} | run_id={run_id}")
    typer.echo(json.dumps(_ingest_summary(report), sort_keys=True))
    if report.failed_stages:
        raise typer.Exit(code=1)


@app.command("ingest-real")
def ingest_real(directory: Path = typer.Argument(..., help="Path to real incident directory"), config: Path = typer.Option(Path("config.yaml"), "--config")) -> None:
    """Validate, ingest, and run S00–S05 on a real incident directory."""
    settings = load_config(config)
    adapter = RealIncidentAdapter()
    try:
        adapter.validate(directory)
        bundle = adapter.load(directory)
    except InquestError as exc:
        typer.echo(f"Real data validation error: {exc}", err=True)
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        typer.echo(f"Real data ingest error: {exc}", err=True)
        raise typer.Exit(code=2) from exc

    names = ["s00_ingest", "s01_vault", "s02_signals", "s03_candidates", "s04_verify", "s05_report"]
    run_id = "real_" + bundle.manifest.scenario_id[4:] + "_" + hashlib.sha256(str(directory.resolve()).encode()).hexdigest()[:8]
    context = _context(settings, bundle.manifest.scenario_id, run_id)
    report = StageRunner(default_registry(settings)).run(context, names, {"folder": str(directory)})

    ingest_result = next((item for item in report.stages if item.stage == "s00_ingest"), None)
    details = ingest_result.output if ingest_result else {}
    diagnostics = {key: details.get(key) for key in ("accepted_counts", "rejected_counts", "warnings", "adapter")}
    quarantined = details.get("quarantined", [])
    if isinstance(quarantined, list) and quarantined:
        lines = "".join(json.dumps(item, sort_keys=True, separators=(",", ":")) + "\n" for item in quarantined)
        write_text(settings.runs_dir / run_id / "quarantine" / "rejected.jsonl", lines)
    write_json(settings.runs_dir / run_id / "ingest_report.json", {
        "run_id": run_id, "scenario_id": report.scenario_id, "source": "real", "synthetic": False,
        **diagnostics, "failed_stages": report.failed_stages, "degraded_stages": report.degraded_stages
    })
    typer.echo(f"Inquest real incident report | source=real | scenario_id={report.scenario_id} | run_id={run_id}")
    typer.echo(json.dumps(_ingest_summary(report), sort_keys=True))
    if report.failed_stages:
        raise typer.Exit(code=1)


@app.command("run")
def run_command(scenario: str = typer.Option(..., "--scenario"), stages: str = typer.Option("smoke", "--stages"), run_id: str | None = typer.Option(None, "--run-id"), source: str = typer.Option("synthetic", "--source"), config: Path = typer.Option(Path("config.yaml"), "--config")) -> None:
    """Run registered plugins using an opaque scenario ID."""
    if not OPAQUE_ID.fullmatch(scenario):
        raise typer.BadParameter("scenario must be an opaque scn_<12 hex> identifier")
    if source not in {"synthetic", "otel", "real"}:
        raise typer.BadParameter("source must be synthetic, otel, or real")
    names = [name.strip() for name in stages.split(",") if name.strip()]
    settings = load_config(config)
    current_run = run_id or _run_id(scenario, settings.global_seed, names)
    report = StageRunner(default_registry(settings)).run(_context(settings, scenario, current_run), names, {"scenario_id": scenario, "source": source})
    typer.echo(f"Inquest report | source={report.source} | scenario_id={report.scenario_id} | synthetic={report.synthetic}")
    typer.echo(json.dumps(report.model_dump(mode="json"), sort_keys=True))


@app.command()
def rerun(run: str = typer.Option(..., "--run"), stage: str = typer.Option(..., "--stage"), config: Path = typer.Option(Path("config.yaml"), "--config")) -> None:
    """Rerun one plugin from its saved input artifact."""
    settings = load_config(config)
    root = settings.runs_dir / run
    report = Report.model_validate(read_json(root / "report.json"))
    folders = sorted(root.glob(f"*_{stage}"))
    if len(folders) != 1:
        raise typer.BadParameter(f"expected one saved artifact directory for stage {stage!r}")
    index = int(folders[0].name.split("_", 1)[0])
    result = StageRunner(default_registry(settings)).rerun(_context(settings, report.scenario_id, run), stage, index)
    typer.echo(json.dumps(result.model_dump(mode="json"), sort_keys=True))


@app.command()
def explain(run: str = typer.Option(..., "--run"), config: Path = typer.Option(Path("config.yaml"), "--config")) -> None:
    """Display saved stage statuses, timing, and errors."""
    settings = load_config(config)
    report = Report.model_validate(read_json(settings.runs_dir / run / "report.json"))
    typer.echo(f"Inquest report | source={report.source} | scenario_id={report.scenario_id} | synthetic={report.synthetic}")
    for result in report.stages:
        typer.echo(f"{result.stage}: {result.status.value} ({result.elapsed_ms:.2f} ms)")
        if result.error:
            typer.echo(f"  {result.error_type}: {result.error}")
            if result.traceback:
                typer.echo(result.traceback)
    typer.echo(report.summary)


@app.command("report")
def report_command(run: str = typer.Argument(...), config: Path = typer.Option(Path("config.yaml"), "--config")) -> None:
    """Print the deterministic S05 incident report saved for a run."""
    settings=load_config(config)
    report_dir=settings.runs_dir/run/"05_s05_report"
    structured=IncidentReport.model_validate(read_json(report_dir/"report.json"))
    _ = structured
    typer.echo((report_dir/"report.md").read_text(encoding="utf-8"),nl=False)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
