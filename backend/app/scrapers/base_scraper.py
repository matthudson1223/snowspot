"""
Base scraper class with retry logic and User-Agent rotation.

Provides foundational functionality for all resort scrapers including:
- Tenacity-based retry with exponential backoff
- User-Agent rotation to avoid blocking
- Scraper run tracking for monitoring
- Condition data persistence
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import random

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.database import SessionLocal

logger = logging.getLogger(__name__)


# User-Agent rotation pool - common browsers to avoid detection
USER_AGENTS: List[str] = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Linux
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def get_random_user_agent() -> str:
    """Return a random User-Agent string from the pool."""
    return random.choice(USER_AGENTS)


class BaseScraper(ABC):
    """
    Base class for all resort scrapers.

    Provides:
    - HTTP client with User-Agent rotation
    - Tenacity retry logic with exponential backoff
    - Scraper run tracking for monitoring
    - Condition data persistence to database

    Subclasses must implement the `scrape()` method.
    """

    # Default request timeout in seconds
    DEFAULT_TIMEOUT = 30.0

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_MIN_WAIT = 2  # seconds
    RETRY_MAX_WAIT = 10  # seconds

    def __init__(self, resort_id: int, resort_name: str):
        """
        Initialize the scraper.

        Args:
            resort_id: Database ID of the resort
            resort_name: Human-readable resort name for logging
        """
        self.resort_id = resort_id
        self.resort_name = resort_name
        self.db: Optional[Session] = None
        self.run_id: Optional[int] = None

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with a random User-Agent.

        Returns:
            Dict of HTTP headers
        """
        return {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _create_client(self) -> httpx.AsyncClient:
        """
        Create an async HTTP client with default configuration.

        Returns:
            Configured httpx.AsyncClient
        """
        return httpx.AsyncClient(
            timeout=self.DEFAULT_TIMEOUT,
            headers=self._get_headers(),
            follow_redirects=True,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _fetch_url(self, url: str) -> httpx.Response:
        """
        Fetch a URL with retry logic and User-Agent rotation.

        Uses tenacity for retry with:
        - Max 3 attempts
        - Exponential backoff (2s, 4s, 8s)
        - Retries on HTTP errors and timeouts
        - Fresh User-Agent on each attempt

        Args:
            url: The URL to fetch

        Returns:
            httpx.Response object

        Raises:
            httpx.HTTPError: After all retries exhausted
        """
        async with self._create_client() as client:
            logger.debug(f"Fetching URL: {url}")
            response = await client.get(url)
            response.raise_for_status()
            return response

    @abstractmethod
    async def scrape(self) -> Dict[str, Any]:
        """
        Scrape data from the resort's source.

        Must be implemented by subclasses.

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
                'precipitation_in': float | None,
                'humidity_percent': int | None,
                'visibility_miles': float | None,
                'lifts_open': int | None,
                'lifts_total': int | None,
                'runs_open': int | None,
                'runs_total': int | None,
                'terrain_parks_open': int | None,
                'snow_quality_score': float | None,
                'skiability_index': float | None,
                'crowd_level': int | None,
                'confidence': float (0-1),
            }
        """
        pass

    def start_run(self) -> None:
        """Record scraper execution start in the database."""
        self.db = SessionLocal()
        try:
            result = self.db.execute(
                text("""
                    INSERT INTO scraper_runs (scraper_name, resort_id, started_at, status)
                    VALUES (:name, :resort_id, :started, 'running')
                    RETURNING id
                """),
                {
                    "name": self.__class__.__name__,
                    "resort_id": self.resort_id,
                    "started": datetime.utcnow(),
                },
            )
            self.run_id = result.fetchone()[0]
            self.db.commit()
            logger.debug(f"Started scraper run {self.run_id} for {self.resort_name}")
        except Exception as e:
            logger.error(f"Failed to start scraper run: {e}")
            if self.db:
                self.db.rollback()

    def end_run(
        self, status: str, records: int = 0, error: Optional[str] = None
    ) -> None:
        """
        Record scraper execution end in the database.

        Args:
            status: Final status ('success', 'failure', 'no_data', 'partial')
            records: Number of records collected
            error: Error message if applicable
        """
        if not self.db or not self.run_id:
            return

        try:
            self.db.execute(
                text("""
                    UPDATE scraper_runs
                    SET completed_at = :completed,
                        status = :status,
                        records_collected = :records,
                        error_message = :error,
                        duration_seconds = EXTRACT(EPOCH FROM (:completed - started_at))
                    WHERE id = :run_id
                """),
                {
                    "run_id": self.run_id,
                    "completed": datetime.utcnow(),
                    "status": status,
                    "records": records,
                    "error": error,
                },
            )
            self.db.commit()
            logger.debug(f"Ended scraper run {self.run_id} with status: {status}")
        except Exception as e:
            logger.error(f"Failed to end scraper run: {e}")
            if self.db:
                self.db.rollback()
        finally:
            if self.db:
                self.db.close()
                self.db = None

    async def run(self) -> Dict[str, Any]:
        """
        Execute the scraper with error handling and monitoring.

        Orchestrates the full scraping workflow:
        1. Record run start
        2. Execute scrape()
        3. Save conditions if data returned
        4. Record run end with status

        Returns:
            Dict of scraped condition data, or empty dict on failure
        """
        self.start_run()

        try:
            logger.info(f"Starting scraper for {self.resort_name}")
            data = await self.scrape()

            if data:
                await self.save_conditions(data)
                self.end_run(status="success", records=1)
                logger.info(f"Successfully scraped {self.resort_name}")
                return data
            else:
                self.end_run(status="no_data")
                logger.warning(f"No data retrieved for {self.resort_name}")
                return {}

        except Exception as e:
            self.end_run(status="failure", error=str(e))
            logger.error(
                f"Scraper failed for {self.resort_name}: {e}", exc_info=True
            )
            raise

    async def save_conditions(self, data: Dict[str, Any]) -> None:
        """
        Save scraped condition data to the database.

        Args:
            data: Dict of condition data matching the conditions table schema
        """
        if not self.db:
            self.db = SessionLocal()

        try:
            self.db.execute(
                text("""
                    INSERT INTO conditions (
                        time, resort_id,
                        base_depth_in, summit_depth_in,
                        new_snow_24h_in, new_snow_48h_in, new_snow_7d_in,
                        temperature_f, wind_speed_mph, wind_direction,
                        precipitation_in, humidity_percent, visibility_miles,
                        lifts_open, lifts_total, runs_open, runs_total,
                        terrain_parks_open, snow_quality_score, skiability_index,
                        crowd_level, data_sources, confidence_score
                    )
                    VALUES (
                        :time, :resort_id,
                        :base_depth_in, :summit_depth_in,
                        :new_snow_24h_in, :new_snow_48h_in, :new_snow_7d_in,
                        :temperature_f, :wind_speed_mph, :wind_direction,
                        :precipitation_in, :humidity_percent, :visibility_miles,
                        :lifts_open, :lifts_total, :runs_open, :runs_total,
                        :terrain_parks_open, :snow_quality_score, :skiability_index,
                        :crowd_level, :data_sources, :confidence_score
                    )
                """),
                {
                    "time": datetime.utcnow(),
                    "resort_id": self.resort_id,
                    "base_depth_in": data.get("base_depth_in"),
                    "summit_depth_in": data.get("summit_depth_in"),
                    "new_snow_24h_in": data.get("new_snow_24h_in"),
                    "new_snow_48h_in": data.get("new_snow_48h_in"),
                    "new_snow_7d_in": data.get("new_snow_7d_in"),
                    "temperature_f": data.get("temperature_f"),
                    "wind_speed_mph": data.get("wind_speed_mph"),
                    "wind_direction": data.get("wind_direction"),
                    "precipitation_in": data.get("precipitation_in"),
                    "humidity_percent": data.get("humidity_percent"),
                    "visibility_miles": data.get("visibility_miles"),
                    "lifts_open": data.get("lifts_open"),
                    "lifts_total": data.get("lifts_total"),
                    "runs_open": data.get("runs_open"),
                    "runs_total": data.get("runs_total"),
                    "terrain_parks_open": data.get("terrain_parks_open"),
                    "snow_quality_score": data.get("snow_quality_score"),
                    "skiability_index": data.get("skiability_index"),
                    "crowd_level": data.get("crowd_level"),
                    "data_sources": {"scraper": self.__class__.__name__},
                    "confidence_score": data.get("confidence", 0.8),
                },
            )
            self.db.commit()
            logger.debug(f"Saved conditions for {self.resort_name}")

        except Exception as e:
            logger.error(f"Failed to save conditions: {e}")
            if self.db:
                self.db.rollback()
            raise
