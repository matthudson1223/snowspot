from sqlalchemy import (
    Column,
    Integer,
    DECIMAL,
    TIMESTAMP,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class Condition(Base):
    """
    Current conditions time-series data.

    This table is designed to be a TimescaleDB hypertable for efficient
    time-series queries. The composite primary key (time, resort_id)
    enables efficient partitioning by time.
    """

    __tablename__ = "conditions"

    time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    resort_id = Column(
        Integer, ForeignKey("resorts.id"), primary_key=True, nullable=False
    )

    # Snow measurements (inches)
    base_depth_in = Column(DECIMAL(6, 2))
    summit_depth_in = Column(DECIMAL(6, 2))
    new_snow_24h_in = Column(DECIMAL(6, 2))
    new_snow_48h_in = Column(DECIMAL(6, 2))
    new_snow_7d_in = Column(DECIMAL(6, 2))

    # Weather conditions
    temperature_f = Column(DECIMAL(5, 2))
    wind_speed_mph = Column(DECIMAL(5, 2))
    wind_direction = Column(Integer)  # Degrees
    precipitation_in = Column(DECIMAL(6, 3))
    humidity_percent = Column(Integer)
    visibility_miles = Column(DECIMAL(5, 2))

    # Resort operations
    lifts_open = Column(Integer)
    lifts_total = Column(Integer)
    runs_open = Column(Integer)
    runs_total = Column(Integer)
    terrain_parks_open = Column(Integer)

    # Derived metrics
    snow_quality_score = Column(DECIMAL(5, 2))  # 0-100 calculated score
    skiability_index = Column(DECIMAL(5, 2))  # 0-100 overall skiability
    crowd_level = Column(Integer)  # 1-5 estimated crowds

    # Data provenance
    data_sources = Column(JSONB)  # Which sources contributed to this record
    confidence_score = Column(DECIMAL(4, 3))  # 0-1 how confident we are

    # Relationships
    resort = relationship("Resort", back_populates="conditions")

    __table_args__ = (
        CheckConstraint(
            "snow_quality_score >= 0 AND snow_quality_score <= 100",
            name="check_snow_quality_score_range",
        ),
        CheckConstraint(
            "skiability_index >= 0 AND skiability_index <= 100",
            name="check_skiability_index_range",
        ),
        CheckConstraint(
            "crowd_level >= 1 AND crowd_level <= 5", name="check_crowd_level_range"
        ),
    )

    def __repr__(self):
        return f"<Condition(resort_id={self.resort_id}, time='{self.time}')>"
