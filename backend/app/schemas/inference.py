"""
CORTANA — Inference Output Schemas.
Output data contracts strictly matching the CORTANA architecture
and frontend types (frontend/src/types/index.ts).
"""

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
Decision = Literal["PASS", "REVIEW"]
DatasetContext = Literal["PaySim", "ULB"]
RuleKey = Literal[
    "HIGH_AMOUNT",
    "ORIGIN_BALANCE_INCONSISTENCY",
    "DESTINATION_BALANCE_INCONSISTENCY",
    "LARGE_BALANCE_CHANGE",
    "HIGH_RISK_TRANSACTION_TYPE",
    "ZERO_BALANCE_ANOMALY",
]


class TriggeredRule(BaseModel):
    """A single behavioral rule that fired on a transaction."""
    rule_key: RuleKey = Field(..., description="Unique rule identifier")
    description: str = Field(..., description="Human-readable rule description")
    severity: RiskLevel = Field(..., description="Severity level of the triggered rule")
    weight: float = Field(..., ge=0.0, le=1.0, description="Configured rule weight")
    field: Optional[str] = Field(default=None, description="Transaction field triggering the rule")
    value: Optional[str] = Field(default=None, description="Formatted value or trigger rationale")


class Model1Signal(BaseModel):
    """Output of Model 1 (Random Forest, PaySim, supervised)."""
    dataset: Literal["PaySim"] = "PaySim"
    raw_probability: float = Field(..., ge=0.0, le=1.0, description="Raw model probability")
    fraud_probability: float = Field(..., ge=0.0, le=1.0, description="Calibrated fraud probability (0..1)")


class Model2Signal(BaseModel):
    """Output of Model 2 (Isolation Forest, ULB, unsupervised)."""
    dataset: Literal["ULB"] = "ULB"
    raw_score: float = Field(..., description="Raw Isolation Forest anomaly score")
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Calibrated anomaly score (0..1)")


class RulesSignal(BaseModel):
    """Output of the Behavioral Rules Engine (PaySim only)."""
    dataset: Literal["PaySim"] = "PaySim"
    raw_rule_score: float = Field(..., ge=0.0, le=1.0, description="Sum of triggered rule weights")
    behavioral_risk: float = Field(..., ge=0.0, le=1.0, description="Calibrated behavioral risk score (0..1)")
    triggered: List[TriggeredRule] = Field(default_factory=list, description="List of triggered rules")


class FusionResult(BaseModel):
    """Fused risk score, risk tier, decision, and weights."""
    fused_risk: float = Field(..., ge=0.0, le=1.0, description="Composite fused risk score in [0, 1]")
    risk_level: RiskLevel = Field(..., description="Categorical risk tier: LOW, MEDIUM, HIGH, CRITICAL")
    decision: Decision = Field(..., description="System decision: PASS or REVIEW")
    weights: Dict[str, float] = Field(..., description="Configured component weights")
    active_weights: Dict[str, float] = Field(..., description="Normalized active weights for this context")
    threshold: float = Field(default=0.98, description="Locked production decision threshold")


class InferenceResult(BaseModel):
    """
    Comprehensive structured output from the CORTANA Inference Engine.
    Guarantees architectural dataset isolation between PaySim and ULB.
    """
    dataset_context: DatasetContext = Field(..., description="Active dataset context ('PaySim' or 'ULB')")
    model_1: Optional[Model1Signal] = Field(default=None, description="Populated ONLY for PaySim context")
    rules: Optional[RulesSignal] = Field(default=None, description="Populated ONLY for PaySim context")
    model_2: Optional[Model2Signal] = Field(default=None, description="Populated ONLY for ULB context")
    fusion: FusionResult = Field(..., description="Fusion result for the active context")
    calibrated_component_risks: Dict[str, float] = Field(..., description="Map of active component risks")
    component_contributions: Dict[str, float] = Field(..., description="Weighted contribution of each component")
    active_components: List[str] = Field(..., description="List of components activated for this scoring")
    fused_risk_score: float = Field(..., ge=0.0, le=1.0, description="Alias for fusion.fused_risk")
    risk_level: RiskLevel = Field(..., description="Alias for fusion.risk_level")
    decision: Decision = Field(..., description="Alias for fusion.decision")
    threshold: float = Field(default=0.98, description="Locked decision threshold")
    architecture_safe: bool = Field(default=True, description="Enforces no cross-dataset row pairing occurred")
