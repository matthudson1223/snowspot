"""
API routers for SnowSpot.

All routers use the standardized API response envelope for consistent
success and error response formatting.
"""

from app.routers import resorts, conditions

__all__ = [
    "resorts",
    "conditions",
]
