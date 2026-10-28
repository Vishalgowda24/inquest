from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="red_herring_deploy", fault_service="payments", fault_start=9,
    fault_intensity=1.4, fault_threshold=22,
    changes=(
        ("configuration_change", "payments", 7, "payments-timeout-3"),
        ("deployment", "inventory", 8, "inventory-release-9"),
    ),
    description="An unrelated inventory deployment precedes a payments configuration fault.",
)


def generate(seed: int):
    return build(SPEC, seed)
