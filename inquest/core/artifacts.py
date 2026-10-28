"""Atomic persistence for per-stage JSON and JSONL artifacts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .errors import ArtifactError


def stage_dir(runs_dir: Path, run_id: str, stage_index: int, stage: str) -> Path:
    return runs_dir / run_id / f"{stage_index:02d}_{stage}"


def _atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_text(json.dumps(value, sort_keys=True, indent=2, default=str) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    except OSError as exc:
        raise ArtifactError(f"Could not write artifact {path}: {exc}", input_path=str(path)) from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_json(path, value)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise ArtifactError(f"Could not write artifact {path}: {exc}", input_path=str(path)) from exc


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ArtifactError(f"Could not read artifact {path}: {exc}", input_path=str(path)) from exc
    if not isinstance(value, dict):
        raise ArtifactError(f"Expected JSON object in {path}", input_path=str(path))
    return value
