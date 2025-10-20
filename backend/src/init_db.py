#!/usr/bin/env python3
"""
Database initialization script for the enhanced Climaborough backend.
Creates all tables and populates with initial data.
"""
import os
import sys
import logging

# Add the app directory to Python path
sys.path.insert(0, '/code')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.models import *  # Import all models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables."""
    logger.info(f"Using database URL: {settings.DATABASE_URL}")
    
    logger.info("Creating database tables...")
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    logger.info("Database tables created successfully!")

def create_sample_data():
    """Create sample dashboard and visualizations."""
    logger.info("Creating sample data...")
    
    db = SessionLocal()
    try:
        from app.services import DashboardService, VisualizationService, CityService, SectionService
        from app.schemas import CityCreate, DashboardCreate, DashboardSectionCreate, VisualizationCreate
        
        dashboard_service = DashboardService()
        section_service = SectionService()
        viz_service = VisualizationService()
        city_service = CityService()
        
        # Create multiple cities that the frontend expects
        cities_data = [
            CityCreate(name="Differdange", code="differdange", country="Luxembourg", timezone="Europe/Luxembourg"),
            CityCreate(name="Cascais", code="cascais", country="Portugal", timezone="Europe/Lisbon"),
            CityCreate(name="Sofia", code="sofia", country="Bulgaria", timezone="Europe/Sofia"),
            CityCreate(name="Maribor", code="maribor", country="Slovenia", timezone="Europe/Ljubljana"),
            CityCreate(name="Athens", code="athens", country="Greece", timezone="Europe/Athens"),
            CityCreate(name="Ioannina", code="ioannina", country="Greece", timezone="Europe/Athens"),
            CityCreate(name="Grenoble", code="grenoble", country="France", timezone="Europe/Paris"),
            CityCreate(name="Torino", code="torino", country="Italy", timezone="Europe/Rome"),
        ]
        
        cities = []
        for city_data in cities_data:
            city = city_service.create_city(db, city_data)
            cities.append(city)
            logger.info(f"Created city: {city.name}")
        
        # Create a sample dashboard for the first city (Differdange)
        dashboard_data = DashboardCreate(
            code="differdange-overview",
            title="Differdange Climate Dashboard",
            description="Main dashboard for Differdange climate data visualization",
            is_public=True,
            city_id=cities[0].id
        )
        dashboard = dashboard_service.create_dashboard(db, dashboard_data)
        logger.info(f"Created dashboard: {dashboard.title}")
        
        # Create sample sections
        sections_data = [
            DashboardSectionCreate(name="Overview", dashboard_id=dashboard.id, order=1, is_active=True),
            DashboardSectionCreate(name="Charts", dashboard_id=dashboard.id, order=2, is_active=True),
            DashboardSectionCreate(name="Analytics", dashboard_id=dashboard.id, order=3, is_active=True),
        ]
        
        sections = []
        for section_data in sections_data:
            section = section_service.create_section(db, section_data)
            sections.append(section)
            logger.info(f"Created section: {section.name}")
        
        # Sample visualizations creation removed - users will create their own visualizations
        # You can manually create visualizations through the UI using your KPI data
        
        db.commit()
        logger.info(f"Sample data created: {len(cities)} cities, 1 dashboard, {len(sections)} sections, 0 visualizations (create your own!)")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main initialization function."""
    try:
        # Create tables
        create_tables()
        
        # Create sample data
        create_sample_data()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    main()