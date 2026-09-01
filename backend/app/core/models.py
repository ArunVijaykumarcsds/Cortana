"""
CORTANA — Model Loaders and Feature Processors.
Authoritative, safe artifact loading for Model 1 (Random Forest)
and Model 2 (Isolation Forest) using joblib.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd


# 14 Engineered features required by Model 1 (RandomForestClassifier)
MODEL_1_FEATURE_COLUMNS: List[str] = [
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "origin_balance_change",
    "destination_balance_change",
    "balance_error_origin",
    "balance_error_destination",
    "amount_to_origin_balance",
    "amount_to_destination_balance",
    "origin_balance_zero_after",
    "destination_balance_zero_before",
    "destination_balance_zero_after",
]

# 30 Continuous features required by Model 2 (IsolationForest)
MODEL_2_FEATURE_COLUMNS: List[str] = [
    "Time",
    "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10",
    "V11", "V12", "V13", "V14", "V15", "V16", "V17", "V18", "V19", "V20",
    "V21", "V22", "V23", "V24", "V25", "V26", "V27", "V28",
    "Amount",
]


class Model1Wrapper:
    """
    Wrapper for CORTANA Model 1: RandomForestClassifier (PaySim supervised fraud).
    """

    def __init__(self, artifact_path: Path, config_path: Optional[Path] = None):
        self.artifact_path = Path(artifact_path)
        self.config_path = Path(config_path) if config_path else self.artifact_path.parent / "model_config.json"
        
        if not self.artifact_path.exists():
            raise FileNotFoundError(f"Model 1 artifact not found at {self.artifact_path}")
        
        # Load metadata
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {}
            
        # Authoritative load using joblib
        self.model = joblib.load(self.artifact_path)
        self.feature_names = getattr(self.model, "feature_names_in_", MODEL_1_FEATURE_COLUMNS).tolist()

    def extract_features(
        self,
        amount: float,
        origin_balance_before: float,
        origin_balance_after: float,
        destination_balance_before: float,
        destination_balance_after: float,
    ) -> pd.DataFrame:
        """
        Constructs the 14-feature vector for PaySim transaction scoring.
        """
        amount = float(amount)
        old_org = float(origin_balance_before)
        new_org = float(origin_balance_after)
        old_dest = float(destination_balance_before)
        new_dest = float(destination_balance_after)

        origin_balance_change = new_org - old_org
        destination_balance_change = new_dest - old_dest
        balance_error_origin = old_org - amount - new_org
        balance_error_destination = old_dest + amount - new_dest

        amount_to_origin_balance = amount / (old_org + 1.0)
        amount_to_destination_balance = amount / (old_dest + 1.0)

        origin_balance_zero_after = 1.0 if new_org == 0.0 else 0.0
        destination_balance_zero_before = 1.0 if old_dest == 0.0 else 0.0
        destination_balance_zero_after = 1.0 if new_dest == 0.0 else 0.0

        row = {
            "amount": amount,
            "oldbalanceOrg": old_org,
            "newbalanceOrig": new_org,
            "oldbalanceDest": old_dest,
            "newbalanceDest": new_dest,
            "origin_balance_change": origin_balance_change,
            "destination_balance_change": destination_balance_change,
            "balance_error_origin": balance_error_origin,
            "balance_error_destination": balance_error_destination,
            "amount_to_origin_balance": amount_to_origin_balance,
            "amount_to_destination_balance": amount_to_destination_balance,
            "origin_balance_zero_after": origin_balance_zero_after,
            "destination_balance_zero_before": destination_balance_zero_before,
            "destination_balance_zero_after": destination_balance_zero_after,
        }

        # Preserve exact trained feature order
        df = pd.DataFrame([row])[self.feature_names]
        return df

    def predict_raw_probability(self, features_df: pd.DataFrame) -> float:
        """
        Computes the supervised fraud probability for class 1.
        Returns float in [0.0, 1.0].
        """
        probas = self.model.predict_proba(features_df)
        prob = float(probas[0, 1])
        return max(0.0, min(1.0, prob))


class Model2Wrapper:
    """
    Wrapper for CORTANA Model 2: IsolationForest (ULB unsupervised anomaly detection).
    """

    def __init__(
        self,
        artifact_path: Path,
        config_path: Optional[Path] = None,
        feature_columns_path: Optional[Path] = None,
        threshold_config_path: Optional[Path] = None,
    ):
        self.artifact_path = Path(artifact_path)
        base_dir = self.artifact_path.parent
        self.config_path = Path(config_path) if config_path else base_dir / "model_config.json"
        self.feature_columns_path = Path(feature_columns_path) if feature_columns_path else base_dir / "feature_columns.json"
        self.threshold_config_path = Path(threshold_config_path) if threshold_config_path else base_dir / "threshold_config.json"

        if not self.artifact_path.exists():
            raise FileNotFoundError(f"Model 2 artifact not found at {self.artifact_path}")

        # Load configs
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {}

        if self.feature_columns_path.exists():
            with open(self.feature_columns_path, "r", encoding="utf-8") as f:
                self.expected_features = json.load(f)
        else:
            self.expected_features = MODEL_2_FEATURE_COLUMNS

        # Authoritative load using joblib
        self.model = joblib.load(self.artifact_path)
        self.feature_names = getattr(self.model, "feature_names_in_", self.expected_features).tolist()

    def extract_features(
        self,
        amount: float,
        time: float = 0.0,
        features_dict: Optional[Dict[str, float]] = None,
    ) -> pd.DataFrame:
        """
        Validates and builds the 30-dimensional ULB feature vector.
        Raises ValueError if any required V1..V28 feature is missing.
        """
        if features_dict is None:
            features_dict = {}

        row: Dict[str, float] = {}
        missing: List[str] = []

        for feat in self.feature_names:
            if feat == "Time":
                row["Time"] = float(features_dict.get("Time", time))
            elif feat == "Amount":
                row["Amount"] = float(features_dict.get("Amount", amount))
            elif feat in features_dict:
                row[feat] = float(features_dict[feat])
            else:
                missing.append(feat)

        if missing:
            raise ValueError(f"ULB transaction missing required features: {missing}")

        df = pd.DataFrame([row])[self.feature_names]
        return df

    def predict_raw_score(self, features_df: pd.DataFrame) -> float:
        """
        Computes the raw anomaly score where higher values represent higher anomaly risk.
        In scikit-learn IsolationForest, decision_function returns negative values for anomalies.
        CORTANA inverts this (-decision_function) so that higher raw_score indicates higher anomaly.
        """
        decision_val = self.model.decision_function(features_df)[0]
        # Invert: -decision_function matches calibration dataset mapping
        raw_anomaly = float(-decision_val)
        return raw_anomaly
