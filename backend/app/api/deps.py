"""
CORTANA — FastAPI API Dependencies.
Provides database sessions and the singleton InferenceEngine instance.
"""

from typing import Generator
from functools import lru_cache
from sqlalchemy.orm import Session
from fastapi import Depends

from backend.app.core.explanation import ExplanationService
from backend.app.core.inference import InferenceEngine
from backend.app.db.database import get_db


@lru_cache()
def get_inference_engine() -> InferenceEngine:
    """
    Returns the singleton CORTANA InferenceEngine.
    Artifacts are loaded once and reused across all requests.
    """
    return InferenceEngine()


@lru_cache()
def get_explanation_service() -> ExplanationService:
    """
    Returns the singleton ExplanationService.
    """
    return ExplanationService()

