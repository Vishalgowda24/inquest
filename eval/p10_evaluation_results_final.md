# P10 Calibrated Confidence Evaluation — Complete Tables

Run commit: `b4aba98866ff0d8609012c0a4566fc43628f1456`  
Config SHA-256: `ffd51fba3632b0f1dbe9db77ff749dfce060a2fed19df25e7b6386241a147fc5`  
Confidence model SHA-256: `179410b35f45c93f741d6805314aa948d6e1a1df4c53cee1f92665341670090f`  
Primary: seeds 72–91 (280 cases). Secondary: seeds 52–71 (280 cases), not used for fitting. Holdout seeds 7–9 were not run.

## Primary fresh evaluation: seeds 72–91

### Per-family calibration and selective accuracy

| Family | n | Accuracy | Mean p | Cal Brier/ECE | Const Brier/ECE | Margin Brier/ECE | High | Med | Low | Insuff | Selective coverage | Selective accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cause_alerts_2_4 | 20 | 0.950 | 0.936 | 0.047/0.014 | 0.048/0.014 | 0.048/0.015 | 14 | 0 | 0 | 6 | 0.700 | 0.9285714285714286 |
| clean_bad_deploy | 20 | 1.000 | 0.942 | 0.003/0.058 | 0.004/0.064 | 0.004/0.065 | 13 | 0 | 0 | 7 | 0.650 | 1.0 |
| coincident_restart | 20 | 0.900 | 0.941 | 0.090/0.041 | 0.091/0.036 | 0.091/0.035 | 14 | 0 | 0 | 6 | 0.700 | 0.8571428571428571 |
| concurrent_causes | 20 | 1.000 | 0.938 | 0.004/0.062 | 0.004/0.064 | 0.004/0.063 | 15 | 0 | 0 | 5 | 0.750 | 1.0 |
| late_alerting_cause | 20 | 0.950 | 0.931 | 0.048/0.019 | 0.048/0.014 | 0.048/0.015 | 13 | 0 | 0 | 7 | 0.650 | 0.9230769230769231 |
| long_seasonal | 20 | 0.750 | 0.934 | 0.216/0.184 | 0.222/0.186 | 0.222/0.185 | 1 | 0 | 0 | 19 | 0.050 | 1.0 |
| missing_telemetry | 20 | 1.000 | 0.946 | 0.003/0.054 | 0.004/0.064 | 0.004/0.065 | 13 | 0 | 0 | 7 | 0.650 | 1.0 |
| noisy_alerts | 20 | 0.950 | 0.936 | 0.047/0.014 | 0.048/0.014 | 0.048/0.015 | 14 | 0 | 0 | 6 | 0.700 | 0.9285714285714286 |
| partial_graph | 20 | 0.950 | 0.932 | 0.047/0.018 | 0.048/0.014 | 0.048/0.015 | 14 | 0 | 0 | 6 | 0.700 | 0.9285714285714286 |
| red_herring_deploy | 20 | 1.000 | 0.937 | 0.004/0.063 | 0.004/0.064 | 0.004/0.063 | 15 | 0 | 0 | 5 | 0.750 | 1.0 |
| red_herring_hard | 20 | 1.000 | 0.937 | 0.004/0.063 | 0.004/0.064 | 0.004/0.064 | 15 | 0 | 0 | 5 | 0.750 | 1.0 |
| shared_dependency | 20 | 0.950 | 0.935 | 0.047/0.015 | 0.048/0.014 | 0.048/0.015 | 14 | 0 | 0 | 6 | 0.700 | 0.9285714285714286 |
| silent_cause | 20 | 0.350 | 0.924 | 0.555/0.574 | 0.570/0.586 | 0.570/0.585 | 16 | 0 | 0 | 4 | 0.800 | 0.4375 |
| unordered_plausible_alerts | 20 | 0.950 | 0.936 | 0.047/0.014 | 0.048/0.014 | 0.048/0.015 | 14 | 0 | 0 | 6 | 0.700 | 0.9285714285714286 |

### Overall calibration scores

| Confidence model | Cases | Brier | ECE | Mean probability |
|---|---:|---:|---:|---:|
| calibrated | 280 | 0.0831 | 0.0289 | 0.9361 |
| constant | 280 | 0.0850 | 0.0284 | 0.9356 |
| margin_only | 280 | 0.0850 | 0.0284 | 0.9355 |

### Reliability table (fixed ten probability bins)

| Model | Bin | n | Mean probability | Empirical accuracy |
|---|---|---:|---:|---:|
| calibrated | [0.0,0.1) | 0 | — | — |
| calibrated | [0.1,0.2) | 0 | — | — |
| calibrated | [0.2,0.3) | 0 | — | — |
| calibrated | [0.3,0.4) | 0 | — | — |
| calibrated | [0.4,0.5) | 0 | — | — |
| calibrated | [0.5,0.6) | 0 | — | — |
| calibrated | [0.6,0.7) | 0 | — | — |
| calibrated | [0.7,0.8) | 0 | — | — |
| calibrated | [0.8,0.9) | 0 | — | — |
| calibrated | [0.9,1.0] | 280 | 0.9360658593364152 | 0.9071428571428571 |
| constant | [0.0,0.1) | 0 | — | — |
| constant | [0.1,0.2) | 0 | — | — |
| constant | [0.2,0.3) | 0 | — | — |
| constant | [0.3,0.4) | 0 | — | — |
| constant | [0.4,0.5) | 0 | — | — |
| constant | [0.5,0.6) | 0 | — | — |
| constant | [0.6,0.7) | 0 | — | — |
| constant | [0.7,0.8) | 0 | — | — |
| constant | [0.8,0.9) | 0 | — | — |
| constant | [0.9,1.0] | 280 | 0.9355670103092785 | 0.9071428571428571 |
| margin_only | [0.0,0.1) | 0 | — | — |
| margin_only | [0.1,0.2) | 0 | — | — |
| margin_only | [0.2,0.3) | 0 | — | — |
| margin_only | [0.3,0.4) | 0 | — | — |
| margin_only | [0.4,0.5) | 0 | — | — |
| margin_only | [0.5,0.6) | 0 | — | — |
| margin_only | [0.6,0.7) | 0 | — | — |
| margin_only | [0.7,0.8) | 0 | — | — |
| margin_only | [0.8,0.9) | 0 | — | — |
| margin_only | [0.9,1.0] | 280 | 0.9355037201843678 | 0.9071428571428571 |

