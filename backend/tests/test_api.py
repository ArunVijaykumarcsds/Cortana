"""
CORTANA Tests — FastAPI API Layer (Stage 4).
Comprehensive testing of REST endpoints, data contracts, status transitions,
error responses, dataset isolation, and OpenAPI documentation.
"""

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.deps import get_db
from backend.app.db.database import Base
from backend.app.main import app


class TestFastAPIBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Isolated test database in memory using StaticPool so all connections share the same memory DB
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

    def tearDown(self):
        Base.metadata.drop_all(bind=self.test_engine)

    def test_01_health_endpoint(self):
        """1. Health endpoint returns operational telemetry."""
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        self.assertEqual(data["ml_engine"], "operational")
        self.assertEqual(data["version"], "1.0.0")

    def test_02_paysim_inference(self):
        """2. PaySim pure inference endpoint."""
        payload = {
            "dataset_context": "PaySim",
            "type": "PAYMENT",
            "amount": 150.0,
            "origin_balance_before": 1000.0,
            "origin_balance_after": 850.0,
            "destination_balance_before": 200.0,
            "destination_balance_after": 350.0,
        }
        resp = self.client.post("/api/v1/inference/paysim", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["dataset_context"], "PaySim")
        self.assertIn("fused_risk_score", data)
        self.assertIn("risk_level", data)
        self.assertIn("decision", data)

    def test_03_ulb_inference(self):
        """3. ULB pure inference endpoint."""
        features = {f"V{i}": 0.0 for i in range(1, 29)}
        payload = {
            "dataset_context": "ULB",
            "amount": 25.0,
            "time": 3600.0,
            "features": features,
        }
        resp = self.client.post("/api/v1/inference/ulb", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["dataset_context"], "ULB")
        self.assertIn("fused_risk_score", data)
        self.assertIn("risk_level", data)

    def test_04_paysim_dataset_isolation(self):
        """4. PaySim inference strictly keeps Model 2 as None."""
        payload = {
            "dataset_context": "PaySim",
            "type": "TRANSFER",
            "amount": 200000.0,
            "origin_balance_before": 200000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 200000.0,
        }
        resp = self.client.post("/api/v1/inference/paysim", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsNotNone(data["model_1"])
        self.assertIsNotNone(data["rules"])
        self.assertIsNone(data["model_2"])
        self.assertEqual(data["active_components"], ["model_1", "rules"])

    def test_05_ulb_dataset_isolation(self):
        """5. ULB inference strictly keeps Model 1 and Rules as None."""
        features = {f"V{i}": 0.0 for i in range(1, 29)}
        payload = {
            "dataset_context": "ULB",
            "amount": 80.0,
            "time": 100.0,
            "features": features,
        }
        resp = self.client.post("/api/v1/inference/ulb", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsNotNone(data["model_2"])
        self.assertIsNone(data["model_1"])
        self.assertIsNone(data["rules"])
        self.assertEqual(data["active_components"], ["model_2"])

    def test_06_invalid_dataset_context_fails(self):
        """6. Invalid dataset context fails safely."""
        payload = {
            "dataset_context": "INVALID_CONTEXT",
            "type": "PAYMENT",
            "amount": 50.0,
        }
        resp = self.client.post("/api/v1/transactions/score", json=payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid or missing 'dataset_context'", resp.json()["error"])

    def test_07_invalid_paysim_payload(self):
        """7. Invalid PaySim payload returns 422 validation error."""
        payload = {
            "dataset_context": "PaySim",
            # Missing amount and balances
            "type": "TRANSFER",
        }
        resp = self.client.post("/api/v1/inference/paysim", json=payload)
        self.assertEqual(resp.status_code, 422)
        self.assertIn("error", resp.json())

    def test_08_missing_ulb_feature_fails(self):
        """8. Missing ULB features fails safely."""
        incomplete_features = {"V1": 0.5, "V2": -1.0}  # Missing V3..V28
        payload = {
            "dataset_context": "ULB",
            "amount": 100.0,
            "time": 50.0,
            "features": incomplete_features,
        }
        resp = self.client.post("/api/v1/inference/ulb", json=payload)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("missing required features", resp.json()["error"].lower())

    def test_09_transaction_scoring_and_persistence(self):
        """9. Transaction creation and scoring via POST /transactions/score."""
        payload = {
            "id": "PSX-API-001",
            "dataset_context": "PaySim",
            "type": "TRANSFER",
            "amount": 350000.0,
            "origin_balance_before": 350000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 1000.0,
            "destination_balance_after": 351000.0,
        }
        resp = self.client.post("/api/v1/transactions/score", json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["id"], "PSX-API-001")
        self.assertEqual(data["dataset_context"], "PaySim")
        self.assertGreaterEqual(data["fusion"]["fused_risk"], 0.0)

    def test_10_transaction_retrieval(self):
        """10. Transaction retrieval by ID."""
        # Create a transaction
        payload = {
            "id": "PSX-API-002",
            "dataset_context": "PaySim",
            "type": "PAYMENT",
            "amount": 50.0,
            "origin_balance_before": 200.0,
            "origin_balance_after": 150.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 50.0,
        }
        self.client.post("/api/v1/transactions/score", json=payload)

        # Retrieve
        resp = self.client.get("/api/v1/transactions/PSX-API-002")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["id"], "PSX-API-002")
        self.assertEqual(data["amount"], 50.0)

    def test_11_transaction_pagination(self):
        """11. Transaction pagination."""
        for i in range(5):
            payload = {
                "id": f"PSX-PAG-{i}",
                "dataset_context": "PaySim",
                "type": "PAYMENT",
                "amount": float(10 * (i + 1)),
                "origin_balance_before": 100.0,
                "origin_balance_after": 100.0 - 10 * (i + 1),
                "destination_balance_before": 0.0,
                "destination_balance_after": float(10 * (i + 1)),
            }
            self.client.post("/api/v1/transactions/score", json=payload)

        # Query with limit 2
        resp = self.client.get("/api/v1/transactions?limit=2&offset=0")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 2)

        # Count endpoint
        count_resp = self.client.get("/api/v1/transactions/count")
        self.assertEqual(count_resp.status_code, 200)
        self.assertEqual(count_resp.json()["total"], 5)

    def test_12_transaction_filtering(self):
        """12. Transaction filtering by context."""
        # Insert 1 PaySim and 1 ULB
        p_payload = {
            "id": "PSX-FILT-1",
            "dataset_context": "PaySim",
            "type": "PAYMENT",
            "amount": 20.0,
            "origin_balance_before": 100.0,
            "origin_balance_after": 80.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 20.0,
        }
        self.client.post("/api/v1/transactions/score", json=p_payload)

        u_payload = {
            "id": "ULB-FILT-1",
            "dataset_context": "ULB",
            "amount": 30.0,
            "time": 200.0,
            "features": {f"V{i}": 0.0 for i in range(1, 29)},
        }
        self.client.post("/api/v1/transactions/score", json=u_payload)

        # Filter PaySim only
        resp_p = self.client.get("/api/v1/transactions?context=PaySim")
        self.assertEqual(resp_p.status_code, 200)
        self.assertEqual(len(resp_p.json()), 1)
        self.assertEqual(resp_p.json()[0]["dataset_context"], "PaySim")

        # Filter ULB only
        resp_u = self.client.get("/api/v1/transactions?context=ULB")
        self.assertEqual(resp_u.status_code, 200)
        self.assertEqual(len(resp_u.json()), 1)
        self.assertEqual(resp_u.json()[0]["dataset_context"], "ULB")

    def test_13_alert_retrieval(self):
        """13. Alert retrieval and filtering."""
        # Insert high risk transaction triggering alert
        payload = {
            "id": "PSX-ALERT-01",
            "dataset_context": "PaySim",
            "type": "TRANSFER",
            "amount": 800000.0,
            "origin_balance_before": 800000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 800000.0,
        }
        self.client.post("/api/v1/transactions/score", json=payload)

        alerts_resp = self.client.get("/api/v1/alerts")
        self.assertEqual(alerts_resp.status_code, 200)
        alerts = alerts_resp.json()
        self.assertGreaterEqual(len(alerts), 1)

    def test_14_alert_status_update(self):
        """14. Alert status update (PATCH /alerts/{id}/status)."""
        payload = {
            "id": "PSX-ALERT-02",
            "dataset_context": "PaySim",
            "type": "CASH_OUT",
            "amount": 900000.0,
            "origin_balance_before": 900000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 0.0,
        }
        self.client.post("/api/v1/transactions/score", json=payload)

        alerts = self.client.get("/api/v1/alerts").json()
        alert_id = alerts[0]["id"]

        # Update to UNDER_REVIEW
        patch_resp = self.client.patch(f"/api/v1/alerts/{alert_id}/status", json={"status": "UNDER_REVIEW"})
        self.assertEqual(patch_resp.status_code, 200)
        self.assertEqual(patch_resp.json()["status"], "UNDER_REVIEW")

    def test_15_investigation_retrieval(self):
        """15. Investigation retrieval."""
        # High risk / review transaction
        payload = {
            "id": "PSX-INV-001",
            "dataset_context": "PaySim",
            "type": "TRANSFER",
            "amount": 950000.0,
            "origin_balance_before": 950000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 0.0,
        }
        self.client.post("/api/v1/transactions/score", json=payload)

        invs_resp = self.client.get("/api/v1/investigations")
        self.assertEqual(invs_resp.status_code, 200)
        invs = invs_resp.json()
        self.assertGreaterEqual(len(invs), 1)

        inv_id = invs[0]["id"]
        single_resp = self.client.get(f"/api/v1/investigations/{inv_id}")
        self.assertEqual(single_resp.status_code, 200)
        self.assertEqual(single_resp.json()["id"], inv_id)
        self.assertGreaterEqual(len(single_resp.json()["audit_trail"]), 1)

    def test_16_audit_event_creation(self):
        """16. Audit event creation via POST /investigations/{id}/events."""
        payload = {
            "id": "PSX-INV-002",
            "dataset_context": "PaySim",
            "type": "TRANSFER",
            "amount": 950000.0,
            "origin_balance_before": 950000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 0.0,
        }
        self.client.post("/api/v1/transactions/score", json=payload)
        inv_id = self.client.get("/api/v1/investigations").json()[0]["id"]

        event_payload = {
            "action": "EXPLANATION_REQUESTED",
            "actor": "R. Castillo",
            "note": "Reviewing customer verification details",
        }
        resp = self.client.post(f"/api/v1/investigations/{inv_id}/events", json=event_payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        actions = [e["action"] for e in data["audit_trail"]]
        self.assertIn("EXPLANATION_REQUESTED", actions)

    def test_17_append_only_audit_behavior(self):
        """17. Append-only audit trail verification on investigation resolution."""
        payload = {
            "id": "PSX-INV-003",
            "dataset_context": "PaySim",
            "type": "TRANSFER",
            "amount": 950000.0,
            "origin_balance_before": 950000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 0.0,
        }
        self.client.post("/api/v1/transactions/score", json=payload)
        inv_id = self.client.get("/api/v1/investigations").json()[0]["id"]

        # Resolve case as CONFIRMED_FRAUD
        update_payload = {
            "resolution": "FRAUD_CONFIRMED",
            "actor": "J. Okafor",
            "note": "Rapid drain pattern confirmed fraudulent",
        }
        resp = self.client.patch(f"/api/v1/investigations/{inv_id}", json=update_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "CLOSED")
        self.assertEqual(data["resolution"], "FRAUD_CONFIRMED")
        actions = [e["action"] for e in data["audit_trail"]]
        self.assertIn("CONFIRMED_FRAUD", actions)

    def test_18_system_and_model_endpoints(self):
        """18. Model and system metadata endpoints."""
        # /system/status
        status_resp = self.client.get("/api/v1/system/status")
        self.assertEqual(status_resp.status_code, 200)
        self.assertIn("services", status_resp.json())
        self.assertEqual(status_resp.json()["locked_threshold"], 0.98)

        # /models
        models_resp = self.client.get("/api/v1/models")
        self.assertEqual(models_resp.status_code, 200)
        m_data = models_resp.json()
        self.assertIn("model_1", m_data)
        self.assertIn("model_2", m_data)
        self.assertIn("rules_engine", m_data)
        self.assertEqual(m_data["model_1"]["weight"], 0.80)
        self.assertEqual(m_data["model_2"]["weight"], 0.10)

        # /fusion/config
        fusion_resp = self.client.get("/api/v1/fusion/config")
        self.assertEqual(fusion_resp.status_code, 200)
        f_data = fusion_resp.json()
        self.assertEqual(f_data["decision_threshold"], 0.98)
        self.assertEqual(f_data["cross_dataset_row_pairing"], False)

    def test_19_cors_and_root_behavior(self):
        """19. CORS and root endpoint."""
        root_resp = self.client.get("/")
        self.assertEqual(root_resp.status_code, 200)
        self.assertEqual(root_resp.json()["status"], "online")

        # Test CORS headers on preflight
        cors_resp = self.client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(cors_resp.status_code, 200)
        self.assertEqual(cors_resp.headers.get("access-control-allow-origin"), "http://localhost:5173")

    def test_20_error_responses(self):
        """20. Structured error responses for 404 not found."""
        resp = self.client.get("/api/v1/transactions/NON_EXISTENT_TX_ID")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("error", resp.json())

        resp_alert = self.client.get("/api/v1/alerts/NON_EXISTENT_ALERT")
        self.assertEqual(resp_alert.status_code, 404)

        resp_inv = self.client.get("/api/v1/investigations/NON_EXISTENT_CASE")
        self.assertEqual(resp_inv.status_code, 404)

    def test_21_openapi_and_docs(self):
        """21. OpenAPI schema and docs availability."""
        docs_resp = self.client.get("/docs")
        self.assertEqual(docs_resp.status_code, 200)

        openapi_resp = self.client.get("/openapi.json")
        self.assertEqual(openapi_resp.status_code, 200)
        schema = openapi_resp.json()
        self.assertEqual(schema["info"]["title"], "CORTANA Financial Risk Intelligence API")
        self.assertIn("/api/v1/health", schema["paths"])
        self.assertIn("/api/v1/transactions", schema["paths"])
        self.assertIn("/api/v1/inference/paysim", schema["paths"])
        self.assertIn("/api/v1/inference/ulb", schema["paths"])


if __name__ == "__main__":
    unittest.main()
