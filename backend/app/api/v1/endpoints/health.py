"""
CORTANA — Health & Readiness Endpoint.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.api.deps import get_db, get_inference_engine
from backend.app.core.inference import InferenceEngine
from backend.app.schemas.api import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health & Diagnostic Check",
)
def check_health(
    db: Session = Depends(get_db),
    engine: InferenceEngine = Depends(get_inference_engine),
):
    """
    Checks operational status of the API, Database connection, and ML Inference Engine.
    Does not leak internal paths or secrets.
    """
    # 1. Check database
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    # 2. Check ML engine
    ml_status = "operational"
    try:
        if not engine.model_1 or not engine.model_2 or not engine.rules_engine:
            ml_status = "error"
    except Exception:
        ml_status = "error"

    overall_status = "healthy"
    if db_status != "connected" or ml_status != "operational":
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        database=db_status,
        ml_engine=ml_status,
        version="1.0.0",
    )
