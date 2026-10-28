"""Default stage registry."""

from pathlib import Path

from inquest.core.config import InquestConfig
from inquest.stages.s00_ingest.stage import IngestStage
from inquest.stages.s01_vault.stage import VaultStage
from inquest.stages.s02_signals.stage import SignalsStage
from inquest.stages.s03_candidates.stage import CandidateStage
from inquest.stages.s04_verify.stage import VerifyStage
from inquest.stages.smoke import SmokeStage
from .registry import StageRegistry


def default_registry(config: InquestConfig | None = None) -> StageRegistry:
    registry = StageRegistry()
    registry.register(SmokeStage())
    mapping_path = config.csv_mapping_path if config else Path("config/csv_mapping.yaml")
    registry.register(IngestStage(mapping_path))
    registry.register(VaultStage())
    registry.register(SignalsStage())
    registry.register(CandidateStage())
    registry.register(VerifyStage())
    return registry
