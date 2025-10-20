"""
Data migration and initialization script.
"""
import asyncio
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import SessionLocal, init_db
from app.schemas import (
    CityCreate, DashboardCreate, KPICreate
)
from app.services import city_service, dashboard_service, kpi_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_initial_cities(db: Session):
    """Create initial cities from the original data."""
    cities_data = [
        {"name": "Ioannina", "code": "ioannina", "country": "Greece"},
        {"name": "Maribor", "code": "maribor", "country": "Slovenia"},
        {"name": "Grenoble-Alpes", "code": "grenoble", "country": "France"},
        {"name": "Athens", "code": "athens", "country": "Greece"},
        {"name": "Differdange", "code": "differdange", "country": "Luxembourg"},
        {"name": "Torino", "code": "torino", "country": "Italy"},
        {"name": "Cascais", "code": "cascais", "country": "Portugal"},
        {"name": "Sofia", "code": "sofia", "country": "Bulgaria"},
    ]
    
    created_cities = {}
    
    for city_data in cities_data:
        try:
            # Check if city already exists
            existing = city_service.city_repo.get_by_code(db, code=city_data["code"])
            if existing:
                logger.info(f"City {city_data['name']} already exists")
                created_cities[city_data["code"]] = existing
                continue
            
            city_create = CityCreate(**city_data)
            city = city_service.create_city(db, city_create)
            created_cities[city_data["code"]] = city
            logger.info(f"Created city: {city.name}")
            
        except Exception as e:
            logger.error(f"Failed to create city {city_data['name']}: {e}")
    
    return created_cities


def create_initial_dashboards(db: Session, cities: dict):
    """Create initial dashboards for cities."""
    for city_code, city in cities.items():
        try:
            # Check if dashboard already exists
            existing = dashboard_service.dashboard_repo.get_by_city_and_code(
                db, city_id=city.id, code=city_code
            )
            if existing:
                logger.info(f"Dashboard for {city.name} already exists")
                continue
            
            dashboard_create = DashboardCreate(
                code=city_code,
                title=f"{city.name} Dashboard",
                description=f"Main dashboard for {city.name}",
                is_public=True,
                city_id=city.id
            )
            
            dashboard = dashboard_service.create_dashboard(db, dashboard_create)
            logger.info(f"Created dashboard for {city.name}")
            
        except Exception as e:
            logger.error(f"Failed to create dashboard for {city.name}: {e}")


def create_sample_kpis(db: Session, cities: dict):
    """Create sample KPIs for cities."""
    
    # Sample KPI data based on the original
    kpis_data = [
        {
            "id_kpi": "money001",
            "name": "Money Invested",
            "category": "Environment",
            "description": "Measures the money invested in green stuff",
            "provider": "BankService",
            "calculation_frequency": "Weekly",
            "unit_text": "Euros",
            "min_threshold": 500.0,
            "max_threshold": 2000.0,
            "city_code": "differdange"
        },
        {
            "id_kpi": "temp001",
            "name": "Average Temperature",
            "category": "Environment",
            "description": "Measures the average temperature of the city",
            "provider": "WeatherService",
            "calculation_frequency": "Daily",
            "unit_text": "Celsius",
            "min_threshold": 15.0,
            "max_threshold": 35.0,
            "city_code": "differdange"
        },
        {
            "id_kpi": "waste_015",
            "name": "Amount of collected textile clothes",
            "category": "Waste",
            "description": "Amount of collected textile clothes",
            "provider": "City of Torino",
            "calculation_frequency": "Monthly",
            "unit_text": "Kg",
            "min_threshold": 90.0,
            "max_threshold": 110.0,
            "city_code": "torino"
        },
        {
            "id_kpi": "participants_006",
            "name": "Households participating in the three bags collection",
            "category": "Waste",
            "description": "Households participating in the three bags collection",
            "provider": "Torino",
            "calculation_frequency": "Monthly",
            "unit_text": "Households",
            "min_threshold": 80.0,
            "max_threshold": 120.0,
            "city_code": "torino"
        }
    ]
    
    for kpi_data in kpis_data:
        try:
            # Check if KPI already exists
            existing = kpi_service.kpi_repo.get_by_kpi_id(db, id_kpi=kpi_data["id_kpi"])
            if existing:
                logger.info(f"KPI {kpi_data['id_kpi']} already exists")
                continue
            
            city = cities.get(kpi_data["city_code"])
            if not city:
                logger.warning(f"City not found for KPI {kpi_data['id_kpi']}")
                continue
            
            kpi_create_data = kpi_data.copy()
            del kpi_create_data["city_code"]
            kpi_create_data["city_id"] = city.id
            kpi_create_data["has_category_label"] = False
            
            kpi_create = KPICreate(**kpi_create_data)
            kpi = kpi_service.create_kpi(db, kpi_create)
            logger.info(f"Created KPI: {kpi.name} for {city.name}")
            
        except Exception as e:
            logger.error(f"Failed to create KPI {kpi_data['id_kpi']}: {e}")


def main():
    """Run the initialization script."""
    logger.info("Starting data initialization...")
    
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized")
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Create initial data
            logger.info("Creating initial cities...")
            cities = create_initial_cities(db)
            
            logger.info("Creating initial dashboards...")
            create_initial_dashboards(db, cities)
            
            logger.info("Creating sample KPIs...")
            create_sample_kpis(db, cities)
            
            logger.info("Data initialization completed successfully!")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise


if __name__ == "__main__":
    main()