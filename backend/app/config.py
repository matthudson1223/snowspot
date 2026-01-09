from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "SnowSpot"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    api_version: str = "v1"

    # Database
    database_url: str = "postgresql://snowspot:snowspot@localhost:5432/snowspot"
    database_pool_size: int = 20
    database_max_overflow: int = 0

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # API Keys
    openweather_api_key: Optional[str] = None
    mapbox_api_key: Optional[str] = None

    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: str = "noreply@snowspot.com"

    # Storage
    storage_type: str = "local"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket_name: Optional[str] = None
    s3_region: str = "us-west-2"

    # Monitoring
    sentry_dsn: Optional[str] = None

    # CORS - can be comma-separated or wildcard
    cors_origins: str = "*"

    # Rate Limiting
    api_rate_limit: int = 100  # per minute

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from string (comma-separated or wildcard)."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
