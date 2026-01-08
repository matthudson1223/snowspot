"""
Standardized API response schemas.

All API responses are wrapped in a standard envelope to provide
consistent structure for success and error cases.
"""

from datetime import datetime
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

# Generic type for response data
T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


class ResponseMeta(BaseModel):
    """Metadata for API responses."""

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp (UTC)",
    )
    pagination: Optional[PaginationMeta] = Field(
        None, description="Pagination info for list responses"
    )
    request_id: Optional[str] = Field(
        None, description="Request ID for tracing"
    )


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    details: Optional[dict[str, Any]] = Field(
        None, description="Additional error context"
    )


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper for successful responses.

    All successful API responses follow this structure:
    {
        "success": true,
        "data": <response data>,
        "message": "optional success message",
        "meta": {
            "timestamp": "2026-01-08T12:00:00Z",
            "pagination": {...}  // if applicable
        }
    }
    """

    success: bool = Field(True, description="Whether the request succeeded")
    data: T = Field(..., description="Response data payload")
    message: Optional[str] = Field(None, description="Optional success message")
    meta: ResponseMeta = Field(
        default_factory=ResponseMeta,
        description="Response metadata",
    )

    class Config:
        from_attributes = True


class APIErrorResponse(BaseModel):
    """
    Standard API response wrapper for error responses.

    All error responses follow this structure:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human-readable message",
            "field": "optional field name",
            "details": {}
        },
        "meta": {
            "timestamp": "2026-01-08T12:00:00Z"
        }
    }
    """

    success: bool = Field(False, description="Always false for errors")
    error: ErrorDetail = Field(..., description="Error information")
    meta: ResponseMeta = Field(
        default_factory=ResponseMeta,
        description="Response metadata",
    )


# Common error codes
class ErrorCodes:
    """Standard error codes for API responses."""

    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMITED = "RATE_LIMITED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


def create_success_response(
    data: T,
    message: Optional[str] = None,
    pagination: Optional[PaginationMeta] = None,
) -> dict:
    """
    Helper function to create a success response dict.

    Args:
        data: Response data payload
        message: Optional success message
        pagination: Optional pagination metadata

    Returns:
        Dictionary conforming to APIResponse structure
    """
    meta = ResponseMeta(pagination=pagination)
    return {
        "success": True,
        "data": data,
        "message": message,
        "meta": meta.model_dump(),
    }


def create_error_response(
    code: str,
    message: str,
    field: Optional[str] = None,
    details: Optional[dict] = None,
) -> dict:
    """
    Helper function to create an error response dict.

    Args:
        code: Error code from ErrorCodes
        message: Human-readable error message
        field: Optional field that caused the error
        details: Optional additional error context

    Returns:
        Dictionary conforming to APIErrorResponse structure
    """
    error = ErrorDetail(code=code, message=message, field=field, details=details)
    meta = ResponseMeta()
    return {
        "success": False,
        "error": error.model_dump(exclude_none=True),
        "meta": meta.model_dump(),
    }


def create_pagination_meta(
    total: int,
    page: int,
    page_size: int,
) -> PaginationMeta:
    """
    Helper function to create pagination metadata.

    Args:
        total: Total number of items
        page: Current page number (1-indexed)
        page_size: Number of items per page

    Returns:
        PaginationMeta instance
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
