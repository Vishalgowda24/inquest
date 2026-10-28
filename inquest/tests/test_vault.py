"""Evidence hash-chain integrity and idempotent append tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from inquest.contracts import Evidence
from inquest.cli import _vault_checks
from inquest.core.vault import append_evidence, verify_chain


def _evidence(identifier: str, value: int) -> Evidence:
    return Evidence(id=identifier, source="fixture.json", timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc), timestamp_uncertainty_ms=0, payload={"value": value})


def test_chain_is_deterministic_and_repeat_ingest_is_idempotent(tmp_path: Path) -> None:
    items = [_evidence("ev-b", 2), _evidence("ev-a", 1)]
    first, second = tmp_path / "first.jsonl", tmp_path / "second.jsonl"
    assert append_evidence(first, items)[0] == 2
    assert append_evidence(second, items)[0] == 2
    before = first.read_bytes()
    assert append_evidence(first, items)[0] == 0
    assert first.read_bytes() == before == second.read_bytes()
    assert verify_chain(first).valid
    assert verify_chain(first).items_checked == 2


def test_tampered_item_fails_verification_and_names_item(tmp_path: Path) -> None:
    path = tmp_path / "chain.jsonl"
    append_evidence(path, [_evidence("ev-target", 7), _evidence("ev-next", 8)])
    lines = path.read_text(encoding="utf-8").splitlines()
    item = json.loads(lines[0])
    tampered_id = item["id"]
    item["payload"]["value"] = 99
    lines[0] = json.dumps(item, sort_keys=True, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = verify_chain(path)
    assert not result.valid
    assert result.item_id == tampered_id
    assert tampered_id in (result.error or "")


def test_chain_detects_removed_and_reordered_items(tmp_path: Path) -> None:
    path = tmp_path / "chain.jsonl"
    append_evidence(path, [_evidence("first", 1), _evidence("second", 2), _evidence("third", 3)])
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join([lines[0], lines[2]]) + "\n", encoding="utf-8")
    assert verify_chain(path).item_id == "third"
    path.write_text("\n".join([lines[1], lines[0], lines[2]]) + "\n", encoding="utf-8")
    assert not verify_chain(path).valid


def test_doctor_vault_check_finds_tampering(tmp_path: Path) -> None:
    path = tmp_path / "runs" / "run_a" / "vault" / "chain.jsonl"
    append_evidence(path, [_evidence("evidence-a", 4)])
    checked, errors = _vault_checks(tmp_path / "runs")
    assert checked == [str(path)]
    assert not errors
    item = json.loads(path.read_text(encoding="utf-8"))
    item["payload"]["value"] = 5
    path.write_text(json.dumps(item) + "\n", encoding="utf-8")
    checked, errors = _vault_checks(tmp_path / "runs")
    assert checked == [str(path)]
    assert errors and "evidence-a" in errors[0]
