from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="silent_cause", fault_service="database", fault_start=10,
    fault_intensity=1.35, suppress_metric_services=frozenset({"database"}),
    description="Database saturation propagates through callers while the database metric stream is silent.",
)


def generate(seed: int):
    return build(SPEC, seed)
