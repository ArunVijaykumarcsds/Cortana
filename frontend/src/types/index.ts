// CORTANA — Frontend type contracts.
// These interfaces describe the shape of data the future FastAPI backend
// is expected to serve. They are derived from the real CORTANA release
// artifacts (fusion/fusion_config.json, rules/risk_rules.json,
// models/model_*/*.json) — no ML fields have been invented here.

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type Decision = "PASS" | "REVIEW";

export type DatasetContext = "PaySim" | "ULB";

export type TransactionType =
  | "PAYMENT"
  | "TRANSFER"
  | "CASH_OUT"
  | "CASH_IN"
  | "DEBIT";

export type RuleKey =
  | "HIGH_AMOUNT"
  | "ORIGIN_BALANCE_INCONSISTENCY"
  | "DESTINATION_BALANCE_INCONSISTENCY"
  | "LARGE_BALANCE_CHANGE"
  | "HIGH_RISK_TRANSACTION_TYPE"
  | "ZERO_BALANCE_ANOMALY";

/** A single rule definition, as configured in rules/risk_rules.json */
export interface RuleDefinition {
  rule_key: RuleKey;
  description: string;
  weight: number;
  enabled: boolean;
}

/** A rule that actually fired against a specific transaction. */
export interface TriggeredRule {
  rule_key: RuleKey;
  description: string;
  severity: RiskLevel;
  field?: string;
  value?: string;
}

/** Output of Model 1 — RandomForestClassifier, PaySim, supervised. */
export interface Model1Signal {
  dataset: "PaySim";
  fraud_probability: number; // 0..1, calibrated
}

/** Output of Model 2 — IsolationForest, ULB, unsupervised. Only present
 *  for transactions evaluated in the ULB context — never row-paired
 *  with a PaySim transaction. */
export interface Model2Signal {
  dataset: "ULB";
  anomaly_score: number; // 0..1, calibrated (rank-based)
}

/** Output of the behavioral rules engine — PaySim only. */
export interface RulesSignal {
  dataset: "PaySim";
  behavioral_risk: number; // 0..1, calibrated
  triggered: TriggeredRule[];
}

export interface FusionResult {
  fused_risk: number; // 0..1
  risk_level: RiskLevel;
  decision: Decision;
  weights: {
    model_1: number;
    model_2: number;
    rules: number;
  };
  threshold: number;
}

export interface Transaction {
  id: string;
  dataset_context: DatasetContext;
  type: TransactionType;
  amount: number;
  currency: string;
  origin_account: string;
  destination_account: string;
  origin_balance_before: number;
  origin_balance_after: number;
  destination_balance_before: number;
  destination_balance_after: number;
  timestamp: string; // ISO
  model_1?: Model1Signal;
  rules?: RulesSignal;
  model_2?: Model2Signal;
  fusion: FusionResult;
}

export interface Alert {
  id: string;
  transaction_id: string;
  dataset_context: DatasetContext;
  type: TransactionType;
  risk_score: number;
  risk_level: RiskLevel;
  decision: Decision;
  status: "OPEN" | "UNDER_REVIEW" | "RESOLVED";
  timestamp: string;
}

export type AnalystAction =
  | "CASE_OPENED"
  | "CORTANA_FLAGGED"
  | "EXPLANATION_REQUESTED"
  | "CONFIRMED_FRAUD"
  | "MARKED_LEGITIMATE"
  | "ESCALATED"
  | "NOTE_ADDED";

export interface AuditEvent {
  id: string;
  action: AnalystAction;
  actor: "CORTANA" | string; // string = analyst name
  timestamp: string;
  note?: string;
}

export type CaseStatus = "OPEN" | "IN_REVIEW" | "ESCALATED" | "CLOSED";
export type CaseResolution = "FRAUD_CONFIRMED" | "LEGITIMATE" | null;

export interface Investigation {
  id: string; // e.g. "C-10291"
  transaction_id: string;
  risk_level: RiskLevel;
  risk_score: number;
  decision: Decision;
  status: CaseStatus;
  resolution: CaseResolution;
  assigned_to?: string;
  opened_at: string;
  audit_trail: AuditEvent[];
}

export type ServiceState = "OPERATIONAL" | "DEGRADED" | "OFFLINE" | "PLANNED";

export interface SystemStatus {
  service: string;
  state: ServiceState;
  detail: string;
}
