"""
CORTANA — API v1 Master Router.
Aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    alerts,
    health,
    inference,
    investigations,
    system,
    transactions,
)

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(inference.router, prefix="/inference", tags=["Inference"])
api_v1_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_v1_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_v1_router.include_router(investigations.router, prefix="/investigations", tags=["Investigations"])
api_v1_router.include_router(system.router, prefix="/system", tags=["System"])

# Additional direct routes matching top-level requirements
api_v1_router.add_api_route(
    "/models",
    system.get_model_intelligence,
    methods=["GET"],
    tags=["System"],
    summary="Get Model Configurations and Evaluation Metrics",
)
api_v1_router.add_api_route(
    "/fusion/config",
    system.get_fusion_configuration,
    methods=["GET"],
    tags=["System"],
    summary="Get Risk Fusion Policy Configuration",
)
