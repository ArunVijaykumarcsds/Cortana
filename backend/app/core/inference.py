"""
CORTANA — High-Level ML Inference Service.
Integrates Model 1, Model 2, Rules Engine, Calibration, and Fusion
into a unified, architecture-safe scoring engine.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union
import pandas as pd

from backend.app.core.calibration import CalibrationEngine
from backend.app.core.fusion import RiskFusionEngine
from backend.app.core.models import Model1Wrapper, Model2Wrapper
from backend.app.core.rules import RulesEngine
from backend.app.schemas.inference import (
    InferenceResult,
    Model1Signal,
    Model2Signal,
    RulesSignal,
)
from backend.app.schemas.transaction import PaySimTransactionInput, ULBTransactionInput


class InferenceEngine:
    """
    Unified CORTANA Inference Service.
    Artifacts are loaded once at instantiation and reused across all scoring requests.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            # Default to repo root (2 levels up from backend/app/core)
            self.root = Path(__file__).resolve().parent.parent.parent.parent
        else:
            self.root = Path(project_root)

        # Artifact locations
        m1_pkl = self.root / "models" / "model_1" / "cortana_model_1_random_forest.pkl"
        m2_pkl = self.root / "models" / "model_2" / "cortana_model_2_isolation_forest.pkl"
        rules_json = self.root / "rules" / "risk_rules.json"
        cal_dir = self.root / "fusion" / "calibration"
        fusion_json = self.root / "fusion" / "fusion_config.json"

        # Load all components once
        self.model_1 = Model1Wrapper(m1_pkl)
        self.model_2 = Model2Wrapper(m2_pkl)
        self.rules_engine = RulesEngine(rules_json)
        self.calibration_engine = CalibrationEngine(cal_dir)
        self.fusion_engine = RiskFusionEngine(fusion_json)

    def score_paysim_transaction(self, tx: Union[PaySimTransactionInput, Dict[str, Any]]) -> InferenceResult:
        """
        Executes inference for a PaySim transaction:
        1. Evaluates Model 1 (Random Forest) -> raw probability -> calibrated risk.
        2. Evaluates Rules Engine (6 behavioral rules) -> raw sum -> calibrated risk.
        3. Fuses Model 1 + Rules.
        Model 2 is STRICTLY NOT evaluated.
        """
        if isinstance(tx, dict):
            tx_obj = PaySimTransactionInput(**tx)
        else:
            tx_obj = tx

        # 1. Model 1 feature extraction & prediction
        feat_df = self.model_1.extract_features(
            amount=tx_obj.amount,
            origin_balance_before=tx_obj.origin_balance_before,
            origin_balance_after=tx_obj.origin_balance_after,
            destination_balance_before=tx_obj.destination_balance_before,
            destination_balance_after=tx_obj.destination_balance_after,
        )
        raw_m1_prob = self.model_1.predict_raw_probability(feat_df)
        cal_m1_risk = self.calibration_engine.calibrate_model1(raw_m1_prob)

        # 2. Behavioral Rules evaluation
        triggered_rules, raw_rule_score = self.rules_engine.evaluate(
            tx_type=tx_obj.type,
            amount=tx_obj.amount,
            origin_balance_before=tx_obj.origin_balance_before,
            origin_balance_after=tx_obj.origin_balance_after,
            destination_balance_before=tx_obj.destination_balance_before,
            destination_balance_after=tx_obj.destination_balance_after,
        )
        cal_rules_risk = self.calibration_engine.calibrate_rules(raw_rule_score)

        # 3. Risk Fusion (PaySim Context)
        fusion_res, cal_components, contributions = self.fusion_engine.fuse_paysim(
            calibrated_model1_risk=cal_m1_risk,
            calibrated_rules_risk=cal_rules_risk,
        )

        model_1_signal = Model1Signal(
            dataset="PaySim",
            raw_probability=raw_m1_prob,
            fraud_probability=cal_m1_risk,
        )

        rules_signal = RulesSignal(
            dataset="PaySim",
            raw_rule_score=raw_rule_score,
            behavioral_risk=cal_rules_risk,
            triggered=triggered_rules,
        )

        return InferenceResult(
            dataset_context="PaySim",
            model_1=model_1_signal,
            rules=rules_signal,
            model_2=None,  # Strictly isolated
            fusion=fusion_res,
            calibrated_component_risks=cal_components,
            component_contributions=contributions,
            active_components=["model_1", "rules"],
            fused_risk_score=fusion_res.fused_risk,
            risk_level=fusion_res.risk_level,
            decision=fusion_res.decision,
            threshold=fusion_res.threshold,
            architecture_safe=True,
        )

    def score_ulb_transaction(self, tx: Union[ULBTransactionInput, Dict[str, Any]]) -> InferenceResult:
        """
        Executes inference for a ULB transaction:
        1. Extracts 30 continuous PCA features.
        2. Evaluates Model 2 (Isolation Forest) -> raw anomaly score -> calibrated risk.
        3. Fuses Model 2.
        Model 1 and Rules Engine are STRICTLY NOT evaluated.
        """
        if isinstance(tx, dict):
            tx_obj = ULBTransactionInput(**tx)
        else:
            tx_obj = tx

        # 1. Model 2 feature extraction & prediction
        feat_df = self.model_2.extract_features(
            amount=tx_obj.amount,
            time=tx_obj.time,
            features_dict=tx_obj.features,
        )
        raw_m2_score = self.model_2.predict_raw_score(feat_df)
        cal_m2_risk = self.calibration_engine.calibrate_model2(raw_m2_score)

        # 2. Risk Fusion (ULB Context)
        fusion_res, cal_components, contributions = self.fusion_engine.fuse_ulb(
            calibrated_model2_risk=cal_m2_risk,
        )

        model_2_signal = Model2Signal(
            dataset="ULB",
            raw_score=raw_m2_score,
            anomaly_score=cal_m2_risk,
        )

        return InferenceResult(
            dataset_context="ULB",
            model_1=None,  # Strictly isolated
            rules=None,    # Strictly isolated
            model_2=model_2_signal,
            fusion=fusion_res,
            calibrated_component_risks=cal_components,
            component_contributions=contributions,
            active_components=["model_2"],
            fused_risk_score=fusion_res.fused_risk,
            risk_level=fusion_res.risk_level,
            decision=fusion_res.decision,
            threshold=fusion_res.threshold,
            architecture_safe=True,
        )

    def score_transaction(
        self,
        tx: Union[PaySimTransactionInput, ULBTransactionInput, Dict[str, Any]],
        dataset_context: Optional[str] = None,
    ) -> InferenceResult:
        """
        Unified routing entrypoint with strict dataset context verification.
        """
        # Determine context
        if isinstance(tx, dict):
            ctx = dataset_context or tx.get("dataset_context")
            if not ctx:
                raise ValueError("Missing 'dataset_context' in transaction payload. Must be 'PaySim' or 'ULB'.")
            if ctx == "PaySim":
                return self.score_paysim_transaction(tx)
            elif ctx == "ULB":
                return self.score_ulb_transaction(tx)
            else:
                raise ValueError(f"Invalid dataset_context '{ctx}'. Must be 'PaySim' or 'ULB'.")
        elif isinstance(tx, PaySimTransactionInput):
            return self.score_paysim_transaction(tx)
        elif isinstance(tx, ULBTransactionInput):
            return self.score_ulb_transaction(tx)
        else:
            raise TypeError(f"Unsupported transaction input type: {type(tx)}")
