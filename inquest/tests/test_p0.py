"""P0 tests for contracts and failure-resilient stage execution."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from inquest.contracts import Report, StageInput, StageResult, StageStatus
from inquest.core.config import InquestConfig
from inquest.core.context import RunContext
from inquest.core.registry import StageRegistry
from inquest.core.runner import StageRunner


class ExplodingStage:
    name = "explode"

    def run(self, ctx: RunContext, inp: StageInput) -> StageResult:
        raise ValueError("deliberate fault for resilience test")


class ObserveMissingStage:
    name = "after_failure"

    def run(self, ctx: RunContext, inp: StageInput) -> StageResult:
        return StageResult(stage=self.name, status=StageStatus.DEGRADED if inp.missing_inputs else StageStatus.OK, output={"missing_inputs": inp.missing_inputs}, elapsed_ms=0)


def _context(tmp_path: Path) -> RunContext:
    config = InquestConfig(global_seed=1, log_level="INFO", data_inbox=tmp_path / "inbox", runs_dir=tmp_path / "runs", csv_mapping_path=tmp_path / "mapping.yaml", simulation_clock="2025-01-15T12:00:00Z", stages={"explode": True, "after_failure": True})
    return RunContext(run_id="run_test", scenario_id="scn_000000000000", runs_dir=config.runs_dir, clock=datetime(2025, 1, 15, tzinfo=timezone.utc), config=config)


def test_raising_stage_marks_failed_and_still_writes_valid_report(tmp_path: Path) -> None:
    registry = StageRegistry()
    registry.register(ExplodingStage())
    registry.register(ObserveMissingStage())
    report = StageRunner(registry).run(_context(tmp_path), ["explode", "after_failure"], {"opaque": True})
    validated = Report.model_validate(report.model_dump())
    saved_report = Report.model_validate_json((tmp_path / "runs" / "run_test" / "report.json").read_text(encoding="utf-8"))
    assert validated.status == StageStatus.FAILED
    assert saved_report.failed_stages == ["explode"]
    assert validated.failed_stages == ["explode"]
    assert validated.stages[0].error_type == "ValueError"
    assert "Traceback" in (validated.stages[0].traceback or "")
    assert validated.stages[1].status == StageStatus.DEGRADED
    missing = validated.stages[1].output["missing_inputs"]
    assert missing[0]["stage"] == "explode"
    stage_dir = tmp_path / "runs" / "run_test" / "00_explode"
    assert {"input.json", "output.json", "log.jsonl", "status.json"} <= {path.name for path in stage_dir.iterdir()}
    assert json.loads((stage_dir / "status.json").read_text(encoding="utf-8"))["status"] == "FAILED"
    assert '"run_id":"run_test"' in (stage_dir / "log.jsonl").read_text(encoding="utf-8")


def test_contract_status_values_are_closed_enum() -> None:
    assert {item.value for item in StageStatus} == {"OK", "DEGRADED", "FAILED"}


def test_unknown_stage_is_recorded_failed_not_raised(tmp_path: Path) -> None:
    report = StageRunner(StageRegistry()).run(_context(tmp_path), ["missing_stage"])
    assert report.status == StageStatus.FAILED
    assert report.stages[0].error_type == "StageError"
