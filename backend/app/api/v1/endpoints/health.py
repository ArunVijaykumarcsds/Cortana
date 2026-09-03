"""
CORTANA — Health & Readiness Endpoint.
"""

import os

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_inference_engine
from backend.app.core.inference import InferenceEngine
from backend.app.schemas.api import HealthResponse, HealthComponentStatus

router = APIRouter()


def _llm_provider_status() -> str:
    """
    LLM is non-critical because CORTANA has a deterministic fallback.
    Reports 'ok' when deterministic fallback is available or a supported
    external provider is configured.
    """
    provider = os.getenv("CORTANA_LLM_PROVIDER", "").strip().lower()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    if provider in ("", "deterministic_fallback"):
        return "ok"

    if provider == "gemini" and gemini_key:
        return "ok"

    return "degraded"


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
    Checks operational status of the API, database, critical ML components,
    calibration/fusion engines, and optional LLM provider.

    LLM degradation does not make the overall service degraded because
    deterministic explanation fallback remains available.
    """

    # 1. Database
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    # 2. Critical ML / risk components
    model1_ok = bool(getattr(engine, "model_1", None))
    model2_ok = bool(getattr(engine, "model_2", None))
    rules_ok = bool(getattr(engine, "rules_engine", None))
    fusion_ok = bool(getattr(engine, "fusion_engine", None))
    calibration_ok = bool(getattr(engine, "calibration_engine", None))

    # 3. Optional explanation provider
    llm_status = _llm_provider_status()

    details = HealthComponentStatus(
        database="ok" if db_ok else "degraded",
        model1="ok" if model1_ok else "degraded",
        model2="ok" if model2_ok else "degraded",
        rules="ok" if rules_ok else "degraded",
        fusion="ok" if fusion_ok else "degraded",
        calibration="ok" if calibration_ok else "degraded",
        llm_provider=llm_status,
    )

    # LLM is deliberately excluded from critical health determination.
    critical_ok = all(
        component == "ok"
        for component in (
            details.database,
            details.model1,
            details.model2,
            details.rules,
            details.fusion,
            details.calibration,
        )
    )

    overall_status = "healthy" if critical_ok else "degraded"

    return HealthResponse(
        status=overall_status,
        database="connected" if db_ok else "disconnected",
        ml_engine=(
            "operational"
            if all(
                component == "ok"
                for component in (
                    details.model1,
                    details.model2,
                    details.rules,
                    details.fusion,
                    details.calibration,
                )
            )
            else "error"
        ),
        details=details,
        version="1.0.0",
    )