"""Generate P8 alert-order audit inputs; this does not run Inquest stages."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulator.core.export import write_export
from simulator.scenarios.registry import SCENARIO_GENERATORS

FAMILIES = ("cause_alerts_2_4", "unordered_plausible_alerts")
SEEDS = range(32, 52)


def main() -> None:
    root = Path(__file__).resolve().parent
    pending = []
    for family in FAMILIES:
        generator = SCENARIO_GENERATORS[family]
        for seed in SEEDS:
            data = generator(seed)
            sid = data.manifest.scenario_id
            export = root / "audit_inputs" / sid / f"seed_{seed}" / "export"
            truth = root / "sim_truth" / family / f"seed_{seed}.truth.json"
            if export.exists() or truth.exists():
                raise FileExistsError(f"refusing to overwrite P8 audit input {family}/{seed}")
            pending.append((family, seed, data, export, truth))
    if len(pending) != 40:
        raise AssertionError(f"expected 40 cases, got {len(pending)}")
    for family, seed, data, export, truth in pending:
        write_export(data, export, truth)
    print(f"Generated {len(pending)} P8 audit inputs for seeds 32–51")


if __name__ == "__main__":
    main()
