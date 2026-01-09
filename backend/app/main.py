"""
SnowSpot API - FastAPI Application Entry Point.

Real-time snow conditions platform API with standardized response formatting.
"""

import json
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Any
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import engine
from app import models
from app.routers import resorts, conditions, forecasts
from app.schemas.api_response import (
    create_success_response,
    create_error_response,
    ErrorCodes,
)

# Optional Sentry integration
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.app_name} API in {settings.environment} mode")

    # Create database tables if they don't exist (for development)
    if settings.debug:
        models.Base.metadata.create_all(bind=engine)

    yield

    # Shutdown
    print(f"Shutting down {settings.app_name} API")


# Initialize Sentry if configured
if SENTRY_AVAILABLE and settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0 if settings.debug else 0.1,
        environment=settings.environment,
    )

# Custom response class that handles Decimal serialization
class CustomJSONResponse(JSONResponse):
    """JSON response that properly serializes Decimal types."""

    def render(self, content: Any) -> bytes:
        """Render content with custom JSON encoder."""
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=self._json_encoder,
        ).encode("utf-8")

    @staticmethod
    def _json_encoder(obj):
        """Custom JSON encoder to handle Decimal types."""
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Automated Snow Intelligence Platform API - Real-time ski resort conditions with quality scoring",
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    default_response_class=CustomJSONResponse,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression for responses larger than 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Custom exception handlers with standardized error responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with standardized response."""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first_error.get("loc", []))
    message = first_error.get("msg", "Validation error")

    return CustomJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            code=ErrorCodes.VALIDATION_ERROR,
            message=message,
            field=field,
            details={"errors": errors},
        ),
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors with standardized response."""
    return CustomJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message="A database error occurred",
            details={"type": type(exc).__name__} if settings.debug else None,
        ),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with standardized response."""
    if settings.debug:
        # In debug mode, include error details
        return CustomJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message=str(exc),
                details={"type": type(exc).__name__},
            ),
        )
    else:
        # In production, hide error details
        return CustomJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message="An unexpected error occurred",
            ),
        )


# Include API routers
app.include_router(
    resorts.router,
    prefix="/api/v1/resorts",
    tags=["Resorts"],
)
app.include_router(
    conditions.router,
    prefix="/api/v1/conditions",
    tags=["Conditions"],
)
app.include_router(
    forecasts.router,
    prefix="/api/v1/forecasts",
    tags=["Forecasts"],
)


# Health check endpoints
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with API info."""
    return create_success_response(
        data={
            "name": settings.app_name,
            "version": settings.api_version,
            "status": "operational",
            "environment": settings.environment,
            "docs_url": "/docs",
        },
        message=f"Welcome to the {settings.app_name} API",
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the current health status of the API and its dependencies.
    """
    # TODO: Add actual health checks for database, redis, celery
    return create_success_response(
        data={
            "status": "healthy",
            "checks": {
                "api": "ok",
                "database": "ok",  # TODO: Implement actual check
                "redis": "ok",  # TODO: Implement actual check
            },
        },
    )


@app.get("/api/v1", tags=["Health"])
async def api_info():
    """
    API version information and available endpoints.
    """
    return create_success_response(
        data={
            "version": settings.api_version,
            "endpoints": {
                "resorts": "/api/v1/resorts",
                "conditions": "/api/v1/conditions",
                "health": "/health",
                "docs": "/docs",
            },
            "features": [
                "Resort listing and details",
                "Real-time snow conditions",
                "Snow quality scoring",
                "Condition history",
                "Multi-resort comparison",
                "Powder day alerts",
            ],
        },
    )


# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
