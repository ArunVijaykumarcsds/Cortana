"""
CORTANA Tests — End-to-End Inference Service Integration.
Validates complete transaction processing, outputs formatting, and serializability.
"""

import unittest
from pathlib import Path
from backend.app.core.inference import InferenceEngine
from backend.app.schemas.transaction import PaySimTransactionInput, ULBTransactionInput


class TestInferenceEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent.parent
        cls.engine = InferenceEngine(cls.root)

    def test_paysim_end_to_end_benign(self):
        tx = PaySimTransactionInput(
            id="PSX-001",
            type="PAYMENT",
            amount=45.50,
            origin_balance_before=500.0,
            origin_balance_after=454.50,
            destination_balance_before=100.0,
            destination_balance_after=145.50,
        )
        res = self.engine.score_paysim_transaction(tx)
        
        self.assertEqual(res.dataset_context, "PaySim")
        self.assertGreaterEqual(res.fused_risk_score, 0.0)
        self.assertLessEqual(res.fused_risk_score, 1.0)
        self.assertIn(res.risk_level, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        self.assertEqual(res.decision, "PASS")
        self.assertEqual(len(res.rules.triggered), 0)

        # JSON serializability check
        json_str = res.model_dump_json()
        self.assertIsInstance(json_str, str)

    def test_paysim_end_to_end_fraud_review(self):
        tx = PaySimTransactionInput(
            id="PSX-999",
            type="TRANSFER",
            amount=850000.0,
            origin_balance_before=850000.0,
            origin_balance_after=0.0,
            destination_balance_before=0.0,
            destination_balance_after=0.0,  # anomalous zero
        )
        res = self.engine.score_paysim_transaction(tx)

        self.assertEqual(res.dataset_context, "PaySim")
        self.assertGreaterEqual(res.fused_risk_score, 0.75)
        self.assertIn(res.risk_level, ["HIGH", "CRITICAL"])
        self.assertGreater(len(res.rules.triggered), 0)

    def test_ulb_end_to_end_scoring(self):
        features = {f"V{i}": 0.0 for i in range(1, 29)}
        features["V1"] = -3.5
        features["V2"] = 4.2
        features["V3"] = -5.1
        tx = ULBTransactionInput(
            id="ULB-001",
            amount=350.0,
            time=45000.0,
            features=features,
        )
        res = self.engine.score_ulb_transaction(tx)

        self.assertEqual(res.dataset_context, "ULB")
        self.assertIsNotNone(res.model_2)
        self.assertGreaterEqual(res.fused_risk_score, 0.0)
        self.assertLessEqual(res.fused_risk_score, 1.0)


if __name__ == "__main__":
    unittest.main()
