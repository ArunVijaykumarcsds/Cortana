"""
CORTANA — Alert Repository.
Data access layer for alert management and workflow updates.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, select

from backend.app.db.models import AlertModel, TransactionModel


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_alert(
        self,
        alert_id: str,
        transaction: TransactionModel,
        status: str = "OPEN",
        timestamp: Optional[datetime] = None,
    ) -> AlertModel:
        alert = AlertModel(
            id=alert_id,
            transaction_id=transaction.id,
            dataset_context=transaction.dataset_context,
            type=transaction.type,
            risk_score=transaction.fused_risk,
            risk_level=transaction.risk_level,
            decision=transaction.decision,
            status=status,
            timestamp=timestamp or transaction.timestamp or datetime.utcnow(),
        )
        self.db.add(alert)
        self.db.flush()
        return alert

    def get_by_id(self, alert_id: str) -> Optional[AlertModel]:
        stmt = select(AlertModel).where(AlertModel.id == alert_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_alerts(
        self,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AlertModel]:
        stmt = select(AlertModel)
        if status and status != "ALL":
            stmt = stmt.where(AlertModel.status == status)
        if risk_level and risk_level != "ALL":
            stmt = stmt.where(AlertModel.risk_level == risk_level)

        stmt = stmt.order_by(desc(AlertModel.timestamp)).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def update_status(self, alert_id: str, new_status: str) -> Optional[AlertModel]:
        alert = self.get_by_id(alert_id)
        if alert:
            alert.status = new_status
            self.db.flush()
        return alert
