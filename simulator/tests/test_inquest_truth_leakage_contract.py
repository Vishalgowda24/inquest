"""Static import/path/fixture contract for the Inquest truth boundary."""

from __future__ import annotations

import ast
import json
from pathlib import Path


def _truth_labels(truth_root: Path) -> set[str]:
    labels = {"sim_truth", "scenario_name", "injected_fault", "ground_truth", "truth.json", "truth"}
    for path in truth_root.rglob("*.truth.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        scenario = payload.get("scenario_name")
        if isinstance(scenario, str):
            labels.add(scenario.casefold())
        fault = payload.get("injected_fault", {})
        if isinstance(fault, dict):
            labels.update(value.casefold() for key, value in fault.items() if key in {"kind", "fault_type"} and isinstance(value, str))
    return labels


def test_inquest_tree_cannot_import_open_or_resolve_simulator_truth() -> None:
    root = Path(__file__).resolve().parents[2]
    inquest = root / "inquest"
    truth_root = root / "simulator" / "sim_truth"
    labels = _truth_labels(truth_root)
    files = [path for path in inquest.rglob("*") if path.is_file() and path.suffix.lower() in {".py", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".txt", ".csv"}]
    assert files
    for path in files:
        text = path.read_text(encoding="utf-8").casefold()
        normalized = text.replace("\\", "/")
        assert "simulator/sim_truth" not in normalized, path
        assert not any(label and label in text for label in labels), path
        if path.suffix.lower() != ".py":
            continue
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = [item.name for item in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                assert not any(module == "simulator" or module.startswith("simulator.") for module in modules), (path, node.lineno)
            if isinstance(node, ast.Name):
                assert node.id.casefold() not in {"truth", "ground_truth", "scenario_name", "injected_fault"}, (path, node.lineno)
            if isinstance(node, ast.Attribute):
                assert node.attr.casefold() not in {"scenario_name", "injected_fault"}, (path, node.lineno)
            if isinstance(node, ast.Call):
                call_name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
                if call_name in {"open", "resolve", "read_text", "read_bytes"}:
                    arguments = ast.unparse(node.args).casefold()
                    assert "sim_truth" not in arguments and "truth.json" not in arguments, (path, node.lineno)
