"""Minimal no-op stage used by doctor and the P0 CLI skeleton."""

from inquest.contracts import StageInput, StageResult, StageStatus
from inquest.core.context import RunContext


class SmokeStage:
    name = "smoke"

    def run(self, ctx: RunContext, inp: StageInput) -> StageResult:
        source = inp.payload.get("source", "synthetic")
        if source not in {"synthetic", "otel", "real"}:
            source = "real"
        return StageResult(stage=self.name, status=StageStatus.OK, output={"scenario_id": ctx.scenario_id, "clock": ctx.clock.isoformat(), "payload_keys": sorted(inp.payload), "source": source, "synthetic": source == "synthetic"}, evidence_ids=[], elapsed_ms=0)
