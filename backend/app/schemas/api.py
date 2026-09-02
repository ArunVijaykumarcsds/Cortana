"""
CORTANA — API Request & Response Schemas.
Data contracts for REST endpoints, health telemetry, case workflow updates,
and system status information.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

from backend.app.schemas.inference import (
    Decision,
    FusionResult,
    Model1Signal,
    Model2Signal,
    RiskLevel,
    RulesSignal,
    TriggeredRule,
)
from backend.app.schemas.transaction import (
    DatasetContext,
    PaySimTransactionInput,
    TransactionType,
    ULBTransactionInput,
)


class HealthComponentStatus(BaseModel):
    database: Literal["ok", "degraded"]
    model1: Literal["ok", "degraded"]
    model2: Literal["ok", "degraded"]
    rules: Literal["ok", "degraded"]
    fusion: Literal["ok", "degraded"]
    calibration: Literal["ok", "degraded"]
    llm_provider: Literal["ok", "degraded"]


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    database: Literal["connected", "disconnected", "error"] = "connected"
    ml_engine: Literal["operational", "error"] = "operational"
    details: HealthComponentStatus
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AlertStatusUpdate(BaseModel):
    status: Literal["OPEN", "UNDER_REVIEW", "RESOLVED"] = Field(..., description="Target alert status")


class InvestigationEventCreate(BaseModel):
    action: Literal[
        "CASE_OPENED",
        "CORTANA_FLAGGED",
        "EXPLANATION_REQUESTED",
        "CONFIRMED_FRAUD",
        "MARKED_LEGITIMATE",
        "ESCALATED",
        "NOTE_ADDED",
    ] = Field(..., description="Audit action")
    actor: str = Field(default="Analyst", description="Actor performing the action")
    note: Optional[str] = Field(default=None, description="Optional note or explanation")


class InvestigationUpdate(BaseModel):
    status: Optional[Literal["OPEN", "IN_REVIEW", "ESCALATED", "CLOSED"]] = None
    resolution: Optional[Literal["FRAUD_CONFIRMED", "LEGITIMATE"]] = None
    assigned_to: Optional[str] = None
    actor: str = Field(default="Analyst", description="Analyst making the update")
    note: Optional[str] = Field(default=None, description="Optional audit note")


class AuditEventResponse(BaseModel):
    id: str
    action: str
    actor: str
    timestamp: str
    note: Optional[str] = None


class InvestigationResponse(BaseModel):
    id: str
    transaction_id: str
    risk_level: RiskLevel
    risk_score: float
    decision: Decision
    status: Literal["OPEN", "IN_REVIEW", "ESCALATED", "CLOSED"]
    resolution: Optional[Literal["FRAUD_CONFIRMED", "LEGITIMATE"]] = None
    assigned_to: Optional[str] = None
    opened_at: str
    audit_trail: List[AuditEventResponse] = Field(default_factory=list)


class AlertResponse(BaseModel):
    id: str
    transaction_id: str
    dataset_context: DatasetContext
    type: TransactionType
    risk_score: float
    risk_level: RiskLevel
    decision: Decision
    status: Literal["OPEN", "UNDER_REVIEW", "RESOLVED"]
    timestamp: str


class TransactionResponse(BaseModel):
    id: str
    dataset_context: DatasetContext
    type: TransactionType
    amount: float
    currency: str
    origin_account: str
    destination_account: str
    origin_balance_before: float
    origin_balance_after: float
    destination_balance_before: float
    destination_balance_after: float
    timestamp: str
    model_1: Optional[Model1Signal] = None
    rules: Optional[RulesSignal] = None
    model_2: Optional[Model2Signal] = None
    fusion: FusionResult


class TransactionCountResponse(BaseModel):
    total: int
    context: Optional[str] = None
    risk_level: Optional[str] = None


class SystemServiceStatus(BaseModel):
    service: str
    state: Literal["OPERATIONAL", "DEGRADED", "OFFLINE", "PLANNED"]
    detail: str


class SystemStatusResponse(BaseModel):
    services: List[SystemServiceStatus]
    model_version: str = "CORTANA_FINAL_v1.0.0"
    release_phase: str = "Phase 6 — Final"
    package_status: str = "Smoke-tested, artifact-reproducible"
    locked_threshold: float = 0.98
