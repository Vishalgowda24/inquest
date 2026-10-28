"""Generate the frozen P7 variance inputs (no Inquest stages are run here)."""
from __future__ import annotations

import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulator.core.export import write_export
from simulator.scenarios.registry import SCENARIO_GENERATORS

SEEDS = range(10, 30)
PREVIOUSLY_EVALUATED_FAMILIES = {
    "concurrent_causes", "noisy_alerts", "partial_graph", "red_herring_hard"
}
OPAQUE_ID = re.compile(r"^scn_[a-f0-9]{12}$")


def main() -> None:
    simulator_root = Path(__file__).resolve().parent
    input_root = simulator_root / "variance_inputs"
    pending = []
    seen_ids: set[str] = set()
    for scenario, generate in SCENARIO_GENERATORS.items():
        family_seeds = [seed for seed in SEEDS if not (scenario in PREVIOUSLY_EVALUATED_FAMILIES and seed in {11, 29})]
        if scenario in PREVIOUSLY_EVALUATED_FAMILIES:
            family_seeds.extend((30, 31))
        for seed in family_seeds:
            dataset = generate(seed)
            scenario_id = dataset.manifest.scenario_id
            if not OPAQUE_ID.fullmatch(scenario_id):
                raise ValueError(f"scenario ID is not opaque: {scenario}/{seed}")
            if scenario_id in seen_ids:
                raise ValueError(f"scenario ID collision: {scenario_id}")
            seen_ids.add(scenario_id)
            export = input_root / scenario_id / f"seed_{seed}" / "export"
            truth = simulator_root / "sim_truth" / scenario / f"seed_{seed}.truth.json"
            if export.exists() or truth.exists():
                raise FileExistsError(f"refusing to overwrite P7 input: {scenario}/{seed}")
            pending.append((scenario, seed, dataset, export, truth))

    for scenario, seed, dataset, export, truth in pending:
        write_export(dataset, export, truth)
    if len(pending) != 240:
        raise AssertionError(f"expected 240 fresh cases; found {len(pending)}")
    print(f"Generated {len(pending)} frozen inputs in {input_root.relative_to(simulator_root)}")


if __name__ == "__main__":
    main()
