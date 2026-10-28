from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="coincident_restart", fault_service="database", fault_start=10, fault_end=16,
    fault_intensity=1.35, changes=(
        ("configuration_change", "database", 10, "db-config-17"),
        ("restart", "database", 16, "db-restart-4"),
    ),
    description="A database configuration change causes saturation; a later restart restores the prior behavior.",
)


def generate(seed: int):
    return build(SPEC, seed)
