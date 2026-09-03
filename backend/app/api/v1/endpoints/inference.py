"""
CORTANA — Pure Inference Endpoints.
Direct scoring endpoints calling the Stage 2 ML Inference Engine.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from backend.app.api.deps import get_inference_engine
from backend.app.core.inference import InferenceEngine
from backend.app.schemas.inference import InferenceResult
from backend.app.schemas.transaction import PaySimTransactionInput, ULBTransactionInput

router = APIRouter()


@router.post(
    "/paysim",
    response_model=InferenceResult,
    status_code=status.HTTP_200_OK,
    summary="Score PaySim Transaction (Model 1 + Behavioral Rules)",
)
def score_paysim(
    payload: PaySimTransactionInput,
    engine: InferenceEngine = Depends(get_inference_engine),
):
    """
    Scores a PaySim mobile transaction:
    - Evaluates Model 1 (Random Forest supervised fraud probability).
    - Evaluates 6 Behavioral Rules.
    - Calibrates signals via empirical percentile rank.
    - Fuses signals with weights 0.80 / 0.10.
    - Model 2 is STRICTLY INACTIVE (NULL).
    """
    try:
        result = engine.score_paysim_transaction(payload)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inference error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference processing failed.",
        )


@router.post(
    "/ulb",
    response_model=InferenceResult,
    status_code=status.HTTP_200_OK,
    summary="Score ULB Transaction (Model 2 Isolation Forest)",
)
def score_ulb(
    payload: ULBTransactionInput,
    engine: InferenceEngine = Depends(get_inference_engine),
):
    """
    Scores a ULB credit card transaction:
    - Extracts 30 continuous PCA features (Time, V1..V28, Amount).
    - Evaluates Model 2 (Isolation Forest unsupervised anomaly score).
    - Calibrates signal via empirical percentile rank.
    - Model 1 and Rules Engine are STRICTLY INACTIVE (NULL).
    """
    try:
        result = engine.score_ulb_transaction(payload)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inference error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference processing failed.",
        )
