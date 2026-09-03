/**
 * CORTANA — Transactions API Client.
 * Connects to /api/v1/transactions with support for filtering, pagination, and real scoring.
 */

import type { ExplanationResponse, Transaction } from "../../types";
import { apiClient, isMockMode } from "./client";
import {
  MOCK_TRANSACTIONS,
  getTransactionById as getMockTransactionById,
} from "../mock/generator";

export interface TransactionFilterParams {
  context?: string;
  risk_level?: string;
  decision?: string;
  limit?: number;
  offset?: number;
}

export async function fetchTransactions(
  params: TransactionFilterParams = {}
): Promise<Transaction[]> {
  if (isMockMode()) {
    const { context, risk_level, decision } = params;
    return MOCK_TRANSACTIONS.filter(
      (t) =>
        (!context || context === "ALL" || t.dataset_context === context) &&
        (!risk_level || risk_level === "ALL" || t.fusion.risk_level === risk_level) &&
        (!decision || decision === "ALL" || t.fusion.decision === decision)
    );
  }

  const query = new URLSearchParams();
  if (params.context && params.context !== "ALL") query.append("context", params.context);
  if (params.risk_level && params.risk_level !== "ALL") query.append("risk_level", params.risk_level);
  if (params.decision && params.decision !== "ALL") query.append("decision", params.decision);
  if (params.limit) query.append("limit", String(params.limit));
  if (params.offset) query.append("offset", String(params.offset));

  const qs = query.toString();
  const path = qs ? `/api/v1/transactions?${qs}` : "/api/v1/transactions";
  return apiClient<Transaction[]>(path);
}

export async function fetchTransactionById(id: string): Promise<Transaction | undefined> {
  if (isMockMode()) {
    return getMockTransactionById(id);
  }

  try {
    return await apiClient<Transaction>(`/api/v1/transactions/${id}`);
  } catch (err: unknown) {
    if (typeof err === "object" && err !== null && "status" in err && (err as { status: number }).status === 404) {
      return undefined;
    }
    throw err;
  }
}

export async function fetchTransactionCount(
  params: { context?: string; risk_level?: string } = {}
): Promise<{ total: number }> {
  if (isMockMode()) {
    const list = await fetchTransactions(params);
    return { total: list.length };
  }

  const query = new URLSearchParams();
  if (params.context && params.context !== "ALL") query.append("context", params.context);
  if (params.risk_level && params.risk_level !== "ALL") query.append("risk_level", params.risk_level);

  const qs = query.toString();
  const path = qs ? `/api/v1/transactions/count?${qs}` : "/api/v1/transactions/count";
  return apiClient<{ total: number }>(path);
}

export async function scoreTransaction(
  payload: Record<string, unknown>
): Promise<Transaction> {
  return apiClient<Transaction>("/api/v1/transactions/score", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchTransactionExplanation(
  id: string
): Promise<ExplanationResponse> {
  if (isMockMode()) {
    const tx = getMockTransactionById(id);
    const scorePct = tx ? `${(tx.fusion.fused_risk * 100).toFixed(1)}%` : "0%";
    const rulesList = tx?.rules?.triggered?.map((r) => r.rule_key).join(", ") || "None";
    return {
      transaction_id: id,
      risk_level: tx?.fusion.risk_level || "LOW",
      decision: tx?.fusion.decision || "PASS",
      fused_risk_score: tx?.fusion.fused_risk || 0.0,
      explanation_text: `Transaction ${id} was evaluated as ${tx?.fusion.risk_level || "LOW"} risk with a fused score of ${scorePct}. Signals evaluated: ${tx?.dataset_context === "PaySim" ? "Model 1 (Random Forest)" : "Model 2 (Isolation Forest)"}. Triggered rules: ${rulesList}.`,
      referenced_signals: tx?.dataset_context === "PaySim" ? ["Model 1 (Random Forest)", "Rules Engine"] : ["Model 2 (Isolation Forest)"],
      provider: "deterministic_fallback",
      is_fallback: true,
    };
  }

  return apiClient<ExplanationResponse>(`/api/v1/transactions/${id}/explain`, {
    method: "POST",
  });
}

