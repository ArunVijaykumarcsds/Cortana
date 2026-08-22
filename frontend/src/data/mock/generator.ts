// Deterministic mock-data generator.
// Isolated from any production/API logic — see src/data/mock/README.md.
// All numeric signal values here are illustrative sample data only,
// per FRONTEND_BRIEF §32 ("Do not invent real model performance").

import type { Transaction, TransactionType, TriggeredRule } from "../../types";
import { riskLevelFromScore, decisionFromScore } from "../../utils/risk";
import { FUSION_WEIGHTS, DECISION_THRESHOLD, RULES } from "../cortanaConfig";

// mulberry32 seeded PRNG — keeps mock data stable across reloads
function seeded(seed: number) {
  let t = seed;
  return function rand() {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r = (r + Math.imul(r ^ (r >>> 7), 61 | r)) ^ r;
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

const rand = seeded(20260821);

const PAYSIM_TYPES: TransactionType[] = [
  "PAYMENT",
  "TRANSFER",
  "CASH_OUT",
  "CASH_IN",
  "DEBIT",
];

function pick<T>(arr: readonly T[]): T {
  return arr[Math.floor(rand() * arr.length)];
}

function acct(prefix: string) {
  return `${prefix}${Math.floor(rand() * 900000000 + 100000000)}`;
}

function isoMinutesAgo(mins: number) {
  return new Date(Date.now() - mins * 60000).toISOString();
}

function triggerRulesFor(risk: number, type: TransactionType, amount: number): TriggeredRule[] {
  const triggered: TriggeredRule[] = [];
  const map = Object.fromEntries(RULES.map((r) => [r.rule_key, r]));

  if (amount > 400000) {
    triggered.push({
      rule_key: "HIGH_AMOUNT",
      description: map.HIGH_AMOUNT.description,
      severity: "HIGH",
      field: "amount",
      value: amount.toLocaleString(),
    });
  }
  if ((type === "CASH_OUT" || type === "TRANSFER") && risk > 0.4) {
    triggered.push({
      rule_key: "HIGH_RISK_TRANSACTION_TYPE",
      description: map.HIGH_RISK_TRANSACTION_TYPE.description,
      severity: "MEDIUM",
      field: "type",
      value: type,
    });
  }
  if (risk > 0.55 && rand() > 0.4) {
    triggered.push({
      rule_key: "ORIGIN_BALANCE_INCONSISTENCY",
      description: map.ORIGIN_BALANCE_INCONSISTENCY.description,
      severity: "HIGH",
      field: "origin_balance_after",
      value: "inconsistent with debit",
    });
  }
  if (risk > 0.65 && rand() > 0.5) {
    triggered.push({
      rule_key: "LARGE_BALANCE_CHANGE",
      description: map.LARGE_BALANCE_CHANGE.description,
      severity: "MEDIUM",
      field: "origin_balance_before",
      value: "> 80% of balance moved",
    });
  }
  if (risk > 0.7 && rand() > 0.6) {
    triggered.push({
      rule_key: "ZERO_BALANCE_ANOMALY",
      description: map.ZERO_BALANCE_ANOMALY.description,
      severity: "LOW",
      field: "destination_balance_after",
      value: "0.00",
    });
  }
  if (risk > 0.5 && rand() > 0.65) {
    triggered.push({
      rule_key: "DESTINATION_BALANCE_INCONSISTENCY",
      description: map.DESTINATION_BALANCE_INCONSISTENCY.description,
      severity: "MEDIUM",
      field: "destination_balance_after",
      value: "inconsistent with credit",
    });
  }
  return triggered;
}

function buildPaySimTransaction(idx: number, forcedRisk?: number): Transaction {
  const type = pick(PAYSIM_TYPES);
  const amount = Math.round(50 + rand() * (forcedRisk && forcedRisk > 0.7 ? 900000 : 60000));
  const originBefore = Math.round(amount + rand() * 200000);
  const originAfter = Math.max(0, originBefore - amount);
  const destBefore = Math.round(rand() * 50000);
  const destAfter = destBefore + amount;

  const model1Prob = forcedRisk ?? Math.min(0.999, Math.pow(rand(), 3));
  const rulesTriggered = triggerRulesFor(model1Prob, type, amount);
  const rulesRisk = Math.min(
    1,
    rulesTriggered.reduce((s, r) => s + (RULES.find((x) => x.rule_key === r.rule_key)?.weight ?? 0), 0) +
      rand() * 0.05
  );

  const fused =
    model1Prob * FUSION_WEIGHTS.model_1 +
    rulesRisk * FUSION_WEIGHTS.rules +
    // Model 2 is not row-paired with PaySim transactions — its share
    // of the fusion weight is not applied in this dataset context.
    0;

  // renormalize against the active weight for this dataset context
  const activeWeight = FUSION_WEIGHTS.model_1 + FUSION_WEIGHTS.rules;
  const fusedRisk = Math.min(0.999, fused / activeWeight);

  return {
    id: `PSX-${100000 + idx}`,
    dataset_context: "PaySim",
    type,
    amount,
    currency: "USD",
    origin_account: acct("C"),
    destination_account: acct(type === "CASH_OUT" ? "M" : "C"),
    origin_balance_before: originBefore,
    origin_balance_after: originAfter,
    destination_balance_before: destBefore,
    destination_balance_after: destAfter,
    timestamp: isoMinutesAgo(Math.floor(rand() * 60 * 24 * 3)),
    model_1: { dataset: "PaySim", fraud_probability: model1Prob },
    rules: { dataset: "PaySim", behavioral_risk: rulesRisk, triggered: rulesTriggered },
    fusion: {
      fused_risk: fusedRisk,
      risk_level: riskLevelFromScore(fusedRisk),
      decision: decisionFromScore(fusedRisk, DECISION_THRESHOLD),
      weights: FUSION_WEIGHTS,
      threshold: DECISION_THRESHOLD,
    },
  };
}

function buildUlbTransaction(idx: number, forcedRisk?: number): Transaction {
  const amount = Math.round(1 + rand() * 4000);
  const anomaly = forcedRisk ?? Math.min(0.999, Math.pow(rand(), 4));
  return {
    id: `ULB-${200000 + idx}`,
    dataset_context: "ULB",
    type: "PAYMENT",
    amount,
    currency: "USD",
    origin_account: acct("CC"),
    destination_account: acct("MERCH"),
    origin_balance_before: 0,
    origin_balance_after: 0,
    destination_balance_before: 0,
    destination_balance_after: 0,
    timestamp: isoMinutesAgo(Math.floor(rand() * 60 * 24 * 3)),
    model_2: { dataset: "ULB", anomaly_score: anomaly },
    fusion: {
      // Model 2 operates independently — its fused_risk uses only the
      // model_2 signal, never blended row-wise with PaySim components.
      fused_risk: anomaly,
      risk_level: riskLevelFromScore(anomaly),
      decision: decisionFromScore(anomaly, DECISION_THRESHOLD),
      weights: FUSION_WEIGHTS,
      threshold: DECISION_THRESHOLD,
    },
  };
}

const forcedRisks = [0.986, 0.94, 0.81, 0.62, 0.55, 0.31, 0.12, 0.08];

export const MOCK_TRANSACTIONS: Transaction[] = [
  ...forcedRisks.map((r, i) => buildPaySimTransaction(i, r)),
  ...Array.from({ length: 34 }, (_, i) => buildPaySimTransaction(i + 20)),
  ...[0.91, 0.72, 0.4, 0.15].map((r, i) => buildUlbTransaction(i, r)),
  ...Array.from({ length: 10 }, (_, i) => buildUlbTransaction(i + 20)),
].sort((a, b) => (a.timestamp < b.timestamp ? 1 : -1));

export function getTransactionById(id: string): Transaction | undefined {
  return MOCK_TRANSACTIONS.find((t) => t.id === id);
}
