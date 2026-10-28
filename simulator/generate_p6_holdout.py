"""Materialize the user-selected P6 seeds without running analysis stages."""
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
        for seed in (7, 8, 9):
            dataset = generate(seed)
            if not dataset.manifest.scenario_id.startswith("scn_"):
                raise ValueError(f"non-opaque scenario ID for {scenario}/{seed}")
            export = root / "exports" / dataset.manifest.scenario_id / f"seed_{seed}" / "export"
            truth = root / "sim_truth" / scenario / f"seed_{seed}.truth.json"
            if export.exists() or truth.exists():
                raise FileExistsError(f"refusing to overwrite P6 holdout input: {scenario}/{seed}")
            pending.append((scenario, seed, dataset, export, truth))

    for scenario, seed, dataset, export, truth in pending:
        write_export(dataset, export, truth)
        print(f"generated {scenario} seed={seed} id={dataset.manifest.scenario_id}")


if __name__ == "__main__":
    main()
