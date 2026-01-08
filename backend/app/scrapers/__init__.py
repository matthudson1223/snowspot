"""
SnowSpot data scrapers package.

This package contains the base scraper class and resort-specific
scraper implementations for collecting ski resort conditions data.
"""

from app.scrapers.base_scraper import (
    BaseScraper,
    USER_AGENTS,
    get_random_user_agent,
)

__all__ = [
    "BaseScraper",
    "USER_AGENTS",
    "get_random_user_agent",
]
