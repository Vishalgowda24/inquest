"""The frozen P10 seed block is complete, opaque, and truth-separated."""
import json
from pathlib import Path

from simulator.scenarios.registry import SCENARIO_GENERATORS


def test_p10_evaluation_inputs_are_committed_and_truth_separated():
    root=Path(__file__).resolve().parents[1]
    count=0
    for family in SCENARIO_GENERATORS:
        for seed in range(72,92):
            truth_path=root/"sim_truth"/family/f"seed_{seed}.truth.json"
            truth=json.loads(truth_path.read_text(encoding="utf-8"))
            scenario_id=truth["scenario_id"]
            assert scenario_id.startswith("scn_") and len(scenario_id)==16
            export=root/"p10_inputs"/scenario_id/f"seed_{seed}"/"export"
            assert export.is_dir()
            texts="\n".join(path.read_text(encoding="utf-8") for path in export.rglob("*") if path.is_file())
            assert family not in texts
            assert "scenario_name" not in texts and "injected_fault" not in texts
            count+=1
    assert count==280
