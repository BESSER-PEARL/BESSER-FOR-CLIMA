# Refactored Backend Architecture

## Overview
The refactored backend follows a clean, layered architecture with proper separation of concerns:

```
app/
├── api/              # API Routes (Controllers)
├── core/             # Core configuration and utilities
├── models/           # SQLAlchemy ORM models
├── repositories/     # Data access layer
├── schemas/          # Pydantic schemas (validation)
└── services/         # Business logic layer
```

## Architecture Layers

### 1. API Layer (`app/api/`)
- **Purpose**: HTTP request handling and routing
- **Files**:
  - `auth.py` - Authentication & authorization endpoints
  - `cities.py` - City management endpoints
  - `dashboards.py` - Dashboard CRUD operations
  - `kpis.py` - KPI and KPI values endpoints

### 2. Core Layer (`app/core/`)
- **Purpose**: Application configuration and shared utilities
- **Components**:
  - Database connection management
  - Configuration settings
  - Security utilities
  - Middleware

### 3. Models Layer (`app/models/`)
- **Purpose**: Database schema definitions using SQLAlchemy ORM
- **Key Models**:
  - `City` - City information
  - `Dashboard` - Dashboard metadata
  - `DashboardSection` - Section organization
  - `KPI` - Key Performance Indicators
  - `KPIValue` - Time series KPI data
  - `Visualization` - Base visualization (polymorphic)
    - `LineChart`, `BarChart`, `PieChart`, `StatChart`, `Table`, `Map`
  - `MapData` - Base map data (polymorphic)
    - `WMS`, `GeoJson`

### 4. Repositories Layer (`app/repositories/`)
- **Purpose**: Data access abstraction
- **Pattern**: Repository pattern for database operations
- **Benefits**:
  - Decouples business logic from data access
  - Makes testing easier
  - Centralizes query logic

### 5. Schemas Layer (`app/schemas/`)
- **Purpose**: Request/Response validation using Pydantic
- **Types**:
  - Request schemas (Create, Update)
  - Response schemas (Read)
  - Query parameter schemas

### 6. Services Layer (`app/services/`)
- **Purpose**: Business logic and orchestration
- **Components**:
  - `auth.py` - Authentication service
  - KPI service - KPI business logic
  - Dashboard service - Dashboard operations

## Database Schema

See `architecture.plantuml` for the complete database schema diagram.

## API Design Principles

1. **RESTful Design**: Standard HTTP methods (GET, POST, PUT, DELETE)
2. **Resource-Based**: URLs represent resources, not actions
3. **Consistent Naming**: snake_case for JSON properties
4. **Versioning Ready**: Structure supports API versioning
5. **Error Handling**: Consistent error responses

## Key Features

### 1. Dashboard System
- Multi-section dashboards
- Drag-and-drop grid layout
- Polymorphic visualizations
- City-specific dashboards

### 2. KPI Management
- Category-based organization
- Time series values
- Threshold management
- Category labels for qualitative data

### 3. Visualization Types
- **LineChart**: Time series trends
- **BarChart**: Comparisons
- **PieChart**: Proportions (with category labels)
- **StatChart**: Single metrics
- **Table**: Tabular data
- **Map**: Geographic data (WMS, GeoJSON)

### 4. Authentication
- Keycloak integration
- JWT token validation
- Role-based access control (RBAC)

## Technology Stack

- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (with mapped_column)
- **Validation**: Pydantic v2
- **Database**: PostgreSQL with PostGIS
- **Authentication**: Keycloak
- **Containerization**: Docker

## API Endpoints Structure

```
/cities
  GET    /                    - List cities
  GET    /{city_id}          - Get city by ID
  GET    /code/{city_code}   - Get city by code
  POST   /                    - Create city
  PUT    /{city_id}          - Update city
  DELETE /{city_id}          - Delete city

/dashboards
  GET    /                    - List dashboards
  GET    /{dashboard_id}     - Get dashboard
  POST   /                    - Create dashboard
  PUT    /{dashboard_id}     - Update dashboard
  DELETE /{dashboard_id}     - Delete dashboard
  
/dashboards/{dashboard_id}/sections
  GET    /                    - List sections
  POST   /                    - Create section
  PUT    /{section_id}       - Update section
  DELETE /{section_id}       - Delete section

/dashboards/{dashboard_id}/visualizations
  GET    /                    - List visualizations
  POST   /                    - Create visualization
  PUT    /{visualization_id} - Update visualization
  DELETE /{visualization_id} - Delete visualization

/kpis
  GET    /                    - List KPIs (filtered by city)
  GET    /{kpi_id}           - Get KPI
  POST   /                    - Create KPI
  PUT    /{kpi_id}           - Update KPI
  DELETE /{kpi_id}           - Delete KPI

/kpis/{kpi_id}/values
  GET    /                    - Get KPI values (with date filtering)
  POST   /                    - Add KPI value
  POST   /bulk               - Bulk add KPI values
```

## Migration from Old Backend

### Key Changes:
1. **Endpoint Structure**: From `/city/{name}/...` to `/cities/{code}/...`
2. **Property Naming**: camelCase → snake_case
3. **Dashboard-First**: Visualizations belong to dashboards, not cities
4. **Section Management**: Proper section hierarchy
5. **Type System**: Proper Pydantic schemas throughout

### Migration Path:
1. Old visualizations are migrated to dashboards
2. City names converted to codes
3. Property names transformed automatically
4. No data loss during migration

## Development Workflow

1. **Database Setup**: `python init_db.py`
2. **Sample Data**: `python create_differdange_kpis.py`
3. **Run Server**: `python run.py` or `uvicorn app.main:app --reload`
4. **Docker**: `docker-compose up`

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## Documentation

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Best Practices

1. **Async/Await**: Use async for I/O operations
2. **Dependency Injection**: FastAPI's dependency system
3. **Type Hints**: Full type coverage
4. **Error Handling**: Proper HTTP exceptions
5. **Logging**: Structured logging throughout
6. **Validation**: Pydantic schemas for all inputs
7. **Security**: JWT validation, CORS configuration
8. **Performance**: Database indexes, query optimization

## Future Enhancements

- [ ] GraphQL endpoint
- [ ] WebSocket support for real-time updates
- [ ] Caching layer (Redis)
- [ ] Rate limiting
- [ ] API versioning
- [ ] More visualization types
- [ ] Advanced filtering and search
- [ ] Export functionality (PDF, Excel)
- [ ] Audit logging
- [ ] Multi-tenancy support
