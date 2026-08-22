import type { Alert } from "../../types";
import { MOCK_TRANSACTIONS } from "./generator";

export const MOCK_ALERTS: Alert[] = MOCK_TRANSACTIONS.filter(
  (t) => t.fusion.risk_level === "HIGH" || t.fusion.risk_level === "CRITICAL"
).map((t, i) => ({
  id: `A-${5000 + i}`,
  transaction_id: t.id,
  dataset_context: t.dataset_context,
  type: t.type,
  risk_score: t.fusion.fused_risk,
  risk_level: t.fusion.risk_level,
  decision: t.fusion.decision,
  status:
    t.fusion.decision === "REVIEW"
      ? i % 3 === 0
        ? "RESOLVED"
        : i % 2 === 0
        ? "UNDER_REVIEW"
        : "OPEN"
      : "RESOLVED",
  timestamp: t.timestamp,
}));

export function getAlertById(id: string): Alert | undefined {
  return MOCK_ALERTS.find((a) => a.id === id);
}
