"""Run context passed to every plugin."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import InquestConfig


@dataclass(frozen=True)
class RunContext:
    run_id: str
    scenario_id: str
    runs_dir: Path
    clock: datetime
    config: InquestConfig
