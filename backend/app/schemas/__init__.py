"""
Pydantic schemas for SnowSpot API.

Includes standardized API response wrappers and data schemas for
resorts, conditions, and other domain models.
"""

from app.schemas.api_response import (
    APIResponse,
    APIErrorResponse,
    PaginationMeta,
    ResponseMeta,
    ErrorDetail,
    ErrorCodes,
    create_success_response,
    create_error_response,
    create_pagination_meta,
)
from app.schemas.resort import (
    ResortBase,
    ResortCreate,
    ResortUpdate,
    ResortResponse,
    ResortSummary,
)
from app.schemas.condition import (
    ConditionBase,
    ConditionCreate,
    ConditionResponse,
    ConditionWithQuality,
    ConditionSummary,
    ConditionHistory,
    LatestConditions,
    ResortWithLatestCondition,
)

__all__ = [
    # API Response wrappers
    "APIResponse",
    "APIErrorResponse",
    "PaginationMeta",
    "ResponseMeta",
    "ErrorDetail",
    "ErrorCodes",
    "create_success_response",
    "create_error_response",
    "create_pagination_meta",
    # Resort schemas
    "ResortBase",
    "ResortCreate",
    "ResortUpdate",
    "ResortResponse",
    "ResortSummary",
    # Condition schemas
    "ConditionBase",
    "ConditionCreate",
    "ConditionResponse",
    "ConditionWithQuality",
    "ConditionSummary",
    "ConditionHistory",
    "LatestConditions",
    "ResortWithLatestCondition",
]
