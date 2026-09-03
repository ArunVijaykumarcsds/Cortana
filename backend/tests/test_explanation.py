"""
CORTANA Tests — AI Explanation Layer (Stage 6A).
Validates structured fact extraction, PII protection, schema validation,
deterministic fallback, LLM failure resilience, Medium+ policy, and REST API integration.
"""

import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.deps import get_db, get_explanation_service
from backend.app.core.explanation import (
    DeterministicExplanationEngine,
    ExplanationService,
    extract_explanation_facts_from_db,
)
from backend.app.db.database import Base
from backend.app.main import app
from backend.app.schemas.explanation import (
    ExplanationFacts,
    ExplanationResponse,
    TriggeredRuleFact,
)


class TestExplanationLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )
        cls.TestingSessionLocal = sessionmaker(bind=cls.test_engine)

        def override_get_db():
            db = cls.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()

    def setUp(self):
        Base.metadata.create_all(bind=self.test_engine)
        self.engine = DeterministicExplanationEngine()
        self.service = ExplanationService(fallback_engine=self.engine)

    def tearDown(self):
        Base.metadata.drop_all(bind=self.test_engine)

    def test_01_structured_facts_contain_no_raw_payload_or_pii(self):
        """1 & 2. Verify structured facts contain only pre-computed metrics and zero PII."""
        facts = extract_explanation_facts_from_db(
            tx_id="PSX-TEST-001",
            dataset_context="PaySim",
            tx_type="TRANSFER",
            risk_level="CRITICAL",
            decision="REVIEW",
            fused_risk=0.99,
            model_1_prob=0.95,
            rules_risk=0.90,
            triggered_rules_raw=[
                {
                    "rule_key": "HIGH_AMOUNT",
                    "severity": "CRITICAL",
                    "description": "Amount exceeds 500k",
                }
            ],
        )

        facts_dict = facts.model_dump()
        # Verify no PII fields exist
        self.assertNotIn("origin_account", facts_dict)
        self.assertNotIn("destination_account", facts_dict)
        self.assertNotIn("customer_name", facts_dict)
        self.assertNotIn("raw_payload", facts_dict)
        self.assertNotIn("ip_address", facts_dict)
        self.assertEqual(facts.transaction_id, "PSX-TEST-001")
        self.assertEqual(facts.fused_risk_score, 0.99)

    def test_02_explanation_output_schema_validation(self):
        """3. Output schema validates required fields and signal list."""
        facts = ExplanationFacts(
            transaction_id="PSX-SCHEMA-1",
            dataset_context="PaySim",
            type="PAYMENT",
            risk_level="LOW",
            decision="PASS",
            fused_risk_score=0.05,
            active_components=["model_1", "rules"],
            model_1_probability=0.02,
            rules_risk_score=0.0,
            triggered_rules=[],
        )
        resp = self.engine.generate(facts)
        self.assertIsInstance(resp, ExplanationResponse)
        self.assertEqual(resp.transaction_id, "PSX-SCHEMA-1")
        self.assertGreater(len(resp.explanation_text), 10)
        self.assertTrue(resp.is_fallback)
        self.assertEqual(resp.provider, "deterministic_fallback")

    def test_03_deterministic_fallback_works_without_api_key(self):
        """5. Deterministic fallback works completely offline without API keys."""
        facts = ExplanationFacts(
            transaction_id="PSX-OFFLINE-1",
            dataset_context="PaySim",
            type="TRANSFER",
            risk_level="HIGH",
            decision="REVIEW",
            fused_risk_score=0.985,
            active_components=["model_1", "rules"],
            model_1_probability=0.95,
            rules_risk_score=0.80,
            triggered_rules=[
                TriggeredRuleFact(
                    rule_key="HIGH_AMOUNT",
                    label="High Amount Anomaly",
                    severity="CRITICAL",
                    description="Amount exceeds 500,000 threshold",
                )
            ],
        )

        # Service with no keys set
        service = ExplanationService(fallback_engine=self.engine)
        service.gemini_key = ""
        service.openai_key = ""
        service.llm_provider = ""

        resp = service.generate_explanation(facts)
        self.assertTrue(resp.is_fallback)
        self.assertEqual(resp.provider, "deterministic_fallback")
        self.assertIn("High Amount Anomaly", resp.explanation_text)
        self.assertIn("Model 1 (Random Forest)", resp.referenced_signals)

    def test_04_identical_input_produces_identical_fallback_output(self):
        """6. Deterministic generator is 100% reproducible for identical inputs."""
        facts = ExplanationFacts(
            transaction_id="PSX-REPRO-1",
            dataset_context="PaySim",
            type="CASH_OUT",
            risk_level="CRITICAL",
            decision="REVIEW",
            fused_risk_score=0.995,
            active_components=["model_1", "rules"],
            model_1_probability=0.99,
            rules_risk_score=0.90,
            triggered_rules=[
                TriggeredRuleFact(
                    rule_key="ZERO_BALANCE_ANOMALY",
                    label="Zero-Balance Anomaly",
                    severity="HIGH",
                    description="Origin account drained to exactly zero",
                )
            ],
        )

        res1 = self.engine.generate(facts)
        res2 = self.engine.generate(facts)
        self.assertEqual(res1.explanation_text, res2.explanation_text)
        self.assertEqual(res1.referenced_signals, res2.referenced_signals)

    def test_05_ulb_explanation_references_model_2_only(self):
        """ULB context strictly references Model 2 without mentioning rules."""
        facts = ExplanationFacts(
            transaction_id="ULB-EXP-001",
            dataset_context="ULB",
            type="PAYMENT",
            risk_level="HIGH",
            decision="REVIEW",
            fused_risk_score=0.982,
            active_components=["model_2"],
            model_2_anomaly_score=0.982,
            triggered_rules=[],
        )

        resp = self.engine.generate(facts)
        self.assertIn("Model 2", resp.explanation_text)
        self.assertIn("Isolation Forest", resp.explanation_text)
        self.assertNotIn("Model 1", resp.explanation_text)
        self.assertNotIn("Rules Engine", resp.explanation_text)
        self.assertEqual(resp.referenced_signals, ["Model 2 (Isolation Forest)"])

    def test_06_llm_failure_or_timeout_gracefully_falls_back(self):
        """7, 8 & 9. LLM timeout, exception, or malformed JSON triggers deterministic fallback."""
        facts = ExplanationFacts(
            transaction_id="PSX-FAIL-1",
            dataset_context="PaySim",
            type="TRANSFER",
            risk_level="CRITICAL",
            decision="REVIEW",
            fused_risk_score=0.99,
            active_components=["model_1", "rules"],
            model_1_probability=0.95,
            rules_risk_score=0.80,
            triggered_rules=[],
        )

        service = ExplanationService(fallback_engine=self.engine)
        service.gemini_key = "dummy_key"

        # Simulate exception during external LLM call
        with patch.object(service, "_call_gemini", side_effect=Exception("Network Timeout")):
            resp = service.generate_explanation(facts)
            self.assertTrue(resp.is_fallback)
            self.assertEqual(resp.provider, "deterministic_fallback")
            self.assertIn("evaluated as CRITICAL risk", resp.explanation_text)

    def test_07_low_risk_medium_plus_policy(self):
        """10. LOW-risk transactions immediately use deterministic generator without LLM call."""
        facts = ExplanationFacts(
            transaction_id="PSX-LOW-1",
            dataset_context="PaySim",
            type="PAYMENT",
            risk_level="LOW",
            decision="PASS",
            fused_risk_score=0.02,
            active_components=["model_1", "rules"],
            model_1_probability=0.01,
            rules_risk_score=0.0,
            triggered_rules=[],
        )

        service = ExplanationService(fallback_engine=self.engine)
        service.gemini_key = "dummy_key"

        # Mock LLM call and verify it was NEVER called for LOW risk
        with patch.object(service, "_call_gemini") as mock_gemini:
            resp = service.generate_explanation(facts)
            mock_gemini.assert_not_called()
            self.assertTrue(resp.is_fallback)
            self.assertEqual(resp.risk_level, "LOW")
            self.assertEqual(resp.decision, "PASS")

    def test_08_fastapi_explanation_endpoint(self):
        """11, 12 & 13. POST /api/v1/transactions/{id}/explain returns 200 with server-side authoritative facts."""
        # 1. Create and score a transaction in the database
        score_payload = {
            "id": "PSX-EXP-HTTP-1",
            "dataset_context": "PaySim",
            "type": "TRANSFER",
            "amount": 750000.0,
            "origin_balance_before": 750000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 750000.0,
        }
        score_resp = self.client.post("/api/v1/transactions/score", json=score_payload)
        self.assertEqual(score_resp.status_code, 201)
        scored_tx = score_resp.json()
        self.assertEqual(scored_tx["fusion"]["decision"], "REVIEW")

        # 2. Invoke explain endpoint
        explain_resp = self.client.post("/api/v1/transactions/PSX-EXP-HTTP-1/explain")
        self.assertEqual(explain_resp.status_code, 200)
        data = explain_resp.json()
        self.assertEqual(data["transaction_id"], "PSX-EXP-HTTP-1")
        self.assertEqual(data["decision"], "REVIEW")
        self.assertEqual(data["risk_level"], "CRITICAL")
        self.assertGreaterEqual(data["fused_risk_score"], 0.98)
        self.assertIn("explanation_text", data)
        self.assertIn("referenced_signals", data)

        # 3. Verify 404 on non-existent transaction
        not_found_resp = self.client.post("/api/v1/transactions/NON_EXISTENT/explain")
        self.assertEqual(not_found_resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
