// Sourced directly from the CORTANA_FINAL_v1.0.0 release package.
// Do not edit these values by hand — they mirror VERSION.json,
// fusion/fusion_config.json, rules/risk_rules.json, and the
// evaluation/* artifacts. If the ML core changes, replace this file
// from the new release ZIP rather than hand-editing numbers here.

import type { RuleDefinition, RiskLevel } from "../types";

export const RELEASE = {
  project: "CORTANA",
  releaseName: "CORTANA_FINAL_v1.0.0",
  version: "1.0.0",
  phase: "Phase 6",
  releaseType: "Final",
  createdUtc: "2026-08-21T10:06:31Z",
};

export const FUSION_WEIGHTS = {
  model_1: 0.8,
  model_2: 0.1,
  rules: 0.1,
};

export const DECISION_THRESHOLD = 0.98;

export const RISK_LEVEL_BANDS: Record<RiskLevel, [number, number]> = {
  LOW: [0.0, 0.25],
  MEDIUM: [0.25, 0.5],
  HIGH: [0.5, 0.75],
  CRITICAL: [0.75, 1.0],
};

export const DATASET_ARCHITECTURE = {
  paysim: ["model_1", "rules"] as const,
  ulb: ["model_2"] as const,
  crossDatasetPairing: false,
};

export const MODEL_1 = {
  name: "CORTANA Model 1",
  algorithm: "Random Forest Classifier",
  dataset: "PaySim",
  learningType: "Supervised",
  purpose: "Supervised fraud probability",
  signal: "fraud_probability",
  weight: 0.8,
  validationRows: 141815,
  testRows: 177268,
};

export const MODEL_2 = {
  name: "CORTANA Model 2",
  algorithm: "Isolation Forest",
  dataset: "ULB",
  learningType: "Unsupervised",
  purpose: "Unsupervised anomaly detection",
  signal: "anomaly_score",
  weight: 0.1,
  nEstimators: 200,
  maxSamples: 0.75,
  maxFeatures: 1.0,
  contamination: "auto",
  operatingPolicy: {
    type: "rank_based",
    anomalyPercentage: 0.3,
  },
  trainingDataset: {
    name: "ULB Credit Card Fraud Dataset",
    trainingRows: 199364,
    testRows: 85443,
    featureCount: 30,
  },
  evaluation: {
    precision: 0.28515625,
    recall: 0.5367647058823529,
    f1: 0.37244897959183676,
    rocAuc: 0.9595797255449005,
    prAuc: 0.3105474488709207,
    truePositives: 73,
    falsePositives: 183,
    trueNegatives: 85124,
    falseNegatives: 63,
    fraudDetected: 73,
    fraudTotal: 136,
    anomaliesFlagged: 256,
    testSamples: 85443,
    note:
      "Final configuration and operating threshold were selected using a validation set. An earlier exploratory hyperparameter experiment used the test set — the final test result is confirmatory rather than a fully virgin holdout evaluation.",
  },
};

export const RULES: RuleDefinition[] = [
  {
    rule_key: "HIGH_AMOUNT",
    description: "Transaction amount is unusually high",
    weight: 0.2,
    enabled: true,
  },
  {
    rule_key: "ORIGIN_BALANCE_INCONSISTENCY",
    description: "Origin account balance changed inconsistently with transaction",
    weight: 0.2,
    enabled: true,
  },
  {
    rule_key: "DESTINATION_BALANCE_INCONSISTENCY",
    description: "Destination account balance changed inconsistently with transaction",
    weight: 0.15,
    enabled: true,
  },
  {
    rule_key: "LARGE_BALANCE_CHANGE",
    description: "Transaction represents a large change relative to origin balance",
    weight: 0.15,
    enabled: true,
  },
  {
    rule_key: "HIGH_RISK_TRANSACTION_TYPE",
    description: "Transaction type is CASH_OUT or TRANSFER",
    weight: 0.15,
    enabled: true,
  },
  {
    rule_key: "ZERO_BALANCE_ANOMALY",
    description: "Transaction leaves an unusual zero-balance condition",
    weight: 0.1,
    enabled: true,
  },
];

// evaluation/final_test_results.json — Step 21, locked threshold, PaySim test set
export const FUSION_FINAL_TEST = {
  dataset: "PaySim",
  testRows: 177268,
  threshold: 0.98,
  precision: 0.27325581395348836,
  recall: 0.9494949494949495,
  f1: 0.42437923250564336,
  rocAuc: 0.9977102271408838,
  prAuc: 0.5870652778184527,
  truePositives: 94,
  falsePositives: 250,
  trueNegatives: 176919,
  falseNegatives: 5,
  knownFraud: 99,
  fraudDetected: 94,
  fraudDetectionRate: 0.9494949494949495,
  reviewedTransactions: 344,
  reviewRate: 0.0019405645689013246,
  testSetTuned: false,
  thresholdSource: "PaySim validation set — Step 20",
};

// evaluation/final_model_comparison.csv
export const MODEL_COMPARISON = [
  {
    system: "Model 1",
    precision: 1.0,
    recall: 0.9595959595959596,
    f1: 0.979381443298969,
    rocAuc: 0.9945798484594776,
    prAuc: 0.9664598026526642,
  },
  {
    system: "Rules Engine",
    precision: 0.0027849437148217636,
    recall: 0.9595959595959596,
    f1: 0.0055537692555026165,
    rocAuc: 0.9096050275799554,
    prAuc: 0.004104886106140051,
  },
  {
    system: "CORTANA Fusion",
    precision: 0.27325581395348836,
    recall: 0.9494949494949495,
    f1: 0.42437923250564336,
    rocAuc: 0.9977102271408838,
    prAuc: 0.5870652778184527,
  },
];

export const VALIDATION_STEPS = [
  { step: "Step 21 — Final Test Evaluation", status: "PASSED" },
  { step: "Step 22 — System-Level Validation", status: "PASSED" },
  { step: "Step 23 — Artifact Reproducibility", status: "PASSED" },
  { step: "Step 24 — Packaging Precheck", status: "PASSED" },
  { step: "Step 25 — Final Packaging", status: "PASSED" },
  { step: "Step 26 — Clean Package Smoke Test", status: "PASSED" },
];