### Confidence-level accuracy and coverage

| Model | Level | n | Coverage | Top-1 accuracy |
|---|---|---:|---:|---:|
| calibrated | high | 185 | 0.661 | 0.9081081081081082 |
| calibrated | medium | 0 | 0.000 | n/a |
| calibrated | low | 0 | 0.000 | n/a |
| calibrated | insufficient_evidence | 95 | 0.339 | 0.9052631578947369 |
| calibrated | selective | 185 | 0.661 | 0.9081081081081082 |
| constant | high | 185 | 0.661 | 0.9081081081081082 |
| constant | medium | 0 | 0.000 | n/a |
| constant | low | 0 | 0.000 | n/a |
| constant | insufficient_evidence | 95 | 0.339 | 0.9052631578947369 |
| constant | selective | 185 | 0.661 | 0.9081081081081082 |
| margin_only | high | 185 | 0.661 | 0.9081081081081082 |
| margin_only | medium | 0 | 0.000 | n/a |
| margin_only | low | 0 | 0.000 | n/a |
| margin_only | insufficient_evidence | 95 | 0.339 | 0.9052631578947369 |
| margin_only | selective | 185 | 0.661 | 0.9081081081081082 |

### High-confidence wrong cases

| Family | Seed | True cause(s) | Top candidate | Probability |
|---|---:|---|---|---:|
| coincident_restart | 75 | database | payments | 0.931 |
| coincident_restart | 85 | database | inventory | 0.936 |
| shared_dependency | 85 | database | inventory | 0.931 |
| late_alerting_cause | 75 | database | payments | 0.927 |
| silent_cause | 72 | database | payments | 0.919 |
| silent_cause | 75 | database | payments | 0.919 |
| silent_cause | 77 | database | payments | 0.929 |
| silent_cause | 82 | database | inventory | 0.927 |
| silent_cause | 83 | database | inventory | 0.921 |
| silent_cause | 85 | database | payments | 0.927 |
| silent_cause | 86 | database | payments | 0.921 |
| silent_cause | 88 | database | payments | 0.919 |
| silent_cause | 89 | database | payments | 0.925 |
| noisy_alerts | 85 | database | inventory | 0.931 |
| partial_graph | 85 | database | inventory | 0.923 |
| cause_alerts_2_4 | 85 | database | inventory | 0.931 |
| unordered_plausible_alerts | 85 | database | inventory | 0.931 |

### Silent, late-alert, and red-herring cases

| Family | n | Accuracy | Mean probability | Probability overstated? | High | High and wrong |
|---|---:|---:|---:|---|---:|---:|
| silent_cause | 20 | 0.35 | 0.9244491471083197 | yes | 16 | 9 |
| late_alerting_cause | 20 | 0.95 | 0.9307395719143695 | no | 13 | 1 |
| red_herring_deploy | 20 | 1.0 | 0.9366525057531512 | no | 15 | 0 |


### Per-family confidence-level accuracy and coverage

