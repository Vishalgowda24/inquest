from simulator.scenarios.factory import ScenarioSpec, generate as build

SPEC = ScenarioSpec(
    key="concurrent_causes",
    fault_service="payments", fault_start=8, fault_intensity=1.5, fault_threshold=22,
    additional_faults=(("inventory", 10, None, 1.45, 16),),
    changes=(
        ("configuration_change", "payments", 7, "payments-timeout-concurrent"),
        ("configuration_change", "inventory", 9, "inventory-capacity-concurrent"),
    ),
    description="Two independent overlapping service-local faults affect payments and inventory.",
)


def generate(seed: int):
    return build(SPEC, seed)
