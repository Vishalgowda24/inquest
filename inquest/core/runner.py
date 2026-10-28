"""Failure-resilient stage execution and report assembly."""

from __future__ import annotations

import traceback as traceback_module
from datetime import datetime
from pathlib import Path
from time import perf_counter

from pydantic import ValidationError

from inquest.contracts import MissingInput, Report, StageInput, StageResult, StageStatus
from .artifacts import read_json, stage_dir, write_json, write_text
from .context import RunContext
from .config import InquestConfig
from .errors import ContractError
from .logging import json_log
from .registry import StageRegistry


class StageRunner:
    def __init__(self, registry: StageRegistry) -> None:
        self.registry = registry

    def run_one(self, ctx: RunContext, inp: StageInput, stage_index: int) -> StageResult:
        started = perf_counter()
        folder = stage_dir(ctx.runs_dir, ctx.run_id, stage_index, inp.stage)
        write_json(folder / "input.json", inp.model_dump(mode="json"))
        try:
            plugin = self.registry.get(inp.stage)
            if not ctx.config.stages.get(inp.stage, False):
                result = StageResult(stage=inp.stage, status=StageStatus.DEGRADED, output={"missing_input": "stage disabled by configuration"}, elapsed_ms=0)
            else:
                result = plugin.run(ctx, inp)
            if result.stage != inp.stage:
                raise ContractError(f"Plugin {inp.stage} returned result for {result.stage}", stage=inp.stage)
            elapsed = (perf_counter() - started) * 1000
            result = result.model_copy(update={"elapsed_ms": elapsed})
        except Exception as exc:  # Plugin exceptions must not escape the runner.
            elapsed = (perf_counter() - started) * 1000
            result = StageResult(stage=inp.stage, status=StageStatus.FAILED, output={}, elapsed_ms=elapsed, error_type=type(exc).__name__, error=str(exc), traceback=traceback_module.format_exc())
        self._persist(ctx, folder, inp, result)
        return result

    def _persist(self, ctx: RunContext, folder: Path, inp: StageInput, result: StageResult) -> None:
        write_json(folder / "output.json", result.model_dump(mode="json"))
        log = json_log(run_id=ctx.run_id, stage=result.stage, event="stage_completed", evidence_ids=result.evidence_ids, elapsed_ms=result.elapsed_ms, level="ERROR" if result.status == StageStatus.FAILED else "INFO", status=result.status.value, error=result.error)
        write_text(folder / "log.jsonl", log + "\n")
        write_json(folder / "status.json", result.model_dump(mode="json"))

    def run(self, ctx: RunContext, stages: list[str], payload: dict[str, object] | None = None) -> Report:
        previous: dict[str, object] = payload or {}
        missing: list[MissingInput] = []
        results: list[StageResult] = []
        for index, name in enumerate(stages):
            stage_input = StageInput(stage=name, payload=previous, missing_inputs=missing)
            result = self.run_one(ctx, stage_input, index)
            results.append(result)
            missing = [MissingInput(stage=result.stage, reason=result.error or result.status.value)] if result.status != StageStatus.OK else []
            previous = {"previous_stage": result.stage, "previous_status": result.status.value, "previous_output": result.output, "missing_input": result.status != StageStatus.OK}
        return self._report(ctx, results)

    def rerun(self, ctx: RunContext, stage: str, stage_index: int) -> StageResult:
        folder = stage_dir(ctx.runs_dir, ctx.run_id, stage_index, stage)
        raw = read_json(folder / "input.json")
        try:
            inp = StageInput.model_validate(raw)
        except ValidationError as exc:
            raise ContractError(f"Saved input is invalid: {exc}", stage=stage, input_path=str(folder / "input.json")) from exc
        result = self.run_one(ctx, inp, stage_index)
        report_path = ctx.runs_dir / ctx.run_id / "report.json"
        if report_path.exists():
            old = read_json(report_path)
            old_results = [StageResult.model_validate(item) for item in old.get("stages", [])]
            updated = [result if item.stage == stage else item for item in old_results]
            self._report(ctx, updated)
        return result

    def _report(self, ctx: RunContext, stages: list[StageResult]) -> Report:
        failed = [result.stage for result in stages if result.status == StageStatus.FAILED]
        degraded = [result.stage for result in stages if result.status == StageStatus.DEGRADED]
        status = StageStatus.FAILED if failed else StageStatus.DEGRADED if degraded else StageStatus.OK
        summary = "All requested stages completed." if status == StageStatus.OK else f"Failed stages: {', '.join(failed)}" if failed else f"Degraded stages: {', '.join(degraded)}"
        source, synthetic = self._source_metadata(stages)
        report = Report(run_id=ctx.run_id, scenario_id=ctx.scenario_id, source=source, synthetic=synthetic, status=status, stages=stages, failed_stages=failed, degraded_stages=degraded, summary=summary)
        write_json(ctx.runs_dir / ctx.run_id / "report.json", report.model_dump(mode="json"))
        return report

    def _source_metadata(self, stages: list[StageResult]) -> tuple[str, bool]:
        source, synthetic = "real", False
        for result in stages:
            candidate = result.output.get("source")
            if isinstance(candidate, str) and candidate in {"synthetic", "otel", "real"}:
                source = str(candidate)
                synthetic = bool(result.output.get("synthetic", source == "synthetic"))
        return source, synthetic


def make_context(run_id: str, scenario_id: str, runs_dir: Path, clock: datetime, config: InquestConfig) -> RunContext:
    return RunContext(run_id=run_id, scenario_id=scenario_id, runs_dir=runs_dir, clock=clock, config=config)
