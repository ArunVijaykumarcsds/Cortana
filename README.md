# CORTANA

CORTANA is a multi-component financial risk intelligence
and fraud detection system.

## Core Components

1. Model 1 — PaySim supervised fraud model
2. Model 2 — ULB unsupervised anomaly model
3. Behavioral Rules Engine
4. Risk Calibration
5. Risk Fusion Engine

## Production Fusion Policy

| Component | Weight |
|-----------|--------|
| Model 1 | 0.80 |
| Model 2 | 0.10 |
| Rules | 0.10 |

Decision threshold: 0.98

## Dataset Architecture

PaySim:
Model 1 + Rules

ULB:
Model 2

The system does not perform artificial row-wise
fusion between PaySim and ULB transactions.

## Final Test Performance

CORTANA Fusion:

Precision: 0.273256
Recall: 0.949495
F1: 0.424379
ROC-AUC: 0.997710
PR-AUC: 0.587065

Confusion Matrix:

TN = 176919
FP = 250
FN = 5
TP = 94

Fraud detection rate = 94.95%

## Important

The final threshold of 0.98 was selected using validation
data and remained locked during final test evaluation.

No test-set threshold optimization was performed.

## Package Status

Phase 6 validation completed.

Artifact reproducibility validated for Model 2.
Final test evaluation completed.
System-level boundary validation completed.