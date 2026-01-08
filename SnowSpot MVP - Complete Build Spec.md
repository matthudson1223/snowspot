# SnowSpot MVP - Complete Build Specification

**Version:** 1.0  
**Target Completion:** 12 weeks  
**Last Updated:** January 8, 2026

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technical Architecture](#technical-architecture)
3. [Prerequisites & Setup](#prerequisites--setup)
4. [Database Schema](#database-schema)
5. [Backend Implementation](#backend-implementation)
6. [Data Collection System](#data-collection-system)
7. [Frontend Implementation](#frontend-implementation)
8. [Deployment Guide](#deployment-guide)
9. [Testing Strategy](#testing-strategy)
10. [Appendix: Code Examples](#appendix-code-examples)

---

## Project Overview

### What We're Building

A fully automated snow conditions platform that provides real-time, accurate ski resort conditions by aggregating data from multiple sources including:
- Resort official reports (APIs/web scraping)
- SNOTEL weather stations (government data)
- Weather forecast APIs (NOAA, OpenWeather)
- Webcam snapshots with basic analysis

### MVP Features (Launch in 12 weeks)

**Core Functionality:**
- ✅ Real-time conditions for 50 ski resorts
- ✅ Automated data collection every 15 minutes
- ✅ Multi-source data fusion with confidence scores
- ✅ Snow quality scoring algorithm (0-100)
- ✅ 7-day weather forecasts
- ✅ Multi-resort comparison
- ✅ Email alerts for powder days
- ✅ Responsive web application
- ✅ Public read-only API

**Out of Scope for MVP:**
- ❌ Mobile apps (Phase 2)
- ❌ Machine learning predictions (Phase 2)
- ❌ Computer vision webcam analysis (Phase 2)
- ❌ User accounts/social features (Phase 2)
- ❌ Payment processing (Phase 2)

### Success Criteria
- 50 resorts with active data collection
- 95%+ uptime for data scrapers
- <30 minute average data freshness
- <2 second page load time
- 1,000 users by week 12

---

## Technical Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ Resort   │  │ SNOTEL   │  │ Weather  │  │ Webcams ││
│  │ APIs     │  │ Stations │  │ APIs     │  │         ││
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘│
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              DATA COLLECTION LAYER                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Celery Workers + Scrapers                       │   │
│  │  - Resort scrapers (BeautifulSoup/Selenium)      │   │
│  │  - SNOTEL API client                             │   │
│  │  - Weather API client                            │   │
│  │  - Scheduled every 15 minutes                    │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              DATA PROCESSING LAYER                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │  ETL Pipeline                                    │   │
│  │  - Data validation & cleaning                    │   │
│  │  - Multi-source fusion                           │   │
│  │  - Quality score calculation                     │   │
│  │  - Confidence scoring                            │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   STORAGE LAYER                          │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐     │
│  │ PostgreSQL │  │   Redis    │  │      S3      │     │
│  │ (TimescaleDB)│ (Cache/Queue)│ (Images/Logs)│     │
│  └────────────┘  └────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    API LAYER                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │  FastAPI Backend                                 │   │
│  │  - REST endpoints                                │   │
│  │  - WebSocket (optional MVP+)                     │   │
│  │  - JWT authentication (simple)                   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 FRONTEND LAYER                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  React + TypeScript                              │   │
│  │  - Dashboard                                     │   │
│  │  - Resort detail pages                           │   │
│  │  - Comparison tool                               │   │
│  │  - Alert management                              │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
```yaml
Language: Python 3.11+
Framework: FastAPI 0.104+
Database: PostgreSQL 16 with TimescaleDB extension
Cache: Redis 7+
Task Queue: Celery 5+ with Redis broker
Scraping: BeautifulSoup4, Selenium, Requests
Data Processing: Pandas, NumPy
API Clients: httpx (async)
```

**Frontend:**
```yaml
Framework: React 18+ with TypeScript
Build Tool: Vite
Styling: Tailwind CSS 3+
Charts: Recharts
Maps: Mapbox GL JS or Leaflet
State: React Query + Context API
HTTP Client: Axios
```

**Infrastructure:**
```yaml
Hosting: Railway / Render / DigitalOcean
CDN: Cloudflare
Storage: AWS S3 or Cloudflare R2
Monitoring: Sentry + UptimeRobot
Analytics: Plausible (privacy-friendly)
```

---

## Prerequisites & Setup

### Required Accounts & API Keys

1. **Cloud Hosting** (choose one):
   - Railway.app (recommended for MVP)
   - Render.com
   - DigitalOcean

2. **Database**:
   - Supabase (managed PostgreSQL, free tier)
   - OR self-hosted PostgreSQL + TimescaleDB

3. **APIs** (all have free tiers):
   - NOAA/NWS API (free, no key needed)
   - OpenWeatherMap (free tier: 1000 calls/day)
   - Mapbox (free tier: 50k map loads/month)

4. **Optional**:
   - Sentry (error tracking)
   - Cloudflare (CDN + DNS)

### Development Environment

```bash
# System Requirements
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+ (Docker recommended)
- Redis 7+
- Git

# Recommended Tools
- VS Code with Python + React extensions
- Postman or Insomnia (API testing)
- pgAdmin or DBeaver (database GUI)
- Docker Desktop (for local development)
```

### Local Setup Commands

```bash
# 1. Clone repository structure
mkdir snowspot && cd snowspot
mkdir -p backend frontend docs scripts

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend setup
cd ../frontend
npm install

# 4. Start services with Docker
docker-compose up -d  # PostgreSQL, Redis, TimescaleDB
```

---

## Database Schema

### Complete SQL Schema

```sql
-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS postgis;  -- For geospatial queries

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Resorts master table
CREATE TABLE resorts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    
    -- Location
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'America/Denver',
    region VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    
    -- Resort stats
    base_elevation_ft INTEGER,
    summit_elevation_ft INTEGER,
    vertical_drop_ft INTEGER,
    total_lifts INTEGER,
    total_runs INTEGER,
    total_acres INTEGER,
    
    -- Data source configuration
    official_url VARCHAR(500),
    data_source_config JSONB,  -- Scraping configs, API endpoints
    snotel_station_ids TEXT[],  -- Array of nearby SNOTEL IDs
    weather_station_id VARCHAR(50),
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_resorts_slug ON resorts(slug);
CREATE INDEX idx_resorts_state ON resorts(state);
CREATE INDEX idx_resorts_active ON resorts(is_active);

-- ============================================================================
-- TIME SERIES DATA (Using TimescaleDB)
-- ============================================================================

-- Current conditions (time-series optimized)
CREATE TABLE conditions (
    time TIMESTAMPTZ NOT NULL,
    resort_id INTEGER NOT NULL REFERENCES resorts(id),
    
    -- Snow measurements (inches)
    base_depth_in DECIMAL(6,2),
    summit_depth_in DECIMAL(6,2),
    new_snow_24h_in DECIMAL(6,2),
    new_snow_48h_in DECIMAL(6,2),
    new_snow_7d_in DECIMAL(6,2),
    
    -- Weather conditions
    temperature_f DECIMAL(5,2),
    wind_speed_mph DECIMAL(5,2),
    wind_direction INTEGER,  -- Degrees
    precipitation_in DECIMAL(6,3),
    humidity_percent INTEGER,
    visibility_miles DECIMAL(5,2),
    
    -- Resort operations
    lifts_open INTEGER,
    lifts_total INTEGER,
    runs_open INTEGER,
    runs_total INTEGER,
    terrain_parks_open INTEGER,
    
    -- Derived metrics
    snow_quality_score DECIMAL(5,2),  -- 0-100 calculated score
    skiability_index DECIMAL(5,2),    -- 0-100 overall skiability
    crowd_level INTEGER,              -- 1-5 estimated crowds
    
    -- Data provenance
    data_sources JSONB,  -- Which sources contributed to this record
    confidence_score DECIMAL(4,3),  -- 0-1 how confident we are
    
    -- Constraints
    PRIMARY KEY (time, resort_id),
    CHECK (snow_quality_score >= 0 AND snow_quality_score <= 100),
    CHECK (skiability_index >= 0 AND skiability_index <= 100),
    CHECK (crowd_level >= 1 AND crowd_level <= 5)
);

-- Convert to hypertable (TimescaleDB)
SELECT create_hypertable('conditions', 'time', 
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Indexes for common queries
CREATE INDEX idx_conditions_resort ON conditions(resort_id, time DESC);
CREATE INDEX idx_conditions_recent ON conditions(time DESC);

-- ============================================================================
-- SNOTEL DATA
-- ============================================================================

CREATE TABLE snotel_stations (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    elevation_ft INTEGER,
    state VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE snotel_readings (
    time TIMESTAMPTZ NOT NULL,
    station_id VARCHAR(50) NOT NULL,
    
    -- Measurements
    snow_depth_in DECIMAL(6,2),
    snow_water_equivalent_in DECIMAL(6,2),  -- SWE
    temperature_f DECIMAL(5,2),
    precipitation_in DECIMAL(6,3),
    
    PRIMARY KEY (time, station_id)
);

SELECT create_hypertable('snotel_readings', 'time',
    chunk_time_interval => INTERVAL '7 days',
    if_not_exists => TRUE
);

-- ============================================================================
-- WEATHER FORECASTS
-- ============================================================================

CREATE TABLE weather_forecasts (
    id SERIAL PRIMARY KEY,
    resort_id INTEGER NOT NULL REFERENCES resorts(id),
    
    -- When forecast was generated and for when
    generated_at TIMESTAMPTZ NOT NULL,
    forecast_for TIMESTAMPTZ NOT NULL,
    
    -- Predictions
    temperature_high_f DECIMAL(5,2),
    temperature_low_f DECIMAL(5,2),
    predicted_snowfall_in DECIMAL(6,2),
    wind_speed_mph DECIMAL(5,2),
    precipitation_prob_percent INTEGER,
    
    -- Metadata
    source VARCHAR(50),  -- 'noaa', 'openweather', etc.
    model VARCHAR(50),   -- 'GFS', 'NAM', etc.
    confidence DECIMAL(4,3),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(resort_id, forecast_for, generated_at, source)
);

CREATE INDEX idx_forecasts_resort_time ON weather_forecasts(resort_id, forecast_for);

-- ============================================================================
-- WEBCAM DATA
-- ============================================================================

CREATE TABLE webcams (
    id SERIAL PRIMARY KEY,
    resort_id INTEGER NOT NULL REFERENCES resorts(id),
    name VARCHAR(255),
    url VARCHAR(500) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    position VARCHAR(50),  -- 'base', 'mid-mountain', 'summit'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE webcam_snapshots (
    id SERIAL PRIMARY KEY,
    webcam_id INTEGER NOT NULL REFERENCES webcams(id),
    captured_at TIMESTAMPTZ NOT NULL,
    image_url VARCHAR(500),  -- S3 or local path
    
    -- Basic analysis (manual for MVP, CV in Phase 2)
    visibility_rating INTEGER,  -- 1-5
    snow_visible BOOLEAN,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_snapshots_webcam ON webcam_snapshots(webcam_id, captured_at DESC);

-- ============================================================================
-- USER & ALERTS (Simple for MVP)
-- ============================================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- bcrypt
    name VARCHAR(255),
    
    -- Preferences
    favorite_resort_ids INTEGER[],
    timezone VARCHAR(50) DEFAULT 'America/Denver',
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resort_id INTEGER NOT NULL REFERENCES resorts(id),
    
    -- Alert configuration
    alert_type VARCHAR(50) NOT NULL,  -- 'powder', 'conditions', 'crowds'
    threshold_config JSONB,  -- e.g., {"snowfall_min_inches": 6}
    
    -- Delivery
    delivery_method VARCHAR(20) DEFAULT 'email',  -- 'email', 'push', 'sms'
    is_active BOOLEAN DEFAULT true,
    
    -- Tracking
    last_triggered_at TIMESTAMPTZ,
    trigger_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_user ON alerts(user_id);
CREATE INDEX idx_alerts_resort ON alerts(resort_id);
CREATE INDEX idx_alerts_active ON alerts(is_active) WHERE is_active = true;

-- ============================================================================
-- DATA QUALITY & MONITORING
-- ============================================================================

CREATE TABLE scraper_runs (
    id SERIAL PRIMARY KEY,
    scraper_name VARCHAR(100) NOT NULL,
    resort_id INTEGER REFERENCES resorts(id),
    
    -- Execution info
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_seconds DECIMAL(10,3),
    
    -- Results
    status VARCHAR(20) NOT NULL,  -- 'success', 'failure', 'partial'
    records_collected INTEGER DEFAULT 0,
    error_message TEXT,
    error_details JSONB,
    
    -- Metadata
    version VARCHAR(20),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scraper_runs_name ON scraper_runs(scraper_name, started_at DESC);
CREATE INDEX idx_scraper_runs_status ON scraper_runs(status);

CREATE TABLE data_quality_checks (
    id SERIAL PRIMARY KEY,
    check_name VARCHAR(100) NOT NULL,
    resort_id INTEGER REFERENCES resorts(id),
    
    -- Check results
    executed_at TIMESTAMPTZ NOT NULL,
    passed BOOLEAN NOT NULL,
    issue_description TEXT,
    severity VARCHAR(20),  -- 'info', 'warning', 'error', 'critical'
    
    -- Context
    affected_records INTEGER,
    metadata JSONB
);

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

-- Latest conditions per resort (refresh every 15 min)
CREATE MATERIALIZED VIEW latest_conditions AS
SELECT DISTINCT ON (resort_id)
    resort_id,
    time,
    base_depth_in,
    summit_depth_in,
    new_snow_24h_in,
    new_snow_48h_in,
    new_snow_7d_in,
    temperature_f,
    wind_speed_mph,
    lifts_open,
    lifts_total,
    runs_open,
    runs_total,
    snow_quality_score,
    skiability_index,
    crowd_level,
    confidence_score
FROM conditions
ORDER BY resort_id, time DESC;

CREATE UNIQUE INDEX idx_latest_conditions_resort ON latest_conditions(resort_id);

-- Refresh function (called by Celery task)
CREATE OR REPLACE FUNCTION refresh_latest_conditions()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY latest_conditions;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Calculate snow quality score
CREATE OR REPLACE FUNCTION calculate_snow_quality(
    new_snow_24h DECIMAL,
    temperature DECIMAL,
    wind_speed DECIMAL,
    snow_age_days INTEGER
)
RETURNS DECIMAL AS $$
DECLARE
    score DECIMAL := 50.0;  -- Start at neutral
BEGIN
    -- More new snow = better (up to 20 points)
    IF new_snow_24h IS NOT NULL THEN
        score := score + LEAST(new_snow_24h * 2, 20);
    END IF;
    
    -- Temperature (ideal: 15-30°F)
    IF temperature IS NOT NULL THEN
        IF temperature BETWEEN 15 AND 30 THEN
            score := score + 15;
        ELSIF temperature BETWEEN 10 AND 35 THEN
            score := score + 10;
        ELSE
            score := score + 5;
        END IF;
    END IF;
    
    -- Wind penalty (high wind = worse)
    IF wind_speed IS NOT NULL THEN
        IF wind_speed < 10 THEN
            score := score + 10;
        ELSIF wind_speed > 25 THEN
            score := score - 10;
        END IF;
    END IF;
    
    -- Age penalty (older snow = worse)
    IF snow_age_days IS NOT NULL THEN
        score := score - (snow_age_days * 2);
    END IF;
    
    -- Clamp to 0-100
    RETURN GREATEST(0, LEAST(100, score));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert sample resort
INSERT INTO resorts (name, slug, latitude, longitude, state, region, 
                     base_elevation_ft, summit_elevation_ft, total_lifts, total_runs)
VALUES 
    ('Vail Mountain Resort', 'vail', 39.6403, -106.3742, 'Colorado', 'Central Rockies', 8120, 11570, 31, 195),
    ('Jackson Hole Mountain Resort', 'jackson-hole', 43.5872, -110.8278, 'Wyoming', 'Tetons', 6311, 10450, 13, 133),
    ('Palisades Tahoe', 'palisades-tahoe', 39.1969, -120.2357, 'California', 'Lake Tahoe', 6200, 9050, 30, 175);

-- ============================================================================
-- MAINTENANCE & OPTIMIZATION
-- ============================================================================

-- Drop old data (run weekly)
CREATE OR REPLACE FUNCTION cleanup_old_conditions()
RETURNS void AS $$
BEGIN
    -- Keep detailed data for 90 days
    DELETE FROM conditions WHERE time < NOW() - INTERVAL '90 days';
    
    -- Keep SNOTEL for 365 days
    DELETE FROM snotel_readings WHERE time < NOW() - INTERVAL '365 days';
    
    -- Keep webcam snapshots for 30 days
    DELETE FROM webcam_snapshots WHERE captured_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Update modified timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER resorts_updated_at BEFORE UPDATE ON resorts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

## Backend Implementation

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings & environment variables
│   ├── database.py             # Database connection
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── resort.py
│   │   ├── condition.py
│   │   ├── forecast.py
│   │   ├── user.py
│   │   └── alert.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── resort.py
│   │   ├── condition.py
│   │   ├── forecast.py
│   │   └── alert.py
│   │
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── resorts.py
│   │   ├── conditions.py
│   │   ├── forecasts.py
│   │   ├── alerts.py
│   │   └── auth.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── data_fusion.py     # Combine multiple sources
│   │   ├── quality_scorer.py   # Calculate quality scores
│   │   ├── alert_manager.py    # Alert processing
│   │   └── cache.py            # Redis caching
│   │
│   └── utils/
│       ├── __init__.py
│       ├── auth.py             # JWT helpers
│       └── validators.py       # Data validation
│
├── scrapers/                   # Data collection
│   ├── __init__.py
│   ├── base_scraper.py         # Base class
│   │
│   ├── resorts/                # Resort-specific scrapers
│   │   ├── __init__.py
│   │   ├── vail.py
│   │   ├── alterra.py
│   │   ├── jackson_hole.py
│   │   └── generic_html.py
│   │
│   ├── weather/                # Weather data
│   │   ├── __init__.py
│   │   ├── noaa.py
│   │   ├── openweather.py
│   │   └── weather_gov.py
│   │
│   ├── snotel.py               # SNOTEL API client
│   └── webcam_fetcher.py       # Webcam snapshots
│
├── tasks/                      # Celery tasks
│   ├── __init__.py
│   ├── celery_app.py           # Celery configuration
│   ├── scrape_tasks.py         # Scheduled scraping
│   ├── alert_tasks.py          # Alert processing
│   └── maintenance_tasks.py    # Cleanup, etc.
│
├── tests/
│   ├── __init__.py
│   ├── test_api/
│   ├── test_scrapers/
│   └── test_services/
│
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
│
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── pytest.ini
├── Dockerfile
└── docker-compose.yml
```

### Core Files

#### `requirements.txt`

```txt
# FastAPI & Web
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Redis & Celery
redis==5.0.1
celery==5.3.4

# HTTP & Scraping
httpx==0.25.1
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
selenium==4.15.2

# Data Processing
pandas==2.1.3
numpy==1.26.2

# Auth & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Email
python-email-validator==2.1.0
emails==0.6

# Monitoring
sentry-sdk[fastapi]==1.38.0

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
python-dateutil==2.8.2
pytz==2023.3
```

#### `.env.example`

```bash
# Application
APP_NAME=SnowSpot
ENVIRONMENT=development  # development, staging, production
DEBUG=true
SECRET_KEY=your-secret-key-change-this-in-production
API_VERSION=v1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/snowspot
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# API Keys
OPENWEATHER_API_KEY=your-key-here
MAPBOX_API_KEY=your-key-here

# Email (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@snowspot.com

# Storage (S3 or local)
STORAGE_TYPE=local  # local or s3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=snowspot-webcams
S3_REGION=us-west-2

# Monitoring
SENTRY_DSN=

# CORS (for frontend)
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Rate Limiting
API_RATE_LIMIT=100  # requests per minute
```

#### `app/config.py`

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "SnowSpot"
    environment: str = "development"
    debug: bool = True
    secret_key: str
    api_version: str = "v1"
    
    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 0
    
    # Redis
    redis_url: str
    
    # Celery
    celery_broker_url: str
    celery_result_backend: str
    
    # API Keys
    openweather_api_key: str | None = None
    mapbox_api_key: str | None = None
    
    # Email
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    email_from: str = "noreply@snowspot.com"
    
    # Storage
    storage_type: str = "local"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    s3_bucket_name: str | None = None
    s3_region: str = "us-west-2"
    
    # Monitoring
    sentry_dsn: str | None = None
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Rate Limiting
    api_rate_limit: int = 100  # per minute
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

#### `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.config import settings
from app.routers import resorts, conditions, forecasts, alerts, auth
from app.database import engine
from app import models

# Initialize Sentry (if configured)
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0 if settings.debug else 0.1,
        environment=settings.environment,
    )

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Automated Snow Intelligence Platform API",
    version=settings.api_version,
    debug=settings.debug,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(resorts.router, prefix="/api/v1/resorts", tags=["resorts"])
app.include_router(conditions.router, prefix="/api/v1/conditions", tags=["conditions"])
app.include_router(forecasts.router, prefix="/api/v1/forecasts", tags=["forecasts"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    # Create database tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    print(f"🚀 {settings.app_name} API started in {settings.environment} mode")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(f"👋 {settings.app_name} API shutting down")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.api_version,
        "status": "operational",
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    # TODO: Add database, redis, celery health checks
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "celery": "running",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
```

#### `app/database.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Test connection before using
    echo=settings.debug,  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency for routes
def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### `app/models/resort.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, ARRAY, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base


class Resort(Base):
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
    
    # Stats
    base_elevation_ft = Column(Integer)
    summit_elevation_ft = Column(Integer)
    vertical_drop_ft = Column(Integer)
    total_lifts = Column(Integer)
    total_runs = Column(Integer)
    total_acres = Column(Integer)
    
    # Data sources
    official_url = Column(String(500))
    data_source_config = Column(JSON)
    snotel_station_ids = Column(ARRAY(String))
    weather_station_id = Column(String(50))
    
    # Metadata
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Resort(id={self.id}, name='{self.name}', slug='{self.slug}')>"
```

#### `app/schemas/resort.py`

```python
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional


class ResortBase(BaseModel):
    name: str
    slug: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    state: Optional[str] = None
    region: Optional[str] = None


class ResortCreate(ResortBase):
    base_elevation_ft: Optional[int] = None
    summit_elevation_ft: Optional[int] = None
    total_lifts: Optional[int] = None
    total_runs: Optional[int] = None
    official_url: Optional[HttpUrl] = None


class ResortResponse(ResortBase):
    id: int
    base_elevation_ft: Optional[int]
    summit_elevation_ft: Optional[int]
    vertical_drop_ft: Optional[int]
    total_lifts: Optional[int]
    total_runs: Optional[int]
    total_acres: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConditionResponse(BaseModel):
    resort_id: int
    time: datetime
    base_depth_in: Optional[float]
    new_snow_24h_in: Optional[float]
    new_snow_48h_in: Optional[float]
    temperature_f: Optional[float]
    wind_speed_mph: Optional[float]
    lifts_open: Optional[int]
    lifts_total: Optional[int]
    snow_quality_score: Optional[float]
    confidence_score: Optional[float]
    
    class Config:
        from_attributes = True


class ResortWithConditions(ResortResponse):
    latest_conditions: Optional[ConditionResponse] = None
```

#### `app/routers/resorts.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from app.database import get_db
from app.models.resort import Resort
from app.schemas.resort import ResortResponse, ResortWithConditions
from app.services.cache import cache_response

router = APIRouter()


@router.get("/", response_model=List[ResortResponse])
@cache_response(expire=300)  # Cache for 5 minutes
async def list_resorts(
    state: Optional[str] = None,
    region: Optional[str] = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    db: Session = Depends(get_db),
):
    """List all resorts with optional filtering"""
    query = db.query(Resort)
    
    if active_only:
        query = query.filter(Resort.is_active == True)
    if state:
        query = query.filter(Resort.state == state)
    if region:
        query = query.filter(Resort.region == region)
    
    resorts = query.offset(skip).limit(limit).all()
    return resorts


@router.get("/{resort_slug}", response_model=ResortWithConditions)
@cache_response(expire=180)  # Cache for 3 minutes
async def get_resort(
    resort_slug: str,
    include_conditions: bool = True,
    db: Session = Depends(get_db),
):
    """Get a single resort by slug with optional latest conditions"""
    resort = db.query(Resort).filter(Resort.slug == resort_slug).first()
    
    if not resort:
        raise HTTPException(status_code=404, detail="Resort not found")
    
    result = resort.__dict__
    
    if include_conditions:
        # Get latest conditions from materialized view
        latest = db.execute(
            text("""
                SELECT * FROM latest_conditions 
                WHERE resort_id = :resort_id
            """),
            {"resort_id": resort.id}
        ).first()
        
        if latest:
            result["latest_conditions"] = dict(latest._mapping)
    
    return result


@router.get("/{resort_slug}/history")
@cache_response(expire=600)  # Cache for 10 minutes
async def get_resort_history(
    resort_slug: str,
    hours: int = Query(default=24, ge=1, le=168),  # Max 7 days
    db: Session = Depends(get_db),
):
    """Get historical conditions for a resort"""
    resort = db.query(Resort).filter(Resort.slug == resort_slug).first()
    
    if not resort:
        raise HTTPException(status_code=404, detail="Resort not found")
    
    # Query time-series data
    results = db.execute(
        text("""
            SELECT 
                time,
                base_depth_in,
                new_snow_24h_in,
                temperature_f,
                wind_speed_mph,
                snow_quality_score
            FROM conditions
            WHERE resort_id = :resort_id
              AND time >= NOW() - INTERVAL ':hours hours'
            ORDER BY time DESC
        """),
        {"resort_id": resort.id, "hours": hours}
    ).fetchall()
    
    return {
        "resort": resort.name,
        "history": [dict(row._mapping) for row in results]
    }
```

---

## Data Collection System

### Base Scraper Class

#### `scrapers/base_scraper.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.database import SessionLocal

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self, resort_id: int, resort_name: str):
        self.resort_id = resort_id
        self.resort_name = resort_name
        self.db: Optional[Session] = None
        self.run_id: Optional[int] = None
    
    @abstractmethod
    async def scrape(self) -> Dict[str, Any]:
        """
        Scrape data from source
        
        Returns:
            Dict with condition data:
            {
                'base_depth_in': float,
                'new_snow_24h_in': float,
                'temperature_f': float,
                'lifts_open': int,
                'lifts_total': int,
                ...
            }
        """
        pass
    
    def start_run(self):
        """Record scraper execution start"""
        self.db = SessionLocal()
        try:
            result = self.db.execute(
                """
                INSERT INTO scraper_runs (scraper_name, resort_id, started_at, status)
                VALUES (:name, :resort_id, :started, 'running')
                RETURNING id
                """,
                {
                    "name": self.__class__.__name__,
                    "resort_id": self.resort_id,
                    "started": datetime.now()
                }
            )
            self.run_id = result.fetchone()[0]
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to start scraper run: {e}")
            if self.db:
                self.db.rollback()
    
    def end_run(self, status: str, records: int = 0, error: str = None):
        """Record scraper execution end"""
        if not self.db or not self.run_id:
            return
        
        try:
            self.db.execute(
                """
                UPDATE scraper_runs
                SET completed_at = :completed,
                    status = :status,
                    records_collected = :records,
                    error_message = :error,
                    duration_seconds = EXTRACT(EPOCH FROM (:completed - started_at))
                WHERE id = :run_id
                """,
                {
                    "run_id": self.run_id,
                    "completed": datetime.now(),
                    "status": status,
                    "records": records,
                    "error": error
                }
            )
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to end scraper run: {e}")
            if self.db:
                self.db.rollback()
        finally:
            if self.db:
                self.db.close()
    
    async def run(self) -> Dict[str, Any]:
        """Execute scraper with error handling and logging"""
        self.start_run()
        
        try:
            logger.info(f"Starting scraper for {self.resort_name}")
            data = await self.scrape()
            
            if data:
                # Save to database
                await self.save_conditions(data)
                self.end_run(status="success", records=1)
                logger.info(f"Successfully scraped {self.resort_name}")
                return data
            else:
                self.end_run(status="no_data")
                logger.warning(f"No data retrieved for {self.resort_name}")
                return {}
        
        except Exception as e:
            self.end_run(status="failure", error=str(e))
            logger.error(f"Scraper failed for {self.resort_name}: {e}", exc_info=True)
            raise
    
    async def save_conditions(self, data: Dict[str, Any]):
        """Save scraped data to database"""
        if not self.db:
            self.db = SessionLocal()
        
        try:
            self.db.execute(
                """
                INSERT INTO conditions (
                    time, resort_id, base_depth_in, summit_depth_in,
                    new_snow_24h_in, new_snow_48h_in, temperature_f,
                    wind_speed_mph, lifts_open, lifts_total, runs_open, runs_total,
                    data_sources, confidence_score
                )
                VALUES (
                    :time, :resort_id, :base_depth, :summit_depth,
                    :snow_24h, :snow_48h, :temp, :wind, :lifts_open, :lifts_total,
                    :runs_open, :runs_total, :sources, :confidence
                )
                """,
                {
                    "time": datetime.now(),
                    "resort_id": self.resort_id,
                    "base_depth": data.get("base_depth_in"),
                    "summit_depth": data.get("summit_depth_in"),
                    "snow_24h": data.get("new_snow_24h_in"),
                    "snow_48h": data.get("new_snow_48h_in"),
                    "temp": data.get("temperature_f"),
                    "wind": data.get("wind_speed_mph"),
                    "lifts_open": data.get("lifts_open"),
                    "lifts_total": data.get("lifts_total"),
                    "runs_open": data.get("runs_open"),
                    "runs_total": data.get("runs_total"),
                    "sources": {"scraper": self.__class__.__name__},
                    "confidence": data.get("confidence", 0.8)
                }
            )
            self.db.commit()
            logger.debug(f"Saved conditions for {self.resort_name}")
        
        except Exception as e:
            logger.error(f"Failed to save conditions: {e}")
            self.db.rollback()
            raise
        finally:
            if self.db:
                self.db.close()
```

### Example Resort Scraper

#### `scrapers/resorts/jackson_hole.py`

```python
import httpx
from bs4 import BeautifulSoup
import re
from typing import Dict, Any

from scrapers.base_scraper import BaseScraper


class JacksonHoleScraper(BaseScraper):
    """Scraper for Jackson Hole Mountain Resort"""
    
    BASE_URL = "https://www.jacksonhole.com/conditions"
    
    async def scrape(self) -> Dict[str, Any]:
        """Scrape Jackson Hole conditions"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.BASE_URL)
            response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {
            "base_depth_in": self._extract_base_depth(soup),
            "new_snow_24h_in": self._extract_snowfall(soup, hours=24),
            "new_snow_48h_in": self._extract_snowfall(soup, hours=48),
            "temperature_f": self._extract_temperature(soup),
            "lifts_open": self._extract_lifts_open(soup),
            "lifts_total": 13,  # Known total
            "confidence": 0.9  # High confidence for official source
        }
        
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    def _extract_base_depth(self, soup: BeautifulSoup) -> float:
        """Extract base depth from page"""
        try:
            # Look for element containing base depth
            depth_element = soup.find(text=re.compile(r'Base Depth', re.I))
            if depth_element:
                parent = depth_element.find_parent()
                # Find number in nearby text
                text = parent.get_text()
                match = re.search(r'(\d+)\s*"', text)
                if match:
                    return float(match.group(1))
        except Exception as e:
            print(f"Error extracting base depth: {e}")
        return None
    
    def _extract_snowfall(self, soup: BeautifulSoup, hours: int) -> float:
        """Extract snowfall for given time period"""
        try:
            if hours == 24:
                pattern = r'24\s*(?:hr|hour)'
            elif hours == 48:
                pattern = r'48\s*(?:hr|hour)'
            else:
                return None
            
            element = soup.find(text=re.compile(pattern, re.I))
            if element:
                parent = element.find_parent()
                text = parent.get_text()
                match = re.search(r'(\d+(?:\.\d+)?)\s*"', text)
                if match:
                    return float(match.group(1))
        except Exception as e:
            print(f"Error extracting snowfall: {e}")
        return None
    
    def _extract_temperature(self, soup: BeautifulSoup) -> float:
        """Extract current temperature"""
        try:
            temp_element = soup.find(text=re.compile(r'Temperature|Temp', re.I))
            if temp_element:
                parent = temp_element.find_parent()
                text = parent.get_text()
                match = re.search(r'(-?\d+)\s*°?F', text)
                if match:
                    return float(match.group(1))
        except Exception as e:
            print(f"Error extracting temperature: {e}")
        return None
    
    def _extract_lifts_open(self, soup: BeautifulSoup) -> int:
        """Extract number of open lifts"""
        try:
            lifts_element = soup.find(text=re.compile(r'Lifts?.*Open', re.I))
            if lifts_element:
                parent = lifts_element.find_parent()
                text = parent.get_text()
                match = re.search(r'(\d+)\s*(?:of|/)', text)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error extracting lifts: {e}")
        return None
```

### SNOTEL Integration

#### `scrapers/snotel.py`

```python
import httpx
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class SNOTELClient:
    """Client for USDA SNOTEL data"""
    
    BASE_URL = "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1"
    
    async def get_station_data(
        self,
        station_id: str,
        hours_back: int = 24
    ) -> Optional[Dict]:
        """
        Get latest data from SNOTEL station
        
        Args:
            station_id: SNOTEL station ID (e.g., "652:WY:SNTL")
            hours_back: How many hours of data to retrieve
        
        Returns:
            Dict with snow depth, SWE, temperature, etc.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours_back)
        
        params = {
            "stationTriplets": station_id,
            "elementCd": "WTEQ,SNWD,TOBS",  # SWE, Snow Depth, Temp
            "ordinal": "1",  # Daily values
            "duration": "DAILY",
            "getFlags": "false",
            "beginDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/data",
                params=params
            )
            response.raise_for_status()
            data = response.json()
        
        if not data:
            return None
        
        # Parse response
        latest = self._parse_snotel_response(data)
        return latest
    
    def _parse_snotel_response(self, data: List[Dict]) -> Dict:
        """Parse SNOTEL API response"""
        result = {
            "snow_depth_in": None,
            "swe_in": None,
            "temperature_f": None,
            "timestamp": None
        }
        
        try:
            for station_data in data:
                element = station_data.get("elementCd")
                values = station_data.get("values", [])
                
                if not values:
                    continue
                
                latest_value = values[-1]  # Get most recent
                value = latest_value.get("value")
                date = latest_value.get("date")
                
                if element == "SNWD":  # Snow depth
                    result["snow_depth_in"] = float(value)
                    result["timestamp"] = date
                elif element == "WTEQ":  # SWE
                    result["swe_in"] = float(value)
                elif element == "TOBS":  # Temperature
                    result["temperature_f"] = float(value)
        
        except Exception as e:
            print(f"Error parsing SNOTEL data: {e}")
        
        return result
    
    async def get_stations_near(
        self,
        latitude: float,
        longitude: float,
        radius_miles: float = 25
    ) -> List[Dict]:
        """Find SNOTEL stations near a location"""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius_miles,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/stations",
                params=params
            )
            response.raise_for_status()
            return response.json()
```

### Celery Tasks

#### `tasks/celery_app.py`

```python
from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Create Celery app
celery_app = Celery(
    "snowspot",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "tasks.scrape_tasks",
        "tasks.alert_tasks",
        "tasks.maintenance_tasks",
    ]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max
    task_soft_time_limit=540,  # 9 minutes soft limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    # Scrape resort conditions every 15 minutes
    "scrape-all-resorts": {
        "task": "tasks.scrape_tasks.scrape_all_resorts",
        "schedule": crontab(minute="*/15"),
    },
    # Fetch SNOTEL data every 30 minutes
    "fetch-snotel-data": {
        "task": "tasks.scrape_tasks.fetch_all_snotel",
        "schedule": crontab(minute="*/30"),
    },
    # Update weather forecasts every hour
    "update-forecasts": {
        "task": "tasks.scrape_tasks.update_all_forecasts",
        "schedule": crontab(minute=5),  # Every hour at :05
    },
    # Process powder alerts every 15 minutes
    "process-alerts": {
        "task": "tasks.alert_tasks.process_all_alerts",
        "schedule": crontab(minute="*/15"),
    },
    # Refresh materialized views every 15 minutes
    "refresh-views": {
        "task": "tasks.maintenance_tasks.refresh_materialized_views",
        "schedule": crontab(minute="*/15"),
    },
    # Cleanup old data daily at 2 AM
    "cleanup-old-data": {
        "task": "tasks.maintenance_tasks.cleanup_old_data",
        "schedule": crontab(hour=2, minute=0),
    },
}
```

#### `tasks/scrape_tasks.py`

```python
from celery import group
from sqlalchemy.orm import Session

from tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.resort import Resort

from scrapers.resorts.jackson_hole import JacksonHoleScraper
from scrapers.snotel import SNOTELClient
# Import other scrapers as implemented


@celery_app.task(name="tasks.scrape_tasks.scrape_all_resorts")
def scrape_all_resorts():
    """Scrape conditions for all active resorts"""
    db: Session = SessionLocal()
    try:
        resorts = db.query(Resort).filter(Resort.is_active == True).all()
        
        # Create task group for parallel execution
        task_group = group(
            scrape_single_resort.s(resort.id, resort.name, resort.slug)
            for resort in resorts
        )
        
        result = task_group.apply_async()
        
        return {
            "status": "started",
            "resorts_count": len(resorts),
            "group_id": result.id
        }
    finally:
        db.close()


@celery_app.task(name="tasks.scrape_tasks.scrape_single_resort")
async def scrape_single_resort(resort_id: int, resort_name: str, resort_slug: str):
    """Scrape a single resort"""
    try:
        # Determine which scraper to use based on resort
        # This would be configured in resort.data_source_config
        scraper = None
        
        if resort_slug == "jackson-hole":
            scraper = JacksonHoleScraper(resort_id, resort_name)
        # Add other resort scrapers here
        else:
            # Use generic HTML scraper
            pass
        
        if scraper:
            await scraper.run()
            return {"resort": resort_name, "status": "success"}
        else:
            return {"resort": resort_name, "status": "no_scraper"}
    
    except Exception as e:
        return {"resort": resort_name, "status": "error", "error": str(e)}


@celery_app.task(name="tasks.scrape_tasks.fetch_all_snotel")
async def fetch_all_snotel():
    """Fetch data from all configured SNOTEL stations"""
    db: Session = SessionLocal()
    client = SNOTELClient()
    
    try:
        # Get all resorts with SNOTEL stations configured
        resorts = db.query(Resort).filter(
            Resort.is_active == True,
            Resort.snotel_station_ids.isnot(None)
        ).all()
        
        results = []
        for resort in resorts:
            for station_id in resort.snotel_station_ids:
                try:
                    data = await client.get_station_data(station_id)
                    if data:
                        # Save to database
                        await save_snotel_data(station_id, data)
                        results.append({
                            "station": station_id,
                            "resort": resort.name,
                            "status": "success"
                        })
                except Exception as e:
                    results.append({
                        "station": station_id,
                        "resort": resort.name,
                        "status": "error",
                        "error": str(e)
                    })
        
        return {"total": len(results), "results": results}
    
    finally:
        db.close()


async def save_snotel_data(station_id: str, data: dict):
    """Save SNOTEL data to database"""
    db = SessionLocal()
    try:
        db.execute(
            """
            INSERT INTO snotel_readings (
                time, station_id, snow_depth_in, 
                snow_water_equivalent_in, temperature_f
            )
            VALUES (:time, :station_id, :depth, :swe, :temp)
            """,
            {
                "time": data.get("timestamp"),
                "station_id": station_id,
                "depth": data.get("snow_depth_in"),
                "swe": data.get("swe_in"),
                "temp": data.get("temperature_f")
            }
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
```

---

## Frontend Implementation

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorMessage.tsx
│   │   ├── resort/
│   │   │   ├── ResortCard.tsx
│   │   │   ├── ResortDetail.tsx
│   │   │   ├── ConditionsPanel.tsx
│   │   │   └── SnowChart.tsx
│   │   ├── comparison/
│   │   │   ├── ComparisonTable.tsx
│   │   │   └── ComparisonChart.tsx
│   │   └── alerts/
│   │       ├── AlertForm.tsx
│   │       └── AlertList.tsx
│   │
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── ResortPage.tsx
│   │   ├── ComparisonPage.tsx
│   │   └── AlertsPage.tsx
│   │
│   ├── services/
│   │   ├── api.ts
│   │   └── types.ts
│   │
│   ├── hooks/
│   │   ├── useResorts.ts
│   │   ├── useConditions.ts
│   │   └── useForecast.ts
│   │
│   ├── utils/
│   │   ├── formatting.ts
│   │   └── scoring.ts
│   │
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
│
├── public/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

### Key Frontend Files

#### `package.json`

```json
{
  "name": "snowspot-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "@tanstack/react-query": "^5.12.2",
    "recharts": "^2.10.3",
    "date-fns": "^2.30.0",
    "react-icons": "^4.12.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@typescript-eslint/eslint-plugin": "^6.13.2",
    "@typescript-eslint/parser": "^6.13.2",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.3",
    "vite": "^5.0.7"
  }
}
```

#### `src/services/types.ts`

```typescript
export interface Resort {
  id: number;
  name: string;
  slug: string;
  latitude: number;
  longitude: number;
  state: string;
  region: string;
  base_elevation_ft: number;
  summit_elevation_ft: number;
  total_lifts: number;
  total_runs: number;
  is_active: boolean;
}

export interface Conditions {
  resort_id: number;
  time: string;
  base_depth_in: number | null;
  summit_depth_in: number | null;
  new_snow_24h_in: number | null;
  new_snow_48h_in: number | null;
  new_snow_7d_in: number | null;
  temperature_f: number | null;
  wind_speed_mph: number | null;
  lifts_open: number | null;
  lifts_total: number | null;
  runs_open: number | null;
  runs_total: number | null;
  snow_quality_score: number | null;
  skiability_index: number | null;
  confidence_score: number | null;
}

export interface ResortWithConditions extends Resort {
  latest_conditions: Conditions | null;
}

export interface Forecast {
  forecast_for: string;
  temperature_high_f: number;
  temperature_low_f: number;
  predicted_snowfall_in: number;
  precipitation_prob_percent: number;
}
```

#### `src/services/api.ts`

```typescript
import axios from 'axios';
import type { Resort, ResortWithConditions, Conditions, Forecast } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Resorts
export const getResorts = async (params?: {
  state?: string;
  region?: string;
}): Promise<Resort[]> => {
  const response = await api.get('/resorts/', { params });
  return response.data;
};

export const getResort = async (slug: string): Promise<ResortWithConditions> => {
  const response = await api.get(`/resorts/${slug}`);
  return response.data;
};

export const getResortHistory = async (
  slug: string,
  hours: number = 24
): Promise<{ resort: string; history: Conditions[] }> => {
  const response = await api.get(`/resorts/${slug}/history`, {
    params: { hours },
  });
  return response.data;
};

// Conditions
export const getLatestConditions = async (): Promise<Conditions[]> => {
  const response = await api.get('/conditions/latest');
  return response.data;
};

// Forecasts
export const getForecast = async (
  resortId: number,
  days: number = 7
): Promise<Forecast[]> => {
  const response = await api.get(`/forecasts/${resortId}`, {
    params: { days },
  });
  return response.data;
};

export default api;
```

#### `src/components/resort/ResortCard.tsx`

```typescript
import { Link } from 'react-router-dom';
import { FiMapPin, FiTrendingUp } from 'react-icons/fi';
import type { ResortWithConditions } from '../../services/types';
import { formatNumber } from '../../utils/formatting';

interface ResortCardProps {
  resort: ResortWithConditions;
}

export default function ResortCard({ resort }: ResortCardProps) {
  const conditions = resort.latest_conditions;
  
  return (
    <Link
      to={`/resort/${resort.slug}`}
      className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{resort.name}</h3>
          <div className="flex items-center text-sm text-gray-600 mt-1">
            <FiMapPin className="mr-1" />
            {resort.state}, {resort.region}
          </div>
        </div>
        
        {conditions?.snow_quality_score && (
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-600">
              {Math.round(conditions.snow_quality_score)}
            </div>
            <div className="text-xs text-gray-500">Quality Score</div>
          </div>
        )}
      </div>
      
      {conditions ? (
        <div className="grid grid-cols-3 gap-4 mt-4">
          <div>
            <div className="text-sm text-gray-500">24h Snow</div>
            <div className="text-lg font-semibold text-gray-900">
              {conditions.new_snow_24h_in 
                ? `${formatNumber(conditions.new_snow_24h_in)}"`
                : '--'
              }
            </div>
          </div>
          
          <div>
            <div className="text-sm text-gray-500">Base Depth</div>
            <div className="text-lg font-semibold text-gray-900">
              {conditions.base_depth_in 
                ? `${formatNumber(conditions.base_depth_in)}"`
                : '--'
              }
            </div>
          </div>
          
          <div>
            <div className="text-sm text-gray-500">Temp</div>
            <div className="text-lg font-semibold text-gray-900">
              {conditions.temperature_f 
                ? `${Math.round(conditions.temperature_f)}°F`
                : '--'
              }
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-gray-500 py-4">
          No recent data available
        </div>
      )}
      
      {conditions?.lifts_open && conditions?.lifts_total && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Lifts Open</span>
            <span className="font-medium">
              {conditions.lifts_open} / {conditions.lifts_total}
            </span>
          </div>
        </div>
      )}
      
      <div className="mt-4 flex items-center text-sm text-blue-600 font-medium">
        View Details
        <FiTrendingUp className="ml-1" />
      </div>
    </Link>
  );
}
```

#### `src/pages/Home.tsx`

```typescript
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getResorts } from '../services/api';
import ResortCard from '../components/resort/ResortCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

export default function Home() {
  const [stateFilter, setStateFilter] = useState<string>('');
  
  const { data: resorts, isLoading, error } = useQuery({
    queryKey: ['resorts', stateFilter],
    queryFn: () => getResorts({ state: stateFilter || undefined }),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
  
  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  const states = [...new Set(resorts?.map(r => r.state))].sort();
  
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          SnowSpot
        </h1>
        <p className="text-xl text-gray-600">
          Real-time snow conditions powered by automated data collection
        </p>
      </div>
      
      <div className="mb-6 flex items-center space-x-4">
        <label className="text-sm font-medium text-gray-700">
          Filter by state:
        </label>
        <select
          value={stateFilter}
          onChange={(e) => setStateFilter(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">All States</option>
          {states.map(state => (
            <option key={state} value={state}>{state}</option>
          ))}
        </select>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {resorts?.map(resort => (
          <ResortCard key={resort.id} resort={resort} />
        ))}
      </div>
      
      {resorts?.length === 0 && (
        <div className="text-center text-gray-500 py-12">
          No resorts found matching your filters
        </div>
      )}
    </div>
  );
}
```

---

## Deployment Guide

### Docker Setup

#### `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_USER: snowspot
      POSTGRES_PASSWORD: snowspot_dev_password
      POSTGRES_DB: snowspot
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U snowspot"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://snowspot:snowspot_dev_password@postgres:5432/snowspot
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A tasks.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://snowspot:snowspot_dev_password@postgres:5432/snowspot
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A tasks.celery_app beat --loglevel=info
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://snowspot:snowspot_dev_password@postgres:5432/snowspot
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

#### `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `frontend/Dockerfile`

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Run development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### Production Deployment (Railway.app)

#### `railway.toml`

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Deployment Steps

1. **Setup Database** (Supabase or Railway PostgreSQL):
```bash
# Create database
# Enable TimescaleDB extension
# Run schema SQL
```

2. **Setup Redis** (Railway Redis or Upstash):
```bash
# Get connection URL
```

3. **Deploy Backend**:
```bash
# Railway
railway login
railway init
railway up

# OR Render
# Connect GitHub repo
# Add environment variables
```

4. **Deploy Frontend** (Vercel/Netlify):
```bash
# Vercel
vercel login
vercel --prod

# OR Netlify
netlify login
netlify deploy --prod
```

5. **Setup Celery Workers** (Railway):
```bash
# Create separate service for Celery worker
# Use same repo, different start command
```

---

## Testing Strategy

### Backend Tests

#### `tests/test_api/test_resorts.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_resorts():
    """Test listing all resorts"""
    response = client.get("/api/v1/resorts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_resort():
    """Test getting a single resort"""
    response = client.get("/api/v1/resorts/jackson-hole")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "jackson-hole"
    assert "latest_conditions" in data


def test_get_resort_not_found():
    """Test 404 for non-existent resort"""
    response = client.get("/api/v1/resorts/fake-resort")
    assert response.status_code == 404
```

### Integration Tests

```python
import pytest
from scrapers.resorts.jackson_hole import JacksonHoleScraper


@pytest.mark.asyncio
async def test_jackson_hole_scraper():
    """Test Jackson Hole scraper"""
    scraper = JacksonHoleScraper(resort_id=1, resort_name="Jackson Hole")
    data = await scraper.scrape()
    
    assert data is not None
    assert "base_depth_in" in data or "new_snow_24h_in" in data
    assert data.get("confidence", 0) > 0.5
```

### Running Tests

```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm test
npm run test:coverage
```

---

## Appendix: Code Examples

### Data Fusion Example

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class DataSource:
    """Single data source with value and metadata"""
    source_name: str
    value: float
    timestamp: datetime
    confidence: float  # 0-1
    weight: float  # Base weight for this source type


class DataFusionEngine:
    """
    Combines data from multiple sources to produce
    best estimate with confidence score
    """
    
    # Source weights (higher = more trusted)
    SOURCE_WEIGHTS = {
        "resort_official": 0.5,
        "snotel": 0.4,
        "weather_api": 0.1,
    }
    
    def fuse_measurements(
        self,
        sources: List[DataSource],
        max_age_hours: int = 24
    ) -> Optional[tuple[float, float]]:
        """
        Fuse multiple measurements into single best estimate
        
        Returns:
            (best_estimate, confidence_score) or None
        """
        if not sources:
            return None
        
        current_time = datetime.now()
        weighted_sum = 0.0
        total_weight = 0.0
        
        for source in sources:
            # Calculate age penalty (exponential decay)
            age_hours = (current_time - source.timestamp).total_seconds() / 3600
            if age_hours > max_age_hours:
                continue  # Too old, skip
            
            age_factor = 0.95 ** age_hours  # Decay by 5% per hour
            
            # Effective weight = base weight * source confidence * age factor
            effective_weight = (
                source.weight *
                source.confidence *
                age_factor
            )
            
            weighted_sum += source.value * effective_weight
            total_weight += effective_weight
        
        if total_weight == 0:
            return None
        
        # Calculate best estimate
        best_estimate = weighted_sum / total_weight
        
        # Calculate confidence (0-1)
        # More sources = higher confidence
        # More recent data = higher confidence
        # Higher weights = higher confidence
        confidence = min(1.0, total_weight / sum(s.weight for s in sources))
        
        return best_estimate, confidence


# Usage example
if __name__ == "__main__":
    fusion = DataFusionEngine()
    
    sources = [
        DataSource(
            source_name="resort_official",
            value=12.0,  # 12 inches new snow
            timestamp=datetime.now() - timedelta(hours=2),
            confidence=0.9,
            weight=DataFusionEngine.SOURCE_WEIGHTS["resort_official"]
        ),
        DataSource(
            source_name="snotel",
            value=11.5,
            timestamp=datetime.now() - timedelta(hours=1),
            confidence=0.95,
            weight=DataFusionEngine.SOURCE_WEIGHTS["snotel"]
        ),
        DataSource(
            source_name="weather_api",
            value=13.0,
            timestamp=datetime.now(),
            confidence=0.7,
            weight=DataFusionEngine.SOURCE_WEIGHTS["weather_api"]
        ),
    ]
    
    result = fusion.fuse_measurements(sources)
    if result:
        estimate, confidence = result
        print(f"Best estimate: {estimate:.1f} inches")
        print(f"Confidence: {confidence:.2f}")
```

### Snow Quality Scorer

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class SnowConditions:
    """Current snow conditions for scoring"""
    new_snow_24h_in: Optional[float] = None
    temperature_f: Optional[float] = None
    wind_speed_mph: Optional[float] = None
    days_since_snow: Optional[int] = None
    humidity_percent: Optional[int] = None


class SnowQualityScorer:
    """Calculate snow quality score (0-100)"""
    
    @staticmethod
    def calculate(conditions: SnowConditions) -> float:
        """
        Calculate overall snow quality score
        
        Factors:
        - New snow amount (max 30 points)
        - Temperature (max 25 points)
        - Wind (max 15 points)
        - Age of snow (max 20 points)
        - Humidity (max 10 points)
        """
        score = 0.0
        
        # New snow amount (0-30 points)
        if conditions.new_snow_24h_in is not None:
            if conditions.new_snow_24h_in >= 12:
                score += 30  # Epic powder day
            elif conditions.new_snow_24h_in >= 6:
                score += 25  # Great day
            elif conditions.new_snow_24h_in >= 3:
                score += 20  # Good day
            elif conditions.new_snow_24h_in >= 1:
                score += 15  # Decent
            else:
                score += 10  # Some fresh snow
        
        # Temperature (0-25 points)
        # Ideal: 15-28°F (light, dry snow)
        if conditions.temperature_f is not None:
            temp = conditions.temperature_f
            if 15 <= temp <= 28:
                score += 25  # Perfect temp for powder
            elif 10 <= temp <= 32:
                score += 20  # Good temp
            elif 5 <= temp <= 35:
                score += 15  # Acceptable
            elif temp < 5:
                score += 10  # Too cold (brittle)
            else:
                score += 5  # Too warm (heavy/wet)
        
        # Wind (0-15 points)
        if conditions.wind_speed_mph is not None:
            wind = conditions.wind_speed_mph
            if wind < 10:
                score += 15  # Calm, perfect
            elif wind < 20:
                score += 10  # Breezy but manageable
            elif wind < 30:
                score += 5  # Windy
            # else: 0 points (too windy)
        
        # Age of snow (0-20 points)
        if conditions.days_since_snow is not None:
            days = conditions.days_since_snow
            if days == 0:
                score += 20  # Fresh today!
            elif days == 1:
                score += 15  # Yesterday's snow
            elif days <= 3:
                score += 10  # Recent snow
            elif days <= 7:
                score += 5  # Week-old snow
            # else: 0 points (old snow)
        
        # Humidity (0-10 points)
        # Lower humidity = lighter, fluffier snow
        if conditions.humidity_percent is not None:
            humidity = conditions.humidity_percent
            if humidity < 30:
                score += 10  # Bone dry powder
            elif humidity < 50:
                score += 8  # Dry
            elif humidity < 70:
                score += 5  # Average
            else:
                score += 2  # Humid (heavier snow)
        
        return min(100.0, score)  # Cap at 100
    
    @staticmethod
    def get_description(score: float) -> str:
        """Get human-readable description of score"""
        if score >= 90:
            return "Epic Powder Day! 🎿"
        elif score >= 80:
            return "Excellent Conditions"
        elif score >= 70:
            return "Great Day to Ski"
        elif score >= 60:
            return "Good Conditions"
        elif score >= 50:
            return "Decent Skiing"
        elif score >= 40:
            return "Fair Conditions"
        else:
            return "Poor Conditions"


# Usage example
if __name__ == "__main__":
    # Powder day conditions
    conditions = SnowConditions(
        new_snow_24h_in=14.0,
        temperature_f=22.0,
        wind_speed_mph=8.0,
        days_since_snow=0,
        humidity_percent=25
    )
    
    scorer = SnowQualityScorer()
    score = scorer.calculate(conditions)
    description = scorer.get_description(score)
    
    print(f"Snow Quality Score: {score:.0f}/100")
    print(f"Description: {description}")
```

---

## Quick Start Commands

### Initial Setup

```bash
# 1. Clone or create project structure
mkdir snowspot && cd snowspot
mkdir -p backend frontend

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Setup frontend
cd ../frontend
npm install

# 4. Start database and redis
docker-compose up -d postgres redis

# 5. Run database migrations
cd backend
alembic upgrade head

# 6. Seed initial data
python scripts/seed_resorts.py

# 7. Start backend
uvicorn app.main:app --reload

# 8. Start Celery (new terminal)
celery -A tasks.celery_app worker -B --loglevel=info

# 9. Start frontend (new terminal)
cd frontend
npm run dev
```

### Development Workflow

```bash
# Backend changes
cd backend
pytest tests/ -v  # Run tests
alembic revision --autogenerate -m "description"  # Create migration
alembic upgrade head  # Apply migration

# Frontend changes
cd frontend
npm run lint  # Check code
npm run build  # Build for production
```

---

**This specification provides everything needed to build the SnowSpot MVP.** Each section can be implemented incrementally, tested independently, and deployed when ready. Start with the database schema and basic scrapers, then build up the API, and finally the frontend.