"""Render P6 Markdown from its immutable saved case JSON; never runs stages."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("p6_evaluator", ROOT / "eval" / "run_p6_holdout.py")
if spec is None or spec.loader is None:
    raise RuntimeError("could not load frozen P6 report renderer")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = json.loads(module.RESULTS.read_text(encoding="utf-8"))
if len(cases) != 36:
    raise SystemExit(f"expected 36 saved holdout cases; found {len(cases)}")
module.REPORT.write_text(module.render(cases), encoding="utf-8")
print(f"Rendered {module.REPORT}")
