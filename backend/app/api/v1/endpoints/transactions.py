"""
CORTANA — Transactions Endpoints.
Endpoints for querying, counting, and scoring transactions with database persistence.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_explanation_service, get_inference_engine
from backend.app.core.explanation import ExplanationService, extract_explanation_facts_from_db
from backend.app.core.inference import InferenceEngine
from backend.app.db.models import TransactionModel
from backend.app.db.repositories.alert_repo import AlertRepository
from backend.app.db.repositories.investigation_repo import InvestigationRepository
from backend.app.db.repositories.transaction_repo import TransactionRepository
from backend.app.schemas.api import TransactionCountResponse, TransactionResponse
from backend.app.schemas.explanation import ExplanationResponse
from backend.app.schemas.inference import (
    FusionResult,
    Model1Signal,
    Model2Signal,
    RulesSignal,
    TriggeredRule,
)
from backend.app.schemas.transaction import PaySimTransactionInput, ULBTransactionInput

router = APIRouter()


def format_transaction_response(tx: TransactionModel) -> TransactionResponse:
    """
    Formats a database TransactionModel into the standard TransactionResponse contract.
    """
    # 1. Model 1 signal
    m1_sig = None
    if tx.model_1_probability is not None:
        raw_prob = tx.raw_payload.get("raw_m1_prob", tx.model_1_probability) if tx.raw_payload else tx.model_1_probability
        m1_sig = Model1Signal(
            dataset="PaySim",
            raw_probability=float(raw_prob),
            fraud_probability=float(tx.model_1_probability),
        )

    # 2. Rules signal
    rules_sig = None
    if tx.rules_risk is not None:
        raw_rules = tx.raw_payload.get("raw_rule_score", tx.rules_risk) if tx.raw_payload else tx.rules_risk
        trig = []
        if tx.triggered_rules and isinstance(tx.triggered_rules, list):
            for r in tx.triggered_rules:
                if isinstance(r, dict):
                    trig.append(TriggeredRule(**r))
        rules_sig = RulesSignal(
            dataset="PaySim",
            raw_rule_score=float(raw_rules),
            behavioral_risk=float(tx.rules_risk),
            triggered=trig,
        )

    # 3. Model 2 signal
    m2_sig = None
    if tx.model_2_score is not None:
        raw_m2 = tx.raw_payload.get("raw_m2_score", tx.model_2_score) if tx.raw_payload else tx.model_2_score
        m2_sig = Model2Signal(
            dataset="ULB",
            raw_score=float(raw_m2),
            anomaly_score=float(tx.model_2_score),
        )

    # 4. Fusion result
    fusion_res = FusionResult(
        fused_risk=float(tx.fused_risk),
        risk_level=tx.risk_level,
        decision=tx.decision,
        weights={"model_1": 0.8, "model_2": 0.1, "rules": 0.1},
        active_weights={"model_1": 0.8 / 0.9, "rules": 0.1 / 0.9} if tx.dataset_context == "PaySim" else {"model_2": 1.0},
        threshold=0.98,
    )

    ts_str = tx.timestamp.isoformat() if isinstance(tx.timestamp, datetime) else str(tx.timestamp)

    return TransactionResponse(
        id=tx.id,
        dataset_context=tx.dataset_context,
        type=tx.type,
        amount=float(tx.amount),
        currency=tx.currency,
        origin_account=tx.origin_account,
        destination_account=tx.destination_account,
        origin_balance_before=float(tx.origin_balance_before),
        origin_balance_after=float(tx.origin_balance_after),
        destination_balance_before=float(tx.destination_balance_before),
        destination_balance_after=float(tx.destination_balance_after),
        timestamp=ts_str,
        model_1=m1_sig,
        rules=rules_sig,
        model_2=m2_sig,
        fusion=fusion_res,
    )


@router.get(
    "",
    response_model=List[TransactionResponse],
    summary="List Transactions (Paginated & Filtered)",
)
def list_transactions(
    context: Optional[str] = Query(None, description="Filter by context ('PaySim', 'ULB', or 'ALL')"),
    risk_level: Optional[str] = Query(None, description="Filter by risk tier ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"),
    decision: Optional[str] = Query(None, description="Filter by decision ('PASS', 'REVIEW')"),
    limit: int = Query(50, ge=1, le=200, description="Max rows to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    repo = TransactionRepository(db)
    records = repo.list_transactions(
        context=context,
        risk_level=risk_level,
        decision=decision,
        limit=limit,
        offset=offset,
    )
    return [format_transaction_response(tx) for tx in records]


@router.get(
    "/count",
    response_model=TransactionCountResponse,
    summary="Count Transactions",
)
def count_transactions(
    context: Optional[str] = Query(None, description="Filter by context ('PaySim', 'ULB', or 'ALL')"),
    risk_level: Optional[str] = Query(None, description="Filter by risk tier"),
    db: Session = Depends(get_db),
):
    repo = TransactionRepository(db)
    total = repo.count_transactions(context=context, risk_level=risk_level)
    return TransactionCountResponse(total=total, context=context, risk_level=risk_level)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get Transaction by ID",
)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
):
    repo = TransactionRepository(db)
    tx = repo.get_by_id(transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{transaction_id}' not found.",
        )
    return format_transaction_response(tx)


@router.post(
    "/{transaction_id}/explain",
    response_model=ExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Plain-English Risk Explanation",
)
def explain_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    explanation_service: ExplanationService = Depends(get_explanation_service),
):
    """
    Generates a natural-language explanation of pre-computed ML inference facts.
    Strictly uses authoritative server-side data (does not trust client scores).
    Never modifies risk score or decision.
    """
    repo = TransactionRepository(db)
    tx = repo.get_by_id(transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{transaction_id}' not found.",
        )

    facts = extract_explanation_facts_from_db(
        tx_id=tx.id,
        dataset_context=tx.dataset_context,
        tx_type=tx.type,
        risk_level=tx.risk_level,
        decision=tx.decision,
        fused_risk=tx.fused_risk,
        model_1_prob=tx.model_1_probability,
        rules_risk=tx.rules_risk,
        model_2_score=tx.model_2_score,
        triggered_rules_raw=tx.triggered_rules,
    )

    try:
        explanation = explanation_service.generate_explanation(facts)
        return explanation
    except Exception:
        # Fallback guarantee
        return explanation_service.fallback_engine.generate(facts)



@router.post(
    "/score",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Score and Persist Transaction",
)
def score_and_persist_transaction(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    engine: InferenceEngine = Depends(get_inference_engine),
):
    """
    Scores a transaction using the ML engine, persists the scored record to the database,
    and automatically creates an Alert and Investigation case if review/high-risk is triggered.
    """
    ctx = payload.get("dataset_context")
    if not ctx or ctx not in ("PaySim", "ULB"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or missing 'dataset_context'. Must be 'PaySim' or 'ULB'.",
        )

    # 1. Execute inference
    try:
        if ctx == "PaySim":
            tx_input = PaySimTransactionInput(**payload)
            inference_res = engine.score_paysim_transaction(tx_input)
            tx_id = payload.get("id") or f"PSX-{int(datetime.now(timezone.utc).timestamp() * 1000) % 1000000}"
        else:
            tx_input = ULBTransactionInput(**payload)
            inference_res = engine.score_ulb_transaction(tx_input)
            tx_id = payload.get("id") or f"ULB-{int(datetime.now(timezone.utc).timestamp() * 1000) % 1000000}"
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation / Inference error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction scoring failed.",
        )

    # 2. Persist to database
    try:
        tx_repo = TransactionRepository(db)
        alert_repo = AlertRepository(db)
        inv_repo = InvestigationRepository(db)

        # Record raw signals in raw_payload
        enriched_payload = {**payload}
        if inference_res.model_1:
            enriched_payload["raw_m1_prob"] = inference_res.model_1.raw_probability
        if inference_res.rules:
            enriched_payload["raw_rule_score"] = inference_res.rules.raw_rule_score
        if inference_res.model_2:
            enriched_payload["raw_m2_score"] = inference_res.model_2.raw_score

        tx_record = tx_repo.create_from_inference(
            tx_id=tx_id,
            input_data=enriched_payload,
            inference_result=inference_res,
        )

        # 3. Create Alert if High/Critical or Review
        if tx_record.risk_level in ("HIGH", "CRITICAL") or tx_record.decision == "REVIEW":
            alert_id = f"A-{int(datetime.now(timezone.utc).timestamp() * 1000) % 1000000}"
            alert_repo.create_alert(alert_id=alert_id, transaction=tx_record)

            # 4. Create Investigation case if REVIEW
            if tx_record.decision == "REVIEW":
                case_id = f"C-{int(datetime.now(timezone.utc).timestamp() * 1000) % 1000000}"
                inv_repo.create_investigation(
                    case_id=case_id,
                    transaction=tx_record,
                    assigned_to="A. Menon",
                )

        db.commit()
        db.refresh(tx_record)
        return format_transaction_response(tx_record)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist transaction to database.",
        )
