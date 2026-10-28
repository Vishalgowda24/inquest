"""Deterministic export writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel

from simulator.scenarios.clean_bad_deploy.model import Dataset


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _write_model_list(path: Path, records: Iterable[BaseModel]) -> None:
    data = [record.model_dump(mode="json") for record in records]
    path.write_bytes(_json_bytes(data))


def _jsonl_line(record: BaseModel) -> bytes:
    payload = record.model_dump(mode="json")
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def write_export(dataset: Dataset, export_dir: Path, truth_path: Path) -> None:
    """Write standard export files and a separately stored evaluation truth file."""
    export_dir.mkdir(parents=True, exist_ok=True)
    (export_dir / "metrics").mkdir(exist_ok=True)
    (export_dir / "traces").mkdir(exist_ok=True)
    (export_dir / "logs").mkdir(exist_ok=True)
    (export_dir / "manifest.json").write_bytes(_json_bytes(dataset.manifest.model_dump(mode="json")))
    _write_model_list(export_dir / "metrics" / "metrics.json", dataset.metrics)
    _write_model_list(export_dir / "traces" / "spans.json", dataset.spans)
    with (export_dir / "logs" / "events.jsonl").open("wb") as output:
        for record in dataset.logs:
            output.write(_jsonl_line(record))
    _write_model_list(export_dir / "events.json", dataset.events)
    _write_model_list(export_dir / "dependency_graph.json", dataset.dependencies)
    truth_path.parent.mkdir(parents=True, exist_ok=True)
    truth_path.write_bytes(_json_bytes(dataset.truth))
