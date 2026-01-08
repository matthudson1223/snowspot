"""
SQLAlchemy ORM models for SnowSpot.

All models are imported here for easy access and to ensure they are
registered with SQLAlchemy's Base metadata for Alembic migrations.
"""

from app.database import Base

from app.models.resort import Resort
from app.models.condition import Condition
from app.models.snotel import SnotelStation, SnotelReading
from app.models.forecast import WeatherForecast
from app.models.webcam import Webcam, WebcamSnapshot
from app.models.user import User
from app.models.alert import Alert
from app.models.monitoring import ScraperRun, DataQualityCheck

__all__ = [
    "Base",
    "Resort",
    "Condition",
    "SnotelStation",
    "SnotelReading",
    "WeatherForecast",
    "Webcam",
    "WebcamSnapshot",
    "User",
    "Alert",
    "ScraperRun",
    "DataQualityCheck",
]
