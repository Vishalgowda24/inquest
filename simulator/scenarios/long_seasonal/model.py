from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="long_seasonal", fault_service="database", fault_start=52,
    fault_intensity=1.35, steps=72,
    changes=(("deployment", "database", 52, "db-release-11"),),
    description="A 72-hour seasonal observation includes two complete diurnal cycles before a database degradation.",
)


def generate(seed: int):
    return build(SPEC, seed)
