from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="shared_dependency", fault_service="database", fault_start=10,
    fault_intensity=1.5, fault_threshold=42,
    description="A shared database dependency saturates without a deployment or configuration event.",
)


def generate(seed: int):
    return build(SPEC, seed)
