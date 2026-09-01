"""
CORTANA Tests — Risk Fusion Engine.
Validates weights, threshold, active component normalization, and fused score outputs.
"""

import unittest
from pathlib import Path
from backend.app.core.fusion import RiskFusionEngine


class TestRiskFusionEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent.parent
        cls.fusion_path = cls.root / "fusion" / "fusion_config.json"

    def test_fusion_policy_configuration(self):
        engine = RiskFusionEngine(self.fusion_path)
        self.assertEqual(engine.weights.get("model_1"), 0.8)
        self.assertEqual(engine.weights.get("model_2"), 0.1)
        self.assertEqual(engine.weights.get("rules"), 0.1)
        self.assertEqual(engine.decision_threshold, 0.98)

    def test_paysim_fusion_weights_and_normalization(self):
        engine = RiskFusionEngine(self.fusion_path)
        fusion_res, components, contribs = engine.fuse_paysim(
            calibrated_model1_risk=0.50,
            calibrated_rules_risk=0.50,
        )
        self.assertAlmostEqual(fusion_res.fused_risk, 0.50, places=5)
        self.assertEqual(fusion_res.risk_level, "HIGH")
        self.assertEqual(fusion_res.decision, "PASS")

        # Active weights sum to 1.0
        self.assertAlmostEqual(sum(fusion_res.active_weights.values()), 1.0, places=5)
        self.assertAlmostEqual(fusion_res.active_weights["model_1"], 0.8 / 0.9, places=5)
        self.assertAlmostEqual(fusion_res.active_weights["rules"], 0.1 / 0.9, places=5)

    def test_ulb_fusion(self):
        engine = RiskFusionEngine(self.fusion_path)
        fusion_res, components, contribs = engine.fuse_ulb(
            calibrated_model2_risk=0.85,
        )
        self.assertAlmostEqual(fusion_res.fused_risk, 0.85, places=5)
        self.assertEqual(fusion_res.risk_level, "CRITICAL")
        self.assertEqual(fusion_res.decision, "PASS")  # 0.85 < 0.98


if __name__ == "__main__":
    unittest.main()
