from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Webcam(Base):
    """Webcam metadata for resorts."""

    __tablename__ = "webcams"

    id = Column(Integer, primary_key=True, index=True)
    resort_id = Column(Integer, ForeignKey("resorts.id"), nullable=False)
    name = Column(String(255))
    url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    position = Column(String(50))  # 'base', 'mid-mountain', 'summit'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    resort = relationship("Resort", back_populates="webcams")
    snapshots = relationship("WebcamSnapshot", back_populates="webcam")

    def __repr__(self):
        return f"<Webcam(id={self.id}, name='{self.name}')>"


class WebcamSnapshot(Base):
    """Webcam snapshot records."""

    __tablename__ = "webcam_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    webcam_id = Column(Integer, ForeignKey("webcams.id"), nullable=False)
    captured_at = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    image_url = Column(String(500))  # S3 or local path

    # Basic analysis (manual for MVP, CV in Phase 2)
    visibility_rating = Column(Integer)  # 1-5
    snow_visible = Column(Boolean)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    webcam = relationship("Webcam", back_populates="snapshots")

    def __repr__(self):
        return f"<WebcamSnapshot(webcam_id={self.webcam_id}, captured_at='{self.captured_at}')>"
