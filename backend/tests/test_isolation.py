"""
CORTANA Tests — Dataset Isolation & Architectural Guardrails.
Guarantees zero cross-dataset row pairing between PaySim and ULB.
"""

import unittest
from pathlib import Path
from backend.app.core.inference import InferenceEngine
from backend.app.schemas.transaction import PaySimTransactionInput, ULBTransactionInput


class TestDatasetIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent.parent
        cls.engine = InferenceEngine(cls.root)

    def test_paysim_activates_model_1_and_rules_only(self):
        """
        5. PaySim activates Model 1 + Rules only.
        7. PaySim never activates Model 2.
        """
        tx = PaySimTransactionInput(
            type="TRANSFER",
            amount=150000.0,
            origin_balance_before=150000.0,
            origin_balance_after=0.0,
            destination_balance_before=5000.0,
            destination_balance_after=155000.0,
        )
        result = self.engine.score_paysim_transaction(tx)

        self.assertEqual(result.dataset_context, "PaySim")
        self.assertIsNotNone(result.model_1)
        self.assertIsNotNone(result.rules)
        self.assertIsNone(result.model_2)  # Strictly None

        self.assertEqual(result.active_components, ["model_1", "rules"])
        self.assertIn("model_1", result.calibrated_component_risks)
        self.assertIn("rules", result.calibrated_component_risks)
        self.assertNotIn("model_2", result.calibrated_component_risks)

        self.assertTrue(result.architecture_safe)

    def test_ulb_activates_model_2_only(self):
        """
        6. ULB activates Model 2 only.
        8. ULB never activates Model 1 or Rules.
        """
        features = {f"V{i}": 0.0 for i in range(1, 29)}
        tx = ULBTransactionInput(
            amount=75.0,
            time=1234.0,
            features=features,
        )
        result = self.engine.score_ulb_transaction(tx)

        self.assertEqual(result.dataset_context, "ULB")
        self.assertIsNotNone(result.model_2)
        self.assertIsNone(result.model_1)  # Strictly None
        self.assertIsNone(result.rules)    # Strictly None

        self.assertEqual(result.active_components, ["model_2"])
        self.assertIn("model_2", result.calibrated_component_risks)
        self.assertNotIn("model_1", result.calibrated_component_risks)
        self.assertNotIn("rules", result.calibrated_component_risks)

        self.assertTrue(result.architecture_safe)

    def test_cross_dataset_fusion_impossible_through_public_api(self):
        """9. Cross-dataset fusion is impossible through the public inference interface."""
        # A payload containing both PaySim and ULB keys processed as PaySim ignores ULB
        mixed_payload = {
            "dataset_context": "PaySim",
            "type": "CASH_OUT",
            "amount": 250000.0,
            "origin_balance_before": 250000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 250000.0,
            # ULB-specific key
            "features": {f"V{i}": 5.0 for i in range(1, 29)},
        }
        res = self.engine.score_transaction(mixed_payload)
        self.assertIsNone(res.model_2)
        self.assertEqual(res.active_components, ["model_1", "rules"])

    def test_artifacts_loaded_once_and_reused(self):
        """13. Model artifacts are loaded once and reused rather than loaded for every request."""
        m1_inst = self.engine.model_1.model
        m2_inst = self.engine.model_2.model

        # Run 5 inferences
        for _ in range(5):
            tx = PaySimTransactionInput(
                type="PAYMENT",
                amount=10.0,
                origin_balance_before=100.0,
                origin_balance_after=90.0,
                destination_balance_before=0.0,
                destination_balance_after=10.0,
            )
            self.engine.score_paysim_transaction(tx)

        self.assertIs(self.engine.model_1.model, m1_inst)
        self.assertIs(self.engine.model_2.model, m2_inst)

    def test_invalid_dataset_context_fails_safely(self):
        """14. Invalid dataset contexts fail safely."""
        invalid_payload = {
            "dataset_context": "INVALID_CONTEXT",
            "amount": 100.0,
        }
        with self.assertRaises(ValueError) as ctx:
            self.engine.score_transaction(invalid_payload)
        self.assertIn("invalid dataset_context", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
