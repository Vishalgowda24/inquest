from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="red_herring_hard", fault_service="payments", fault_start=9,
    fault_intensity=1.45, fault_threshold=22,
    changes=(
        ("configuration_change", "payments", 8, "payments-timeout-hard"),
        ("deployment", "inventory", 7, "inventory-release-decoy"),
    ),
    description="A payments configuration fault overlaps an unrelated inventory deploy; database is a shared-ancestry graph decoy.",
)


def generate(seed: int):
    return build(SPEC, seed)
