/**
 * CORTANA — Alerts API Client.
 * Connects to /api/v1/alerts for querying and status updates.
 */

import type { Alert } from "../../types";
import { apiClient, isMockMode } from "./client";
import { MOCK_ALERTS, getAlertById as getMockAlertById } from "../mock/alerts";

export interface AlertFilterParams {
  status?: string;
  risk_level?: string;
  limit?: number;
  offset?: number;
}

export async function fetchAlerts(params: AlertFilterParams = {}): Promise<Alert[]> {
  if (isMockMode()) {
    const { status, risk_level } = params;
    return MOCK_ALERTS.filter(
      (a) =>
        (!status || status === "ALL" || a.status === status) &&
        (!risk_level || risk_level === "ALL" || a.risk_level === risk_level)
    );
  }

  const query = new URLSearchParams();
  if (params.status && params.status !== "ALL") query.append("status", params.status);
  if (params.risk_level && params.risk_level !== "ALL") query.append("risk_level", params.risk_level);
  if (params.limit) query.append("limit", String(params.limit));
  if (params.offset) query.append("offset", String(params.offset));

  const qs = query.toString();
  const path = qs ? `/api/v1/alerts?${qs}` : "/api/v1/alerts";
  return apiClient<Alert[]>(path);
}

export async function fetchAlertById(id: string): Promise<Alert | undefined> {
  if (isMockMode()) {
    return getMockAlertById(id);
  }

  try {
    return await apiClient<Alert>(`/api/v1/alerts/${id}`);
  } catch (err: unknown) {
    if (typeof err === "object" && err !== null && "status" in err && (err as { status: number }).status === 404) {
      return undefined;
    }
    throw err;
  }
}

export async function updateAlertStatus(
  id: string,
  newStatus: "OPEN" | "UNDER_REVIEW" | "RESOLVED"
): Promise<Alert> {
  if (isMockMode()) {
    const alert = MOCK_ALERTS.find((a) => a.id === id);
    if (alert) alert.status = newStatus;
    return alert || {
      id,
      transaction_id: "PSX-MOCK",
      dataset_context: "PaySim",
      type: "PAYMENT",
      risk_score: 0.9,
      risk_level: "CRITICAL",
      decision: "REVIEW",
      status: newStatus,
      timestamp: new Date().toISOString(),
    };
  }

  return apiClient<Alert>(`/api/v1/alerts/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status: newStatus }),
  });
}
