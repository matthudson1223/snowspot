# SnowSpot

> **Automated Snow Intelligence Platform** - Real-time ski resort conditions powered by multi-source data aggregation and quality scoring.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-blue.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-blue.svg)](https://www.typescriptlang.org/)

## Overview

SnowSpot is a comprehensive snow conditions platform that automatically aggregates data from multiple sources to provide accurate, real-time information about ski resort conditions. Unlike traditional condition reports that rely on manual updates, SnowSpot combines official resort data, government weather stations (SNOTEL), weather APIs, and webcam analysis to deliver reliable, frequently-updated conditions.

### Key Features

- **Real-Time Conditions**: Automated data collection every 15 minutes from 50+ ski resorts
- **Multi-Source Data Fusion**: Combines resort reports, SNOTEL stations, and weather APIs with confidence scoring
- **Snow Quality Scoring**: Proprietary algorithm that rates snow quality (0-100) based on freshness, temperature, wind, and other factors
- **7-Day Forecasts**: Integrated weather forecasting for planning your next ski trip
- **Resort Comparison**: Side-by-side comparison of multiple resorts
- **Powder Alerts**: Email notifications when conditions meet your criteria
- **Public API**: RESTful API with standardized responses for developers

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  DATA SOURCES                            │
│   Resort APIs │ SNOTEL Stations │ Weather APIs │ Webcams │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              DATA COLLECTION (Celery)                    │
│   Scrapers │ API Clients │ Scheduled Tasks              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│       PROCESSING & STORAGE                               │
│   Data Fusion │ Quality Scoring │ PostgreSQL+TimescaleDB│
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 API LAYER (FastAPI)                      │
│   REST Endpoints │ Validation │ Error Handling          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              FRONTEND (React + TypeScript)               │
│   Dashboard │ Resort Pages │ Comparison │ Alerts        │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend
- **Framework**: FastAPI 0.104+ (Python 3.11+)
- **Database**: PostgreSQL 16 with TimescaleDB extension
- **Cache**: Redis 7+
- **Task Queue**: Celery 5+ with Redis broker
- **Web Scraping**: BeautifulSoup4, Selenium, httpx
- **Data Processing**: Pandas, NumPy
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic

### Frontend
- **Framework**: React 19 with TypeScript 5.9
- **Build Tool**: Vite 7
- **Styling**: TailwindCSS 4
- **State Management**: React Query (TanStack Query)
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Routing**: React Router v7

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions (optional)
- **Monitoring**: Sentry (optional)
- **Deployment**: Railway / Render / Vercel

## Project Structure

```
snowspot/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   │   ├── data_fusion.py
│   │   │   └── quality_scorer.py
│   │   ├── scrapers/          # Data collection
│   │   └── utils/
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suite
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client
│   │   ├── hooks/            # Custom React hooks
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── .env.example
│
└── docs/                      # Documentation
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 16+ (or Docker)
- Redis 7+ (or Docker)

### Quick Start with Docker

The fastest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/yourusername/snowspot.git
cd snowspot

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --port 8000

# In a separate terminal, start Celery worker
celery -A tasks.celery_app worker --loglevel=info

# In another terminal, start Celery beat scheduler
celery -A tasks.celery_app beat --loglevel=info
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file and configure
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173)

### Environment Variables

#### Backend (.env)

```bash
# Application
APP_NAME=SnowSpot
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here
API_VERSION=v1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/snowspot

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# API Keys (optional)
OPENWEATHER_API_KEY=your-key-here
MAPBOX_API_KEY=your-key-here

# CORS
CORS_ORIGINS=["http://localhost:5173"]
```

#### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

## API Documentation

### Base URL

```
http://localhost:8000/api/v1
```

### Endpoints

#### Resorts

**List all resorts**
```http
GET /resorts/
```

Query Parameters:
- `state` (optional): Filter by state
- `region` (optional): Filter by region
- `active_only` (optional, default: true): Only active resorts

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Jackson Hole Mountain Resort",
      "slug": "jackson-hole",
      "state": "Wyoming",
      "region": "Tetons",
      "base_elevation_ft": 6311,
      "summit_elevation_ft": 10450
    }
  ]
}
```

**Get resort details**
```http
GET /resorts/{slug}
```

Response includes latest conditions:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Jackson Hole Mountain Resort",
    "slug": "jackson-hole",
    "latest_conditions": {
      "time": "2026-01-08T10:00:00Z",
      "base_depth_in": 45.0,
      "new_snow_24h_in": 8.0,
      "temperature_f": 24.0,
      "snow_quality_score": 87.5,
      "confidence_score": 0.92
    }
  }
}
```

**Get historical data**
```http
GET /resorts/{slug}/history?hours=24
```

#### Conditions

**Get latest conditions for all resorts**
```http
GET /conditions/latest
```

**Compare multiple resorts**
```http
GET /conditions/compare?resorts=jackson-hole,vail,palisades-tahoe
```

For complete API documentation, visit [http://localhost:8000/docs](http://localhost:8000/docs) when running the server.

## Development

### Running Tests

**Backend Tests**
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

**Frontend Tests**
```bash
cd frontend
npm test
npm run test:coverage
```

### Database Migrations

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

### Code Quality

**Backend Linting**
```bash
cd backend
black app/  # Format code
flake8 app/  # Check style
mypy app/  # Type checking
```

**Frontend Linting**
```bash
cd frontend
npm run lint
npm run lint:fix
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=false` in backend environment
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database (managed PostgreSQL)
- [ ] Configure production Redis
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS origins for production domain
- [ ] Set up monitoring (Sentry)
- [ ] Configure backup strategy for database
- [ ] Set up CDN for frontend static assets
- [ ] Configure environment-specific API keys

### Deployment Options

#### Option 1: Railway (Recommended for MVP)

1. Create Railway account
2. Connect GitHub repository
3. Add PostgreSQL and Redis services
4. Configure environment variables
5. Deploy backend and frontend services

#### Option 2: Docker on VPS

```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

