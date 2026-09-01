"""Initial CORTANA schema migration.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-22 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. transactions
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("dataset_context", sa.String(length=16), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=8), server_default="USD", nullable=False),
        sa.Column("origin_account", sa.String(length=64), server_default="", nullable=False),
        sa.Column("destination_account", sa.String(length=64), server_default="", nullable=False),
        sa.Column("origin_balance_before", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("origin_balance_after", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("destination_balance_before", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("destination_balance_after", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_1_probability", sa.Float(), nullable=True),
        sa.Column("model_2_score", sa.Float(), nullable=True),
        sa.Column("rules_risk", sa.Float(), nullable=True),
        sa.Column("triggered_rules", sa.JSON(), nullable=True),
        sa.Column("fused_risk", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.CheckConstraint("dataset_context IN ('PaySim', 'ULB')", name="ck_transactions_dataset_context"),
        sa.CheckConstraint("amount >= 0.0", name="ck_transactions_amount_non_negative"),
        sa.CheckConstraint("fused_risk >= 0.0 AND fused_risk <= 1.0", name="ck_transactions_fused_risk_range"),
        sa.CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="ck_transactions_risk_level"),
        sa.CheckConstraint("decision IN ('PASS', 'REVIEW')", name="ck_transactions_decision"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transactions_id"), "transactions", ["id"], unique=False)
    op.create_index(op.f("ix_transactions_dataset_context"), "transactions", ["dataset_context"], unique=False)
    op.create_index(op.f("ix_transactions_timestamp"), "transactions", ["timestamp"], unique=False)
    op.create_index(op.f("ix_transactions_fused_risk"), "transactions", ["fused_risk"], unique=False)
    op.create_index("ix_transactions_ctx_timestamp", "transactions", ["dataset_context", "timestamp"], unique=False)
    op.create_index("ix_transactions_fused_risk_desc", "transactions", ["fused_risk"], unique=False)

    # 2. alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("transaction_id", sa.String(length=64), nullable=False),
        sa.Column("dataset_context", sa.String(length=16), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="OPEN", nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("dataset_context IN ('PaySim', 'ULB')", name="ck_alerts_dataset_context"),
        sa.CheckConstraint("risk_score >= 0.0 AND risk_score <= 1.0", name="ck_alerts_risk_score_range"),
        sa.CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="ck_alerts_risk_level"),
        sa.CheckConstraint("decision IN ('PASS', 'REVIEW')", name="ck_alerts_decision"),
        sa.CheckConstraint("status IN ('OPEN', 'UNDER_REVIEW', 'RESOLVED')", name="ck_alerts_status"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_id"), "alerts", ["id"], unique=False)
    op.create_index(op.f("ix_alerts_transaction_id"), "alerts", ["transaction_id"], unique=False)
    op.create_index(op.f("ix_alerts_status"), "alerts", ["status"], unique=False)
    op.create_index(op.f("ix_alerts_risk_level"), "alerts", ["risk_level"], unique=False)
    op.create_index(op.f("ix_alerts_timestamp"), "alerts", ["timestamp"], unique=False)
    op.create_index("ix_alerts_status_timestamp", "alerts", ["status", "timestamp"], unique=False)

    # 3. investigations
    op.create_table(
        "investigations",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("transaction_id", sa.String(length=64), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="OPEN", nullable=False),
        sa.Column("resolution", sa.String(length=32), nullable=True),
        sa.Column("assigned_to", sa.String(length=64), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("risk_score >= 0.0 AND risk_score <= 1.0", name="ck_investigations_risk_score_range"),
        sa.CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="ck_investigations_risk_level"),
        sa.CheckConstraint("decision IN ('PASS', 'REVIEW')", name="ck_investigations_decision"),
        sa.CheckConstraint("status IN ('OPEN', 'IN_REVIEW', 'ESCALATED', 'CLOSED')", name="ck_investigations_status"),
        sa.CheckConstraint("resolution IS NULL OR resolution IN ('FRAUD_CONFIRMED', 'LEGITIMATE')", name="ck_investigations_resolution"),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
    )
    op.create_index(op.f("ix_investigations_id"), "investigations", ["id"], unique=False)
    op.create_index(op.f("ix_investigations_transaction_id"), "investigations", ["transaction_id"], unique=True)
    op.create_index(op.f("ix_investigations_status"), "investigations", ["status"], unique=False)
    op.create_index(op.f("ix_investigations_assigned_to"), "investigations", ["assigned_to"], unique=False)
    op.create_index(op.f("ix_investigations_opened_at"), "investigations", ["opened_at"], unique=False)
    op.create_index("ix_investigations_status_opened", "investigations", ["status", "opened_at"], unique=False)

    # 4. audit_events
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("investigation_id", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("actor", sa.String(length=64), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "action IN ('CASE_OPENED', 'CORTANA_FLAGGED', 'EXPLANATION_REQUESTED', 'CONFIRMED_FRAUD', 'MARKED_LEGITIMATE', 'ESCALATED', 'NOTE_ADDED')",
            name="ck_audit_events_action",
        ),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_events_id"), "audit_events", ["id"], unique=False)
    op.create_index(op.f("ix_audit_events_investigation_id"), "audit_events", ["investigation_id"], unique=False)
    op.create_index(op.f("ix_audit_events_timestamp"), "audit_events", ["timestamp"], unique=False)
    op.create_index("ix_audit_events_inv_time", "audit_events", ["investigation_id", "timestamp"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("investigations")
    op.drop_table("alerts")
    op.drop_table("transactions")