| Family | Model | Level | n | Coverage | Top-1 accuracy |
|---|---|---|---:|---:|---:|
| cause_alerts_2_4 | calibrated | high | 14 | 0.700 | 0.929 |
| cause_alerts_2_4 | calibrated | medium | 0 | 0.000 | n/a |
| cause_alerts_2_4 | calibrated | low | 0 | 0.000 | n/a |
| cause_alerts_2_4 | calibrated | insufficient_evidence | 6 | 0.300 | 1.000 |
| cause_alerts_2_4 | constant | high | 14 | 0.700 | 0.929 |
| cause_alerts_2_4 | constant | medium | 0 | 0.000 | n/a |
| cause_alerts_2_4 | constant | low | 0 | 0.000 | n/a |
| cause_alerts_2_4 | constant | insufficient_evidence | 6 | 0.300 | 1.000 |
| cause_alerts_2_4 | margin_only | high | 14 | 0.700 | 0.929 |
| cause_alerts_2_4 | margin_only | medium | 0 | 0.000 | n/a |
| cause_alerts_2_4 | margin_only | low | 0 | 0.000 | n/a |
| cause_alerts_2_4 | margin_only | insufficient_evidence | 6 | 0.300 | 1.000 |
| clean_bad_deploy | calibrated | high | 13 | 0.650 | 1.000 |
| clean_bad_deploy | calibrated | medium | 0 | 0.000 | n/a |
| clean_bad_deploy | calibrated | low | 0 | 0.000 | n/a |
| clean_bad_deploy | calibrated | insufficient_evidence | 7 | 0.350 | 1.000 |
| clean_bad_deploy | constant | high | 13 | 0.650 | 1.000 |
| clean_bad_deploy | constant | medium | 0 | 0.000 | n/a |
| clean_bad_deploy | constant | low | 0 | 0.000 | n/a |
| clean_bad_deploy | constant | insufficient_evidence | 7 | 0.350 | 1.000 |
| clean_bad_deploy | margin_only | high | 13 | 0.650 | 1.000 |
| clean_bad_deploy | margin_only | medium | 0 | 0.000 | n/a |
| clean_bad_deploy | margin_only | low | 0 | 0.000 | n/a |
| clean_bad_deploy | margin_only | insufficient_evidence | 7 | 0.350 | 1.000 |
| coincident_restart | calibrated | high | 14 | 0.700 | 0.857 |
| coincident_restart | calibrated | medium | 0 | 0.000 | n/a |
| coincident_restart | calibrated | low | 0 | 0.000 | n/a |
| coincident_restart | calibrated | insufficient_evidence | 6 | 0.300 | 1.000 |
| coincident_restart | constant | high | 14 | 0.700 | 0.857 |
| coincident_restart | constant | medium | 0 | 0.000 | n/a |
| coincident_restart | constant | low | 0 | 0.000 | n/a |
| coincident_restart | constant | insufficient_evidence | 6 | 0.300 | 1.000 |
| coincident_restart | margin_only | high | 14 | 0.700 | 0.857 |
| coincident_restart | margin_only | medium | 0 | 0.000 | n/a |
| coincident_restart | margin_only | low | 0 | 0.000 | n/a |
| coincident_restart | margin_only | insufficient_evidence | 6 | 0.300 | 1.000 |
| concurrent_causes | calibrated | high | 15 | 0.750 | 1.000 |
| concurrent_causes | calibrated | medium | 0 | 0.000 | n/a |
| concurrent_causes | calibrated | low | 0 | 0.000 | n/a |
| concurrent_causes | calibrated | insufficient_evidence | 5 | 0.250 | 1.000 |
| concurrent_causes | constant | high | 15 | 0.750 | 1.000 |
| concurrent_causes | constant | medium | 0 | 0.000 | n/a |
| concurrent_causes | constant | low | 0 | 0.000 | n/a |
| concurrent_causes | constant | insufficient_evidence | 5 | 0.250 | 1.000 |
| concurrent_causes | margin_only | high | 15 | 0.750 | 1.000 |
| concurrent_causes | margin_only | medium | 0 | 0.000 | n/a |
| concurrent_causes | margin_only | low | 0 | 0.000 | n/a |
| concurrent_causes | margin_only | insufficient_evidence | 5 | 0.250 | 1.000 |
| late_alerting_cause | calibrated | high | 13 | 0.650 | 0.923 |
| late_alerting_cause | calibrated | medium | 0 | 0.000 | n/a |
| late_alerting_cause | calibrated | low | 0 | 0.000 | n/a |
| late_alerting_cause | calibrated | insufficient_evidence | 7 | 0.350 | 1.000 |
| late_alerting_cause | constant | high | 13 | 0.650 | 0.923 |
| late_alerting_cause | constant | medium | 0 | 0.000 | n/a |
| late_alerting_cause | constant | low | 0 | 0.000 | n/a |
| late_alerting_cause | constant | insufficient_evidence | 7 | 0.350 | 1.000 |
| late_alerting_cause | margin_only | high | 13 | 0.650 | 0.923 |
| late_alerting_cause | margin_only | medium | 0 | 0.000 | n/a |
| late_alerting_cause | margin_only | low | 0 | 0.000 | n/a |
| late_alerting_cause | margin_only | insufficient_evidence | 7 | 0.350 | 1.000 |
| long_seasonal | calibrated | high | 1 | 0.050 | 1.000 |
| long_seasonal | calibrated | medium | 0 | 0.000 | n/a |
| long_seasonal | calibrated | low | 0 | 0.000 | n/a |
| long_seasonal | calibrated | insufficient_evidence | 19 | 0.950 | 0.737 |
| long_seasonal | constant | high | 1 | 0.050 | 1.000 |
| long_seasonal | constant | medium | 0 | 0.000 | n/a |
| long_seasonal | constant | low | 0 | 0.000 | n/a |
| long_seasonal | constant | insufficient_evidence | 19 | 0.950 | 0.737 |
| long_seasonal | margin_only | high | 1 | 0.050 | 1.000 |
| long_seasonal | margin_only | medium | 0 | 0.000 | n/a |
| long_seasonal | margin_only | low | 0 | 0.000 | n/a |
| long_seasonal | margin_only | insufficient_evidence | 19 | 0.950 | 0.737 |
| missing_telemetry | calibrated | high | 13 | 0.650 | 1.000 |
| missing_telemetry | calibrated | medium | 0 | 0.000 | n/a |
| missing_telemetry | calibrated | low | 0 | 0.000 | n/a |
| missing_telemetry | calibrated | insufficient_evidence | 7 | 0.350 | 1.000 |
| missing_telemetry | constant | high | 13 | 0.650 | 1.000 |
| missing_telemetry | constant | medium | 0 | 0.000 | n/a |
| missing_telemetry | constant | low | 0 | 0.000 | n/a |
| missing_telemetry | constant | insufficient_evidence | 7 | 0.350 | 1.000 |
| missing_telemetry | margin_only | high | 13 | 0.650 | 1.000 |
| missing_telemetry | margin_only | medium | 0 | 0.000 | n/a |
| missing_telemetry | margin_only | low | 0 | 0.000 | n/a |
| missing_telemetry | margin_only | insufficient_evidence | 7 | 0.350 | 1.000 |
| noisy_alerts | calibrated | high | 14 | 0.700 | 0.929 |
| noisy_alerts | calibrated | medium | 0 | 0.000 | n/a |
| noisy_alerts | calibrated | low | 0 | 0.000 | n/a |
| noisy_alerts | calibrated | insufficient_evidence | 6 | 0.300 | 1.000 |
| noisy_alerts | constant | high | 14 | 0.700 | 0.929 |
| noisy_alerts | constant | medium | 0 | 0.000 | n/a |
| noisy_alerts | constant | low | 0 | 0.000 | n/a |
| noisy_alerts | constant | insufficient_evidence | 6 | 0.300 | 1.000 |
| noisy_alerts | margin_only | high | 14 | 0.700 | 0.929 |
| noisy_alerts | margin_only | medium | 0 | 0.000 | n/a |
| noisy_alerts | margin_only | low | 0 | 0.000 | n/a |
| noisy_alerts | margin_only | insufficient_evidence | 6 | 0.300 | 1.000 |
| partial_graph | calibrated | high | 14 | 0.700 | 0.929 |
| partial_graph | calibrated | medium | 0 | 0.000 | n/a |
| partial_graph | calibrated | low | 0 | 0.000 | n/a |
| partial_graph | calibrated | insufficient_evidence | 6 | 0.300 | 1.000 |
| partial_graph | constant | high | 14 | 0.700 | 0.929 |
| partial_graph | constant | medium | 0 | 0.000 | n/a |
| partial_graph | constant | low | 0 | 0.000 | n/a |
| partial_graph | constant | insufficient_evidence | 6 | 0.300 | 1.000 |
| partial_graph | margin_only | high | 14 | 0.700 | 0.929 |
| partial_graph | margin_only | medium | 0 | 0.000 | n/a |
| partial_graph | margin_only | low | 0 | 0.000 | n/a |
| partial_graph | margin_only | insufficient_evidence | 6 | 0.300 | 1.000 |
| red_herring_deploy | calibrated | high | 15 | 0.750 | 1.000 |
| red_herring_deploy | calibrated | medium | 0 | 0.000 | n/a |
| red_herring_deploy | calibrated | low | 0 | 0.000 | n/a |
| red_herring_deploy | calibrated | insufficient_evidence | 5 | 0.250 | 1.000 |
| red_herring_deploy | constant | high | 15 | 0.750 | 1.000 |
| red_herring_deploy | constant | medium | 0 | 0.000 | n/a |
| red_herring_deploy | constant | low | 0 | 0.000 | n/a |
| red_herring_deploy | constant | insufficient_evidence | 5 | 0.250 | 1.000 |
| red_herring_deploy | margin_only | high | 15 | 0.750 | 1.000 |
| red_herring_deploy | margin_only | medium | 0 | 0.000 | n/a |
| red_herring_deploy | margin_only | low | 0 | 0.000 | n/a |
| red_herring_deploy | margin_only | insufficient_evidence | 5 | 0.250 | 1.000 |
| red_herring_hard | calibrated | high | 15 | 0.750 | 1.000 |
| red_herring_hard | calibrated | medium | 0 | 0.000 | n/a |
| red_herring_hard | calibrated | low | 0 | 0.000 | n/a |
| red_herring_hard | calibrated | insufficient_evidence | 5 | 0.250 | 1.000 |
| red_herring_hard | constant | high | 15 | 0.750 | 1.000 |
| red_herring_hard | constant | medium | 0 | 0.000 | n/a |
| red_herring_hard | constant | low | 0 | 0.000 | n/a |
| red_herring_hard | constant | insufficient_evidence | 5 | 0.250 | 1.000 |
| red_herring_hard | margin_only | high | 15 | 0.750 | 1.000 |
| red_herring_hard | margin_only | medium | 0 | 0.000 | n/a |
| red_herring_hard | margin_only | low | 0 | 0.000 | n/a |
| red_herring_hard | margin_only | insufficient_evidence | 5 | 0.250 | 1.000 |
| shared_dependency | calibrated | high | 14 | 0.700 | 0.929 |
| shared_dependency | calibrated | medium | 0 | 0.000 | n/a |
| shared_dependency | calibrated | low | 0 | 0.000 | n/a |
| shared_dependency | calibrated | insufficient_evidence | 6 | 0.300 | 1.000 |
| shared_dependency | constant | high | 14 | 0.700 | 0.929 |
| shared_dependency | constant | medium | 0 | 0.000 | n/a |
| shared_dependency | constant | low | 0 | 0.000 | n/a |
| shared_dependency | constant | insufficient_evidence | 6 | 0.300 | 1.000 |
| shared_dependency | margin_only | high | 14 | 0.700 | 0.929 |
| shared_dependency | margin_only | medium | 0 | 0.000 | n/a |
| shared_dependency | margin_only | low | 0 | 0.000 | n/a |
| shared_dependency | margin_only | insufficient_evidence | 6 | 0.300 | 1.000 |
| silent_cause | calibrated | high | 16 | 0.800 | 0.438 |
| silent_cause | calibrated | medium | 0 | 0.000 | n/a |
| silent_cause | calibrated | low | 0 | 0.000 | n/a |
| silent_cause | calibrated | insufficient_evidence | 4 | 0.200 | 0.000 |
| silent_cause | constant | high | 16 | 0.800 | 0.438 |
| silent_cause | constant | medium | 0 | 0.000 | n/a |
| silent_cause | constant | low | 0 | 0.000 | n/a |
| silent_cause | constant | insufficient_evidence | 4 | 0.200 | 0.000 |
| silent_cause | margin_only | high | 16 | 0.800 | 0.438 |
| silent_cause | margin_only | medium | 0 | 0.000 | n/a |
| silent_cause | margin_only | low | 0 | 0.000 | n/a |
| silent_cause | margin_only | insufficient_evidence | 4 | 0.200 | 0.000 |
| unordered_plausible_alerts | calibrated | high | 14 | 0.700 | 0.929 |
| unordered_plausible_alerts | calibrated | medium | 0 | 0.000 | n/a |
| unordered_plausible_alerts | calibrated | low | 0 | 0.000 | n/a |
| unordered_plausible_alerts | calibrated | insufficient_evidence | 6 | 0.300 | 1.000 |
| unordered_plausible_alerts | constant | high | 14 | 0.700 | 0.929 |
| unordered_plausible_alerts | constant | medium | 0 | 0.000 | n/a |
| unordered_plausible_alerts | constant | low | 0 | 0.000 | n/a |
| unordered_plausible_alerts | constant | insufficient_evidence | 6 | 0.300 | 1.000 |
| unordered_plausible_alerts | margin_only | high | 14 | 0.700 | 0.929 |
| unordered_plausible_alerts | margin_only | medium | 0 | 0.000 | n/a |
| unordered_plausible_alerts | margin_only | low | 0 | 0.000 | n/a |
| unordered_plausible_alerts | margin_only | insufficient_evidence | 6 | 0.300 | 1.000 |
## Secondary evaluation: seeds 52–71

