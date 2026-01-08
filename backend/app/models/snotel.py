from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func

from app.database import Base


class SnotelStation(Base):
    """SNOTEL weather station metadata."""

    __tablename__ = "snotel_stations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    elevation_ft = Column(Integer)
    state = Column(String(50))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SnotelStation(station_id='{self.station_id}', name='{self.name}')>"


class SnotelReading(Base):
    """
    SNOTEL station readings time-series data.

    This table is designed to be a TimescaleDB hypertable for efficient
    time-series queries.
    """

    __tablename__ = "snotel_readings"

    time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    station_id = Column(String(50), primary_key=True, nullable=False)

    # Measurements
    snow_depth_in = Column(DECIMAL(6, 2))
    snow_water_equivalent_in = Column(DECIMAL(6, 2))  # SWE
    temperature_f = Column(DECIMAL(5, 2))
    precipitation_in = Column(DECIMAL(6, 3))

    def __repr__(self):
        return f"<SnotelReading(station_id='{self.station_id}', time='{self.time}')>"
