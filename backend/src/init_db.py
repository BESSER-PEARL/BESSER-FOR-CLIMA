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

def create_sample_data(engine):
    """Create sample cities and minimal KPIs if database is empty."""
    
    with Session(engine) as db:
        try:
            # Check if cities already exist
            cities = db.query(City).all()  # FIX: Direct query instead of service method
            
            if len(cities) > 0:
                logger.info(f"Cities already exist ({len(cities)} cities found). Skipping sample data creation.")
                return
            
            logger.info("No cities found. Creating default cities...")
            
            # Create default cities
            default_cities = [
                {"name": "Torino", "code": "torino"},
                {"name": "Cascais", "code": "cascais"},
                {"name": "Differdange", "code": "differdange"},
                {"name": "Sofia", "code": "sofia"},
                {"name": "Athens", "code": "athens"},
                {"name": "Grenoble", "code": "grenoble"},
                {"name": "Maribor", "code": "maribor"},
                {"name": "Ioannina", "code": "ioannina"}
            ]
            
            for city_data in default_cities:
                city = City(**city_data)
                db.add(city)
            
            db.commit()
            logger.info(f"Created {len(default_cities)} default cities")
            
        except Exception as e:
            logger.error(f"Error creating sample data: {e}")
            db.rollback()
            raise

def main():
    """Main initialization function."""
    try:
        # Create tables
        create_tables()
        
        # Create sample data
        create_sample_data(engine)
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    main()