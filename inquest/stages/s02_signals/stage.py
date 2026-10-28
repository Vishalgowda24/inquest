"""S02 per-series robust onset analysis."""

from __future__ import annotations

from inquest.contracts import CanonicalBundle, StageInput, StageResult, StageStatus
from inquest.core.context import RunContext
from inquest.core.signals import analyze_signals


class SignalsStage:
    name = "s02_signals"

    def run(self, ctx: RunContext, inp: StageInput) -> StageResult:
        bundle_data = self._bundle_data(inp)
        if not bundle_data:
            return StageResult(stage=self.name, status=StageStatus.DEGRADED, output={"missing_input": "canonical bundle unavailable"}, elapsed_ms=0)
        bundle = CanonicalBundle.model_validate(bundle_data)
        analysis = analyze_signals(bundle)
        status = StageStatus.DEGRADED if analysis.coverage_gaps else StageStatus.OK
        return StageResult(stage=self.name, status=status, output={"bundle": bundle.model_dump(mode="json"), "analysis": analysis.model_dump(mode="json"), "source": bundle.manifest.source, "synthetic": bundle.manifest.synthetic}, evidence_ids=[item.id for item in bundle.metrics], elapsed_ms=0)

    def _bundle_data(self, inp: StageInput) -> dict[str, object] | None:
        previous = inp.payload.get("previous_output")
        if isinstance(previous, dict):
            bundle = previous.get("bundle")
            return bundle if isinstance(bundle, dict) else None
        return None
