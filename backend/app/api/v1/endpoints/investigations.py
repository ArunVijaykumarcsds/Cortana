"""
CORTANA — Investigations & Case Management Endpoints.
Endpoints for human-in-the-loop investigation workflows and immutable audit trails.
"""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.db.models import InvestigationModel
from backend.app.db.repositories.investigation_repo import InvestigationRepository
from backend.app.security import get_api_key
from backend.app.schemas.api import (
    AuditEventResponse,
    InvestigationEventCreate,
    InvestigationResponse,
    InvestigationUpdate,
)

router = APIRouter()


def format_investigation_response(inv: InvestigationModel) -> InvestigationResponse:
    opened_str = inv.opened_at.isoformat() if isinstance(inv.opened_at, datetime) else str(inv.opened_at)
    
    trail = []
    if inv.audit_trail:
        for e in inv.audit_trail:
            t_str = e.timestamp.isoformat() if isinstance(e.timestamp, datetime) else str(e.timestamp)
            trail.append(
                AuditEventResponse(
                    id=e.id,
                    action=e.action,
                    actor=e.actor,
                    timestamp=t_str,
                    note=e.note,
                )
            )

    return InvestigationResponse(
        id=inv.id,
        transaction_id=inv.transaction_id,
        risk_level=inv.risk_level,
        risk_score=float(inv.risk_score),
        decision=inv.decision,
        status=inv.status,
        resolution=inv.resolution,
        assigned_to=inv.assigned_to,
        opened_at=opened_str,
        audit_trail=trail,
    )


@router.get(
    "",
    response_model=List[InvestigationResponse],
    summary="List Investigations (Paginated & Filtered)",
)
def list_investigations(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status ('OPEN', 'IN_REVIEW', 'ESCALATED', 'CLOSED')"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned analyst"),
    limit: int = Query(50, ge=1, le=200, description="Max cases to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    repo = InvestigationRepository(db)
    records = repo.list_investigations(
        status=status_filter,
        assigned_to=assigned_to,
        limit=limit,
        offset=offset,
    )
    return [format_investigation_response(inv) for inv in records]


@router.get(
    "/{investigation_id}",
    response_model=InvestigationResponse,
    summary="Get Investigation by ID",
)
def get_investigation(
    investigation_id: str,
    db: Session = Depends(get_db),
):
    repo = InvestigationRepository(db)
    inv = repo.get_by_id(investigation_id)
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation case '{investigation_id}' not found.",
        )
    return format_investigation_response(inv)


@router.post(
    "/{investigation_id}/events",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Append Audit Event to Investigation",
)
def append_audit_event(
    investigation_id: str,
    payload: InvestigationEventCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    """
    Appends an immutable audit event to the investigation's audit trail.
    """
    repo = InvestigationRepository(db)
    inv = repo.get_by_id(investigation_id)
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation case '{investigation_id}' not found.",
        )

    event_id = f"e-{inv.id}-{len(inv.audit_trail) + 1}"
    repo.add_audit_event(
        event_id=event_id,
        investigation_id=inv.id,
        action=payload.action,
        actor=payload.actor,
        note=payload.note,
    )
    db.commit()
    db.refresh(inv)
    return format_investigation_response(inv)


@router.patch(
    "/{investigation_id}",
    response_model=InvestigationResponse,
    summary="Update Investigation Status or Resolution",
)
def update_investigation(
    investigation_id: str,
    payload: InvestigationUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    repo = InvestigationRepository(db)
    inv = repo.get_by_id(investigation_id)
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation case '{investigation_id}' not found.",
        )

    # 1. Update assignment if provided
    if payload.assigned_to is not None:
        inv.assigned_to = payload.assigned_to

    # 2. Update resolution if provided
    if payload.resolution is not None:
        repo.resolve_case(
            case_id=investigation_id,
            resolution=payload.resolution,
            actor=payload.actor,
            note=payload.note,
        )
    elif payload.status is not None:
        repo.update_status(
            case_id=investigation_id,
            new_status=payload.status,
            actor=payload.actor,
            note=payload.note,
        )
    elif payload.note:
        event_id = f"e-{inv.id}-{len(inv.audit_trail) + 1}"
        repo.add_audit_event(
            event_id=event_id,
            investigation_id=inv.id,
            action="NOTE_ADDED",
            actor=payload.actor,
            note=payload.note,
        )

    db.commit()
    db.refresh(inv)
    return format_investigation_response(inv)
