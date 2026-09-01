"""
CORTANA Tests — Model Loading and Feature Processing.
Validates Model 1 (RandomForest) and Model 2 (IsolationForest) loading and scoring.
"""

import unittest
from pathlib import Path
from backend.app.core.models import Model1Wrapper, Model2Wrapper, MODEL_1_FEATURE_COLUMNS, MODEL_2_FEATURE_COLUMNS


class TestModelLoaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent.parent
        cls.m1_path = cls.root / "models" / "model_1" / "cortana_model_1_random_forest.pkl"
        cls.m2_path = cls.root / "models" / "model_2" / "cortana_model_2_isolation_forest.pkl"

    def test_model_1_loads_successfully(self):
        """1. Model 1 loads successfully."""
        wrapper = Model1Wrapper(self.m1_path)
        self.assertIsNotNone(wrapper.model)
        self.assertEqual(len(wrapper.feature_names), 14)
        self.assertEqual(wrapper.feature_names, MODEL_1_FEATURE_COLUMNS)

    def test_model_2_loads_successfully(self):
        """2. Model 2 loads successfully using joblib."""
        wrapper = Model2Wrapper(self.m2_path)
        self.assertIsNotNone(wrapper.model)
        self.assertEqual(len(wrapper.feature_names), 30)
        self.assertEqual(wrapper.feature_names, MODEL_2_FEATURE_COLUMNS)

    def test_model_1_scoring(self):
        wrapper = Model1Wrapper(self.m1_path)
        df = wrapper.extract_features(
            amount=50000.0,
            origin_balance_before=50000.0,
            origin_balance_after=0.0,
            destination_balance_before=1000.0,
            destination_balance_after=51000.0,
        )
        self.assertEqual(df.shape, (1, 14))
        prob = wrapper.predict_raw_probability(df)
        self.assertIsInstance(prob, float)
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)

    def test_model_2_scoring(self):
        wrapper = Model2Wrapper(self.m2_path)
        sample_features = {f"V{i}": 0.0 for i in range(1, 29)}
        df = wrapper.extract_features(amount=100.0, time=10.0, features_dict=sample_features)
        self.assertEqual(df.shape, (1, 30))
        raw_score = wrapper.predict_raw_score(df)
        self.assertIsInstance(raw_score, float)

    def test_model_2_missing_features_fail_safely(self):
        """15. Missing required ULB features fail safely."""
        wrapper = Model2Wrapper(self.m2_path)
        incomplete_features = {"V1": 0.0, "V2": 1.0}  # Missing V3..V28
        with self.assertRaises(ValueError) as ctx:
            wrapper.extract_features(amount=100.0, time=0.0, features_dict=incomplete_features)
        self.assertIn("missing required features", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
