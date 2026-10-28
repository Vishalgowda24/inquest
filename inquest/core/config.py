"""Validated YAML configuration loaded at the CLI boundary."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .errors import ConfigurationError


class InquestConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    global_seed: int = Field(ge=0)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    data_inbox: Path
    runs_dir: Path
    csv_mapping_path: Path
    simulation_clock: datetime
    stages: dict[str, bool]
    candidate_methods: dict[str, bool] = Field(default_factory=lambda: {"change_based": True, "graph_rwr": True, "trace_ochiai": True, "temporal_lag": True})
    verification_methods: dict[str, bool] = Field(default_factory=lambda: {"vault_evidence": True, "dependency_path": True, "temporal_consistency": True, "recovery_check": True, "alternative_check": True})
    verification_rerank: bool = False
    fusion_abstention: bool = True
    fusion_variant: Literal["v0", "v1", "v2", "v3", "v4"] = "v0"

    @field_validator("simulation_clock")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("simulation_clock must include a timezone")
        return value


def load_config(path: Path) -> InquestConfig:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return InquestConfig.model_validate(raw)
    except (OSError, yaml.YAMLError, ValidationError) as exc:
        raise ConfigurationError(f"Invalid configuration at {path}: {exc}", input_path=str(path)) from exc
