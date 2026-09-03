"""
CORTANA — Empirical Percentile Rank Calibration Engine.
Loads model1, model2, and rules calibration tables at startup
and executes fast, deterministic O(log N) risk calibration.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd


class CalibrationEngine:
    """
    In-memory empirical calibration engine.
    Ensures deterministic monotonic risk scores in [0.0, 1.0].
    """

    def __init__(self, calibration_dir: Path):
        self.calibration_dir = Path(calibration_dir)
        if not self.calibration_dir.exists():
            raise FileNotFoundError(f"Calibration directory not found at {self.calibration_dir}")

        m1_path = self.calibration_dir / "model1_calibration.csv"
        m2_path = self.calibration_dir / "model2_calibration.csv"
        rules_path = self.calibration_dir / "rules_calibration.csv"

        for p in (m1_path, m2_path, rules_path):
            if not p.exists():
                raise FileNotFoundError(f"Missing calibration CSV: {p}")

        # Load and sort arrays once at startup
        self.m1_raw, self.m1_cal = self._load_calibration_curve(m1_path)
        self.m2_raw, self.m2_cal = self._load_calibration_curve(m2_path)
        self.rules_raw, self.rules_cal = self._load_calibration_curve(rules_path)

    @staticmethod
    def _load_calibration_curve(csv_path: Path) -> Tuple[np.ndarray, np.ndarray]:
        """
        Loads CSV and returns sorted 1D numpy arrays (raw_score, calibrated_risk).
        """
        df = pd.read_csv(csv_path)
        if "raw_score" not in df.columns or "calibrated_risk" not in df.columns:
            raise ValueError(f"Invalid columns in {csv_path}. Expected 'raw_score' and 'calibrated_risk'.")
        
        # Sort by calibrated_risk to preserve monotonic percentile mapping
        df_sorted = df.sort_values(by=["calibrated_risk", "raw_score"])
        raw_arr = df_sorted["raw_score"].to_numpy(dtype=np.float64)
        cal_arr = df_sorted["calibrated_risk"].to_numpy(dtype=np.float64)
        return raw_arr, cal_arr

    def calibrate_model1(self, raw_probability: float) -> float:
        """
        Calibrates Model 1 supervised fraud probability.
        Returns float in [0.0, 1.0].
        """
        raw_val = float(raw_probability)
        cal_val = float(np.interp(raw_val, self.m1_raw, self.m1_cal))
        return max(0.0, min(1.0, cal_val))

    def calibrate_model2(self, raw_anomaly_score: float) -> float:
        """
        Calibrates Model 2 unsupervised anomaly score.
        Returns float in [0.0, 1.0].
        """
        raw_val = float(raw_anomaly_score)
        cal_val = float(np.interp(raw_val, self.m2_raw, self.m2_cal))
        return max(0.0, min(1.0, cal_val))

    def calibrate_rules(self, raw_rule_score: float) -> float:
        """
        Calibrates Behavioral Rules sum.
        Returns float in [0.0, 1.0].
        """
        raw_val = float(raw_rule_score)
        cal_val = float(np.interp(raw_val, self.rules_raw, self.rules_cal))
        return max(0.0, min(1.0, cal_val))
