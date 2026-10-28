"""Append-only SHA-256 evidence chain with deterministic serialization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import ValidationError

from inquest.contracts import Evidence, VaultEntry, VaultVerification
from .errors import ArtifactError, StageError

GENESIS = "0" * 64


def _canonical_record(evidence: Evidence) -> dict[str, object]:
    return {"id": evidence.id, "source": evidence.source, "ts": evidence.timestamp.isoformat() if evidence.timestamp else None, "ts_uncertainty_ms": evidence.timestamp_uncertainty_ms, "payload": evidence.payload}


def _entry_hash(previous: str, record: dict[str, object]) -> str:
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256((previous + canonical).encode("utf-8")).hexdigest()


def verify_chain(path: Path) -> VaultVerification:
    if not path.exists():
        return VaultVerification(valid=True, items_checked=0)
    previous = GENESIS
    checked = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return VaultVerification(valid=False, items_checked=0, error=f"Cannot read vault {path}: {exc}")
    for line_number, line in enumerate(lines, start=1):
        result = _verify_line(line, line_number, previous, checked)
        if isinstance(result, VaultVerification):
            return result
        previous = result.hash
        checked += 1
    return VaultVerification(valid=True, items_checked=checked)


def read_vault_ids(path: Path) -> set[str]:
    """Return verified IDs from a vault for provenance validation downstream."""
    verification = verify_chain(path)
    if not verification.valid:
        raise StageError(f"Vault integrity failure at {verification.item_id}: {verification.error}", stage="s01_vault", input_path=str(path))
    return {entry.id for entry in _load_entries(path)}


def read_vault_entries(path: Path) -> dict[str, dict[str, object]]:
    """Return payloads only after validating the full append-only hash chain."""
    verification = verify_chain(path)
    if not verification.valid:
        raise StageError(f"Vault integrity failure at {verification.item_id}: {verification.error}", stage="s01_vault", input_path=str(path))
    return {entry.id: {"source": entry.source, "ts": entry.ts.isoformat() if entry.ts else None, "payload": entry.payload} for entry in _load_entries(path)}


def _verify_line(line: str, line_number: int, previous: str, checked: int) -> VaultEntry | VaultVerification:
    try:
        entry = VaultEntry.model_validate_json(line)
    except ValidationError as exc:
        return VaultVerification(valid=False, items_checked=checked, item_id=f"line:{line_number}", error=f"Invalid vault item at line {line_number}: {exc}")
    payload_record = {"id": entry.id, "source": entry.source, "ts": entry.ts.isoformat() if entry.ts else None, "ts_uncertainty_ms": entry.ts_uncertainty_ms, "payload": entry.payload}
    expected = _entry_hash(previous, payload_record)
    if entry.prev_hash != previous:
        return VaultVerification(valid=False, items_checked=checked, item_id=entry.id, error=f"Previous hash mismatch at item {entry.id}")
    if entry.hash != expected:
        return VaultVerification(valid=False, items_checked=checked, item_id=entry.id, error=f"Hash mismatch at item {entry.id}")
    return entry


def append_evidence(path: Path, evidence: list[Evidence]) -> tuple[int, str]:
    verification = verify_chain(path)
    if not verification.valid:
        raise StageError(f"Vault integrity failure at {verification.item_id}: {verification.error}", stage="s01_vault", input_path=str(path))
    entries = _load_entries(path)
    existing = {entry.id: entry for entry in entries}
    previous = entries[-1].hash if entries else GENESIS
    to_append: list[VaultEntry] = []
    for item in sorted(evidence, key=lambda record: record.id):
        record = _canonical_record(item)
        current = existing.get(item.id)
        if current is not None:
            if _canonical_record_from_entry(current) != record:
                raise StageError(f"Evidence ID collision with different content: {item.id}", stage="s01_vault", input_path=str(path))
            continue
        digest = _entry_hash(previous, record)
        entry = VaultEntry(**record, prev_hash=previous, hash=digest)
        to_append.append(entry)
        previous = digest
    _append_lines(path, to_append)
    final = to_append[-1].hash if to_append else (entries[-1].hash if entries else GENESIS)
    return len(to_append), final


def _canonical_record_from_entry(entry: VaultEntry) -> dict[str, object]:
    return {"id": entry.id, "source": entry.source, "ts": entry.ts.isoformat() if entry.ts else None, "ts_uncertainty_ms": entry.ts_uncertainty_ms, "payload": entry.payload}


def _load_entries(path: Path) -> list[VaultEntry]:
    if not path.exists():
        return []
    try:
        return [VaultEntry.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines()]
    except (OSError, ValidationError) as exc:
        raise ArtifactError(f"Cannot parse evidence vault {path}: {exc}", stage="s01_vault", input_path=str(path)) from exc


def _append_lines(path: Path, entries: list[VaultEntry]) -> None:
    if not entries:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("a", encoding="utf-8", newline="\n") as output:
            for entry in entries:
                output.write(entry.model_dump_json(by_alias=True) + "\n")
    except OSError as exc:
        raise ArtifactError(f"Cannot append evidence vault {path}: {exc}", stage="s01_vault", input_path=str(path)) from exc


def evidence_from_bundle(bundle) -> list[Evidence]:
    result = [Evidence(id=f"manifest:{bundle.manifest.scenario_id}", source="manifest.json", timestamp=None, timestamp_uncertainty_ms=0, payload=bundle.manifest.model_dump(mode="json"), source_reference="manifest.json")]
    for collection in (bundle.metrics, bundle.spans, bundle.logs, bundle.changes, bundle.dependencies):
        result.extend(_evidence(item) for item in collection)
    return result


def _evidence(record) -> Evidence:
    identity = getattr(record, "id", None) or f"span:{record.trace_id}:{record.span_id}"
    timestamp = getattr(record, "timestamp", None) or getattr(record, "start_time", None)
    return Evidence(id=str(identity), source=record.source, timestamp=timestamp, timestamp_uncertainty_ms=getattr(record, "timestamp_uncertainty_ms", 0), payload=record.model_dump(mode="json"), source_reference=record.source_metadata.get("file"))
