"""
CORTANA — FastAPI Application Bootstrap.
Main entry point configuring middleware, routers, error handlers, and lifecycle hooks.
"""

import os
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.deps import get_inference_engine
from backend.app.api.v1.router import api_v1_router
from backend.app.db.database import create_all_tables


# Allowed CORS origins — customizable via environment variable
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
env_origins = os.getenv("CORTANA_CORS_ORIGINS")
if env_origins:
    CORS_ORIGINS: List[str] = [o.strip() for o in env_origins.split(",") if o.strip()]
else:
    CORS_ORIGINS = DEFAULT_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Initializes database tables and warms up the ML inference engine on startup.
    """
    # 1. Initialize DB tables if they don't exist
    create_all_tables()

    # 2. Warm up ML inference engine
    _ = get_inference_engine()

    yield


app = FastAPI(
    title="CORTANA Financial Risk Intelligence API",
    description=(
        "Production-grade backend API for CORTANA multi-component financial risk "
        "intelligence and fraud detection platform. Strictly preserves dataset context "
        "separation between PaySim and ULB transactions."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers — Safe structured error responses without leaking stack traces
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Invalid field")
        errors.append({"field": loc, "message": msg})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "details": errors,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Exception",
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log internally without leaking stack traces or filesystem paths to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred during processing.",
        },
    )


# Mount v1 router at /api/v1
app.include_router(api_v1_router, prefix="/api")


@app.get("/", tags=["Root"], summary="API Root Redirect / Status")
def root_status():
    return {
        "service": "CORTANA Risk Intelligence API",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "api_v1": "/api/v1",
    }
