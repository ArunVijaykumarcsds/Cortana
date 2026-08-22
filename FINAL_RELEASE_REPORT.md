# CORTANA — Phase 6 Final Release Report

## Release

Version: 1.0.0

Status: FINAL

## Architecture

CORTANA contains three independent risk components:

### Model 1
- Dataset: PaySim
- Model: RandomForestClassifier
- Signal: supervised fraud probability
- Fusion weight: 0.80

### Model 2
- Dataset: ULB
- Model: IsolationForest
- Signal: unsupervised anomaly score
- Fusion weight: 0.10

### Rules Engine
- Dataset: PaySim
- Rules: 6 refined behavioral rules
- Fusion weight: 0.10

## Dataset Safety

PaySim transactions use:

Model 1 + Rules

ULB transactions use:

Model 2

Artificial row-wise fusion between PaySim and ULB
transactions is disabled.

## Final Decision Policy

Fused risk >= 0.98:
REVIEW

Fused risk < 0.98:
PASS

The threshold was selected using validation data and
remained locked during final test evaluation.

## Final Untouched PaySim Test

Precision: 0.273256

Recall: 0.949495

F1 Score: 0.424379

ROC-AUC: 0.997710

PR-AUC: 0.587065

## Confusion Matrix

True Negatives: 176919

False Positives: 250

False Negatives: 5

True Positives: 94

## Fraud Detection

Known fraud transactions: 99

Detected fraud transactions: 94

Fraud detection rate: 94.95%

## Validation Status

Step 21 — Final Test Evaluation: PASSED

Step 22 — System-Level Validation: PASSED

Step 23 — Artifact Reproducibility: PASSED

Step 24 — Packaging Precheck: PASSED

Step 25 — Final Packaging: PASSED

Step 26 — Clean Package Smoke Test: PASSED

## Artifact Integrity

All release artifacts have SHA-256 hashes recorded
in MANIFEST_SHA256.json.

## Release Status

CORTANA Phase 6 final package prepared.