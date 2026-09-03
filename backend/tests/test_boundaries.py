"""
CORTANA Tests — Boundary Value Verification.
Explicitly validates exact risk level and decision thresholds.
"""

import unittest
from pathlib import Path
from backend.app.core.fusion import RiskFusionEngine


class TestBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent.parent
        cls.fusion_path = cls.root / "fusion" / "fusion_config.json"
        cls.engine = RiskFusionEngine(cls.fusion_path)

    def test_risk_level_boundaries(self):
        """
        10. Risk levels obey:
        0.249999 -> LOW
        0.250000 -> MEDIUM
        0.499999 -> MEDIUM
        0.500000 -> HIGH
        0.749999 -> HIGH
        0.750000 -> CRITICAL
        """
        self.assertEqual(self.engine.determine_risk_level(0.249999), "LOW")
        self.assertEqual(self.engine.determine_risk_level(0.250000), "MEDIUM")
        self.assertEqual(self.engine.determine_risk_level(0.499999), "MEDIUM")
        self.assertEqual(self.engine.determine_risk_level(0.500000), "HIGH")
        self.assertEqual(self.engine.determine_risk_level(0.749999), "HIGH")
        self.assertEqual(self.engine.determine_risk_level(0.750000), "CRITICAL")

        # Edge checks
        self.assertEqual(self.engine.determine_risk_level(0.0), "LOW")
        self.assertEqual(self.engine.determine_risk_level(1.0), "CRITICAL")

    def test_decision_threshold_boundaries(self):
        """
        11. Decisions obey:
        0.979999 -> PASS
        0.980000 -> REVIEW
        0.990000 -> REVIEW
        """
        self.assertEqual(self.engine.determine_decision(0.979999), "PASS")
        self.assertEqual(self.engine.determine_decision(0.980000), "REVIEW")
        self.assertEqual(self.engine.determine_decision(0.990000), "REVIEW")

        # Additional edge checks
        self.assertEqual(self.engine.determine_decision(0.0), "PASS")
        self.assertEqual(self.engine.determine_decision(0.9799), "PASS")
        self.assertEqual(self.engine.determine_decision(1.0), "REVIEW")


if __name__ == "__main__":
    unittest.main()
