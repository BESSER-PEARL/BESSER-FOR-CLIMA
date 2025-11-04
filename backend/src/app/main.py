"""
Main FastAPI application with improved architecture.
"""
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
import time

from .core.config import settings
from .core.database import init_db
from .api import auth, cities, kpis, dashboards, mapdata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc", 
    openapi_url="/api/openapi.json",
    description="""
    ## Climaborough Data Platform API
    
    A modern, scalable API for managing city data, KPIs, dashboards, and visualizations.
    
    ### Features
    - **Cities**: Manage city information and metadata
    - **KPIs**: Create and manage Key Performance Indicators
    - **Dashboards**: Create customizable dashboards for data visualization
    - **Visualizations**: Support for various chart types (line, bar, pie, etc.)
    - **Authentication**: Keycloak integration for secure access
    
    ### Authentication
    Most endpoints require authentication. Use the `/auth/token` endpoint to get an access token,
    then include it in the Authorization header: `Bearer <your_token>`
    """
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": str(exc),
            "detail": "Invalid input data provided"
        }
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {exc}")
    
    # Extract more detailed error information
    error_detail = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "Conflict",
            "message": "Data conflict occurred",
            "detail": error_detail
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Handle general SQLAlchemy errors."""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error", 
            "message": "Database operation failed",
            "detail": "An internal database error occurred"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Error",
            "message": exc.detail,
            "detail": f"HTTP {exc.status_code} error occurred"
        }
    )


# Include API routers
app.include_router(auth.router)
app.include_router(cities.router)
app.include_router(kpis.router)
app.include_router(dashboards.router)
app.include_router(mapdata.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Climaborough API...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    logger.info("Application startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Climaborough API...")


@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Climaborough Data Platform API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "openapi": "/api/openapi.json"
    }


@app.get("/health", summary="Health check")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION
    }


# Optional: Keep one legacy endpoint for compatibility during migration
@app.get("/cities/{city_code}/summary", summary="Get city summary (legacy)")
async def get_city_summary_legacy(city_code: str):
    """
    Legacy endpoint for city summary.
    This can help during the migration from the old API structure.
    """
    # This would call the appropriate service methods
    return {
        "message": f"Legacy endpoint for {city_code}",
        "redirect": f"/cities/code/{city_code}",
        "note": "Please use the new API endpoints"
    }