### Per-family calibration and selective accuracy

| Family | n | Accuracy | Mean p | Cal Brier/ECE | Const Brier/ECE | Margin Brier/ECE | High | Med | Low | Insuff | Selective coverage | Selective accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cause_alerts_2_4 | 20 | 0.900 | 0.934 | 0.088/0.034 | 0.091/0.036 | 0.091/0.035 | 15 | 0 | 0 | 5 | 0.750 | 0.9333333333333333 |
| clean_bad_deploy | 20 | 0.950 | 0.942 | 0.046/0.008 | 0.048/0.014 | 0.048/0.015 | 16 | 0 | 0 | 4 | 0.800 | 0.9375 |
| coincident_restart | 20 | 0.900 | 0.941 | 0.087/0.041 | 0.091/0.036 | 0.091/0.035 | 15 | 0 | 0 | 5 | 0.750 | 0.9333333333333333 |
| concurrent_causes | 20 | 1.000 | 0.939 | 0.004/0.061 | 0.004/0.064 | 0.004/0.064 | 14 | 0 | 0 | 6 | 0.700 | 1.0 |
| late_alerting_cause | 20 | 0.900 | 0.933 | 0.089/0.033 | 0.091/0.036 | 0.091/0.035 | 15 | 0 | 0 | 5 | 0.750 | 0.9333333333333333 |
| long_seasonal | 20 | 0.950 | 0.935 | 0.047/0.015 | 0.048/0.014 | 0.048/0.015 | 3 | 0 | 0 | 17 | 0.150 | 1.0 |
| missing_telemetry | 20 | 1.000 | 0.947 | 0.003/0.053 | 0.004/0.064 | 0.004/0.065 | 15 | 0 | 0 | 5 | 0.750 | 1.0 |
| noisy_alerts | 20 | 0.900 | 0.934 | 0.088/0.034 | 0.091/0.036 | 0.091/0.035 | 15 | 0 | 0 | 5 | 0.750 | 0.9333333333333333 |
| partial_graph | 20 | 0.900 | 0.931 | 0.089/0.031 | 0.091/0.036 | 0.091/0.035 | 15 | 0 | 0 | 5 | 0.750 | 0.9333333333333333 |
| red_herring_deploy | 20 | 1.000 | 0.937 | 0.004/0.063 | 0.004/0.064 | 0.004/0.062 | 14 | 0 | 0 | 6 | 0.700 | 1.0 |
| red_herring_hard | 20 | 1.000 | 0.937 | 0.004/0.063 | 0.004/0.064 | 0.004/0.063 | 14 | 0 | 0 | 6 | 0.700 | 1.0 |
| shared_dependency | 20 | 0.950 | 0.934 | 0.046/0.016 | 0.048/0.014 | 0.048/0.015 | 14 | 0 | 0 | 6 | 0.700 | 1.0 |
| silent_cause | 20 | 0.300 | 0.927 | 0.601/0.627 | 0.614/0.636 | 0.613/0.635 | 16 | 0 | 0 | 4 | 0.800 | 0.375 |
| unordered_plausible_alerts | 20 | 0.900 | 0.934 | 0.088/0.034 | 0.091/0.036 | 0.091/0.035 | 15 | 0 | 0 | 5 | 0.750 | 0.9333333333333333 |

