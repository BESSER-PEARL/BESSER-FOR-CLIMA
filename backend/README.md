# Climaborough Data Platform - Backend

Modern FastAPI backend with clean architecture for the Climaborough Data Platform.

## Architecture

The backend follows a **layered architecture** with clear separation of concerns:

```
backend/
├── src/              # Main application (clean architecture)
│   ├── app/
│   │   ├── api/            # FastAPI routes (controllers)
│   │   ├── core/           # Configuration & utilities
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── repositories/   # Data access layer
│   │   ├── schemas/        # Pydantic validation schemas
│   │   └── services/       # Business logic
│   ├── ARCHITECTURE.md     # Detailed architecture docs
│   ├── architecture.plantuml  # Visual architecture diagram
│   ├── init_db.py          # Database initialization
│   └── run.py              # Server entry point
├── Docker/                  # Docker configurations
└── CLEANUP_SUMMARY.md       # Backend cleanup documentation
```

## Technology Stack

- **Framework**: FastAPI (async web framework)
- **ORM**: SQLAlchemy 2.0+ (with modern `Mapped` types)
- **Validation**: Pydantic v2
- **Database**: PostgreSQL 15+ with PostGIS
- **Authentication**: Keycloak (JWT tokens)
- **Python**: 3.11+

## Database Models

11 main models with proper relationships:

- **City** - City information (name, code, country, timezone)
- **Dashboard** - Dashboard metadata and configuration
- **DashboardSection** - Section organization within dashboards
- **KPI** - Key Performance Indicators
- **KPIValue** - Time series KPI data
- **Visualization** - Polymorphic base (LineChart, BarChart, PieChart, StatChart, Table, Map)
- **TableColumn** - Table column definitions
- **MapData** - Polymorphic map layers (WMS, GeoJson)

## Quick Start

### Requirements
- Python 3.11+
- PostgreSQL 15+ with PostGIS
- Docker (optional, for containerized setup)

### 1. Setup Virtual Environment

```bash
cd backend/src
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file in `backend/src/`:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/climaborough
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=climaborough

# Security
SECRET_KEY=your-secret-key-here
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=climaborough
KEYCLOAK_CLIENT_ID=climaborough-api

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4. Initialize Database

```bash
python init_db.py
```

This creates all tables and sets up PostGIS extension.

### 5. Run Development Server

```bash
python run.py
# or
uvicorn app.main:app --reload --port 8000
```

Server runs at: **http://localhost:8000**

## API Documentation

Once the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Cities
```
GET    /cities                  - List all cities
GET    /cities/{city_id}        - Get city by ID
GET    /cities/code/{code}      - Get city by code
POST   /cities                  - Create city
PUT    /cities/{city_id}        - Update city
DELETE /cities/{city_id}        - Delete city
```

### Dashboards
```
GET    /dashboards                           - List dashboards
GET    /dashboards/{dashboard_id}            - Get dashboard
GET    /dashboards/{id}/with-visualizations  - Get full dashboard
POST   /dashboards                           - Create dashboard
PUT    /dashboards/{dashboard_id}            - Update dashboard
DELETE /dashboards/{dashboard_id}            - Delete dashboard
```

### KPIs
```
GET    /kpis/?city_id={id}      - List KPIs for city
GET    /kpis/{kpi_id}           - Get KPI
GET    /kpis/{kpi_id}/values    - Get KPI values (with date filtering)
POST   /kpis                    - Create KPI
PUT    /kpis/{kpi_id}           - Update KPI
DELETE /kpis/{kpi_id}           - Delete KPI
```

### Sections & Visualizations
```
GET    /dashboards/{id}/sections              - List sections
POST   /dashboards/{id}/sections              - Create section
PUT    /sections/{section_id}                 - Update section
DELETE /sections/{section_id}                 - Delete section

GET    /dashboards/{id}/visualizations        - List visualizations
POST   /dashboards/{id}/visualizations        - Create visualization
PUT    /visualizations/{visualization_id}     - Update visualization
DELETE /visualizations/{visualization_id}     - Delete visualization
```

## Docker Deployment

### Option 1: Full Stack (PostgreSQL + Backend)

```bash
cd backend/src
docker-compose up -d
```

Includes:
- PostgreSQL with PostGIS (port 5432)
- PgAdmin (http://localhost:5050)
- FastAPI backend (http://localhost:8000)

### Option 2: Backend Only

```bash
cd backend/src
docker build -t climaborough-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  climaborough-backend
```

## Development

### Project Structure

```
app/
├── api/                    # API endpoints
│   ├── auth.py            # Authentication routes
│   ├── cities.py          # City management
│   ├── dashboards.py      # Dashboard CRUD
│   └── kpis.py            # KPI management
├── core/                   # Core configuration
│   ├── config.py          # Settings
│   ├── database.py        # DB connection
│   └── security.py        # Auth utilities
├── models/                 # SQLAlchemy models
│   └── __init__.py        # All 11 models
├── repositories/           # Data access layer
├── schemas/                # Pydantic schemas
│   ├── city.py
│   ├── dashboard.py
│   ├── kpi.py
│   └── visualization.py
└── services/               # Business logic
    ├── auth.py
    └── kpi.py
```

### Adding a New Endpoint

1. **Define Schema** (`app/schemas/your_model.py`)
```python
from pydantic import BaseModel

class YourModelCreate(BaseModel):
    name: str
    description: str | None = None
```

2. **Create Route** (`app/api/your_model.py`)
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(prefix="/your-models", tags=["Your Models"])

@router.get("/")
async def list_your_models(db: Session = Depends(get_db)):
    return db.query(YourModel).all()
```

3. **Register Router** (`app/main.py`)
```python
from app.api import your_model
app.include_router(your_model.router)
```

### Running Tests

```bash
pytest
pytest --cov=app --cov-report=html
pytest tests/test_cities.py -v
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Key Features

### 1. Polymorphic Visualizations
- Single table inheritance for different chart types
- Type discriminator for runtime type checking
- Shared base attributes + type-specific properties

### 2. Time Series Data
- Efficient KPI value storage
- Date range filtering
- Category label support for qualitative data
- Composite indexes for performance

### 3. Dashboard System
- Multi-section layout
- Grid-based positioning
- Drag-and-drop support
- Section duplication and reordering

### 4. Security
- Keycloak integration
- JWT token validation
- Role-based access control (RBAC)
- CORS configuration

### 5. Performance
- Async/await throughout
- Database connection pooling
- Composite indexes
- Query optimization

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql -h localhost -U postgres -d climaborough

# Check environment variables
echo $DATABASE_URL
```

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000    # Windows
lsof -i :8000                    # Linux/Mac

# Kill process or change port in run.py
```

### Import Errors
```bash
# Ensure you're in the right directory
cd backend/src

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Contributing

1. Follow the layered architecture pattern
2. Add type hints to all functions
3. Use Pydantic schemas for validation
4. Write tests for new endpoints
5. Update API documentation
6. Follow REST conventions


## License

See main project LICENSE file.
