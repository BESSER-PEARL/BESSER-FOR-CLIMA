#!/usr/bin/env python3
"""
Minimal KPI creation script for demo/testing purposes.
Creates 3 essential KPIs with historical data.
This runs automatically on container startup if the database is empty.
"""
import os
import sys
from datetime import datetime, timedelta
import random
from typing import List, Dict

# Add the app directory to Python path
sys.path.insert(0, '/code')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import City, KPI, KPIValue

def get_or_create_city(db: Session) -> City:
    """Get Differdange city or create it if it doesn't exist."""
    city = db.query(City).filter(City.code == "differdange").first()
    
    if not city:
        city = City(
            name="Differdange",
            code="differdange",
            country="Luxembourg",
            timezone="Europe/Luxembourg"
        )
        db.add(city)
        db.commit()
        db.refresh(city)
        print(f"✓ Created city: {city.name}")
    
    return city

def create_minimal_kpis_data(city_id: int) -> List[Dict]:
    """Define 3 essential KPIs for demo/testing."""
    return [
        # 1. Air Quality Index (with category labels)
        {
            "id_kpi": "DIF_AQ_AQI",
            "name": "Air Quality Index",
            "description": "Overall air quality index based on multiple pollutants",
            "category": "Air Quality",
            "unit_text": "AQI",
            "provider": "Luxembourg Environment Agency",
            "calculation_frequency": "Hourly",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": True,
            "category_label_dictionary": {
                0: "Good",
                50: "Moderate",
                100: "Unhealthy for Sensitive Groups",
                150: "Unhealthy"
            },
            "city_id": city_id,
            "value_range": (20, 80),
            "trend": "fluctuating"
        },
        
        # 2. Temperature
        {
            "id_kpi": "DIF_CLIMATE_TEMP",
            "name": "Average Temperature",
            "description": "Daily average air temperature",
            "category": "Climate",
            "unit_text": "°C",
            "provider": "MeteoLux",
            "calculation_frequency": "Daily",
            "min_threshold": -10.0,
            "max_threshold": 35.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (5, 20),
            "trend": "seasonal"
        },
        
        # 3. CO2 Emissions
        {
            "id_kpi": "DIF_EMISSION_CO2",
            "name": "CO2 Emissions",
            "description": "Total carbon dioxide emissions",
            "category": "Emissions",
            "unit_text": "tonnes",
            "provider": "Luxembourg Environment Agency",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 1000.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (200, 600),
            "trend": "decreasing"
        }
    ]

def generate_time_series_values(kpi_id: int, kpi_config: Dict, days: int = 90) -> List[KPIValue]:
    """Generate realistic time series values for a KPI."""
    values = []
    now = datetime.utcnow()
    min_val, max_val = kpi_config["value_range"]
    trend = kpi_config["trend"]
    has_category_label = kpi_config.get("has_category_label", False)
    category_label_dict = kpi_config.get("category_label_dictionary", {})
    
    for day in range(days, 0, -1):
        timestamp = now - timedelta(days=day)
        
        # Generate value based on trend
        if trend == "increasing":
            base_value = min_val + (max_val - min_val) * (days - day) / days
            value = base_value + random.uniform(-5, 5)
        elif trend == "decreasing":
            base_value = max_val - (max_val - min_val) * (days - day) / days
            value = base_value + random.uniform(-5, 5)
        elif trend == "seasonal":
            day_of_year = timestamp.timetuple().tm_yday
            seasonal_factor = 0.5 + 0.5 * random.random() * (1 + 0.3 * random.random() * (day_of_year / 365))
            value = min_val + (max_val - min_val) * seasonal_factor
        else:  # fluctuating
            value = random.uniform(min_val, max_val)
        
        # Ensure value stays within bounds
        value = max(min_val * 0.8, min(max_val * 1.2, value))
        
        # Determine category label if applicable
        category_label = None
        if has_category_label and category_label_dict:
            sorted_thresholds = sorted(category_label_dict.keys(), reverse=True)
            for threshold in sorted_thresholds:
                if value >= threshold:
                    category_label = category_label_dict[threshold]
                    break
            if category_label is None and sorted_thresholds:
                category_label = category_label_dict[min(category_label_dict.keys())]
        
        values.append(KPIValue(
            kpi_id=kpi_id,
            value=round(value, 2),
            category_label=category_label,
            timestamp=timestamp
        ))
    
    return values

def create_minimal_kpis(db: Session, city: City):
    """Create 3 essential KPIs with historical values."""
    kpis_data = create_minimal_kpis_data(city.id)
    
    print(f"Creating {len(kpis_data)} KPIs for {city.name}...")
    
    for kpi_config in kpis_data:
        # Extract metadata
        value_range = kpi_config.pop("value_range")
        trend = kpi_config.pop("trend")
        has_category_label = kpi_config.get("has_category_label", False)
        category_label_dict = kpi_config.get("category_label_dictionary", {})
        
        # Check if KPI exists
        existing_kpi = db.query(KPI).filter(KPI.id_kpi == kpi_config["id_kpi"]).first()
        
        if existing_kpi:
            print(f"  ⚠️  Skipping existing KPI: {kpi_config['name']}")
            continue
        
        # Create KPI
        kpi = KPI(**kpi_config)
        db.add(kpi)
        db.flush()
        print(f"  ✓ Created KPI: {kpi.name}")
        
        # Generate 90 days of historical data
        values = generate_time_series_values(
            kpi.id,
            {
                "value_range": value_range,
                "trend": trend,
                "has_category_label": has_category_label,
                "category_label_dictionary": category_label_dict
            },
            days=90
        )
        
        db.bulk_save_objects(values)
        print(f"    → Generated {len(values)} historical values")
    
    db.commit()
    print(f"✅ Created {len(kpis_data)} KPIs with historical data")

def should_create_kpis(db: Session) -> bool:
    """Check if KPIs need to be created."""
    kpi_count = db.query(KPI).count()
    return kpi_count == 0

def main():
    """Main execution function."""
    db = SessionLocal()
    try:
        # Check if we need to create KPIs
        if not should_create_kpis(db):
            print("ℹ️  KPIs already exist. Skipping creation.")
            return
        
        print("=" * 60)
        print("Auto-creating minimal KPIs (3 KPIs)")
        print("=" * 60)
        
        city = get_or_create_city(db)
        create_minimal_kpis(db, city)
        
        print("=" * 60)
        print("✅ KPI auto-creation completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
