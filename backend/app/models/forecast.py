from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class WeatherForecast(Base):
    """Weather forecast data for resorts."""

    __tablename__ = "weather_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    resort_id = Column(Integer, ForeignKey("resorts.id"), nullable=False)

    # When forecast was generated and for when
    generated_at = Column(TIMESTAMP(timezone=True), nullable=False)
    forecast_for = Column(TIMESTAMP(timezone=True), nullable=False)

    # Predictions
    temperature_high_f = Column(DECIMAL(5, 2))
    temperature_low_f = Column(DECIMAL(5, 2))
    predicted_snowfall_in = Column(DECIMAL(6, 2))
    wind_speed_mph = Column(DECIMAL(5, 2))
    precipitation_prob_percent = Column(Integer)

    # Metadata
    source = Column(String(50))  # 'noaa', 'openweather', etc.
    model = Column(String(50))  # 'GFS', 'NAM', etc.
    confidence = Column(DECIMAL(4, 3))

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    resort = relationship("Resort", back_populates="forecasts")

    __table_args__ = (
        UniqueConstraint(
            "resort_id",
            "forecast_for",
            "generated_at",
            "source",
            name="uq_forecast_resort_time_source",
        ),
    )

    def __repr__(self):
        return f"<WeatherForecast(resort_id={self.resort_id}, forecast_for='{self.forecast_for}')>"
