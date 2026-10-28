"""Explicit scenario registry; holdout is intentionally never imported here."""

from simulator.scenarios.clean_bad_deploy.model import generate as clean_bad_deploy
from simulator.scenarios.coincident_restart import generate as coincident_restart
from simulator.scenarios.red_herring_deploy import generate as red_herring_deploy
from simulator.scenarios.shared_dependency import generate as shared_dependency
from simulator.scenarios.missing_telemetry import generate as missing_telemetry
from simulator.scenarios.long_seasonal import generate as long_seasonal
from simulator.scenarios.late_alerting_cause import generate as late_alerting_cause
from simulator.scenarios.silent_cause import generate as silent_cause

SCENARIO_GENERATORS = {
    "clean_bad_deploy": clean_bad_deploy,
    "coincident_restart": coincident_restart,
    "red_herring_deploy": red_herring_deploy,
    "shared_dependency": shared_dependency,
    "missing_telemetry": missing_telemetry,
    "long_seasonal": long_seasonal,
    "late_alerting_cause": late_alerting_cause,
    "silent_cause": silent_cause,
}
DEFAULT_EVAL_SCENARIOS = tuple(SCENARIO_GENERATORS)
