"""S00 adapter-driven canonical input stage."""

from __future__ import annotations

from pathlib import Path

from inquest.contracts import StageInput, StageResult, StageStatus
from inquest.core.context import RunContext
from .adapters import default_adapter_registry


class IngestStage:
    name = "s00_ingest"

    def __init__(self, mapping_path: Path) -> None:
        self.mapping_path = mapping_path

    def run(self, ctx: RunContext, inp: StageInput) -> StageResult:
        folder = inp.payload.get("folder")
        if not isinstance(folder, str):
            return StageResult(stage=self.name, status=StageStatus.FAILED, error_type="IngestError", error="Stage input must include a folder path", elapsed_ms=0)
        registry = default_adapter_registry(self.mapping_path)
        adapter = registry.select(Path(folder))
        bundle = adapter.load(Path(folder))
        diagnostics = bundle.diagnostics
        rejected = sum(diagnostics.rejected_counts.values())
        status = StageStatus.DEGRADED if rejected or diagnostics.warnings else StageStatus.OK
        output = {"bundle": bundle.model_dump(mode="json"), "source": bundle.manifest.source, "synthetic": bundle.manifest.synthetic, "adapter": adapter.name, "accepted_counts": diagnostics.accepted_counts, "rejected_counts": diagnostics.rejected_counts, "warnings": diagnostics.warnings, "quarantined": [item.model_dump(mode="json") for item in diagnostics.quarantined]}
        evidence_ids = [self._record_id(item) for group in (bundle.metrics, bundle.spans, bundle.logs, bundle.changes, bundle.dependencies) for item in group]
        return StageResult(stage=self.name, status=status, output=output, evidence_ids=evidence_ids, elapsed_ms=0)

    def _record_id(self, item) -> str:
        return item.id if hasattr(item, "id") else f"span:{item.trace_id}:{item.span_id}"
