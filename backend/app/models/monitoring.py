from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DECIMAL,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ScraperRun(Base):
    """Scraper execution tracking for monitoring and debugging."""

    __tablename__ = "scraper_runs"

    id = Column(Integer, primary_key=True, index=True)
    scraper_name = Column(String(100), nullable=False, index=True)
    resort_id = Column(Integer, ForeignKey("resorts.id"))

    # Execution info
    started_at = Column(TIMESTAMP(timezone=True), nullable=False)
    completed_at = Column(TIMESTAMP(timezone=True))
    duration_seconds = Column(DECIMAL(10, 3))

    # Results
    status = Column(
        String(20), nullable=False, index=True
    )  # 'success', 'failure', 'partial'
    records_collected = Column(Integer, default=0)
    error_message = Column(Text)
    error_details = Column(JSONB)

    # Metadata
    version = Column(String(20))

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    resort = relationship("Resort", back_populates="scraper_runs")

    def __repr__(self):
        return f"<ScraperRun(id={self.id}, scraper='{self.scraper_name}', status='{self.status}')>"


class DataQualityCheck(Base):
    """Data quality check results for monitoring data integrity."""

    __tablename__ = "data_quality_checks"

    id = Column(Integer, primary_key=True, index=True)
    check_name = Column(String(100), nullable=False)
    resort_id = Column(Integer, ForeignKey("resorts.id"))

    # Check results
    executed_at = Column(TIMESTAMP(timezone=True), nullable=False)
    passed = Column(Boolean, nullable=False)
    issue_description = Column(Text)
    severity = Column(String(20))  # 'info', 'warning', 'error', 'critical'

    # Context
    affected_records = Column(Integer)
    check_metadata = Column(JSONB)

    # Relationships
    resort = relationship("Resort", back_populates="data_quality_checks")

    def __repr__(self):
        return f"<DataQualityCheck(id={self.id}, check='{self.check_name}', passed={self.passed})>"