### Overall calibration scores

| Confidence model | Cases | Brier | ECE | Mean probability |
|---|---:|---:|---:|---:|
| calibrated | 280 | 0.0916 | 0.0396 | 0.9360 |
| constant | 280 | 0.0944 | 0.0391 | 0.9356 |
| margin_only | 280 | 0.0943 | 0.0392 | 0.9356 |

### Reliability table (fixed ten probability bins)

| Model | Bin | n | Mean probability | Empirical accuracy |
|---|---|---:|---:|---:|
| calibrated | [0.0,0.1) | 0 | — | — |
| calibrated | [0.1,0.2) | 0 | — | — |
| calibrated | [0.2,0.3) | 0 | — | — |
| calibrated | [0.3,0.4) | 0 | — | — |
| calibrated | [0.4,0.5) | 0 | — | — |
| calibrated | [0.5,0.6) | 0 | — | — |
| calibrated | [0.6,0.7) | 0 | — | — |
| calibrated | [0.7,0.8) | 0 | — | — |
| calibrated | [0.8,0.9) | 0 | — | — |
| calibrated | [0.9,1.0] | 280 | 0.9359968487623553 | 0.8964285714285715 |
| constant | [0.0,0.1) | 0 | — | — |
| constant | [0.1,0.2) | 0 | — | — |
| constant | [0.2,0.3) | 0 | — | — |
| constant | [0.3,0.4) | 0 | — | — |
| constant | [0.4,0.5) | 0 | — | — |
| constant | [0.5,0.6) | 0 | — | — |
| constant | [0.6,0.7) | 0 | — | — |
| constant | [0.7,0.8) | 0 | — | — |
| constant | [0.8,0.9) | 0 | — | — |
| constant | [0.9,1.0] | 280 | 0.9355670103092785 | 0.8964285714285715 |
| margin_only | [0.0,0.1) | 0 | — | — |
| margin_only | [0.1,0.2) | 0 | — | — |
| margin_only | [0.2,0.3) | 0 | — | — |
| margin_only | [0.3,0.4) | 0 | — | — |
| margin_only | [0.4,0.5) | 0 | — | — |
| margin_only | [0.5,0.6) | 0 | — | — |
| margin_only | [0.6,0.7) | 0 | — | — |
| margin_only | [0.7,0.8) | 0 | — | — |
| margin_only | [0.8,0.9) | 0 | — | — |
| margin_only | [0.9,1.0] | 280 | 0.935632158195522 | 0.8964285714285715 |

### Confidence-level accuracy and coverage

