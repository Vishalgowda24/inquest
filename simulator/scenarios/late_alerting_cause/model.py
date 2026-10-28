from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="late_alerting_cause", fault_service="database", fault_start=10,
    fault_intensity=1.35, fault_metric_visibility_delay=5,
    description="Database saturation propagates immediately, but the database metric alert is delayed by five windows.",
)


def generate(seed: int):
    return build(SPEC, seed)
