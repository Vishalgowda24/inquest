# P10 Calibrated Confidence Evaluation

Run commit: `b4aba98866ff0d8609012c0a4566fc43628f1456`  
Config SHA-256: `ffd51fba3632b0f1dbe9db77ff749dfce060a2fed19df25e7b6386241a147fc5`  
Confidence model SHA-256: `179410b35f45c93f741d6805314aa948d6e1a1df4c53cee1f92665341670090f`  
Primary evaluation: seeds 72–91 (280 cases). Secondary check: seeds 52–71 (280 cases), not used for fitting. Holdout seeds 7–9 were not run.

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

## Plain results

On seeds 72–91 the calibrated model has Brier 0.0831 and ECE 0.0289; constant baseline Brier/ECE 0.0850/0.0284; margin-only 0.0850/0.0284.
Selective top-1 after withholding low and insufficient-evidence cases is 0.9081081081081082 at coverage 0.661; full top-1 is 0.907.
These are synthetic-only calibration results; no model refit or threshold adjustment occurred after the fresh evaluation.
