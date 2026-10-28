"""S03 method behavior, isolation, and vault evidence contracts."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

import pytest

from inquest.contracts import Report, VaultEntry
from inquest.core.builtins import default_registry
from inquest.core.config import InquestConfig
from inquest.core.context import RunContext
from inquest.core.runner import StageRunner
from simulator.core.export import write_export
from simulator.scenarios.clean_bad_deploy.model import generate as clean_bad_deploy
from simulator.scenarios.red_herring_deploy import generate as red_herring_deploy
from simulator.scenarios.missing_telemetry import generate as missing_telemetry


def _run(dataset, tmp_path: Path, candidate_methods: dict[str, bool] | None = None):
    folder = tmp_path / "input" / dataset.manifest.scenario_id / "export"
    write_export(dataset, folder, tmp_path / "sim_truth" / f"{dataset.manifest.seed}.truth.json")
    config = InquestConfig(
        global_seed=dataset.manifest.seed, log_level="INFO", data_inbox=tmp_path / "inbox",
        runs_dir=tmp_path / "runs", csv_mapping_path=Path("config/csv_mapping.yaml"),
        simulation_clock=datetime(2025, 1, 15, 12, tzinfo=timezone.utc),
        stages={"smoke": True, "s00_ingest": True, "s01_vault": True, "s02_signals": True, "s03_candidates": True},
        candidate_methods=candidate_methods or {name: True for name in ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag")},
    )
    ctx = RunContext(run_id="run_candidates", scenario_id=dataset.manifest.scenario_id, runs_dir=config.runs_dir, clock=config.simulation_clock, config=config)
    report = StageRunner(default_registry(config)).run(ctx, ["s00_ingest", "s01_vault", "s02_signals", "s03_candidates"], {"folder": str(folder)})
    result = next(item for item in report.stages if item.stage == "s03_candidates")
    analysis = result.output["analysis"]
    entries = [VaultEntry.model_validate_json(line) for line in (config.runs_dir / ctx.run_id / "vault" / "chain.jsonl").read_text(encoding="utf-8").splitlines()]
    return report, result, analysis, {item.id for item in entries}


def test_candidate_evidence_ids_are_all_present_in_vault(tmp_path: Path) -> None:
    report, result, analysis, vault_ids = _run(clean_bad_deploy(1), tmp_path)
    assert report.status.value in {"OK", "DEGRADED"}
    assert result.status.value == "OK"
    for method_candidates in analysis["per_method"].values():
        for candidate in method_candidates:
            assert candidate["evidence_ids"]
            assert set(candidate["evidence_ids"]) <= vault_ids
    for candidate in analysis["candidates"]:
        assert set(candidate["evidence_ids"]) <= vault_ids
    graph = analysis["per_method"]["graph_rwr"]
    assert graph[0]["target"] == "database"
    temporal = analysis["per_method"]["temporal_lag"]
    dependency_callees = {"payments", "inventory", "database"}
    assert temporal and all(item["target"] in dependency_callees and "r=" in item["rationale"] for item in temporal)
    assert analysis["per_method"]["trace_ochiai"]


def test_red_herring_method_scores_expose_service_relevance(tmp_path: Path) -> None:
    _, _, analysis, _ = _run(red_herring_deploy(1), tmp_path)
    changes = analysis["per_method"]["change_based"]
    assert changes
    assert changes[0]["service"] == "payments"
    assert "service relevance" in changes[0]["rationale"]


def test_missing_traces_degrade_trace_method_without_breaking_stage(tmp_path: Path) -> None:
    report, result, analysis, _ = _run(missing_telemetry(1), tmp_path)
    trace = next(item for item in analysis["method_results"] if item["method"] == "trace_ochiai")
    assert trace["status"] == "DEGRADED"
    assert "inventory" in trace["note"]
    assert result.status.value == "DEGRADED"
    saved = Report.model_validate_json((tmp_path / "runs" / "run_candidates" / "report.json").read_text(encoding="utf-8"))
    assert saved.status.value == "DEGRADED"


@pytest.mark.parametrize("disabled", ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag"))
def test_disabling_any_single_method_keeps_a_valid_candidate_result(tmp_path: Path, disabled: str) -> None:
    flags = {name: name != disabled for name in ("change_based", "graph_rwr", "trace_ochiai", "temporal_lag")}
    _, result, analysis, vault_ids = _run(clean_bad_deploy(2), tmp_path, flags)
    assert result.status.value == "OK"
    assert analysis["disabled_methods"] == [disabled]
    assert analysis["candidates"]
    assert all(set(item["evidence_ids"]) <= vault_ids for item in analysis["candidates"])


def test_candidate_methods_do_not_import_each_other() -> None:
    root = Path(__file__).resolve().parents[2] / "inquest" / "stages" / "s03_candidates" / "methods"
    method_files = [path for path in root.glob("*.py") if path.stem not in {"__init__", "common", "registry"}]
    other_method = re.compile(r"(?:from|import)\s+(?:\.\s*)?(change_based|graph_rwr|trace_ochiai|temporal_lag)\b")
    for source in method_files:
        text = source.read_text(encoding="utf-8")
        for match in other_method.finditer(text):
            assert match.group(1) == source.stem, f"{source.name} imports {match.group(1)}"
