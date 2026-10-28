from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="partial_graph", fault_service="database", fault_start=10,
    fault_intensity=1.4, fault_threshold=42,
    description="The true graph propagates a database fault, but one declared edge is missing.",
)


def generate(seed: int):
    return build(SPEC, seed)
