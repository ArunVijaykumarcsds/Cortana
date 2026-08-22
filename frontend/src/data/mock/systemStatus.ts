import type { SystemStatus } from "../../types";

export const MOCK_SYSTEM_STATUS: SystemStatus[] = [
  { service: "Model 1 — Random Forest", state: "OPERATIONAL", detail: "PaySim · fraud_probability" },
  { service: "Model 2 — Isolation Forest", state: "OPERATIONAL", detail: "ULB · anomaly_score" },
  { service: "Rules Engine", state: "OPERATIONAL", detail: "6 behavioral rules active" },
  { service: "Fusion Engine", state: "OPERATIONAL", detail: "Weights 0.80 / 0.10 / 0.10 · threshold 0.98" },
  { service: "Calibration", state: "OPERATIONAL", detail: "Percentile-rank, higher-is-riskier" },
  { service: "Database (PostgreSQL)", state: "PLANNED", detail: "Scheduled for integration phase" },
  { service: "AI Explanation Layer", state: "PLANNED", detail: "LLM explanation service — not yet connected" },
  { service: "API Gateway (FastAPI)", state: "PLANNED", detail: "Frontend currently on mock data layer" },
];

export const DEPLOYMENT = {
  modelVersion: "CORTANA_FINAL_v1.0.0",
  releasePhase: "Phase 6 — Final",
  packageStatus: "Smoke-tested, artifact-reproducible",
};
