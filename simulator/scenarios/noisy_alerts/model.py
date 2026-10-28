import random

from simulator.contracts import LogEvent
from simulator.scenarios.factory import ScenarioSpec, generate as build
from simulator.scenarios.clean_bad_deploy.model import SERVICES, _timestamp

SPEC = ScenarioSpec(
    key="noisy_alerts", fault_service="database", fault_start=10,
    fault_intensity=1.4, fault_threshold=42,
    description="A real database fault is obscured by randomly ordered alerts and healthy-service false alerts.",
)


def generate(seed: int):
    data = build(SPEC, seed)
    rng = random.Random(seed ^ 0x5A17)
    # Every service emits one alert at a seeded random time, irrespective of
    # whether it is healthy. Raw metrics and spans remain untouched.
    alert_logs = []
    schedule = {service: rng.randrange(5, 16) for service in SERVICES}
    for index, service in enumerate(SERVICES, start=1):
        alert_logs.append(LogEvent(
            id=f"alert-{seed}-{index}", timestamp=_timestamp(schedule[service]),
            service=service, level="WARN", message="synthetic alert emitted",
            attributes={"alert_emission": True}, timestamp_uncertainty_ms=0,
        ))
    logs = tuple(sorted((*data.logs, *alert_logs), key=lambda item: (item.timestamp, item.id)))
    truth = {**data.truth, "alert_schedule": schedule, "spurious_alert_services": [s for s in SERVICES if s != "database"]}
    manifest = data.manifest.model_copy(update={"record_counts": {**data.manifest.record_counts, "logs": len(logs)}})
    return data.__class__(manifest, data.metrics, data.spans, logs, data.events, data.dependencies, truth)
