# CORTANA — ML Inference Core (Stage 2)

This directory contains the Python ML inference service for CORTANA. It loads the authoritative, frozen release artifacts from `models/`, `fusion/`, and `rules/` and executes real-time, calibrated fraud risk scoring with strict dataset isolation.

## Architecture

```
backend/
├── app/
│   ├── core/
│   │   ├── calibration.py       # Empirical percentile-rank calibration engine
│   │   ├── fusion.py            # Risk fusion policy & thresholding
│   │   ├── inference.py         # Unified InferenceEngine service
│   │   ├── models.py            # Joblib model wrappers (Model 1 & Model 2)
│   │   └── rules.py             # 6 behavioral rules evaluator
│   └── schemas/
│       ├── inference.py         # Output schemas matching frontend types
│       └── transaction.py       # PaySim & ULB input transaction schemas
├── tests/
│   ├── run_all_tests.py         # Unified test suite runner
│   ├── test_boundaries.py      # Threshold boundary tests
│   ├── test_calibration.py     # Calibration table tests
│   ├── test_fusion.py          # Fusion policy & weight tests
│   ├── test_inference.py       # End-to-end inference integration tests
│   ├── test_isolation.py       # Strict dataset context isolation tests
│   ├── test_models.py          # Model 1 & Model 2 loaders tests
│   └── test_rules.py           # Behavioral rules engine tests
├── README.md
└── requirements.txt
```

## Dataset Separation Policy

CORTANA enforces strict architectural dataset context isolation:

1. **PaySim Context**:
   - Evaluates **Model 1** (RandomForestClassifier, supervised fraud probability)
   - Evaluates **Rules Engine** (6 deterministic behavioral rules)
   - Calibrates both raw signals using empirical percentile rank curves
   - Fuses signals with weights `Model 1 = 0.80`, `Rules = 0.10` (normalized to active sum `0.90`)
   - **Model 2 is never evaluated in PaySim context**.

2. **ULB Context**:
   - Evaluates **Model 2** (IsolationForest, unsupervised anomaly score)
   - Calibrates the inverted decision function (`-decision_function`)
   - Fuses with active weight `1.0`
   - **Model 1 and Rules Engine are never evaluated in ULB context**.

3. **Decision Policy**:
   - Fused Risk Score $\ge 0.98 \implies$ `REVIEW`
   - Fused Risk Score $< 0.98 \implies$ `PASS`

## Running Tests

Execute the comprehensive test suite:

```bash
python backend/tests/run_all_tests.py
```
