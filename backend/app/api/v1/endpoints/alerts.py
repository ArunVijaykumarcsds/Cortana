"""
CORTANA — Alerts Endpoints.
Endpoints for viewing and transitioning fraud risk alerts.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.db.models import AlertModel
from backend.app.db.repositories.alert_repo import AlertRepository
from backend.app.schemas.api import AlertResponse, AlertStatusUpdate

router = APIRouter()


def format_alert_response(alert: AlertModel) -> AlertResponse:
    ts_str = alert.timestamp.isoformat() if isinstance(alert.timestamp, datetime) else str(alert.timestamp)
    return AlertResponse(
        id=alert.id,
        transaction_id=alert.transaction_id,
        dataset_context=alert.dataset_context,
        type=alert.type,
        risk_score=float(alert.risk_score),
        risk_level=alert.risk_level,
        decision=alert.decision,
        status=alert.status,
        timestamp=ts_str,
    )


@router.get(
    "",
    response_model=List[AlertResponse],
    summary="List Alerts (Paginated & Filtered)",
)
def list_alerts(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status ('OPEN', 'UNDER_REVIEW', 'RESOLVED')"),
    risk_level: Optional[str] = Query(None, description="Filter by risk tier"),
    limit: int = Query(50, ge=1, le=200, description="Max rows to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    repo = AlertRepository(db)
    records = repo.list_alerts(status=status_filter, risk_level=risk_level, limit=limit, offset=offset)
    return [format_alert_response(a) for a in records]


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
    summary="Get Alert by ID",
)
def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
):
    repo = AlertRepository(db)
    alert = repo.get_by_id(alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found.",
        )
    return format_alert_response(alert)


@router.patch(
    "/{alert_id}/status",
    response_model=AlertResponse,
    summary="Update Alert Status",
)
def update_alert_status(
    alert_id: str,
    payload: AlertStatusUpdate,
    db: Session = Depends(get_db),
):
    repo = AlertRepository(db)
    alert = repo.get_by_id(alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found.",
        )

    updated = repo.update_status(alert_id, payload.status)
    db.commit()
    db.refresh(updated)
    return format_alert_response(updated)
