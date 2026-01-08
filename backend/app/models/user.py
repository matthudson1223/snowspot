from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ARRAY,
    TIMESTAMP,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """User accounts for alerts and preferences."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))  # bcrypt
    name = Column(String(255))

    # Preferences
    favorite_resort_ids = Column(ARRAY(Integer))
    timezone = Column(String(50), default="America/Denver")

    # Status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_login = Column(TIMESTAMP(timezone=True))

    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
