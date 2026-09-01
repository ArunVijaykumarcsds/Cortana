"""
CORTANA — SQLAlchemy Declarative Database Models.
Defines transactions, alerts, investigations, and audit_events with
strict referential integrity, indexes, and database constraints.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.app.db.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TransactionModel(Base):
    """
    Persistent record of a scored financial transaction.
    Preserves dataset context separation (PaySim vs ULB).
    """
    __tablename__ = "transactions"

    id = Column(String(64), primary_key=True, index=True)
    dataset_context = Column(String(16), nullable=False, index=True)
    type = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False, default="USD")
    origin_account = Column(String(64), nullable=False, default="")
    destination_account = Column(String(64), nullable=False, default="")
    origin_balance_before = Column(Float, nullable=False, default=0.0)
    origin_balance_after = Column(Float, nullable=False, default=0.0)
    destination_balance_before = Column(Float, nullable=False, default=0.0)
    destination_balance_after = Column(Float, nullable=False, default=0.0)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    # Model Signals (Strict context isolation)
    model_1_probability = Column(Float, nullable=True)  # Populated ONLY for PaySim
    model_2_score = Column(Float, nullable=True)        # Populated ONLY for ULB
    rules_risk = Column(Float, nullable=True)           # Populated ONLY for PaySim
    triggered_rules = Column(JSON, nullable=True)       # List of triggered rule dictionaries
    fused_risk = Column(Float, nullable=False, index=True)
    risk_level = Column(String(16), nullable=False)
    decision = Column(String(16), nullable=False)
    raw_payload = Column(JSON, nullable=True)

    # Relationships
    alerts = relationship("AlertModel", back_populates="transaction", cascade="all, delete-orphan")
    investigation = relationship("InvestigationModel", back_populates="transaction", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("dataset_context IN ('PaySim', 'ULB')", name="ck_transactions_dataset_context"),
        CheckConstraint("amount >= 0.0", name="ck_transactions_amount_non_negative"),
        CheckConstraint("fused_risk >= 0.0 AND fused_risk <= 1.0", name="ck_transactions_fused_risk_range"),
        CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="ck_transactions_risk_level"),
        CheckConstraint("decision IN ('PASS', 'REVIEW')", name="ck_transactions_decision"),
        CheckConstraint("model_1_probability IS NULL OR (model_1_probability >= 0.0 AND model_1_probability <= 1.0)", name="ck_transactions_m1_range"),
        CheckConstraint("model_2_score IS NULL OR (model_2_score >= 0.0 AND model_2_score <= 1.0)", name="ck_transactions_m2_range"),
        CheckConstraint("rules_risk IS NULL OR (rules_risk >= 0.0 AND rules_risk <= 1.0)", name="ck_transactions_rules_range"),
        Index("ix_transactions_ctx_timestamp", "dataset_context", "timestamp"),
        Index("ix_transactions_fused_risk_desc", "fused_risk"),
    )


class AlertModel(Base):
    """
    Persistent alert associated with high-risk or reviewed transactions.
    """
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True, index=True)
    transaction_id = Column(String(64), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_context = Column(String(16), nullable=False)
    type = Column(String(32), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(16), nullable=False, index=True)
    decision = Column(String(16), nullable=False)
    status = Column(String(32), nullable=False, default="OPEN", index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    # Relationships
    transaction = relationship("TransactionModel", back_populates="alerts")

    __table_args__ = (
        CheckConstraint("dataset_context IN ('PaySim', 'ULB')", name="ck_alerts_dataset_context"),
        CheckConstraint("risk_score >= 0.0 AND risk_score <= 1.0", name="ck_alerts_risk_score_range"),
        CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="ck_alerts_risk_level"),
        CheckConstraint("decision IN ('PASS', 'REVIEW')", name="ck_alerts_decision"),
        CheckConstraint("status IN ('OPEN', 'UNDER_REVIEW', 'RESOLVED')", name="ck_alerts_status"),
        Index("ix_alerts_status_timestamp", "status", "timestamp"),
    )


class InvestigationModel(Base):
    """
    Persistent case file for human-in-the-loop investigation workflows.
    """
    __tablename__ = "investigations"

    id = Column(String(64), primary_key=True, index=True)
    transaction_id = Column(String(64), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    risk_level = Column(String(16), nullable=False)
    risk_score = Column(Float, nullable=False)
    decision = Column(String(16), nullable=False)
    status = Column(String(32), nullable=False, default="OPEN", index=True)
    resolution = Column(String(32), nullable=True)
    assigned_to = Column(String(64), nullable=True, index=True)
    opened_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    # Relationships
    transaction = relationship("TransactionModel", back_populates="investigation")
    audit_trail = relationship("AuditEventModel", back_populates="investigation", cascade="all, delete-orphan", order_by="AuditEventModel.timestamp.asc()")

    __table_args__ = (
        CheckConstraint("risk_score >= 0.0 AND risk_score <= 1.0", name="ck_investigations_risk_score_range"),
        CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="ck_investigations_risk_level"),
        CheckConstraint("decision IN ('PASS', 'REVIEW')", name="ck_investigations_decision"),
        CheckConstraint("status IN ('OPEN', 'IN_REVIEW', 'ESCALATED', 'CLOSED')", name="ck_investigations_status"),
        CheckConstraint("resolution IS NULL OR resolution IN ('FRAUD_CONFIRMED', 'LEGITIMATE')", name="ck_investigations_resolution"),
        Index("ix_investigations_status_opened", "status", "opened_at"),
    )


class AuditEventModel(Base):
    """
    Immutable, append-only audit event for case actions and notes.
    """
    __tablename__ = "audit_events"

    id = Column(String(64), primary_key=True, index=True)
    investigation_id = Column(String(64), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    actor = Column(String(64), nullable=False)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utcnow, index=True)

    # Relationships
    investigation = relationship("InvestigationModel", back_populates="audit_trail")

    __table_args__ = (
        CheckConstraint(
            "action IN ('CASE_OPENED', 'CORTANA_FLAGGED', 'EXPLANATION_REQUESTED', 'CONFIRMED_FRAUD', 'MARKED_LEGITIMATE', 'ESCALATED', 'NOTE_ADDED')",
            name="ck_audit_events_action",
        ),
        Index("ix_audit_events_inv_time", "investigation_id", "timestamp"),
    )
