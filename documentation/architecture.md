# CORTANA Risk Intelligence Architecture

## Components

### Model 1 — Supervised Fraud Model
- Dataset: PaySim
- Model: RandomForestClassifier
- Signal: fraud probability

### Model 2 — Unsupervised Anomaly Model
- Dataset: ULB
- Model: IsolationForest
- Signal: anomaly score

### Rules Engine
- Dataset: PaySim
- Six behavioral rules
- Signal: calibrated rule risk

## Fusion Policy

Model 1 weight: 0.80
Model 2 weight: 0.10
Rules weight: 0.10

Total weight: 1.00

## Decision Policy

Fused risk >= 0.98:
REVIEW

Fused risk < 0.98:
PASS

## Risk Levels

0.00 <= risk < 0.25:
LOW

0.25 <= risk < 0.50:
MEDIUM

0.50 <= risk < 0.75:
HIGH

0.75 <= risk <= 1.00:
CRITICAL

## Dataset Safety

PaySim:
Model 1 + Rules

ULB:
Model 2

Cross-dataset row-wise fusion:
DISABLED

## Final Test Results

Precision: 0.273256
Recall: 0.949495
F1: 0.424379
ROC-AUC: 0.997710
PR-AUC: 0.587065

True Positives: 94
False Positives: 250
True Negatives: 176919
False Negatives: 5

Fraud detection rate:
94.95%

Decision threshold:
0.98