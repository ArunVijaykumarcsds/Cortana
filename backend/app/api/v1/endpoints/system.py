"""
CORTANA — System & Model Intelligence Endpoints.
Read-only endpoints providing safe operational status and model release metadata.
Does not expose secrets or raw filesystem paths.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.api.deps import get_db, get_inference_engine
from backend.app.core.inference import InferenceEngine
from backend.app.schemas.api import SystemServiceStatus, SystemStatusResponse

router = APIRouter()


@router.get(
    "/status",
    response_model=SystemStatusResponse,
    summary="Get Operational System Status",
)
def get_system_status(
    db: Session = Depends(get_db),
    engine: InferenceEngine = Depends(get_inference_engine),
):
    """
    Returns operational states of all CORTANA components.
    """
    # Check DB
    db_state = "OPERATIONAL"
    db_detail = "Connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_state = "DEGRADED"
        db_detail = "Connection failed"

    services = [
        SystemServiceStatus(
            service="Model 1 — Random Forest",
            state="OPERATIONAL" if engine.model_1 else "OFFLINE",
            detail="PaySim · Supervised fraud_probability · Weight 0.80",
        ),
        SystemServiceStatus(
            service="Model 2 — Isolation Forest",
            state="OPERATIONAL" if engine.model_2 else "OFFLINE",
            detail="ULB · Unsupervised anomaly_score · Weight 0.10",
        ),
        SystemServiceStatus(
            service="Rules Engine",
            state="OPERATIONAL" if engine.rules_engine else "OFFLINE",
            detail="6 behavioral rules active · Weight 0.10",
        ),
        SystemServiceStatus(
            service="Risk Fusion Engine",
            state="OPERATIONAL" if engine.fusion_engine else "OFFLINE",
            detail="Weights 0.80 / 0.10 / 0.10 · Locked threshold 0.98",
        ),
        SystemServiceStatus(
            service="Calibration Engine",
            state="OPERATIONAL" if engine.calibration_engine else "OFFLINE",
            detail="Percentile-rank empirical mapping",
        ),
        SystemServiceStatus(
            service="Database Persistence",
            state=db_state,
            detail=db_detail,
        ),
        SystemServiceStatus(
            service="API Gateway (FastAPI)",
            state="OPERATIONAL",
            detail="REST API v1 active",
        ),
    ]

    # Determine overall health of critical services
    critical_services = [
        services[0],  # Model 1
        services[1],  # Model 2
        services[2],  # Rules Engine
        services[3],  # Fusion Engine
        services[4],  # Calibration Engine
        services[5],  # Database Persistence
    ]
    all_operational = all(s.state == "OPERATIONAL" for s in critical_services)

    response_body = SystemStatusResponse(
        services=services,
        model_version="CORTANA_FINAL_v1.0.0",
        release_phase="Phase 6 — Final",
        package_status="Smoke-tested, artifact-reproducible",
        locked_threshold=0.98,
    )
    if all_operational:
        return response_body
    else:
        from fastapi.responses import JSONResponse
        from fastapi import status as http_status
        return JSONResponse(status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE, content=response_body.dict())


@router.get(
    "/models",
    summary="Get Model Configurations and Evaluation Metrics",
)
def get_model_intelligence(
    engine: InferenceEngine = Depends(get_inference_engine),
) -> Dict[str, Any]:
    """
    Returns model architectures, configurations, and reference validation metrics.
    """
    return {
        "model_1": {
            "name": "CORTANA Model 1",
            "algorithm": "RandomForestClassifier",
            "dataset": "PaySim",
            "learning_type": "Supervised",
            "features_count": len(engine.model_1.feature_names),
            "weight": 0.80,
            "validation_rows": 141815,
            "test_rows": 177268,
        },
        "model_2": {
            "name": "CORTANA Model 2",
            "algorithm": "IsolationForest",
            "dataset": "ULB",
            "learning_type": "Unsupervised Anomaly Detection",
            "features_count": len(engine.model_2.feature_names),
            "weight": 0.10,
            "operating_policy": {"type": "rank_based", "anomaly_percentage": 0.3},
        },
        "rules_engine": {
            "rules_count": len(engine.rules_engine.rules_definitions),
            "weight": 0.10,
            "rules": engine.rules_engine.rules_definitions,
        },
        "final_evaluation_benchmarks": {
            "precision": 0.273256,
            "recall": 0.949495,
            "f1": 0.424379,
            "roc_auc": 0.997710,
            "pr_auc": 0.587065,
            "fraud_detection_rate": "94.95% (94 of 99 fraud transactions detected)",
            "decision_threshold": 0.98,
        },
    }


@router.get(
    "/fusion/config",
    summary="Get Risk Fusion Policy Configuration",
)
def get_fusion_configuration(
    engine: InferenceEngine = Depends(get_inference_engine),
) -> Dict[str, Any]:
    """
    Returns the locked production fusion configuration.
    """
    return {
        "weights": engine.fusion_engine.weights,
        "decision_threshold": engine.fusion_engine.decision_threshold,
        "risk_levels": engine.fusion_engine.risk_levels,
        "cross_dataset_row_pairing": False,
        "dataset_architecture": {
            "paysim": ["model_1", "rules"],
            "ulb": ["model_2"],
        },
    }
