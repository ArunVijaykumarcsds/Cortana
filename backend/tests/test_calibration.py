"""
CORTANA Tests — Calibration Engine.
Validates loading of all 3 calibration tables, deterministic outputs,
and boundary boundedness in [0.0, 1.0].
"""

import unittest
from pathlib import Path
from backend.app.core.calibration import CalibrationEngine


class TestCalibrationEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent.parent
        cls.cal_dir = cls.root / "fusion" / "calibration"

    def test_all_three_calibration_tables_load_successfully(self):
        """4. All three calibration tables load successfully."""
        cal = CalibrationEngine(self.cal_dir)
        self.assertEqual(len(cal.m1_raw), 141815)
        self.assertEqual(len(cal.m2_raw), 39873)
        self.assertEqual(len(cal.rules_raw), 141815)

    def test_deterministic_and_bounded(self):
        """12. All output risk scores remain in [0,1]."""
        cal = CalibrationEngine(self.cal_dir)

        # Test across arbitrary values including negatives and > 1.0
        test_inputs = [-10.0, 0.0, 0.1, 0.5, 0.95, 1.0, 10.0]
        for val in test_inputs:
            c1 = cal.calibrate_model1(val)
            c2 = cal.calibrate_model2(val)
            c3 = cal.calibrate_rules(val)

            self.assertGreaterEqual(c1, 0.0)
            self.assertLessEqual(c1, 1.0)

            self.assertGreaterEqual(c2, 0.0)
            self.assertLessEqual(c2, 1.0)

            self.assertGreaterEqual(c3, 0.0)
            self.assertLessEqual(c3, 1.0)

            # Determinism check
            self.assertEqual(c1, cal.calibrate_model1(val))
            self.assertEqual(c2, cal.calibrate_model2(val))
            self.assertEqual(c3, cal.calibrate_rules(val))


if __name__ == "__main__":
    unittest.main()
