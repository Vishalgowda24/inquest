"""Minimal structured JSONL event formatter."""

from __future__ import annotations

import json
from typing import Any


def json_log(*, run_id: str, stage: str, event: str, evidence_ids: list[str], elapsed_ms: float, level: str = "INFO", **fields: Any) -> str:
    payload = {"run_id": run_id, "stage": stage, "evidence_ids": evidence_ids, "elapsed_ms": round(elapsed_ms, 3), "level": level, "event": event, **fields}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
