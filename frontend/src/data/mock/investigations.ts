import type { Investigation, AuditEvent } from "../../types";
import { MOCK_TRANSACTIONS } from "./generator";

const ANALYSTS = ["A. Menon", "R. Castillo", "J. Okafor"];

function buildTrail(base: Date, resolved: boolean, resolution: "FRAUD_CONFIRMED" | "LEGITIMATE" | null, analyst: string): AuditEvent[] {
  const t = (mins: number) => new Date(base.getTime() + mins * 60000).toISOString();
  const trail: AuditEvent[] = [
    { id: "e1", action: "CORTANA_FLAGGED", actor: "CORTANA", timestamp: t(0) },
    { id: "e2", action: "CASE_OPENED", actor: analyst, timestamp: t(2) },
    { id: "e3", action: "EXPLANATION_REQUESTED", actor: analyst, timestamp: t(5) },
  ];
  if (resolved && resolution) {
    trail.push({
      id: "e4",
      action: resolution === "FRAUD_CONFIRMED" ? "CONFIRMED_FRAUD" : "MARKED_LEGITIMATE",
      actor: analyst,
      timestamp: t(9),
      note:
        resolution === "FRAUD_CONFIRMED"
          ? "Pattern consistent with rapid cash-out after balance depletion. Confirmed."
          : "Customer verified via callback. Legitimate high-value transfer.",
    });
  }
  return trail;
}

const reviewTx = MOCK_TRANSACTIONS.filter((t) => t.fusion.decision === "REVIEW");

export const MOCK_INVESTIGATIONS: Investigation[] = reviewTx.map((t, i) => {
  const opened = new Date(t.timestamp);
  const resolved = i % 3 === 0;
  const resolution = resolved ? (i % 6 === 0 ? "LEGITIMATE" : "FRAUD_CONFIRMED") : null;
  const analyst = ANALYSTS[i % ANALYSTS.length];
  return {
    id: `C-${10200 + i}`,
    transaction_id: t.id,
    risk_level: t.fusion.risk_level,
    risk_score: t.fusion.fused_risk,
    decision: t.fusion.decision,
    status: resolved ? "CLOSED" : i % 4 === 0 ? "ESCALATED" : i % 2 === 0 ? "IN_REVIEW" : "OPEN",
    resolution,
    assigned_to: analyst,
    opened_at: t.timestamp,
    audit_trail: buildTrail(opened, resolved, resolution, analyst),
  };
});

export function getInvestigationById(id: string): Investigation | undefined {
  return MOCK_INVESTIGATIONS.find((c) => c.id === id);
}
