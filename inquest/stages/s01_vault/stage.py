"""S01 append-only evidence vault stage."""

from __future__ import annotations

from inquest.contracts import CanonicalBundle, StageInput, StageResult, StageStatus
from inquest.core.context import RunContext
from inquest.core.errors import ContractError
from inquest.core.vault import append_evidence, evidence_from_bundle, verify_chain


class VaultStage:
    name = "s01_vault"

    def run(self, ctx: RunContext, inp: StageInput) -> StageResult:
        bundle_data = self._bundle_data(inp)
        if not bundle_data:
            return StageResult(stage=self.name, status=StageStatus.DEGRADED, output={"missing_input": "canonical bundle unavailable"}, elapsed_ms=0)
        bundle = CanonicalBundle.model_validate(bundle_data)
        vault_path = ctx.runs_dir / ctx.run_id / "vault" / "chain.jsonl"
        appended, head = append_evidence(vault_path, evidence_from_bundle(bundle))
        verified = verify_chain(vault_path)
        if not verified.valid:
            raise ContractError(f"New vault failed verification at {verified.item_id}: {verified.error}", stage=self.name, input_path=str(vault_path))
        return StageResult(stage=self.name, status=StageStatus.OK, output={"bundle": bundle.model_dump(mode="json"), "vault_path": str(vault_path), "items_appended": appended, "items_checked": verified.items_checked, "head_hash": head, "integrity": "OK"}, evidence_ids=[item.id for item in evidence_from_bundle(bundle)], elapsed_ms=0)

    def _bundle_data(self, inp: StageInput) -> dict[str, object] | None:
        previous = inp.payload.get("previous_output")
        if isinstance(previous, dict):
            bundle = previous.get("bundle")
            return bundle if isinstance(bundle, dict) else None
        return None
