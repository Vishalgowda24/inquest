"""Materialize the frozen P5 seed-4-through-6 simulator inputs only.

This utility intentionally imports no inquest package and never runs a stage.
It refuses to overwrite either an export or a truth artifact.
"""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulator.core.export import write_export
from simulator.scenarios.registry import SCENARIO_GENERATORS


def main() -> None:
    root = Path(__file__).resolve().parent
    pending = []
    for scenario, generate in SCENARIO_GENERATORS.items():
        for seed in (4, 5, 6):
            dataset = generate(seed)
            if not dataset.manifest.scenario_id.startswith("scn_"):
                raise ValueError(f"non-opaque scenario ID for {scenario}/{seed}")
            export = root / "exports" / dataset.manifest.scenario_id / f"seed_{seed}" / "export"
            truth = root / "sim_truth" / scenario / f"seed_{seed}.truth.json"
            if export.exists() or truth.exists():
                raise FileExistsError(f"refusing to overwrite P5 input: {scenario}/{seed}")
            pending.append((scenario, seed, dataset, export, truth))

    for scenario, seed, dataset, export, truth in pending:
        write_export(dataset, export, truth)
        print(f"generated {scenario} seed={seed} id={dataset.manifest.scenario_id}")


if __name__ == "__main__":
    main()
