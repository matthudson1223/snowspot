"""
Generic HTML scraper for configuration-driven resort scraping.

Uses CSS selectors and optional regex patterns to extract condition values
from arbitrary resort webpages without needing custom scraper code.
"""

import logging
import re
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup

from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class GenericHTMLScraper(BaseScraper):
    """
    Generic configuration-driven scraper for resort conditions.

    Config format:
    {
        "url": "https://www.resort.com/conditions",
        "selectors": {
            "base_depth_in": {
                "selector": ".snow-report .base-value",
                "regex": "(\\d+)"
            },
            "temperature_f": {
                "selector": "#current-temp",
                "regex": "(-?\\d+)"
            }
        }
    }
    """

    CONDITION_KEYS = [
        "base_depth_in",
        "summit_depth_in",
        "new_snow_24h_in",
        "new_snow_48h_in",
        "new_snow_7d_in",
        "temperature_f",
        "wind_speed_mph",
        "wind_direction",
        "precipitation_in",
        "humidity_percent",
        "visibility_miles",
        "lifts_open",
        "lifts_total",
        "runs_open",
        "runs_total",
        "terrain_parks_open",
        "snow_quality_score",
        "skiability_index",
        "crowd_level",
        "confidence",
    ]

    FLOAT_KEYS = {
        "base_depth_in",
        "summit_depth_in",
        "new_snow_24h_in",
        "new_snow_48h_in",
        "new_snow_7d_in",
        "temperature_f",
        "wind_speed_mph",
        "precipitation_in",
        "visibility_miles",
        "snow_quality_score",
        "skiability_index",
        "confidence",
    }

    INT_KEYS = {
        "wind_direction",
        "humidity_percent",
        "lifts_open",
        "lifts_total",
        "runs_open",
        "runs_total",
        "terrain_parks_open",
        "crowd_level",
    }

    def __init__(self, resort_id: int, resort_name: str, config: Dict[str, Any]):
        super().__init__(resort_id, resort_name)
        self.config = config

    async def scrape(self) -> Dict[str, Any]:
        """
        Scrape resort conditions based on provided configuration.

        Returns:
            Dict with condition data matching the conditions table schema.
        """
        url = self.config.get("url")
        if not url:
            logger.warning("GenericHTMLScraper missing url in config for %s", self.resort_name)
            return {}

        response = await self._fetch_url(url)
        soup = BeautifulSoup(response.text, "lxml")

        selectors = self.config.get("selectors", {})
        data: Dict[str, Any] = {}

        for key in self.CONDITION_KEYS:
            if key not in selectors:
                continue
            try:
                value = self._extract_value(key, selectors.get(key), soup)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Error extracting %s for %s: %s", key, self.resort_name, exc)
                value = None
            data[key] = value

        return {k: v for k, v in data.items() if v is not None}

    def _extract_value(
        self, key: str, selector_config: Any, soup: BeautifulSoup
    ) -> Optional[Any]:
        selector, pattern = self._normalize_selector_config(selector_config)
        if not selector:
            return None

        element = soup.select_one(selector)
        if not element:
            return None

        text = element.get_text(separator=" ", strip=True)
        if not text:
            return None

        raw_value = text
        if pattern:
            match = re.search(pattern, text)
            if not match:
                return None
            raw_value = match.group(1) if match.groups() else match.group(0)

        numeric_text = self._extract_numeric(raw_value)
        if numeric_text is None:
            return None

        return self._cast_value(key, numeric_text)

    @staticmethod
    def _normalize_selector_config(selector_config: Any) -> tuple[Optional[str], Optional[str]]:
        if isinstance(selector_config, str):
            return selector_config, None
        if isinstance(selector_config, dict):
            return selector_config.get("selector"), selector_config.get("regex")
        return None, None

    @staticmethod
    def _extract_numeric(value: str) -> Optional[str]:
        if value is None:
            return None
        match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if not match:
            return None
        return match.group(0)

    def _cast_value(self, key: str, value: str) -> Optional[Any]:
        if key in self.FLOAT_KEYS:
            try:
                return float(value)
            except ValueError:
                return None
        if key in self.INT_KEYS:
            try:
                return int(float(value))
            except ValueError:
                return None
        return value
