"""Materialize the frozen P9 confirmation block; runs no Inquest stages."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulator.core.export import write_export
from simulator.scenarios.registry import SCENARIO_GENERATORS

SEEDS = range(52, 72)


def main() -> None:
    root=Path(__file__).resolve().parent
    pending=[]
    ids=set()
    for family,generator in SCENARIO_GENERATORS.items():
        for seed in SEEDS:
            data=generator(seed)
            sid=data.manifest.scenario_id
            if not sid.startswith("scn_") or len(sid)!=16 or sid in ids:
                raise ValueError(f"scenario ID is not unique and opaque: {family}/{seed}/{sid}")
            ids.add(sid)
            export=root/"p9_inputs"/sid/f"seed_{seed}"/"export"
            truth=root/"sim_truth"/family/f"seed_{seed}.truth.json"
            if export.exists() or truth.exists():
                raise FileExistsError(f"refusing to overwrite P9 confirmation input {family}/{seed}")
            pending.append((data,export,truth))
    if len(pending)!=len(SCENARIO_GENERATORS)*len(SEEDS):
        raise AssertionError(f"expected 280 inputs, found {len(pending)}")
    for data,export,truth in pending:
        write_export(data,export,truth)
    print(f"Generated {len(pending)} P9 confirmation inputs (14 families × seeds 52–71)")


if __name__=="__main__": main()
