"""
CORTANA — Investigation & Audit Event Repository.
Data access layer for human-in-the-loop fraud case management
and immutable append-only audit logging.
"""

from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc, select

from backend.app.db.models import AuditEventModel, InvestigationModel, TransactionModel


class InvestigationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_investigation(
        self,
        case_id: str,
        transaction: TransactionModel,
        assigned_to: Optional[str] = None,
        opened_at: Optional[datetime] = None,
    ) -> InvestigationModel:
        inv = InvestigationModel(
            id=case_id,
            transaction_id=transaction.id,
            risk_level=transaction.risk_level,
            risk_score=transaction.fused_risk,
            decision=transaction.decision,
            status="OPEN",
            resolution=None,
            assigned_to=assigned_to,
            opened_at=opened_at or transaction.timestamp or datetime.now(timezone.utc),
        )
        self.db.add(inv)
        self.db.flush()

        # Add initial CORTANA_FLAGGED audit event
        self.add_audit_event(
            event_id=f"e-{inv.id}-1",
            investigation_id=inv.id,
            action="CORTANA_FLAGGED",
            actor="CORTANA",
            note=f"Transaction flagged for review with fused risk {transaction.fused_risk:.4f} ({transaction.risk_level})",
            timestamp=inv.opened_at,
        )

        return inv

    def get_by_id(self, case_id: str) -> Optional[InvestigationModel]:
        stmt = select(InvestigationModel).where(InvestigationModel.id == case_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_transaction_id(self, transaction_id: str) -> Optional[InvestigationModel]:
        stmt = select(InvestigationModel).where(InvestigationModel.transaction_id == transaction_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_investigations(
        self,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[InvestigationModel]:
        stmt = select(InvestigationModel)
        if status and status != "ALL":
            stmt = stmt.where(InvestigationModel.status == status)
        if assigned_to and assigned_to != "ALL":
            stmt = stmt.where(InvestigationModel.assigned_to == assigned_to)

        stmt = stmt.order_by(desc(InvestigationModel.opened_at)).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def add_audit_event(
        self,
        event_id: str,
        investigation_id: str,
        action: str,
        actor: str,
        note: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> AuditEventModel:
        """
        Appends an immutable audit event to the investigation's audit trail.
        """
        event = AuditEventModel(
            id=event_id,
            investigation_id=investigation_id,
            action=action,
            actor=actor,
            note=note,
            timestamp=timestamp or datetime.now(timezone.utc),
        )
        self.db.add(event)
        self.db.flush()
        return event

    def update_status(self, case_id: str, new_status: str, actor: str, note: Optional[str] = None) -> Optional[InvestigationModel]:
        inv = self.get_by_id(case_id)
        if not inv:
            return None

        inv.status = new_status
        # Append audit event
        count = len(inv.audit_trail) + 1
        self.add_audit_event(
            event_id=f"e-{inv.id}-{count}",
            investigation_id=inv.id,
            action="ESCALATED" if new_status == "ESCALATED" else "NOTE_ADDED",
            actor=actor,
            note=note or f"Status changed to {new_status}",
        )
        self.db.flush()
        return inv

    def resolve_case(
        self,
        case_id: str,
        resolution: str,
        actor: str,
        note: Optional[str] = None,
    ) -> Optional[InvestigationModel]:
        inv = self.get_by_id(case_id)
        if not inv:
            return None

        if resolution not in ("FRAUD_CONFIRMED", "LEGITIMATE"):
            raise ValueError(f"Invalid resolution '{resolution}'. Must be 'FRAUD_CONFIRMED' or 'LEGITIMATE'.")

        inv.resolution = resolution
        inv.status = "CLOSED"

        count = len(inv.audit_trail) + 1
        action = "CONFIRMED_FRAUD" if resolution == "FRAUD_CONFIRMED" else "MARKED_LEGITIMATE"
        self.add_audit_event(
            event_id=f"e-{inv.id}-{count}",
            investigation_id=inv.id,
            action=action,
            actor=actor,
            note=note or f"Case resolved as {resolution}",
        )
        self.db.flush()
        return inv
