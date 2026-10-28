from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="missing_telemetry", fault_service="database", fault_start=10,
    fault_intensity=1.35,
    changes=(("configuration_change", "database", 10, "db-pool-limit-2"),),
    missing_windows={"checkout": set(range(7, 14))},
    no_trace_services=frozenset({"inventory"}),
    description="Database saturation propagates while inventory traces and a long checkout metric interval are absent.",
)


def generate(seed: int):
    return build(SPEC, seed)
