"""
CORTANA — Structured Explanation Schemas.
Pydantic v2 schemas for explanation input facts and validated explanation output.
Strictly isolates explanation facts from raw transaction data and PII.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class TriggeredRuleFact(BaseModel):
    """Safe behavioral rule representation without raw PII."""
    rule_key: str = Field(..., description="Rule identifier")
    label: str = Field(..., description="Human-readable rule name")
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Rule risk severity")
    description: str = Field(..., description="Rule behavioral rationale")
    field: Optional[str] = Field(default=None, description="Generic field category (e.g. amount, balance)")


class ExplanationFacts(BaseModel):
    """
    Structured, schema-validated facts derived from authoritative ML scoring.
    Contains strictly pre-computed metrics and categorical signals.
    NO raw account IDs, customer names, or PII.
    """
    transaction_id: str = Field(..., description="Transaction identifier")
    dataset_context: Literal["PaySim", "ULB"] = Field(..., description="Dataset context")
    type: str = Field(..., description="Transaction category/type")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Computed risk tier")
    decision: Literal["PASS", "REVIEW"] = Field(..., description="Authoritative fusion decision")
    fused_risk_score: float = Field(..., ge=0.0, le=1.0, description="Authoritative fused risk score")
    active_components: List[str] = Field(..., description="Active pipeline components for context")
    
    # Pre-computed calibrated model signals
    model_1_probability: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Model 1 fraud probability")
    rules_risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Behavioral rules score")
    model_2_anomaly_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Model 2 anomaly score")
    triggered_rules: List[TriggeredRuleFact] = Field(default_factory=list, description="List of triggered behavioral rules")


class ExplanationResponse(BaseModel):
    """
    Validated response schema returned by the explanation engine to the frontend.
    """
    transaction_id: str = Field(..., description="Transaction identifier")
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Preserved risk tier")
    decision: Literal["PASS", "REVIEW"] = Field(..., description="Preserved decision")
    fused_risk_score: float = Field(..., ge=0.0, le=1.0, description="Preserved fused score")
    explanation_text: str = Field(..., min_length=10, description="Clear, plain-English explanation")
    referenced_signals: List[str] = Field(default_factory=list, description="Signal identifiers referenced in explanation")
    provider: Literal["deterministic_fallback", "gemini", "openai", "custom_llm"] = Field(
        ..., description="Source of the explanation"
    )
    is_fallback: bool = Field(..., description="True if deterministic fallback generated the text")

    @field_validator("referenced_signals")
    @classmethod
    def validate_signals(cls, v: List[str]) -> List[str]:
        # Clean and deduplicate signal labels
        return list(dict.fromkeys(s.strip() for s in v if s.strip()))
