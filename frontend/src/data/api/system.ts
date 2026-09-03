/**
 * CORTANA — System & Model Intelligence API Client.
 * Connects to /api/v1/system/status, /api/v1/models, /api/v1/fusion/config, and /api/v1/health.
 */

import type { SystemStatus } from "../../types";
import { apiClient, isMockMode } from "./client";
import { MOCK_SYSTEM_STATUS } from "../mock/systemStatus";

export interface SystemStatusData {
  services: SystemStatus[];
  model_version: string;
  release_phase: string;
  package_status: string;
  locked_threshold: number;
}

export async function fetchSystemStatus(): Promise<SystemStatusData> {
  if (isMockMode()) {
    return {
      services: MOCK_SYSTEM_STATUS,
      model_version: "CORTANA_FINAL_v1.0.0",
      release_phase: "Phase 6 — Final",
      package_status: "Smoke-tested, artifact-reproducible",
      locked_threshold: 0.98,
    };
  }

  return apiClient<SystemStatusData>("/api/v1/system/status");
}

export async function fetchModelIntelligence(): Promise<Record<string, unknown>> {
  if (isMockMode()) {
    return {
      source: "mock",
    };
  }

  return apiClient<Record<string, unknown>>("/api/v1/models");
}

export async function fetchFusionConfig(): Promise<Record<string, unknown>> {
  if (isMockMode()) {
    return {
      weights: { model_1: 0.8, model_2: 0.1, rules: 0.1 },
      decision_threshold: 0.98,
    };
  }

  return apiClient<Record<string, unknown>>("/api/v1/fusion/config");
}

export async function checkHealth(): Promise<{ status: string; database: string; ml_engine: string; version: string }> {
  return apiClient("/api/v1/health");
}
