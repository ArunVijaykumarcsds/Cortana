"""
CORTANA Tests — Behavioral Rules Engine.
Validates the loading and execution of all 6 behavioral rules.
"""

import unittest
from pathlib import Path
from backend.app.core.rules import RulesEngine


class TestRulesEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent.parent
        cls.rules_path = cls.root / "rules" / "risk_rules.json"

    def test_six_rules_load_successfully(self):
        """3. Six rules load successfully."""
        engine = RulesEngine(self.rules_path)
        self.assertEqual(len(engine.rules_definitions), 6)
        expected_keys = {
            "HIGH_AMOUNT",
            "ORIGIN_BALANCE_INCONSISTENCY",
            "DESTINATION_BALANCE_INCONSISTENCY",
            "LARGE_BALANCE_CHANGE",
            "HIGH_RISK_TRANSACTION_TYPE",
            "ZERO_BALANCE_ANOMALY",
        }
        self.assertEqual(set(engine.rules_by_key.keys()), expected_keys)

    def test_clean_transaction_triggers_no_rules(self):
        engine = RulesEngine(self.rules_path)
        triggered, raw_score = engine.evaluate(
            tx_type="PAYMENT",
            amount=50.0,
            origin_balance_before=1000.0,
            origin_balance_after=950.0,
            destination_balance_before=200.0,
            destination_balance_after=250.0,
        )
        self.assertEqual(len(triggered), 0)
        self.assertEqual(raw_score, 0.0)

    def test_high_amount_rule_trigger(self):
        engine = RulesEngine(self.rules_path)
        triggered, raw_score = engine.evaluate(
            tx_type="PAYMENT",
            amount=350000.0,
            origin_balance_before=500000.0,
            origin_balance_after=150000.0,
            destination_balance_before=0.0,
            destination_balance_after=350000.0,
        )
        keys = [r.rule_key for r in triggered]
        self.assertIn("HIGH_AMOUNT", keys)
        self.assertGreaterEqual(raw_score, 0.20)

    def test_high_risk_type_rule_trigger(self):
        engine = RulesEngine(self.rules_path)
        triggered, raw_score = engine.evaluate(
            tx_type="TRANSFER",
            amount=50.0,
            origin_balance_before=1000.0,
            origin_balance_after=950.0,
            destination_balance_before=200.0,
            destination_balance_after=250.0,
        )
        keys = [r.rule_key for r in triggered]
        self.assertIn("HIGH_RISK_TRANSACTION_TYPE", keys)
        self.assertAlmostEqual(raw_score, 0.15, places=5)

    def test_all_rules_trigger_on_severe_anomaly(self):
        engine = RulesEngine(self.rules_path)
        # High amount (300k), Transfer, balance inconsistency on both ends, large balance change, zero balance
        triggered, raw_score = engine.evaluate(
            tx_type="CASH_OUT",
            amount=300000.0,
            origin_balance_before=300000.0,
            origin_balance_after=0.0,
            destination_balance_before=0.0,
            destination_balance_after=0.0,  # missing credit
        )
        keys = [r.rule_key for r in triggered]
        self.assertIn("HIGH_AMOUNT", keys)
        self.assertIn("HIGH_RISK_TRANSACTION_TYPE", keys)
        self.assertIn("LARGE_BALANCE_CHANGE", keys)
        self.assertIn("ZERO_BALANCE_ANOMALY", keys)
        self.assertIn("DESTINATION_BALANCE_INCONSISTENCY", keys)
        self.assertGreaterEqual(raw_score, 0.75)


if __name__ == "__main__":
    unittest.main()
