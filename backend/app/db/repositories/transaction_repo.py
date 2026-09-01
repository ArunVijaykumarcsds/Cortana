"""
CORTANA — Transaction Repository.
Data access layer for transaction persistence and queries.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, select

from backend.app.db.models import TransactionModel
from backend.app.schemas.inference import InferenceResult
from backend.app.schemas.transaction import PaySimTransactionInput, ULBTransactionInput


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_from_inference(
        self,
        tx_id: str,
        input_data: dict,
        inference_result: InferenceResult,
        timestamp: Optional[datetime] = None,
    ) -> TransactionModel:
        """
        Creates a transaction record preserving the exact inference outputs.
        Ensures strict separation: PaySim has model_2_score=None; ULB has model_1_prob=None, rules_risk=None.
        """
        ctx = inference_result.dataset_context
        
        # PaySim signals
        m1_prob = inference_result.model_1.fraud_probability if inference_result.model_1 else None
        rules_risk = inference_result.rules.behavioral_risk if inference_result.rules else None
        triggered = [r.model_dump() for r in inference_result.rules.triggered] if inference_result.rules else None
        
        # ULB signals
        m2_score = inference_result.model_2.anomaly_score if inference_result.model_2 else None

        db_tx = TransactionModel(
            id=tx_id,
            dataset_context=ctx,
            type=input_data.get("type", "PAYMENT"),
            amount=float(input_data.get("amount", 0.0)),
            currency=input_data.get("currency", "USD"),
            origin_account=input_data.get("origin_account", ""),
            destination_account=input_data.get("destination_account", ""),
            origin_balance_before=float(input_data.get("origin_balance_before", 0.0)),
            origin_balance_after=float(input_data.get("origin_balance_after", 0.0)),
            destination_balance_before=float(input_data.get("destination_balance_before", 0.0)),
            destination_balance_after=float(input_data.get("destination_balance_after", 0.0)),
            timestamp=timestamp or datetime.utcnow(),
            model_1_probability=m1_prob,
            model_2_score=m2_score,
            rules_risk=rules_risk,
            triggered_rules=triggered,
            fused_risk=inference_result.fused_risk_score,
            risk_level=inference_result.risk_level,
            decision=inference_result.decision,
            raw_payload=input_data,
        )

        self.db.add(db_tx)
        self.db.flush()
        return db_tx

    def get_by_id(self, tx_id: str) -> Optional[TransactionModel]:
        stmt = select(TransactionModel).where(TransactionModel.id == tx_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_transactions(
        self,
        context: Optional[str] = None,
        risk_level: Optional[str] = None,
        decision: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[TransactionModel]:
        stmt = select(TransactionModel)
        if context and context != "ALL":
            stmt = stmt.where(TransactionModel.dataset_context == context)
        if risk_level and risk_level != "ALL":
            stmt = stmt.where(TransactionModel.risk_level == risk_level)
        if decision and decision != "ALL":
            stmt = stmt.where(TransactionModel.decision == decision)

        stmt = stmt.order_by(desc(TransactionModel.timestamp)).offset(offset).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_transactions(
        self,
        context: Optional[str] = None,
        risk_level: Optional[str] = None,
    ) -> int:
        stmt = select(TransactionModel)
        if context and context != "ALL":
            stmt = stmt.where(TransactionModel.dataset_context == context)
        if risk_level and risk_level != "ALL":
            stmt = stmt.where(TransactionModel.risk_level == risk_level)
        return len(list(self.db.execute(stmt).scalars().all()))
