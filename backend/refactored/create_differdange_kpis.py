#!/usr/bin/env python3
"""
Script to create comprehensive KPIs for Differdange, Luxembourg.
This script populates the database with realistic climate and environmental KPIs.
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
from app.core.database import SessionLocal, engine
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
        print(f"Created city: {city.name}")
    else:
        print(f"Found existing city: {city.name}")
    
    return city

def create_kpis_data(city_id: int) -> List[Dict]:
    """Define all KPIs for Differdange."""
    return [
        # AIR QUALITY KPIs
        {
            "id_kpi": "DIF_AQ_PM25",
            "name": "PM2.5 Concentration",
            "description": "Fine particulate matter (PM2.5) concentration in the air",
            "category": "Air Quality",
            "unit_text": "µg/m³",
            "provider": "Luxembourg Environment Agency",
            "calculation_frequency": "Hourly",
            "min_threshold": 0.0,
            "max_threshold": 25.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (5, 35),
            "trend": "fluctuating"
        },
        {
            "id_kpi": "DIF_AQ_PM10",
            "name": "PM10 Concentration",
            "description": "Coarse particulate matter (PM10) concentration in the air",
            "category": "Air Quality",
            "unit_text": "µg/m³",
            "provider": "Luxembourg Environment Agency",
            "calculation_frequency": "Hourly",
            "min_threshold": 0.0,
            "max_threshold": 50.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (10, 60),
            "trend": "fluctuating"
        },
        {
            "id_kpi": "DIF_AQ_NO2",
            "name": "Nitrogen Dioxide (NO2)",
            "description": "Nitrogen dioxide concentration in the air",
            "category": "Air Quality",
            "unit_text": "µg/m³",
            "provider": "Luxembourg Environment Agency",
            "calculation_frequency": "Hourly",
            "min_threshold": 0.0,
            "max_threshold": 40.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (15, 55),
            "trend": "decreasing"
        },
        {
            "id_kpi": "DIF_AQ_O3",
            "name": "Ozone (O3)",
            "description": "Ground-level ozone concentration",
            "category": "Air Quality",
            "unit_text": "µg/m³",
            "provider": "Luxembourg Environment Agency",
            "calculation_frequency": "Hourly",
            "min_threshold": 0.0,
            "max_threshold": 120.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (30, 100),
            "trend": "seasonal"
        },
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
                150: "Unhealthy",
                200: "Very Unhealthy"
            },
            "city_id": city_id,
            "value_range": (20, 80),
            "trend": "fluctuating"
        },
        
        # CLIMATE & WEATHER KPIs
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
        {
            "id_kpi": "DIF_CLIMATE_HUMIDITY",
            "name": "Relative Humidity",
            "description": "Average relative humidity percentage",
            "category": "Climate",
            "unit_text": "%",
            "provider": "MeteoLux",
            "calculation_frequency": "Hourly",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (50, 90),
            "trend": "fluctuating"
        },
        {
            "id_kpi": "DIF_CLIMATE_PRECIP",
            "name": "Precipitation",
            "description": "Daily rainfall amount",
            "category": "Climate",
            "unit_text": "mm",
            "provider": "MeteoLux",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (0, 30),
            "trend": "random"
        },
        {
            "id_kpi": "DIF_CLIMATE_WIND",
            "name": "Wind Speed",
            "description": "Average wind speed",
            "category": "Climate",
            "unit_text": "km/h",
            "provider": "MeteoLux",
            "calculation_frequency": "Hourly",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (5, 40),
            "trend": "fluctuating"
        },
        
        # ENERGY KPIs
        {
            "id_kpi": "DIF_ENERGY_CONSUMPTION",
            "name": "Total Energy Consumption",
            "description": "Total energy consumption in the city",
            "category": "Energy",
            "unit_text": "MWh",
            "provider": "Creos Luxembourg",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 10000.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (2000, 5000),
            "trend": "increasing"
        },
        {
            "id_kpi": "DIF_ENERGY_RENEWABLE",
            "name": "Renewable Energy Share",
            "description": "Percentage of energy from renewable sources",
            "category": "Energy",
            "unit_text": "%",
            "provider": "Creos Luxembourg",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (25, 45),
            "trend": "increasing"
        },
        {
            "id_kpi": "DIF_ENERGY_SOLAR",
            "name": "Solar Energy Production",
            "description": "Energy produced from solar panels",
            "category": "Energy",
            "unit_text": "kWh",
            "provider": "Creos Luxembourg",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 5000.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (500, 2000),
            "trend": "seasonal"
        },
        {
            "id_kpi": "DIF_ENERGY_EFFICIENCY",
            "name": "Energy Efficiency Index",
            "description": "Overall energy efficiency score (0-100)",
            "category": "Energy",
            "unit_text": "points",
            "provider": "Municipal Energy Office",
            "calculation_frequency": "Monthly",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (60, 85),
            "trend": "increasing"
        },
        
        # EMISSIONS KPIs
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
        },
        {
            "id_kpi": "DIF_EMISSION_GHG",
            "name": "Greenhouse Gas Emissions",
            "description": "Total greenhouse gas emissions (CO2 equivalent)",
            "category": "Emissions",
            "unit_text": "tonnes CO2e",
            "provider": "Luxembourg Environment Agency",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 1500.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (300, 800),
            "trend": "decreasing"
        },
        {
            "id_kpi": "DIF_EMISSION_TRANSPORT",
            "name": "Transport Emissions",
            "description": "Emissions from transportation sector",
            "category": "Emissions",
            "unit_text": "tonnes CO2",
            "provider": "Ministry of Mobility",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 500.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (100, 300),
            "trend": "fluctuating"
        },
        
        # WASTE MANAGEMENT KPIs
        {
            "id_kpi": "DIF_WASTE_TOTAL",
            "name": "Total Waste Generated",
            "description": "Total amount of waste generated",
            "category": "Waste",
            "unit_text": "tonnes",
            "provider": "Municipal Waste Management",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (20, 50),
            "trend": "fluctuating"
        },
        {
            "id_kpi": "DIF_WASTE_RECYCLED",
            "name": "Waste Recycling Rate",
            "description": "Percentage of waste that is recycled",
            "category": "Waste",
            "unit_text": "%",
            "provider": "Municipal Waste Management",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (45, 70),
            "trend": "increasing"
        },
        {
            "id_kpi": "DIF_WASTE_ORGANIC",
            "name": "Organic Waste Composted",
            "description": "Amount of organic waste composted",
            "category": "Waste",
            "unit_text": "tonnes",
            "provider": "Municipal Waste Management",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 50.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (5, 20),
            "trend": "increasing"
        },
        
        # WATER MANAGEMENT KPIs
        {
            "id_kpi": "DIF_WATER_CONSUMPTION",
            "name": "Water Consumption",
            "description": "Daily water consumption per capita",
            "category": "Water",
            "unit_text": "L/person",
            "provider": "SEBES (Water Service)",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 500.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (100, 200),
            "trend": "decreasing"
        },
        {
            "id_kpi": "DIF_WATER_QUALITY",
            "name": "Water Quality Index",
            "description": "Drinking water quality index",
            "category": "Water",
            "unit_text": "points",
            "provider": "SEBES (Water Service)",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (85, 98),
            "trend": "stable"
        },
        {
            "id_kpi": "DIF_WATER_LEAKAGE",
            "name": "Water Network Leakage",
            "description": "Percentage of water lost through leaks",
            "category": "Water",
            "unit_text": "%",
            "provider": "SEBES (Water Service)",
            "calculation_frequency": "Monthly",
            "min_threshold": 0.0,
            "max_threshold": 50.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (8, 15),
            "trend": "decreasing"
        },
        
        # BIODIVERSITY & GREEN SPACES KPIs
        {
            "id_kpi": "DIF_GREEN_COVERAGE",
            "name": "Green Space Coverage",
            "description": "Percentage of city area covered by green spaces",
            "category": "Biodiversity",
            "unit_text": "%",
            "provider": "Municipal Urban Planning",
            "calculation_frequency": "Quarterly",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (30, 40),
            "trend": "increasing"
        },
        {
            "id_kpi": "DIF_TREE_COUNT",
            "name": "Urban Tree Count",
            "description": "Number of trees in urban areas",
            "category": "Biodiversity",
            "unit_text": "trees",
            "provider": "Municipal Parks Department",
            "calculation_frequency": "Annually",
            "min_threshold": 0.0,
            "max_threshold": 10000.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (3000, 4500),
            "trend": "increasing"
        },
        {
            "id_kpi": "DIF_BIODIVERSITY_INDEX",
            "name": "Biodiversity Index",
            "description": "Overall biodiversity health score",
            "category": "Biodiversity",
            "unit_text": "index",
            "provider": "natur&ëmwelt",
            "calculation_frequency": "Annually",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (60, 80),
            "trend": "increasing"
        },
        
        # MOBILITY KPIs
        {
            "id_kpi": "DIF_MOBILITY_PUBLIC_USAGE",
            "name": "Public Transport Usage",
            "description": "Daily public transport users",
            "category": "Mobility",
            "unit_text": "users",
            "provider": "TICE (Transport)",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 5000.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (1000, 2500),
            "trend": "increasing"
        },
        {
            "id_kpi": "DIF_MOBILITY_BIKE_TRIPS",
            "name": "Bicycle Trips",
            "description": "Number of bicycle trips per day",
            "category": "Mobility",
            "unit_text": "trips",
            "provider": "Municipal Mobility Office",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 2000.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (200, 800),
            "trend": "increasing"
        },
        {
            "id_kpi": "DIF_MOBILITY_EV_CHARGING",
            "name": "EV Charging Sessions",
            "description": "Electric vehicle charging sessions per day",
            "category": "Mobility",
            "unit_text": "sessions",
            "provider": "Chargy Luxembourg",
            "calculation_frequency": "Daily",
            "min_threshold": 0.0,
            "max_threshold": 500.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (50, 200),
            "trend": "increasing"
        },
        {
            "id_kpi": "DIF_MOBILITY_TRAFFIC_INDEX",
            "name": "Traffic Congestion Index",
            "description": "Traffic congestion level (lower is better)",
            "category": "Mobility",
            "unit_text": "index",
            "provider": "Ministry of Mobility",
            "calculation_frequency": "Hourly",
            "min_threshold": 0.0,
            "max_threshold": 100.0,
            "has_category_label": False,
            "city_id": city_id,
            "value_range": (20, 60),
            "trend": "fluctuating"
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
            # Gradually increasing with noise
            base_value = min_val + (max_val - min_val) * (days - day) / days
            value = base_value + random.uniform(-5, 5)
        elif trend == "decreasing":
            # Gradually decreasing with noise
            base_value = max_val - (max_val - min_val) * (days - day) / days
            value = base_value + random.uniform(-5, 5)
        elif trend == "seasonal":
            # Sinusoidal pattern (seasonal variation)
            day_of_year = timestamp.timetuple().tm_yday
            seasonal_factor = 0.5 + 0.5 * random.random() * (1 + 0.3 * random.random() * (day_of_year / 365))
            value = min_val + (max_val - min_val) * seasonal_factor
        elif trend == "random":
            # Completely random (e.g., for precipitation)
            if random.random() < 0.3:  # 30% chance of rain
                value = random.uniform(min_val, max_val * 0.5)
            else:
                value = 0.0
        elif trend == "stable":
            # Stable with minor variations
            base_value = (min_val + max_val) / 2
            value = base_value + random.uniform(-2, 2)
        else:  # fluctuating
            # Random walk
            value = random.uniform(min_val, max_val)
        
        # Ensure value stays within bounds
        value = max(min_val * 0.8, min(max_val * 1.2, value))
        
        # Determine category label if applicable
        category_label = None
        if has_category_label and category_label_dict:
            # Find the appropriate category based on value
            # Sort thresholds in descending order to find the right category
            sorted_thresholds = sorted(category_label_dict.keys(), reverse=True)
            for threshold in sorted_thresholds:
                if value >= threshold:
                    category_label = category_label_dict[threshold]
                    break
            # If no threshold matched, use the lowest category
            if category_label is None and sorted_thresholds:
                category_label = category_label_dict[min(category_label_dict.keys())]
        
        values.append(KPIValue(
            kpi_id=kpi_id,
            value=round(value, 2),
            category_label=category_label,
            timestamp=timestamp
        ))
    
    return values

def create_kpis_with_values(db: Session, city: City):
    """Create all KPIs and their historical values."""
    kpis_data = create_kpis_data(city.id)
    
    print(f"\nCreating {len(kpis_data)} KPIs for {city.name}...")
    
    created_kpis = 0
    created_values = 0
    
    for kpi_config in kpis_data:
        # Extract metadata for value generation
        value_range = kpi_config.pop("value_range")
        trend = kpi_config.pop("trend")
        has_category_label = kpi_config.get("has_category_label", False)
        category_label_dict = kpi_config.get("category_label_dictionary", {})
        
        # Check if KPI already exists
        existing_kpi = db.query(KPI).filter(KPI.id_kpi == kpi_config["id_kpi"]).first()
        
        if existing_kpi:
            print(f"  ⚠️  KPI already exists: {kpi_config['name']} ({kpi_config['id_kpi']})")
            kpi = existing_kpi
        else:
            # Create new KPI
            kpi = KPI(**kpi_config)
            db.add(kpi)
            db.flush()  # Get the KPI ID
            created_kpis += 1
            print(f"  ✓ Created KPI: {kpi.name} ({kpi.id_kpi})")
        
        # Generate historical values (last 90 days)
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
        
        # Add values to database
        db.bulk_save_objects(values)
        created_values += len(values)
        
        if has_category_label:
            print(f"    → Generated {len(values)} historical values with category labels")
        else:
            print(f"    → Generated {len(values)} historical values")
    
    db.commit()
    
    print(f"\n✅ Summary:")
    print(f"   - Created {created_kpis} new KPIs")
    print(f"   - Generated {created_values} historical values")
    print(f"   - Total KPIs in database: {db.query(KPI).filter(KPI.city_id == city.id).count()}")

def main():
    """Main execution function."""
    print("=" * 70)
    print("Creating KPIs for Differdange, Luxembourg")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        # Get or create Differdange city
        city = get_or_create_city(db)
        
        # Create KPIs with historical values
        create_kpis_with_values(db, city)
        
        print("\n" + "=" * 70)
        print("✅ KPI creation completed successfully!")
        print("=" * 70)
        
        # Print summary by category
        print("\nKPIs by Category:")
        categories = db.query(KPI.category).filter(KPI.city_id == city.id).distinct().all()
        for (category,) in categories:
            count = db.query(KPI).filter(
                KPI.city_id == city.id,
                KPI.category == category
            ).count()
            print(f"  - {category}: {count} KPIs")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
