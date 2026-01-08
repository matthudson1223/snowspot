"""
Jackson Hole Mountain Resort scraper.

Scrapes current conditions from the official Jackson Hole website
and returns data matching the conditions table schema.
"""

import re
import logging
from typing import Dict, Any, Optional

from bs4 import BeautifulSoup

from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class JacksonHoleScraper(BaseScraper):
    """
    Scraper for Jackson Hole Mountain Resort.

    Extracts snow conditions, weather data, and lift/run status
    from the official Jackson Hole conditions page.
    """

    BASE_URL = "https://www.jacksonhole.com/conditions"

    # Known resort totals (updated periodically)
    TOTAL_LIFTS = 13
    TOTAL_RUNS = 133
    TOTAL_TERRAIN_PARKS = 2

    async def scrape(self) -> Dict[str, Any]:
        """
        Scrape Jackson Hole conditions.

        Returns:
            Dict with condition data matching the conditions table schema:
            {
                'base_depth_in': float | None,
                'summit_depth_in': float | None,
                'new_snow_24h_in': float | None,
                'new_snow_48h_in': float | None,
                'new_snow_7d_in': float | None,
                'temperature_f': float | None,
                'wind_speed_mph': float | None,
                'wind_direction': int | None,
                'humidity_percent': int | None,
                'lifts_open': int | None,
                'lifts_total': int,
                'runs_open': int | None,
                'runs_total': int,
                'terrain_parks_open': int | None,
                'confidence': float,
            }
        """
        response = await self._fetch_url(self.BASE_URL)
        soup = BeautifulSoup(response.text, "lxml")

        data = {
            # Snow measurements
            "base_depth_in": self._extract_base_depth(soup),
            "summit_depth_in": self._extract_summit_depth(soup),
            "new_snow_24h_in": self._extract_snowfall(soup, hours=24),
            "new_snow_48h_in": self._extract_snowfall(soup, hours=48),
            "new_snow_7d_in": self._extract_snowfall(soup, hours=168),
            # Weather conditions
            "temperature_f": self._extract_temperature(soup),
            "wind_speed_mph": self._extract_wind_speed(soup),
            "wind_direction": self._extract_wind_direction(soup),
            "humidity_percent": self._extract_humidity(soup),
            # Resort operations
            "lifts_open": self._extract_lifts_open(soup),
            "lifts_total": self.TOTAL_LIFTS,
            "runs_open": self._extract_runs_open(soup),
            "runs_total": self.TOTAL_RUNS,
            "terrain_parks_open": self._extract_terrain_parks(soup),
            # High confidence for official source
            "confidence": 0.9,
        }

        # Remove None values for cleaner data
        return {k: v for k, v in data.items() if v is not None}

    def _extract_base_depth(self, soup: BeautifulSoup) -> Optional[float]:
        """
        Extract base depth from the page.

        Args:
            soup: Parsed HTML document

        Returns:
            Base depth in inches, or None if not found
        """
        try:
            # Look for element containing base depth
            depth_element = soup.find(string=re.compile(r"Base\s*Depth", re.I))
            if depth_element:
                parent = depth_element.find_parent()
                if parent:
                    text = parent.get_text()
                    # Match patterns like "62"" or "62 inches"
                    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:"|in|inches)', text, re.I)
                    if match:
                        return float(match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting base depth: {e}")
        return None

    def _extract_summit_depth(self, soup: BeautifulSoup) -> Optional[float]:
        """
        Extract summit snow depth from the page.

        Args:
            soup: Parsed HTML document

        Returns:
            Summit depth in inches, or None if not found
        """
        try:
            # Look for summit/top depth
            depth_element = soup.find(
                string=re.compile(r"Summit\s*Depth|Top\s*Depth", re.I)
            )
            if depth_element:
                parent = depth_element.find_parent()
                if parent:
                    text = parent.get_text()
                    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:"|in|inches)', text, re.I)
                    if match:
                        return float(match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting summit depth: {e}")
        return None

    def _extract_snowfall(
        self, soup: BeautifulSoup, hours: int
    ) -> Optional[float]:
        """
        Extract snowfall for the given time period.

        Args:
            soup: Parsed HTML document
            hours: Time period in hours (24, 48, or 168 for 7 days)

        Returns:
            Snowfall in inches, or None if not found
        """
        try:
            # Build regex pattern based on hours
            if hours == 24:
                pattern = r"24\s*(?:hr|hour|h)\s*(?:snow|snowfall)?"
            elif hours == 48:
                pattern = r"48\s*(?:hr|hour|h)\s*(?:snow|snowfall)?"
            elif hours == 168:
                pattern = r"(?:7\s*day|week|168\s*hr)"
            else:
                return None

            element = soup.find(string=re.compile(pattern, re.I))
            if element:
                parent = element.find_parent()
                if parent:
                    text = parent.get_text()
                    match = re.search(
                        r'(\d+(?:\.\d+)?)\s*(?:"|in|inches)', text, re.I
                    )
                    if match:
                        return float(match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting snowfall ({hours}h): {e}")
        return None

    def _extract_temperature(self, soup: BeautifulSoup) -> Optional[float]:
        """
        Extract current temperature from the page.

        Args:
            soup: Parsed HTML document

        Returns:
            Temperature in Fahrenheit, or None if not found
        """
        try:
            temp_element = soup.find(string=re.compile(r"Temperature|Temp|Current", re.I))
            if temp_element:
                parent = temp_element.find_parent()
                if parent:
                    text = parent.get_text()
                    # Match patterns like "-5°F" or "20 F"
                    match = re.search(r"(-?\d+(?:\.\d+)?)\s*°?\s*F", text, re.I)
                    if match:
                        return float(match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting temperature: {e}")
        return None

    def _extract_wind_speed(self, soup: BeautifulSoup) -> Optional[float]:
        """
        Extract wind speed from the page.

        Args:
            soup: Parsed HTML document

        Returns:
            Wind speed in MPH, or None if not found
        """
        try:
            wind_element = soup.find(string=re.compile(r"Wind\s*Speed|Wind", re.I))
            if wind_element:
                parent = wind_element.find_parent()
                if parent:
                    text = parent.get_text()
                    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:mph|mi/?h)", text, re.I)
                    if match:
                        return float(match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting wind speed: {e}")
        return None

    def _extract_wind_direction(self, soup: BeautifulSoup) -> Optional[int]:
        """
        Extract wind direction from the page.

        Args:
            soup: Parsed HTML document

        Returns:
            Wind direction in degrees (0-360), or None if not found
        """
        # Mapping of cardinal directions to degrees
        direction_map = {
            "N": 0,
            "NNE": 22,
            "NE": 45,
            "ENE": 67,
            "E": 90,
            "ESE": 112,
            "SE": 135,
            "SSE": 157,
            "S": 180,
            "SSW": 202,
            "SW": 225,
            "WSW": 247,
            "W": 270,
            "WNW": 292,
            "NW": 315,
            "NNW": 337,
        }

        try:
            wind_element = soup.find(string=re.compile(r"Wind", re.I))
            if wind_element:
                parent = wind_element.find_parent()
                if parent:
                    text = parent.get_text().upper()
                    # Check for cardinal directions
                    for direction, degrees in direction_map.items():
                        if re.search(rf"\b{direction}\b", text):
                            return degrees
        except Exception as e:
            logger.warning(f"Error extracting wind direction: {e}")
        return None

    def _extract_humidity(self, soup: BeautifulSoup) -> Optional[int]:
        """
        Extract humidity percentage from the page.

        Args:
            soup: Parsed HTML document

        Returns:
            Humidity percentage (0-100), or None if not found
        """
        try:
            humidity_element = soup.find(string=re.compile(r"Humidity", re.I))
            if humidity_element:
                parent = humidity_element.find_parent()
                if parent:
                    text = parent.get_text()
                    match = re.search(r"(\d+)\s*%", text)
                    if match:
                        return int(match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting humidity: {e}")
        return None

    def _extract_lifts_open(self, soup: BeautifulSoup) -> Optional[int]:
        """
        Extract number of open lifts from the page.

        Args:
            soup: Parsed HTML document

        Returns:
            Number of open lifts, or None if not found
        """
        try:
            lifts_element = soup.find(string=re.compile(r"Lifts?\s*Open", re.I))
            if lifts_element:
                parent = lifts_element.find_parent()
                if parent:
                    text = parent.get_text()
                    # Match patterns like "10 of 13" or "10/13"
                    match = re.search(r"(\d+)\s*(?:of|/)\s*\d+", text)
                    if match:
                        return int(match.group(1))
                    # Or just a number
                    match = re.search(r"(\d+)", text)
                    if match:
                        return int(match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting lifts open: {e}")
        return None

    def _extract_runs_open(self, soup: BeautifulSoup) -> Optional[int]:
        """
        Extract number of open runs/trails from the page.

        Args:
            soup: Parsed HTML document

        Returns:
            Number of open runs, or None if not found
        """
        try:
            runs_element = soup.find(
                string=re.compile(r"(?:Runs?|Trails?)\s*Open", re.I)
            )
            if runs_element:
                parent = runs_element.find_parent()
                if parent:
                    text = parent.get_text()
                    match = re.search(r"(\d+)\s*(?:of|/)\s*\d+", text)
                    if match:
                        return int(match.group(1))
                    match = re.search(r"(\d+)", text)
                    if match:
                        return int(match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting runs open: {e}")
        return None

    def _extract_terrain_parks(self, soup: BeautifulSoup) -> Optional[int]:
        """
        Extract number of open terrain parks from the page.

        Args:
            soup: Parsed HTML document

        Returns:
            Number of open terrain parks, or None if not found
        """
        try:
            parks_element = soup.find(
                string=re.compile(r"Terrain\s*Park|Park", re.I)
            )
            if parks_element:
                parent = parks_element.find_parent()
                if parent:
                    text = parent.get_text()
                    match = re.search(r"(\d+)\s*(?:of|/|open)", text, re.I)
                    if match:
                        return int(match.group(1))
        except Exception as e:
            logger.warning(f"Error extracting terrain parks: {e}")
        return None
