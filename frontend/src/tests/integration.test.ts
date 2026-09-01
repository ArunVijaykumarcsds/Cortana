/**
 * CORTANA — Frontend Integration Tests (Stage 5).
 * Tests API client, mock fallback behaviors, error handling, and data contracts.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

import { ApiError, apiClient } from "../data/api/client";
import {
  fetchTransactions,
  fetchTransactionById,
  fetchTransactionCount,
  fetchTransactionExplanation,
  scoreTransaction,
} from "../data/api/transactions";
import {
  fetchAlerts,
  fetchAlertById,
  updateAlertStatus,
} from "../data/api/alerts";
import {
  fetchInvestigations,
  fetchInvestigationById,
  appendInvestigationEvent,
  updateInvestigation,
} from "../data/api/investigations";
import {
  fetchSystemStatus,
  fetchModelIntelligence,
  fetchFusionConfig,
  checkHealth,
} from "../data/api/system";

describe("Frontend API Client & Integration Layer", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("1. ApiError encapsulates status, message, and error body", () => {
    const err = new ApiError("Not found", 404, { detail: "Missing record" });
    expect(err.status).toBe(404);
    expect(err.message).toBe("Not found");
    expect(err.data).toEqual({ detail: "Missing record" });
  });

  it("2. Health endpoint parses operational state correctly", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          status: "healthy",
          database: "connected",
          ml_engine: "operational",
          version: "1.0.0",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const res = await checkHealth();
    expect(res.status).toBe("healthy");
    expect(res.database).toBe("connected");
    expect(res.ml_engine).toBe("operational");
    expect(res.version).toBe("1.0.0");
  });

  it("3. fetchTransactions appends filter parameters and parses response", async () => {
    globalThis.fetch = vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
      const urlStr = input.toString();
      expect(urlStr).toContain("context=PaySim");
      expect(urlStr).toContain("risk_level=HIGH");
      return new Response(
        JSON.stringify([
          {
            id: "PSX-101",
            dataset_context: "PaySim",
            type: "TRANSFER",
            amount: 50000,
            currency: "USD",
            origin_account: "C101",
            destination_account: "C102",
            origin_balance_before: 50000,
            origin_balance_after: 0,
            destination_balance_before: 0,
            destination_balance_after: 50000,
            timestamp: "2026-08-22T00:00:00Z",
            fusion: {
              fused_risk: 0.95,
              risk_level: "HIGH",
              decision: "PASS",
              weights: { model_1: 0.8, model_2: 0.1, rules: 0.1 },
              active_weights: { model_1: 0.88, rules: 0.11 },
              threshold: 0.98,
            },
          },
        ]),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    });

    const res = await fetchTransactions({ context: "PaySim", risk_level: "HIGH" });
    expect(res.length).toBe(1);
    expect(res[0].id).toBe("PSX-101");
    expect(res[0].dataset_context).toBe("PaySim");
  });

  it("4. fetchTransactionById retrieves single transaction or undefined on 404", async () => {
    // Found case
    globalThis.fetch = vi.fn().mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          id: "PSX-102",
          dataset_context: "PaySim",
          type: "PAYMENT",
          amount: 100,
          currency: "USD",
          origin_account: "C1",
          destination_account: "M1",
          origin_balance_before: 200,
          origin_balance_after: 100,
          destination_balance_before: 0,
          destination_balance_after: 100,
          timestamp: "2026-08-22T00:00:00Z",
          fusion: {
            fused_risk: 0.05,
            risk_level: "LOW",
            decision: "PASS",
            weights: { model_1: 0.8, model_2: 0.1, rules: 0.1 },
            active_weights: { model_1: 0.88, rules: 0.11 },
            threshold: 0.98,
          },
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const found = await fetchTransactionById("PSX-102");
    expect(found).toBeDefined();
    expect(found?.id).toBe("PSX-102");

    // 404 case
    globalThis.fetch = vi.fn().mockResolvedValueOnce(
      new Response(JSON.stringify({ error: "Not found" }), {
        status: 404,
        statusText: "Not Found",
        headers: { "Content-Type": "application/json" },
      })
    );

    const notFound = await fetchTransactionById("PSX-UNKNOWN");
    expect(notFound).toBeUndefined();
  });

  it("5. fetchTransactionCount retrieves transaction counts", async () => {
    globalThis.fetch = vi.fn().mockResolvedValueOnce(
      new Response(
        JSON.stringify({ total: 42, context: "PaySim", risk_level: "HIGH" }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const count = await fetchTransactionCount({ context: "PaySim", risk_level: "HIGH" });
    expect(count.total).toBe(42);
  });

  it("6. fetchAlerts and fetchAlertById query alert queue", async () => {
    globalThis.fetch = vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
      const urlStr = input.toString();
      if (urlStr.includes("/api/v1/alerts/A-1")) {
        return new Response(
          JSON.stringify({
            id: "A-1",
            transaction_id: "PSX-101",
            dataset_context: "PaySim",
            type: "TRANSFER",
            risk_score: 0.99,
            risk_level: "CRITICAL",
            decision: "REVIEW",
            status: "OPEN",
            timestamp: "2026-08-22T00:00:00Z",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      return new Response(
        JSON.stringify([
          {
            id: "A-1",
            transaction_id: "PSX-101",
            dataset_context: "PaySim",
            type: "TRANSFER",
            risk_score: 0.99,
            risk_level: "CRITICAL",
            decision: "REVIEW",
            status: "OPEN",
            timestamp: "2026-08-22T00:00:00Z",
          },
        ]),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    });

    const alerts = await fetchAlerts({ status: "OPEN" });
    expect(alerts.length).toBe(1);
    expect(alerts[0].status).toBe("OPEN");

    const singleAlert = await fetchAlertById("A-1");
    expect(singleAlert?.id).toBe("A-1");
  });

  it("7. updateAlertStatus issues PATCH request and updates record", async () => {
    globalThis.fetch = vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      expect(init?.method).toBe("PATCH");
      expect(input.toString()).toContain("/api/v1/alerts/A-1/status");
      const parsedBody = JSON.parse(init?.body as string);
      expect(parsedBody.status).toBe("UNDER_REVIEW");

      return new Response(
        JSON.stringify({
          id: "A-1",
          transaction_id: "PSX-101",
          dataset_context: "PaySim",
          type: "TRANSFER",
          risk_score: 0.99,
          risk_level: "CRITICAL",
          decision: "REVIEW",
          status: "UNDER_REVIEW",
          timestamp: "2026-08-22T00:00:00Z",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    });

    const updated = await updateAlertStatus("A-1", "UNDER_REVIEW");
    expect(updated.status).toBe("UNDER_REVIEW");
  });

  it("8. fetchInvestigations and fetchInvestigationById retrieve cases", async () => {
    globalThis.fetch = vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
      const urlStr = input.toString();
      if (urlStr.includes("/api/v1/investigations/C-1")) {
        return new Response(
          JSON.stringify({
            id: "C-1",
            transaction_id: "PSX-101",
            risk_level: "CRITICAL",
            risk_score: 0.99,
            decision: "REVIEW",
            status: "OPEN",
            opened_at: "2026-08-22T00:00:00Z",
            audit_trail: [
              {
                id: "e-1",
                action: "CASE_OPENED",
                actor: "System",
                timestamp: "2026-08-22T00:00:00Z",
              },
            ],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      return new Response(
        JSON.stringify([
          {
            id: "C-1",
            transaction_id: "PSX-101",
            risk_level: "CRITICAL",
            risk_score: 0.99,
            decision: "REVIEW",
            status: "OPEN",
            opened_at: "2026-08-22T00:00:00Z",
            audit_trail: [
              {
                id: "e-1",
                action: "CASE_OPENED",
                actor: "System",
                timestamp: "2026-08-22T00:00:00Z",
              },
            ],
          },
        ]),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    });

    const list = await fetchInvestigations({ status: "OPEN" });
    expect(list.length).toBeGreaterThan(0);

    const inv = await fetchInvestigationById("C-1");
    expect(inv).toBeDefined();
    expect(inv?.id).toBe("C-1");
    expect(inv?.audit_trail.length).toBe(1);
  });

  it("9. appendInvestigationEvent and updateInvestigation modify case status and audit trail", async () => {
    globalThis.fetch = vi.fn().mockImplementation(async (_input: RequestInfo | URL, init?: RequestInit) => {
      const parsed = JSON.parse(init?.body as string);

      if (init?.method === "POST") {
        expect(parsed.action).toBe("NOTE_ADDED");
        return new Response(
          JSON.stringify({
            id: "C-1",
            transaction_id: "PSX-101",
            risk_level: "CRITICAL",
            risk_score: 0.99,
            decision: "REVIEW",
            status: "OPEN",
            opened_at: "2026-08-22T00:00:00Z",
            audit_trail: [
              { id: "e-1", action: "CASE_OPENED", actor: "System", timestamp: "2026-08-22T00:00:00Z" },
              { id: "e-2", action: "NOTE_ADDED", actor: "Analyst", timestamp: "2026-08-22T00:01:00Z", note: "Test note" },
            ],
          }),
          { status: 201, headers: { "Content-Type": "application/json" } }
        );
      } else {
        expect(parsed.resolution).toBe("FRAUD_CONFIRMED");
        return new Response(
          JSON.stringify({
            id: "C-1",
            transaction_id: "PSX-101",
            risk_level: "CRITICAL",
            risk_score: 0.99,
            decision: "REVIEW",
            status: "CLOSED",
            resolution: "FRAUD_CONFIRMED",
            opened_at: "2026-08-22T00:00:00Z",
            audit_trail: [
              { id: "e-1", action: "CASE_OPENED", actor: "System", timestamp: "2026-08-22T00:00:00Z" },
              { id: "e-2", action: "CONFIRMED_FRAUD", actor: "Analyst", timestamp: "2026-08-22T00:02:00Z" },
            ],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
    });

    const updatedEvent = await appendInvestigationEvent("C-1", {
      action: "NOTE_ADDED",
      actor: "Analyst",
      note: "Test note",
    });
    expect(updatedEvent.audit_trail.length).toBe(2);

    const updatedCase = await updateInvestigation("C-1", {
      resolution: "FRAUD_CONFIRMED",
      actor: "Analyst",
    });
    expect(updatedCase.status).toBe("CLOSED");
    expect(updatedCase.resolution).toBe("FRAUD_CONFIRMED");
  });

  it("10. fetchSystemStatus retrieves pipeline state", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          services: [
            { service: "Model 1", state: "OPERATIONAL", detail: "Random Forest" },
            { service: "Model 2", state: "OPERATIONAL", detail: "Isolation Forest" },
          ],
          model_version: "CORTANA_FINAL_v1.0.0",
          release_phase: "Phase 6 — Final",
          package_status: "Smoke-tested",
          locked_threshold: 0.98,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const statusData = await fetchSystemStatus();
    expect(statusData.services.length).toBe(2);
    expect(statusData.locked_threshold).toBe(0.98);
  });

  it("11. fetchModelIntelligence & fetchFusionConfig retrieve configuration", async () => {
    globalThis.fetch = vi.fn().mockImplementation(async (input: RequestInfo | URL) => {
      if (input.toString().includes("fusion/config")) {
        return new Response(
          JSON.stringify({
            weights: { model_1: 0.8, model_2: 0.1, rules: 0.1 },
            decision_threshold: 0.98,
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      }
      return new Response(
        JSON.stringify({
          model_1: { algorithm: "RandomForestClassifier", weight: 0.8 },
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    });

    const models = await fetchModelIntelligence();
    expect(models.model_1).toBeDefined();
    const fusion = await fetchFusionConfig();
    expect(fusion.decision_threshold).toBe(0.98);
  });

  it("12. Error handling: HTTP 500 error throws ApiError with clean message", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: "Internal Server Error" }), {
        status: 500,
        statusText: "Internal Server Error",
        headers: { "Content-Type": "application/json" },
      })
    );

    await expect(apiClient("/api/v1/health")).rejects.toThrow(ApiError);
  });

  it("13. scoreTransaction sends payload to /api/v1/transactions/score", async () => {
    globalThis.fetch = vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      expect(init?.method).toBe("POST");
      expect(input.toString()).toContain("/api/v1/transactions/score");
      return new Response(
        JSON.stringify({
          id: "PSX-SCORED-1",
          dataset_context: "PaySim",
          type: "TRANSFER",
          amount: 200000,
          currency: "USD",
          origin_account: "C1",
          destination_account: "C2",
          origin_balance_before: 200000,
          origin_balance_after: 0,
          destination_balance_before: 0,
          destination_balance_after: 200000,
          timestamp: "2026-08-22T00:00:00Z",
          fusion: {
            fused_risk: 0.99,
            risk_level: "CRITICAL",
            decision: "REVIEW",
            weights: { model_1: 0.8, model_2: 0.1, rules: 0.1 },
            active_weights: { model_1: 0.88, rules: 0.11 },
            threshold: 0.98,
          },
        }),
        { status: 201, headers: { "Content-Type": "application/json" } }
      );
    });

    const res = await scoreTransaction({
      dataset_context: "PaySim",
      type: "TRANSFER",
      amount: 200000,
      origin_balance_before: 200000,
      origin_balance_after: 0,
      destination_balance_before: 0,
      destination_balance_after: 200000,
    });

    expect(res.id).toBe("PSX-SCORED-1");
    expect(res.fusion.decision).toBe("REVIEW");
  });

  it("14. fetchTransactionExplanation calls POST /api/v1/transactions/{id}/explain", async () => {
    globalThis.fetch = vi.fn().mockImplementation(async (input: RequestInfo | URL, init?: RequestInit) => {
      expect(init?.method).toBe("POST");
      expect(input.toString()).toContain("/api/v1/transactions/PSX-EXP-1/explain");
      return new Response(
        JSON.stringify({
          transaction_id: "PSX-EXP-1",
          risk_level: "CRITICAL",
          decision: "REVIEW",
          fused_risk_score: 0.99,
          explanation_text: "Transaction was evaluated as CRITICAL risk due to rapid balance drain.",
          referenced_signals: ["Model 1 (Random Forest)", "Rule: HIGH_AMOUNT"],
          provider: "deterministic_fallback",
          is_fallback: true,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    });

    const res = await fetchTransactionExplanation("PSX-EXP-1");
    expect(res.transaction_id).toBe("PSX-EXP-1");
    expect(res.decision).toBe("REVIEW");
    expect(res.is_fallback).toBe(true);
    expect(res.referenced_signals).toContain("Model 1 (Random Forest)");
  });

  it("15. fetchTransactionExplanation handles error responses safely", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: "Transaction not found" }), {
        status: 404,
        statusText: "Not Found",
        headers: { "Content-Type": "application/json" },
      })
    );

    await expect(fetchTransactionExplanation("NON_EXISTENT")).rejects.toThrow(ApiError);
  });
});