| Model | Level | n | Coverage | Top-1 accuracy |
|---|---|---:|---:|---:|
| calibrated | high | 196 | 0.700 | 0.9132653061224489 |
| calibrated | medium | 0 | 0.000 | n/a |
| calibrated | low | 0 | 0.000 | n/a |
| calibrated | insufficient_evidence | 84 | 0.300 | 0.8571428571428571 |
| calibrated | selective | 196 | 0.700 | 0.9132653061224489 |
| constant | high | 196 | 0.700 | 0.9132653061224489 |
| constant | medium | 0 | 0.000 | n/a |
| constant | low | 0 | 0.000 | n/a |
| constant | insufficient_evidence | 84 | 0.300 | 0.8571428571428571 |
| constant | selective | 196 | 0.700 | 0.9132653061224489 |
| margin_only | high | 196 | 0.700 | 0.9132653061224489 |
| margin_only | medium | 0 | 0.000 | n/a |
| margin_only | low | 0 | 0.000 | n/a |
| margin_only | insufficient_evidence | 84 | 0.300 | 0.8571428571428571 |
| margin_only | selective | 196 | 0.700 | 0.9132653061224489 |

### High-confidence wrong cases

| Family | Seed | True cause(s) | Top candidate | Probability |
|---|---:|---|---|---:|
| clean_bad_deploy | 58 | database | payments | 0.923 |
| coincident_restart | 58 | database | payments | 0.923 |
| late_alerting_cause | 58 | database | payments | 0.926 |
| silent_cause | 53 | database | inventory | 0.929 |
| silent_cause | 54 | database | payments | 0.935 |
| silent_cause | 57 | database | payments | 0.925 |
| silent_cause | 58 | database | payments | 0.926 |
| silent_cause | 61 | database | inventory | 0.921 |
| silent_cause | 62 | database | payments | 0.942 |
| silent_cause | 63 | database | payments | 0.927 |
| silent_cause | 65 | database | payments | 0.925 |
| silent_cause | 66 | database | checkout | 0.933 |
| silent_cause | 68 | database | payments | 0.919 |
| noisy_alerts | 58 | database | payments | 0.923 |
| partial_graph | 58 | database | payments | 0.926 |
| cause_alerts_2_4 | 58 | database | payments | 0.923 |
| unordered_plausible_alerts | 58 | database | payments | 0.923 |

### Silent, late-alert, and red-herring cases

| Family | n | Accuracy | Mean probability | Probability overstated? | High | High and wrong |
|---|---:|---:|---:|---|---:|---:|
| silent_cause | 20 | 0.3 | 0.9273205319284832 | yes | 16 | 10 |
| late_alerting_cause | 20 | 0.9 | 0.932572713666428 | yes | 15 | 1 |
| red_herring_deploy | 20 | 1.0 | 0.9373513378812254 | no | 14 | 0 |


### Per-family confidence-level accuracy and coverage

