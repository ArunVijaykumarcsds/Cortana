"""
CORTANA — Risk Fusion Engine.
Authoritative implementation of the multi-component fusion policy
defined in fusion/fusion_config.json with strict dataset isolation.
"""

import json
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple
from backend.app.schemas.inference import Decision, FusionResult, RiskLevel


class RiskFusionEngine:
    """
    Combines calibrated risk signals according to the validated CORTANA policy.
    """

    def __init__(self, fusion_config_path: Path):
        self.fusion_config_path = Path(fusion_config_path)
        if not self.fusion_config_path.exists():
            raise FileNotFoundError(f"Fusion config not found at {self.fusion_config_path}")

        with open(self.fusion_config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.weights = self.config.get("weights", {"model_1": 0.8, "model_2": 0.1, "rules": 0.1})
        self.decision_threshold = float(self.config.get("decision_threshold", 0.98))
        self.risk_levels = self.config.get(
            "risk_levels",
            {
                "LOW": [0.0, 0.25],
                "MEDIUM": [0.25, 0.5],
                "HIGH": [0.5, 0.75],
                "CRITICAL": [0.75, 1.0],
            },
        )

    def determine_risk_level(self, score: float) -> RiskLevel:
        """
        Maps score in [0, 1] to categorical risk level.
        Boundaries:
          [0.00, 0.25) -> LOW
          [0.25, 0.50) -> MEDIUM
          [0.50, 0.75) -> HIGH
          [0.75, 1.00] -> CRITICAL
        """
        score = max(0.0, min(1.0, float(score)))
        if score >= 0.75:
            return "CRITICAL"
        elif score >= 0.50:
            return "HIGH"
        elif score >= 0.25:
            return "MEDIUM"
        else:
            return "LOW"

    def determine_decision(self, score: float) -> Decision:
        """
        Maps score to system decision.
        score < 0.98 -> PASS
        score >= 0.98 -> REVIEW
        """
        score = max(0.0, min(1.0, float(score)))
        return "REVIEW" if score >= self.decision_threshold else "PASS"

    def fuse_paysim(
        self,
        calibrated_model1_risk: float,
        calibrated_rules_risk: float,
    ) -> Tuple[FusionResult, Dict[str, float], Dict[str, float]]:
        """
        Fuses Model 1 and Rules for PaySim transactions.
        Model 2 is NOT activated or row-paired in PaySim context.
        """
        m1_risk = max(0.0, min(1.0, float(calibrated_model1_risk)))
        r_risk = max(0.0, min(1.0, float(calibrated_rules_risk)))

        w_m1 = self.weights.get("model_1", 0.8)
        w_rules = self.weights.get("rules", 0.1)
        active_weight_sum = w_m1 + w_rules  # 0.90

        # Normalized active weights
        norm_w_m1 = w_m1 / active_weight_sum
        norm_w_rules = w_rules / active_weight_sum

        fused_risk = (m1_risk * w_m1 + r_risk * w_rules) / active_weight_sum
        fused_risk = max(0.0, min(1.0, float(fused_risk)))

        risk_level = self.determine_risk_level(fused_risk)
        decision = self.determine_decision(fused_risk)

        calibrated_components = {
            "model_1": m1_risk,
            "rules": r_risk,
        }

        contributions = {
            "model_1": m1_risk * norm_w_m1,
            "rules": r_risk * norm_w_rules,
        }

        active_weights = {
            "model_1": norm_w_m1,
            "rules": norm_w_rules,
        }

        fusion_result = FusionResult(
            fused_risk=fused_risk,
            risk_level=risk_level,
            decision=decision,
            weights=self.weights,
            active_weights=active_weights,
            threshold=self.decision_threshold,
        )

        return fusion_result, calibrated_components, contributions

    def fuse_ulb(
        self,
        calibrated_model2_risk: float,
    ) -> Tuple[FusionResult, Dict[str, float], Dict[str, float]]:
        """
        Fuses Model 2 for ULB transactions.
        Model 1 and Rules Engine are NOT activated in ULB context.
        """
        m2_risk = max(0.0, min(1.0, float(calibrated_model2_risk)))
        fused_risk = m2_risk

        risk_level = self.determine_risk_level(fused_risk)
        decision = self.determine_decision(fused_risk)

        calibrated_components = {
            "model_2": m2_risk,
        }

        contributions = {
            "model_2": m2_risk,
        }

        active_weights = {
            "model_2": 1.0,
        }

        fusion_result = FusionResult(
            fused_risk=fused_risk,
            risk_level=risk_level,
            decision=decision,
            weights=self.weights,
            active_weights=active_weights,
            threshold=self.decision_threshold,
        )

        return fusion_result, calibrated_components, contributions
