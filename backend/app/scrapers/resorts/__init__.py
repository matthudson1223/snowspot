"""
Resort-specific scrapers package.

Contains individual scraper implementations for each supported ski resort.
"""

from app.scrapers.resorts.jackson_hole import JacksonHoleScraper

__all__ = [
    "JacksonHoleScraper",
]