| Family | Model | Level | n | Coverage | Top-1 accuracy |
|---|---|---|---:|---:|---:|
| cause_alerts_2_4 | calibrated | high | 15 | 0.750 | 0.933 |
| cause_alerts_2_4 | calibrated | medium | 0 | 0.000 | n/a |
| cause_alerts_2_4 | calibrated | low | 0 | 0.000 | n/a |
| cause_alerts_2_4 | calibrated | insufficient_evidence | 5 | 0.250 | 0.800 |
| cause_alerts_2_4 | constant | high | 15 | 0.750 | 0.933 |
| cause_alerts_2_4 | constant | medium | 0 | 0.000 | n/a |
| cause_alerts_2_4 | constant | low | 0 | 0.000 | n/a |
| cause_alerts_2_4 | constant | insufficient_evidence | 5 | 0.250 | 0.800 |
| cause_alerts_2_4 | margin_only | high | 15 | 0.750 | 0.933 |
| cause_alerts_2_4 | margin_only | medium | 0 | 0.000 | n/a |
| cause_alerts_2_4 | margin_only | low | 0 | 0.000 | n/a |
| cause_alerts_2_4 | margin_only | insufficient_evidence | 5 | 0.250 | 0.800 |
| clean_bad_deploy | calibrated | high | 16 | 0.800 | 0.938 |
| clean_bad_deploy | calibrated | medium | 0 | 0.000 | n/a |
| clean_bad_deploy | calibrated | low | 0 | 0.000 | n/a |
| clean_bad_deploy | calibrated | insufficient_evidence | 4 | 0.200 | 1.000 |
| clean_bad_deploy | constant | high | 16 | 0.800 | 0.938 |
| clean_bad_deploy | constant | medium | 0 | 0.000 | n/a |
| clean_bad_deploy | constant | low | 0 | 0.000 | n/a |
| clean_bad_deploy | constant | insufficient_evidence | 4 | 0.200 | 1.000 |
| clean_bad_deploy | margin_only | high | 16 | 0.800 | 0.938 |
| clean_bad_deploy | margin_only | medium | 0 | 0.000 | n/a |
| clean_bad_deploy | margin_only | low | 0 | 0.000 | n/a |
| clean_bad_deploy | margin_only | insufficient_evidence | 4 | 0.200 | 1.000 |
| coincident_restart | calibrated | high | 15 | 0.750 | 0.933 |
| coincident_restart | calibrated | medium | 0 | 0.000 | n/a |
| coincident_restart | calibrated | low | 0 | 0.000 | n/a |
| coincident_restart | calibrated | insufficient_evidence | 5 | 0.250 | 0.800 |
| coincident_restart | constant | high | 15 | 0.750 | 0.933 |
| coincident_restart | constant | medium | 0 | 0.000 | n/a |
| coincident_restart | constant | low | 0 | 0.000 | n/a |
| coincident_restart | constant | insufficient_evidence | 5 | 0.250 | 0.800 |
| coincident_restart | margin_only | high | 15 | 0.750 | 0.933 |
| coincident_restart | margin_only | medium | 0 | 0.000 | n/a |
| coincident_restart | margin_only | low | 0 | 0.000 | n/a |
| coincident_restart | margin_only | insufficient_evidence | 5 | 0.250 | 0.800 |
| concurrent_causes | calibrated | high | 14 | 0.700 | 1.000 |
| concurrent_causes | calibrated | medium | 0 | 0.000 | n/a |
| concurrent_causes | calibrated | low | 0 | 0.000 | n/a |
| concurrent_causes | calibrated | insufficient_evidence | 6 | 0.300 | 1.000 |
| concurrent_causes | constant | high | 14 | 0.700 | 1.000 |
| concurrent_causes | constant | medium | 0 | 0.000 | n/a |
| concurrent_causes | constant | low | 0 | 0.000 | n/a |
| concurrent_causes | constant | insufficient_evidence | 6 | 0.300 | 1.000 |
| concurrent_causes | margin_only | high | 14 | 0.700 | 1.000 |
| concurrent_causes | margin_only | medium | 0 | 0.000 | n/a |
| concurrent_causes | margin_only | low | 0 | 0.000 | n/a |
| concurrent_causes | margin_only | insufficient_evidence | 6 | 0.300 | 1.000 |
| late_alerting_cause | calibrated | high | 15 | 0.750 | 0.933 |
| late_alerting_cause | calibrated | medium | 0 | 0.000 | n/a |
| late_alerting_cause | calibrated | low | 0 | 0.000 | n/a |
| late_alerting_cause | calibrated | insufficient_evidence | 5 | 0.250 | 0.800 |
| late_alerting_cause | constant | high | 15 | 0.750 | 0.933 |
| late_alerting_cause | constant | medium | 0 | 0.000 | n/a |
| late_alerting_cause | constant | low | 0 | 0.000 | n/a |
| late_alerting_cause | constant | insufficient_evidence | 5 | 0.250 | 0.800 |
| late_alerting_cause | margin_only | high | 15 | 0.750 | 0.933 |
| late_alerting_cause | margin_only | medium | 0 | 0.000 | n/a |
| late_alerting_cause | margin_only | low | 0 | 0.000 | n/a |
| late_alerting_cause | margin_only | insufficient_evidence | 5 | 0.250 | 0.800 |
| long_seasonal | calibrated | high | 3 | 0.150 | 1.000 |
| long_seasonal | calibrated | medium | 0 | 0.000 | n/a |
| long_seasonal | calibrated | low | 0 | 0.000 | n/a |
| long_seasonal | calibrated | insufficient_evidence | 17 | 0.850 | 0.941 |
| long_seasonal | constant | high | 3 | 0.150 | 1.000 |
| long_seasonal | constant | medium | 0 | 0.000 | n/a |
| long_seasonal | constant | low | 0 | 0.000 | n/a |
| long_seasonal | constant | insufficient_evidence | 17 | 0.850 | 0.941 |
| long_seasonal | margin_only | high | 3 | 0.150 | 1.000 |
| long_seasonal | margin_only | medium | 0 | 0.000 | n/a |
| long_seasonal | margin_only | low | 0 | 0.000 | n/a |
| long_seasonal | margin_only | insufficient_evidence | 17 | 0.850 | 0.941 |
| missing_telemetry | calibrated | high | 15 | 0.750 | 1.000 |
| missing_telemetry | calibrated | medium | 0 | 0.000 | n/a |
| missing_telemetry | calibrated | low | 0 | 0.000 | n/a |
| missing_telemetry | calibrated | insufficient_evidence | 5 | 0.250 | 1.000 |
| missing_telemetry | constant | high | 15 | 0.750 | 1.000 |
| missing_telemetry | constant | medium | 0 | 0.000 | n/a |
| missing_telemetry | constant | low | 0 | 0.000 | n/a |
| missing_telemetry | constant | insufficient_evidence | 5 | 0.250 | 1.000 |
| missing_telemetry | margin_only | high | 15 | 0.750 | 1.000 |
| missing_telemetry | margin_only | medium | 0 | 0.000 | n/a |
| missing_telemetry | margin_only | low | 0 | 0.000 | n/a |
| missing_telemetry | margin_only | insufficient_evidence | 5 | 0.250 | 1.000 |
| noisy_alerts | calibrated | high | 15 | 0.750 | 0.933 |
| noisy_alerts | calibrated | medium | 0 | 0.000 | n/a |
| noisy_alerts | calibrated | low | 0 | 0.000 | n/a |
| noisy_alerts | calibrated | insufficient_evidence | 5 | 0.250 | 0.800 |
| noisy_alerts | constant | high | 15 | 0.750 | 0.933 |
| noisy_alerts | constant | medium | 0 | 0.000 | n/a |
| noisy_alerts | constant | low | 0 | 0.000 | n/a |
| noisy_alerts | constant | insufficient_evidence | 5 | 0.250 | 0.800 |
| noisy_alerts | margin_only | high | 15 | 0.750 | 0.933 |
| noisy_alerts | margin_only | medium | 0 | 0.000 | n/a |
| noisy_alerts | margin_only | low | 0 | 0.000 | n/a |
| noisy_alerts | margin_only | insufficient_evidence | 5 | 0.250 | 0.800 |
| partial_graph | calibrated | high | 15 | 0.750 | 0.933 |
| partial_graph | calibrated | medium | 0 | 0.000 | n/a |
| partial_graph | calibrated | low | 0 | 0.000 | n/a |
| partial_graph | calibrated | insufficient_evidence | 5 | 0.250 | 0.800 |
| partial_graph | constant | high | 15 | 0.750 | 0.933 |
| partial_graph | constant | medium | 0 | 0.000 | n/a |
| partial_graph | constant | low | 0 | 0.000 | n/a |
| partial_graph | constant | insufficient_evidence | 5 | 0.250 | 0.800 |
| partial_graph | margin_only | high | 15 | 0.750 | 0.933 |
| partial_graph | margin_only | medium | 0 | 0.000 | n/a |
| partial_graph | margin_only | low | 0 | 0.000 | n/a |
| partial_graph | margin_only | insufficient_evidence | 5 | 0.250 | 0.800 |
| red_herring_deploy | calibrated | high | 14 | 0.700 | 1.000 |
| red_herring_deploy | calibrated | medium | 0 | 0.000 | n/a |
| red_herring_deploy | calibrated | low | 0 | 0.000 | n/a |
| red_herring_deploy | calibrated | insufficient_evidence | 6 | 0.300 | 1.000 |
| red_herring_deploy | constant | high | 14 | 0.700 | 1.000 |
| red_herring_deploy | constant | medium | 0 | 0.000 | n/a |
| red_herring_deploy | constant | low | 0 | 0.000 | n/a |
| red_herring_deploy | constant | insufficient_evidence | 6 | 0.300 | 1.000 |
| red_herring_deploy | margin_only | high | 14 | 0.700 | 1.000 |
| red_herring_deploy | margin_only | medium | 0 | 0.000 | n/a |
| red_herring_deploy | margin_only | low | 0 | 0.000 | n/a |
| red_herring_deploy | margin_only | insufficient_evidence | 6 | 0.300 | 1.000 |
| red_herring_hard | calibrated | high | 14 | 0.700 | 1.000 |
| red_herring_hard | calibrated | medium | 0 | 0.000 | n/a |
| red_herring_hard | calibrated | low | 0 | 0.000 | n/a |
| red_herring_hard | calibrated | insufficient_evidence | 6 | 0.300 | 1.000 |
| red_herring_hard | constant | high | 14 | 0.700 | 1.000 |
| red_herring_hard | constant | medium | 0 | 0.000 | n/a |
| red_herring_hard | constant | low | 0 | 0.000 | n/a |
| red_herring_hard | constant | insufficient_evidence | 6 | 0.300 | 1.000 |
| red_herring_hard | margin_only | high | 14 | 0.700 | 1.000 |
| red_herring_hard | margin_only | medium | 0 | 0.000 | n/a |
| red_herring_hard | margin_only | low | 0 | 0.000 | n/a |
| red_herring_hard | margin_only | insufficient_evidence | 6 | 0.300 | 1.000 |
| shared_dependency | calibrated | high | 14 | 0.700 | 1.000 |
| shared_dependency | calibrated | medium | 0 | 0.000 | n/a |
| shared_dependency | calibrated | low | 0 | 0.000 | n/a |
| shared_dependency | calibrated | insufficient_evidence | 6 | 0.300 | 0.833 |
| shared_dependency | constant | high | 14 | 0.700 | 1.000 |
| shared_dependency | constant | medium | 0 | 0.000 | n/a |
| shared_dependency | constant | low | 0 | 0.000 | n/a |
| shared_dependency | constant | insufficient_evidence | 6 | 0.300 | 0.833 |
| shared_dependency | margin_only | high | 14 | 0.700 | 1.000 |
| shared_dependency | margin_only | medium | 0 | 0.000 | n/a |
| shared_dependency | margin_only | low | 0 | 0.000 | n/a |
| shared_dependency | margin_only | insufficient_evidence | 6 | 0.300 | 0.833 |
| silent_cause | calibrated | high | 16 | 0.800 | 0.375 |
| silent_cause | calibrated | medium | 0 | 0.000 | n/a |
| silent_cause | calibrated | low | 0 | 0.000 | n/a |
| silent_cause | calibrated | insufficient_evidence | 4 | 0.200 | 0.000 |
| silent_cause | constant | high | 16 | 0.800 | 0.375 |
| silent_cause | constant | medium | 0 | 0.000 | n/a |
| silent_cause | constant | low | 0 | 0.000 | n/a |
| silent_cause | constant | insufficient_evidence | 4 | 0.200 | 0.000 |
| silent_cause | margin_only | high | 16 | 0.800 | 0.375 |
| silent_cause | margin_only | medium | 0 | 0.000 | n/a |
| silent_cause | margin_only | low | 0 | 0.000 | n/a |
| silent_cause | margin_only | insufficient_evidence | 4 | 0.200 | 0.000 |
| unordered_plausible_alerts | calibrated | high | 15 | 0.750 | 0.933 |
| unordered_plausible_alerts | calibrated | medium | 0 | 0.000 | n/a |
| unordered_plausible_alerts | calibrated | low | 0 | 0.000 | n/a |
| unordered_plausible_alerts | calibrated | insufficient_evidence | 5 | 0.250 | 0.800 |
| unordered_plausible_alerts | constant | high | 15 | 0.750 | 0.933 |
| unordered_plausible_alerts | constant | medium | 0 | 0.000 | n/a |
| unordered_plausible_alerts | constant | low | 0 | 0.000 | n/a |
| unordered_plausible_alerts | constant | insufficient_evidence | 5 | 0.250 | 0.800 |
| unordered_plausible_alerts | margin_only | high | 15 | 0.750 | 0.933 |
| unordered_plausible_alerts | margin_only | medium | 0 | 0.000 | n/a |
| unordered_plausible_alerts | margin_only | low | 0 | 0.000 | n/a |
| unordered_plausible_alerts | margin_only | insufficient_evidence | 5 | 0.250 | 0.800 |
## Required plain statements

On seeds 72–91, calibrated Brier is 0.0831 versus 0.0850 for each baseline, while calibrated ECE is 0.0289 versus 0.0284 for each baseline. The model is not consistently better calibrated: its Brier improvement is small and its ECE is slightly worse.
Withholding low and insufficient-evidence cases gives 90.8% top-1 at 66.1% coverage versus 90.7% top-1 without withholding; this is a negligible observed increase, not a meaningful demonstrated gain.
All evaluated probabilities fall in the top reliability bin and the model emits no medium or low cases; silent_cause is sharply overconfident. Treat these synthetic calibration results as weak evidence, not operational calibration.
