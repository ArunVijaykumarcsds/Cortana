/**
 * CORTANA — Investigations API Client.
 * Connects to /api/v1/investigations for case files and immutable audit trail actions.
 */

import type { Investigation } from "../../types";
import { apiClient, isMockMode } from "./client";
import {
  MOCK_INVESTIGATIONS,
  getInvestigationById as getMockInvestigationById,
} from "../mock/investigations";

export interface InvestigationFilterParams {
  status?: string;
  assigned_to?: string;
  limit?: number;
  offset?: number;
}

export async function fetchInvestigations(
  params: InvestigationFilterParams = {}
): Promise<Investigation[]> {
  if (isMockMode()) {
    const { status, assigned_to } = params;
    return MOCK_INVESTIGATIONS.filter(
      (c) =>
        (!status || status === "ALL" || c.status === status) &&
        (!assigned_to || assigned_to === "ALL" || c.assigned_to === assigned_to)
    );
  }

  const query = new URLSearchParams();
  if (params.status && params.status !== "ALL") query.append("status", params.status);
  if (params.assigned_to && params.assigned_to !== "ALL") query.append("assigned_to", params.assigned_to);
  if (params.limit) query.append("limit", String(params.limit));
  if (params.offset) query.append("offset", String(params.offset));

  const qs = query.toString();
  const path = qs ? `/api/v1/investigations?${qs}` : "/api/v1/investigations";
  return apiClient<Investigation[]>(path);
}

export async function fetchInvestigationById(id: string): Promise<Investigation | undefined> {
  if (isMockMode()) {
    return getMockInvestigationById(id);
  }

  try {
    return await apiClient<Investigation>(`/api/v1/investigations/${id}`);
  } catch (err: unknown) {
    if (typeof err === "object" && err !== null && "status" in err && (err as { status: number }).status === 404) {
      return undefined;
    }
    throw err;
  }
}

export async function appendInvestigationEvent(
  id: string,
  event: { action: string; actor: string; note?: string }
): Promise<Investigation> {
  if (isMockMode()) {
    const inv = getMockInvestigationById(id);
    if (inv) {
      inv.audit_trail.push({
        id: `e-${inv.audit_trail.length + 1}`,
        action: event.action as any,
        actor: event.actor,
        timestamp: new Date().toISOString(),
        note: event.note,
      });
      return { ...inv };
    }
    throw new Error(`Investigation ${id} not found in mock data`);
  }

  return apiClient<Investigation>(`/api/v1/investigations/${id}/events`, {
    method: "POST",
    body: JSON.stringify(event),
  });
}

export async function updateInvestigation(
  id: string,
  update: {
    status?: "OPEN" | "IN_REVIEW" | "ESCALATED" | "CLOSED";
    resolution?: "FRAUD_CONFIRMED" | "LEGITIMATE";
    assigned_to?: string;
    actor: string;
    note?: string;
  }
): Promise<Investigation> {
  if (isMockMode()) {
    const inv = getMockInvestigationById(id);
    if (inv) {
      if (update.status) inv.status = update.status;
      if (update.resolution) {
        inv.resolution = update.resolution;
        inv.status = "CLOSED";
      }
      if (update.assigned_to) inv.assigned_to = update.assigned_to;
      inv.audit_trail.push({
        id: `e-${inv.audit_trail.length + 1}`,
        action: (update.resolution ? (update.resolution === "FRAUD_CONFIRMED" ? "CONFIRMED_FRAUD" : "MARKED_LEGITIMATE") : "NOTE_ADDED") as any,
        actor: update.actor,
        timestamp: new Date().toISOString(),
        note: update.note,
      });
      return { ...inv };
    }
    throw new Error(`Investigation ${id} not found in mock data`);
  }

  return apiClient<Investigation>(`/api/v1/investigations/${id}`, {
    method: "PATCH",
    body: JSON.stringify(update),
  });
}