#### Option 3: Separate Services

- **Backend**: Railway / Render / Fly.io
- **Frontend**: Vercel / Netlify / Cloudflare Pages
- **Database**: Supabase / Railway PostgreSQL
- **Redis**: Upstash / Railway Redis

## Data Sources

SnowSpot aggregates data from multiple sources:

1. **Official Resort APIs/Websites**: Direct snow reports, lift status, terrain info
2. **SNOTEL Stations**: USDA snow telemetry network for accurate snow depth and weather
3. **Weather APIs**: NOAA, OpenWeatherMap for forecasts
4. **Webcams**: Visual verification of conditions (MVP: manual, Phase 2: computer vision)

### Data Freshness

- Resort conditions: Updated every 15 minutes
- SNOTEL data: Updated every 30 minutes
- Weather forecasts: Updated hourly
- Confidence scores provided for all data points

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript strict mode
- Write tests for new features
- Update documentation as needed
- Keep commits focused and descriptive

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

### Phase 1: MVP (Current)
- [x] Core backend API
- [x] Data scrapers for major resorts
- [x] SNOTEL integration
- [x] Frontend dashboard
- [x] Quality scoring algorithm
- [ ] Email alerts
- [ ] 50 resort coverage

### Phase 2: Enhanced Features
- [ ] Mobile applications (iOS/Android)
- [ ] Machine learning predictions
- [ ] Computer vision webcam analysis
- [ ] User accounts and favorites
- [ ] Social features
- [ ] Advanced analytics

### Phase 3: Growth
- [ ] 500+ resort coverage
- [ ] International resorts
- [ ] Premium features
- [ ] API marketplace
- [ ] Partnership integrations

## Support

- **Documentation**: [Full build spec](./SnowSpot%20MVP%20-%20Complete%20Build%20Spec.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/snowspot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/snowspot/discussions)

## Acknowledgments

- USDA SNOTEL network for providing open weather data
- All ski resorts that provide public condition information
- Open source community for the amazing tools and libraries

---

**Built with passion for powder by skiers, for skiers.**
