"""Generate the P10 fresh confidence-calibration evaluation block only."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulator.core.export import write_export
from simulator.scenarios.registry import SCENARIO_GENERATORS

SEEDS=range(72,92)


def main()->None:
    root=Path(__file__).resolve().parent
    pending=[]; seen=set()
    for family,generator in SCENARIO_GENERATORS.items():
        for seed in SEEDS:
            data=generator(seed); scenario_id=data.manifest.scenario_id
            if not scenario_id.startswith("scn_") or len(scenario_id)!=16 or scenario_id in seen:
                raise ValueError(f"invalid or colliding opaque scenario ID at {family}/{seed}")
            seen.add(scenario_id)
            export=root/"p10_inputs"/scenario_id/f"seed_{seed}"/"export"
            truth=root/"sim_truth"/family/f"seed_{seed}.truth.json"
            if export.exists() or truth.exists():
                raise FileExistsError(f"refusing to overwrite P10 input {family}/{seed}")
            pending.append((data,export,truth))
    if len(pending)!=280: raise AssertionError(f"expected 280 inputs; got {len(pending)}")
    for data,export,truth in pending: write_export(data,export,truth)
    print("Generated 280 P10 evaluation inputs for seeds 72–91; no stages were run.")


if __name__=="__main__": main()
