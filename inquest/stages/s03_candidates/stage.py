"""S03 independent candidate methods and ensemble stage."""

from __future__ import annotations

from inquest.contracts import CandidateAnalysis, CandidateMethodResult, CanonicalBundle, SignalAnalysis, StageInput, StageResult, StageStatus
from inquest.core.context import RunContext
from inquest.core.vault import read_vault_ids
from .ensemble import rank_aggregate
from .methods.registry import default_method_registry


class CandidateStage:
    name = "s03_candidates"

    def run(self, ctx: RunContext, inp: StageInput) -> StageResult:
        previous = inp.payload.get("previous_output")
        previous = previous if isinstance(previous, dict) else {}
        try:
            bundle = CanonicalBundle.model_validate(previous.get("bundle"))
            signals = SignalAnalysis.model_validate(previous.get("analysis"))
        except Exception as exc:
            return StageResult(stage=self.name, status=StageStatus.DEGRADED, output={"reason": f"S02 analysis unavailable: {exc}"}, elapsed_ms=0)

        vault_path = ctx.runs_dir / ctx.run_id / "vault" / "chain.jsonl"
        try:
            vault_ids = read_vault_ids(vault_path)
        except Exception as exc:
            return StageResult(stage=self.name, status=StageStatus.FAILED, output={}, error_type=type(exc).__name__, error=str(exc), elapsed_ms=0)

        registry = default_method_registry()
        configured = ctx.config.candidate_methods
        results: list[CandidateMethodResult] = []
        for name in registry.names():
            if not configured.get(name, True):
                results.append(CandidateMethodResult(method=name, status="DISABLED", note="Disabled in config.yaml"))
                continue
            try:
                method_result = registry.get(name).run(bundle, signals, vault_ids)
                invalid = [candidate.id for candidate in method_result.candidates if not set(candidate.evidence_ids) <= vault_ids]
                if invalid:
                    raise ValueError(f"Method {name} returned evidence IDs absent from the vault: {invalid}")
                results.append(method_result)
            except Exception as exc:
                results.append(CandidateMethodResult(method=name, status="DEGRADED", note=f"{type(exc).__name__}: {exc}"))
        ensemble, disagreement, abstentions = rank_aggregate(
            results,
            abstain_without_evidence=ctx.config.fusion_abstention,
            variant=ctx.config.fusion_variant,
        )
        telemetry_gaps = {gap.service for gap in signals.coverage_gaps}
        traced_services = {span.service for span in bundle.spans}
        telemetry_gaps.update(set(bundle.manifest.services) - traced_services)
        per_method = {item.method: item.candidates for item in results if item.status != "DISABLED"}
        analysis = CandidateAnalysis(
            candidates=ensemble, per_method=per_method, method_results=results,
            disabled_methods=[item.method for item in results if item.status == "DISABLED"],
            disagreement=disagreement,
            abstentions=abstentions,
        )
        failed_methods = [item for item in results if item.status == "DEGRADED"]
        status = StageStatus.DEGRADED if failed_methods or not ensemble else StageStatus.OK
        evidence_ids = sorted({identifier for candidate in ensemble for identifier in candidate.evidence_ids})
        return StageResult(
            stage=self.name, status=status,
            output={"analysis": analysis.model_dump(mode="json"), "source": bundle.manifest.source, "synthetic": bundle.manifest.synthetic, "vault_evidence_count": len(vault_ids), "verification_context": {"dependencies": [edge.model_dump(mode="json") for edge in bundle.dependencies], "dependency_graph_complete": bundle.manifest.dependency_graph_complete, "onsets": [onset.model_dump(mode="json") for onset in signals.onsets], "coverage_gaps": [gap.model_dump(mode="json") for gap in signals.coverage_gaps], "telemetry_gaps": sorted(telemetry_gaps), "changes": [event.model_dump(mode="json") for event in bundle.changes], "metrics": [point.model_dump(mode="json") for point in bundle.metrics]}},
            evidence_ids=evidence_ids, elapsed_ms=0,
        )
