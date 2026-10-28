# Simulator and signal summary

Seed `1` produces export ID `scn_97c7c6c85675` in this checkout. The value is a salted HMAC and cannot be decoded into the scenario name; the salt and truth are stored only in `simulator/sim_truth/`. An export scan found no scenario name or injected fault type.

## Checkout latency observations

The simulator samples 20 hourly windows. Two checkout latency windows are absent; the ingester preserves them as coverage gaps. Across the 18 observed windows, checkout latency averages **62.91 ms**, ranges from **54.84 to 82.66 ms**, and has a population standard deviation of **8.53 ms**. This combines generated diurnal load, graph-propagated degradation, and seeded jitter. Checkout source timestamps carry **800 ms** clock uncertainty.

This is a generated time series, not a per-service outcome fixture: each service's values are computed from load, its local parameters, and the preceding dependency state. The fault-sensitivity pytest changes database fault intensity while holding the seed fixed and verifies downstream metric changes. Three additional seeded tests recover the database -> payments -> checkout latency onset order within each onset's clock/gap uncertainty.

S02 reports CUSUM in the current dependency set. The 20-hour window is shorter than two 24-hour cycles, so the baseline's seasonal normalization is deliberately skipped and recorded as a warning. The clean seed reports 9 service/metric onset records and explicit coverage gaps; no missing windows are filled in.
