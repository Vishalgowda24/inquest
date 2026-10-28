"""Explicit scenario registry; holdout is intentionally never imported here."""

from simulator.scenarios.clean_bad_deploy.model import generate as clean_bad_deploy
from simulator.scenarios.coincident_restart import generate as coincident_restart
from simulator.scenarios.red_herring_deploy import generate as red_herring_deploy
from simulator.scenarios.shared_dependency import generate as shared_dependency
from simulator.scenarios.missing_telemetry import generate as missing_telemetry
from simulator.scenarios.long_seasonal import generate as long_seasonal
from simulator.scenarios.late_alerting_cause import generate as late_alerting_cause
from simulator.scenarios.silent_cause import generate as silent_cause
from simulator.scenarios.concurrent_causes import generate as concurrent_causes
from simulator.scenarios.noisy_alerts import generate as noisy_alerts
from simulator.scenarios.partial_graph import generate as partial_graph
from simulator.scenarios.red_herring_hard import generate as red_herring_hard
from simulator.scenarios.cause_alerts_2_4 import generate as cause_alerts_2_4
from simulator.scenarios.unordered_plausible_alerts import generate as unordered_plausible_alerts

SCENARIO_GENERATORS = {
    "clean_bad_deploy": clean_bad_deploy,
    "coincident_restart": coincident_restart,
    "red_herring_deploy": red_herring_deploy,
    "shared_dependency": shared_dependency,
    "missing_telemetry": missing_telemetry,
    "long_seasonal": long_seasonal,
    "late_alerting_cause": late_alerting_cause,
    "silent_cause": silent_cause,
    "concurrent_causes": concurrent_causes,
    "noisy_alerts": noisy_alerts,
    "partial_graph": partial_graph,
    "red_herring_hard": red_herring_hard,
    "cause_alerts_2_4": cause_alerts_2_4,
    "unordered_plausible_alerts": unordered_plausible_alerts,
}
DEFAULT_EVAL_SCENARIOS = tuple(SCENARIO_GENERATORS)
