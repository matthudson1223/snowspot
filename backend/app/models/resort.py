from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DECIMAL,
    ARRAY,
    Text,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Resort(Base):
    """Ski resort master table."""

    __tablename__ = "resorts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    # Location
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    timezone = Column(String(50), nullable=False, default="America/Denver")
    region = Column(String(100))
    state = Column(String(50), index=True)
    country = Column(String(50), default="USA")

    # Resort stats
    base_elevation_ft = Column(Integer)
    summit_elevation_ft = Column(Integer)
    vertical_drop_ft = Column(Integer)
    total_lifts = Column(Integer)
    total_runs = Column(Integer)
    total_acres = Column(Integer)

    # Data source configuration
    official_url = Column(String(500))
    data_source_config = Column(JSONB)  # Scraping configs, API endpoints
    snotel_station_ids = Column(ARRAY(Text))  # Array of nearby SNOTEL IDs
    weather_station_id = Column(String(50))

    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    conditions = relationship("Condition", back_populates="resort")
    forecasts = relationship("WeatherForecast", back_populates="resort")
    webcams = relationship("Webcam", back_populates="resort")
    alerts = relationship("Alert", back_populates="resort")
    scraper_runs = relationship("ScraperRun", back_populates="resort")
    data_quality_checks = relationship("DataQualityCheck", back_populates="resort")

    def __repr__(self):
        return f"<Resort(id={self.id}, name='{self.name}', slug='{self.slug}')>"
