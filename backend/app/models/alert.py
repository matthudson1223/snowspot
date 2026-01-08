from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Alert(Base):
    """User alert configurations."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resort_id = Column(Integer, ForeignKey("resorts.id"), nullable=False, index=True)

    # Alert configuration
    alert_type = Column(String(50), nullable=False)  # 'powder', 'conditions', 'crowds'
    threshold_config = Column(JSONB)  # e.g., {"snowfall_min_inches": 6}

    # Delivery
    delivery_method = Column(
        String(20), default="email"
    )  # 'email', 'push', 'sms'
    is_active = Column(Boolean, default=True, index=True)

    # Tracking
    last_triggered_at = Column(TIMESTAMP(timezone=True))
    trigger_count = Column(Integer, default=0)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="alerts")
    resort = relationship("Resort", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, user_id={self.user_id}, resort_id={self.resort_id}, type='{self.alert_type}')>"
