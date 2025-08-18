# Python standard library imports
import os
import json
import logging
import requests

# FastAPI related imports
from fastapi import FastAPI, HTTPException, Body, Query, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware

# Database related imports
import psycopg2
from sqlalchemy import create_engine, func, inspect, MetaData, select
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.exc import IntegrityError

# Type hints and data validation
from typing import List, Optional, Union
from pydantic import BaseModel

# Geospatial imports
from geoalchemy2.shape import from_shape
from shapely.geometry import shape

# Authentication related imports
from auth.auth_bearer import KeycloakBearer

# Keycloak configuration constants
AUTH_SERVER_URL = os.environ.get("KEYCLOAK_SERVER_URL", "https://auth.climaplatform.eu")
KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "climaborough")
CLIENT_ID = os.environ.get("KEYCLOAK_CLIENT_ID", "climaborough-platform")

# Construct the full auth URL for token operations
KEYCLOAK_AUTH_URL = f"{AUTH_SERVER_URL}/realms/{KEYCLOAK_REALM}"

# Local application imports
from pydantic_classes import MapData, Visualisation, BarChart, WMS, KPI, KPIValue, Map, City, GeoJson, Dashboard, LineChart, Table, StatChart, TableColumn, PieChart
from sql_alchemy import Base
from sql_alchemy import MapData as MapDataDB, Visualisation as VisualisationDB, BarChart as BarChartDB, WMS as WMSDB, KPI as KPIDB, KPIValue as KPIValueDB, Map as MapDB, City as CityDB, GeoJson as GeoJsonDB, Dashboard as DashboardDB, LineChart as LineChartDB, Table as TableDB, StatChart as StatChartDB, TableColumn as TableColumnDB, PieChart as PieChartDB
from sql_alchemy import KPI as KPIDB, KPIValue as KPIValueDB

import logging

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)


app = FastAPI()

# Authentication endpoints for API users
@app.post("/auth/token", summary="Get access token", tags=["Authentication"])
async def get_token(
    username: str = Body(...),
    password: str = Body(...)
):
    """
    Get an access token using username and password.
    This token can be used in the Authorization header for protected endpoints.
    
    Example usage:
    1. Call this endpoint with your username and password
    2. Copy the access_token from the response
    3. Use it in the Authorization header: 'Bearer <access_token>'
    4. In Swagger UI, click 'Authorize' and enter: 'Bearer <access_token>'
    """
    try:        # Keycloak token endpoint
        token_url = f"{KEYCLOAK_AUTH_URL}/protocol/openid-connect/token"
        
        data = {
            'grant_type': 'password',
            'client_id': CLIENT_ID,
            'username': username,
            'password': password,
            'scope': 'openid'
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            return {
                "access_token": token_data["access_token"],
                "token_type": "bearer",
                "expires_in": token_data["expires_in"],
                "refresh_token": token_data.get("refresh_token")
            }
        else:
            raise HTTPException(
                status_code=401, 
                detail="Invalid credentials"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Authentication failed: {str(e)}"
        )

@app.post("/auth/refresh", summary="Refresh access token", tags=["Authentication"])
async def refresh_token(refresh_token: str = Body(...)):
    """
    Refresh an expired access token using a refresh token.
    
    Example usage:
    1. Use the refresh_token from a previous /auth/token call
    2. Get a new access_token without re-entering credentials
    """
    try:
        token_url = f"{KEYCLOAK_AUTH_URL}/protocol/openid-connect/token"
        
        data = {
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'refresh_token': refresh_token
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            return {
                "access_token": token_data["access_token"],
                "token_type": "bearer",
                "expires_in": token_data["expires_in"],
                "refresh_token": token_data.get("refresh_token")
            }
        else:
            raise HTTPException(
                status_code=401, 
                detail="Invalid refresh token"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Token refresh failed: {str(e)}"
        )

@app.get("/auth/info", summary="Authentication Information", tags=["Authentication"])
async def auth_info():
    """
    Get information about how to authenticate with this API.
    
    This endpoint provides step-by-step instructions for API authentication.
    """
    return {
        "message": "This API uses Keycloak for authentication",
        "steps": [
            "1. Get a token using POST /auth/token with your username/password",
            "2. Use the token in the Authorization header: 'Bearer <token>'",
            "3. In Swagger UI, click 'Authorize' and enter: 'Bearer <token>'"
        ],        "keycloak_server": AUTH_SERVER_URL,
        "client_id": CLIENT_ID,
        "direct_token_url": f"{KEYCLOAK_AUTH_URL}/protocol/openid-connect/token",
        "example_curl": f"curl -X POST '{KEYCLOAK_AUTH_URL}/protocol/openid-connect/token' -H 'Content-Type: application/x-www-form-urlencoded' -d 'grant_type=password&client_id={CLIENT_ID}&username=YOUR_USERNAME&password=YOUR_PASSWORD'"
    }

db_host = os.environ.get("DB_HOST")
if db_host is None:
    db_host = "127.0.0.1"

db_name = os.environ.get("DB_NAME")
if db_name is None:
    db_name = "root"

db_password = os.environ.get("DB_PASSWORD")
if db_password is None:
    db_password = "password"

db_user = os.environ.get("DB_USER")
if db_user is None:
    db_user = "root"

engine = create_engine("postgresql://" + db_host + "/" + db_name +
                       "?user=" + db_user + "&password=" + db_password)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

session = SessionLocal()




ioannina = session.query(CityDB).filter_by(name= "Ioannina").first()

if ioannina is None:
    ioannina = CityDB(name= "Ioannina")
try:
    session.add(ioannina)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 1")


dashboard_ioannina = session.query(DashboardDB).filter_by(code="ioannina").first()
if dashboard_ioannina is None:
    dashboard_ioannina = DashboardDB(code="ioannina", City=ioannina)

try:
    session.add(dashboard_ioannina)
    session.commit()
except IntegrityError:
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 1")


maribor = session.query(CityDB).filter_by(name= "Maribor").first()

if maribor is None:
    maribor = CityDB(name= "Maribor")
try:
    session.add(maribor)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 2")


dashboard_maribor = session.query(DashboardDB).filter_by(code="maribor").first()
if dashboard_maribor is None:
    dashboard_maribor = DashboardDB(code="maribor", City=maribor)

try:
    session.add(dashboard_maribor)
    session.commit()
except IntegrityError:
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 2")


grenoble = session.query(CityDB).filter_by(name= "Grenoble-Alpes").first()

if grenoble is None:
    grenoble = CityDB(name= "Grenoble-Alpes")
try:
    session.add(grenoble)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 3")


dashboard_grenoble = session.query(DashboardDB).filter_by(code="grenoble").first()
if dashboard_grenoble is None:
    dashboard_grenoble = DashboardDB(code="grenoble", City=grenoble)

try:
    session.add(dashboard_grenoble)
    session.commit()
except IntegrityError:
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 3")


athens = session.query(CityDB).filter_by(name= "Athens").first()

if athens is None:
    athens = CityDB(name= "Athens")
try:
    session.add(athens)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 4")


dashboard_athens = session.query(DashboardDB).filter_by(code="athens").first()
if dashboard_athens is None:
    dashboard_athens = DashboardDB(code="athens", City=athens)

try:
    session.add(dashboard_athens)
    session.commit()
except IntegrityError:
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 4")


differdange = session.query(CityDB).filter_by(name= "Differdange").first()

if differdange is None:
    differdange = CityDB(name= "Differdange")
try:
    session.add(differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 5")


dashboard_differdange = session.query(DashboardDB).filter_by(code="differdange").first()
if dashboard_differdange is None:
    dashboard_differdange = DashboardDB(code="differdange", City=differdange)

try:
    session.add(dashboard_differdange)
    session.commit()
except IntegrityError:
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 5")


torino = session.query(CityDB).filter_by(name= "Torino").first()

if torino is None:
    torino = CityDB(name= "Torino")
try:
    session.add(torino)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 6")


dashboard_torino = session.query(DashboardDB).filter_by(code="torino").first()
if dashboard_torino is None:
    dashboard_torino = DashboardDB(code="torino", City=torino)

try:
    session.add(dashboard_torino)
    session.commit()
except IntegrityError:
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 6")


cascais = session.query(CityDB).filter_by(name= "Cascais").first()

if cascais is None:
    cascais = CityDB(name= "Cascais")
try:
    session.add(cascais)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 7")


dashboard_cascais = session.query(DashboardDB).filter_by(code="cascais").first()
if dashboard_cascais is None:
    dashboard_cascais = DashboardDB(code="cascais", City=cascais)

try:
    session.add(dashboard_cascais)
    session.commit()
except IntegrityError:
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 7")


sofia = session.query(CityDB).filter_by(name= "Sofia").first()

if sofia is None:
    sofia = CityDB(name= "Sofia")
try:
    session.add(sofia)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 8")


dashboard_sofia = session.query(DashboardDB).filter_by(code="sofia").first()
if dashboard_sofia is None:
    dashboard_sofia = DashboardDB(code="sofia", City=sofia)

try:
    session.add(dashboard_sofia)
    session.commit()
except IntegrityError:
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 8")


kpiMoney_Differdange = session.query(KPIDB).filter_by(id_kpi= "money001", name= "Money Invested", category= "Environment", description= "Measures the money invested in green stuff", provider= "BankService", calculationFrequency= "Weekly", unitText= "Euros", minThreshold= 500.0, maxThreshold= 2000.0).first()

if kpiMoney_Differdange is None:
    kpiMoney_Differdange = KPIDB(id_kpi= "money001", name= "Money Invested", category= "Environment", description= "Measures the money invested in green stuff", provider= "BankService", calculationFrequency= "Weekly", unitText= "Euros", minThreshold= 500.0, maxThreshold= 2000.0, hasCategoryLabel= False, city_id=differdange.id)
try:
    session.add(kpiMoney_Differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 9")


kpiTemp_Differdange = session.query(KPIDB).filter_by(id_kpi= "temp001", name= "Average Temperature", category= "Environment", description= "Measures the average temperature of the city", provider= "WeatherService", calculationFrequency= "Daily", unitText= "Celsius", minThreshold= 15.0, maxThreshold= 35.0).first()

if kpiTemp_Differdange is None:
    kpiTemp_Differdange = KPIDB(id_kpi= "temp001", name= "Average Temperature", category= "Environment", description= "Measures the average temperature of the city", provider= "WeatherService", calculationFrequency= "Daily", unitText= "Celsius", minThreshold= 15.0, maxThreshold= 35.0, hasCategoryLabel= False, city_id=differdange.id)
try:
    session.add(kpiTemp_Differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 10")


kpiCollectedClothes2 = session.query(KPIDB).filter_by(id_kpi= "waste_015", name= "Amount of collected textile clothes", category= "Waste", description= "Amount of collected textile clothes", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", minThreshold= 90.0, maxThreshold= 110.0).first()

if kpiCollectedClothes2 is None:
    kpiCollectedClothes2 = KPIDB(id_kpi= "waste_015", name= "Amount of collected textile clothes", category= "Waste", description= "Amount of collected textile clothes", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", minThreshold= 90.0, maxThreshold= 110.0, city_id=torino.id)
try:
    session.add(kpiCollectedClothes2)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 11")


kpiHouseholdInvolvedThreeBagCollection = session.query(KPIDB).filter_by(id_kpi= "participants_006", name= "Households participating in the three bags collection", category= "Waste", description= "Households participating in the three bags collection", provider= "Torino", calculationFrequency= "Monthly", unitText= "Households", minThreshold= 80.0, maxThreshold= 120.0).first()

if kpiHouseholdInvolvedThreeBagCollection is None:
    kpiHouseholdInvolvedThreeBagCollection = KPIDB(id_kpi= "participants_006", name= "Households participating in the three bags collection", category= "Waste", description= "Households participating in the three bags collection", provider= "Torino", calculationFrequency= "Monthly", unitText= "Households", minThreshold= 80.0, maxThreshold= 120.0, city_id=torino.id)
try:
    session.add(kpiHouseholdInvolvedThreeBagCollection)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 12")


kpiTextileWastePerPerson = session.query(KPIDB).filter_by(id_kpi= "waste_010", name= "Amount of yearly textile waste per person", category= "Waste", description= "Amount of yearly textile waste per person", provider= "City", calculationFrequency= "Yearly", unitText= "Kg", minThreshold= 10.0, maxThreshold= 30.0).first()

if kpiTextileWastePerPerson is None:
    kpiTextileWastePerPerson = KPIDB(id_kpi= "waste_010", name= "Amount of yearly textile waste per person", category= "Waste", description= "Amount of yearly textile waste per person", provider= "City", calculationFrequency= "Yearly", unitText= "Kg", minThreshold= 10.0, maxThreshold= 30.0, city_id=torino.id)
try:
    session.add(kpiTextileWastePerPerson)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 13")


kpiCollectedWaste = session.query(KPIDB).filter_by(id_kpi= "waste_007", name= "Amount of collected textile waste", category= "Waste", description= "Amount of collected textile waste", provider= "ReLearn", calculationFrequency= "Monthly", unitText= "Kg", minThreshold= 5000.0, maxThreshold= 7000.0).first()

if kpiCollectedWaste is None:
    kpiCollectedWaste = KPIDB(id_kpi= "waste_007", name= "Amount of collected textile waste", category= "Waste", description= "Amount of collected textile waste", provider= "ReLearn", calculationFrequency= "Monthly", unitText= "Kg", minThreshold= 5000.0, maxThreshold= 7000.0, city_id=torino.id)
try:
    session.add(kpiCollectedWaste)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 14")


kpiWasteSorted = session.query(KPIDB).filter_by(id_kpi= "waste_006", name= "Amount of correctly sorted waste in bins using ReLearn sensors", category= "Waste", description= "Amount of correctly sorted waste in bins using ReLearn sensors", provider= "ReLearn", calculationFrequency= "Monthly", unitText= "Kg", minThreshold= 800.0, maxThreshold= 1200.0).first()

if kpiWasteSorted is None:
    kpiWasteSorted = KPIDB(id_kpi= "waste_006", name= "Amount of correctly sorted waste in bins using ReLearn sensors", category= "Waste", description= "Amount of correctly sorted waste in bins using ReLearn sensors", provider= "ReLearn", calculationFrequency= "Monthly", unitText= "Kg", minThreshold= 800.0, maxThreshold= 1200.0, city_id=torino.id)
try:
    session.add(kpiWasteSorted)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 15")


kpiCo2Avoided = session.query(KPIDB).filter_by(id_kpi= "co2_001", name= "Co2 avoided through collection of waste through Re4Circular", category= "Waste", description= "Co2 avoided through collection of waste through Re4Circular", provider= "DKSR", calculationFrequency= "Monthly", unitText= "Tons", minThreshold= 2.0, maxThreshold= 8.0).first()

if kpiCo2Avoided is None:
    kpiCo2Avoided = KPIDB(id_kpi= "co2_001", name= "Co2 avoided through collection of waste through Re4Circular", category= "Waste", description= "Co2 avoided through collection of waste through Re4Circular", provider= "DKSR", calculationFrequency= "Monthly", unitText= "Tons", minThreshold= 2.0, maxThreshold= 8.0, city_id=torino.id)
try:
    session.add(kpiCo2Avoided)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 16")


kpiWasteAvoided = session.query(KPIDB).filter_by(id_kpi= "waste_001", name= "Waste avoided through Re4Circular", category= "Waste", description= "Waste avoided through Re4Circular (collecting material before it becomes waste)", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Tons", minThreshold= 8.0, maxThreshold= 12.0).first()

if kpiWasteAvoided is None:
    kpiWasteAvoided = KPIDB(id_kpi= "waste_001", name= "Waste avoided through Re4Circular", category= "Waste", description= "Waste avoided through Re4Circular (collecting material before it becomes waste)", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Tons", minThreshold= 8.0, maxThreshold= 12.0, city_id=torino.id)
try:
    session.add(kpiWasteAvoided)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 17")


kpiReuseBusinesses = session.query(KPIDB).filter_by(id_kpi= "participants_005", name= "Businesses re-using textiles through Re4Circular", category= "Waste", description= "Businesses re-using textiles through Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of businesses", minThreshold= 8.0, maxThreshold= 12.0).first()

if kpiReuseBusinesses is None:
    kpiReuseBusinesses = KPIDB(id_kpi= "participants_005", name= "Businesses re-using textiles through Re4Circular", category= "Waste", description= "Businesses re-using textiles through Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of businesses", minThreshold= 8.0, maxThreshold= 12.0, city_id=torino.id)
try:
    session.add(kpiReuseBusinesses)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 18")


kpiInvolvedBusinesses = session.query(KPIDB).filter_by(id_kpi= "participants_004", name= "Businesses active on Re4Circular", category= "Waste", description= "Businesses active on Re4Circular", unitText= "Number of businesses").first()

if kpiInvolvedBusinesses is None:
    kpiInvolvedBusinesses = KPIDB(id_kpi= "participants_004", name= "Businesses active on Re4Circular", category= "Waste", description= "Businesses active on Re4Circular", unitText= "Number of businesses", city_id=torino.id)
try:
    session.add(kpiInvolvedBusinesses)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 19")


kpiInformedBusinesses = session.query(KPIDB).filter_by(id_kpi= "participants_003", name= "Businesses informed through Re4Circular", category= "Waste", description= "Businesses informed through Re4Circular", unitText= "Number of businesses").first()

if kpiInformedBusinesses is None:
    kpiInformedBusinesses = KPIDB(id_kpi= "participants_003", name= "Businesses informed through Re4Circular", category= "Waste", description= "Businesses informed through Re4Circular", unitText= "Number of businesses", city_id=torino.id)
try:
    session.add(kpiInformedBusinesses)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 20")


kpiInvolvedCitizens = session.query(KPIDB).filter_by(id_kpi= "participants_002", name= "Citizens active on Re4Circular", category= "Waste", description= "Citizens active on Re4Circular", unitText= "Number of people").first()

if kpiInvolvedCitizens is None:
    kpiInvolvedCitizens = KPIDB(id_kpi= "participants_002", name= "Citizens active on Re4Circular", category= "Waste", description= "Citizens active on Re4Circular", unitText= "Number of people", city_id=torino.id)
try:
    session.add(kpiInvolvedCitizens)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 21")


kpiDiscardedWaste = session.query(KPIDB).filter_by(id_kpi= "waste_013", name= "Amount of textile waste discarded from the differentiated share", category= "Waste", description= "Amount of textile waste discarded from the differentiated share", unitText= "Kg").first()

if kpiDiscardedWaste is None:
    kpiDiscardedWaste = KPIDB(id_kpi= "waste_013", name= "Amount of textile waste discarded from the differentiated share", category= "Waste", description= "Amount of textile waste discarded from the differentiated share", unitText= "Kg", city_id=torino.id)
try:
    session.add(kpiDiscardedWaste)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 22")


kpiInformedCitizens = session.query(KPIDB).filter_by(id_kpi= "participants_001", name= "Citizens informed through Re4Circular", category= "Waste", description= "Citizens informed through Re4Circular", unitText= "Number of people").first()

if kpiInformedCitizens is None:
    kpiInformedCitizens = KPIDB(id_kpi= "participants_001", name= "Citizens informed through Re4Circular", category= "Waste", description= "Citizens informed through Re4Circular", unitText= "Number of people", city_id=torino.id)
try:
    session.add(kpiInformedCitizens)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 23")


kpiCollectedTextileWasteEcoIsole = session.query(KPIDB).filter_by(id_kpi= "waste_014", name= "Amount of textile left in the indifferentiated waste (Eco-Isole)", category= "Waste", description= "Amount of textile left in the indifferentiated waste (Eco-Isole)", unitText= "Kg").first()

if kpiCollectedTextileWasteEcoIsole is None:
    kpiCollectedTextileWasteEcoIsole = KPIDB(id_kpi= "waste_014", name= "Amount of textile left in the indifferentiated waste (Eco-Isole)", category= "Waste", description= "Amount of textile left in the indifferentiated waste (Eco-Isole)", unitText= "Kg", city_id=torino.id)
try:
    session.add(kpiCollectedTextileWasteEcoIsole)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 24")


kpiCollectedTextileWaste = session.query(KPIDB).filter_by(id_kpi= "waste_012", name= "Amount of other types of textiles collected", category= "Waste", description= "Amount of other types of textiles collected", unitText= "Kg").first()

if kpiCollectedTextileWaste is None:
    kpiCollectedTextileWaste = KPIDB(id_kpi= "waste_012", name= "Amount of other types of textiles collected", category= "Waste", description= "Amount of other types of textiles collected", unitText= "Kg", city_id=torino.id)
try:
    session.add(kpiCollectedTextileWaste)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 25")


kpiCollectedClothes = session.query(KPIDB).filter_by(id_kpi= "waste_011", name= "Amount of collected textile clothes", category= "Waste", description= "Amount of collected textile clothes", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", minThreshold= 5500.0, maxThreshold= 6500.0).first()

if kpiCollectedClothes is None:
    kpiCollectedClothes = KPIDB(id_kpi= "waste_011", name= "Amount of collected textile clothes", category= "Waste", description= "Amount of collected textile clothes", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", minThreshold= 5500.0, maxThreshold= 6500.0, city_id=torino.id)
try:
    session.add(kpiCollectedClothes)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 26")


kpiCSecondHandCustomers_Cascais = session.query(KPIDB).filter_by(id_kpi= "waste002", name= "Customers in second hand shops", category= "Waste", description= "Daily number of customers in second hand shops", provider= "Shops", calculationFrequency= "Daily", unitText= "Number of people", minThreshold= 500.0, maxThreshold= 1500.0).first()

if kpiCSecondHandCustomers_Cascais is None:
    kpiCSecondHandCustomers_Cascais = KPIDB(id_kpi= "waste002", name= "Customers in second hand shops", category= "Waste", description= "Daily number of customers in second hand shops", provider= "Shops", calculationFrequency= "Daily", unitText= "Number of people", minThreshold= 500.0, maxThreshold= 1500.0, hasCategoryLabel= True, categoryLabelDictionary= {1: "Low", 2: "Medium", 3: "High"}, city_id=cascais.id)
try:
    session.add(kpiCSecondHandCustomers_Cascais)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 27")


kpiCollectedWaste_Cascais = session.query(KPIDB).filter_by(id_kpi= "waste001", name= "Collected Textile Waste in Ton", category= "Waste", description= "Total textile waste collected in Cascais", provider= "WasteDepartment", calculationFrequency= "Weekly", unitText= "Tons", minThreshold= 5.0, maxThreshold= 15.0).first()

if kpiCollectedWaste_Cascais is None:
    kpiCollectedWaste_Cascais = KPIDB(id_kpi= "waste001", name= "Collected Textile Waste in Ton", category= "Waste", description= "Total textile waste collected in Cascais", provider= "WasteDepartment", calculationFrequency= "Weekly", unitText= "Tons", minThreshold= 5.0, maxThreshold= 15.0, hasCategoryLabel= False, city_id=cascais.id)
try:
    session.add(kpiCollectedWaste_Cascais)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 28")


kpiPeakSolarEnergy_Differdange = session.query(KPIDB).filter_by(id_kpi= "energy003", name= "Peak solar energy", category= "Energy", description= "Peak solar energy in Differdange", provider= "Differdange", calculationFrequency= "Monthly", unitText= "KW peak", minThreshold= 800.0, maxThreshold= 1200.0).first()

if kpiPeakSolarEnergy_Differdange is None:
    kpiPeakSolarEnergy_Differdange = KPIDB(id_kpi= "energy003", name= "Peak solar energy", category= "Energy", description= "Peak solar energy in Differdange", provider= "Differdange", calculationFrequency= "Monthly", unitText= "KW peak", minThreshold= 800.0, maxThreshold= 1200.0, hasCategoryLabel= False, city_id=differdange.id)
try:
    session.add(kpiPeakSolarEnergy_Differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 29")


kpiNumberHouseholdRenewableEnergy_Differdange = session.query(KPIDB).filter_by(id_kpi= "energy002", name= "Household with renewable energy", category= "Energy", description= "Number of households producing any kind of renewable energy", provider= "Citizens", calculationFrequency= "Monthly", unitText= "Number", minThreshold= 300.0, maxThreshold= 700.0).first()

if kpiNumberHouseholdRenewableEnergy_Differdange is None:
    kpiNumberHouseholdRenewableEnergy_Differdange = KPIDB(id_kpi= "energy002", name= "Household with renewable energy", category= "Energy", description= "Number of households producing any kind of renewable energy", provider= "Citizens", calculationFrequency= "Monthly", unitText= "Number", minThreshold= 300.0, maxThreshold= 700.0, hasCategoryLabel= False, city_id=differdange.id)
try:
    session.add(kpiNumberHouseholdRenewableEnergy_Differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 30")


kpiTotalRenewableEnergy_Differdange = session.query(KPIDB).filter_by(id_kpi= "energy001", name= "Percentage of renewable energy in Differdange", category= "Energy", description= "Percentage of renewable energy in Differdange based on total amount of energy", provider= "Solution Provider", calculationFrequency= "Monthly", unitText= "Percentage", minThreshold= 15.0, maxThreshold= 25.0).first()

if kpiTotalRenewableEnergy_Differdange is None:
    kpiTotalRenewableEnergy_Differdange = KPIDB(id_kpi= "energy001", name= "Percentage of renewable energy in Differdange", category= "Energy", description= "Percentage of renewable energy in Differdange based on total amount of energy", provider= "Solution Provider", calculationFrequency= "Monthly", unitText= "Percentage", minThreshold= 15.0, maxThreshold= 25.0, hasCategoryLabel= False, city_id=differdange.id)
try:
    session.add(kpiTotalRenewableEnergy_Differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 31")


kpiTrafficCongestion_Sofia = session.query(KPIDB).filter_by(id_kpi= "traffic001", name= "Traffic Congestion Level", category= "Transport", description= "Measures the level of traffic congestion", provider= "TransportDepartment", calculationFrequency= "Hourly", unitText= "Number of Cars", minThreshold= 10.0, maxThreshold= 50.0).first()

if kpiTrafficCongestion_Sofia is None:
    kpiTrafficCongestion_Sofia = KPIDB(id_kpi= "traffic001", name= "Traffic Congestion Level", category= "Transport", description= "Measures the level of traffic congestion", provider= "TransportDepartment", calculationFrequency= "Hourly", unitText= "Number of Cars", minThreshold= 10.0, maxThreshold= 50.0, hasCategoryLabel= False, city_id=sofia.id)
try:
    session.add(kpiTrafficCongestion_Sofia)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 32")


moneyValue1 = session.query(KPIValueDB).filter_by(kpiValue= 1200, timestamp= "2025-07-07 10:00:00").first()

if moneyValue1 is None:
    moneyValue1 = KPIValueDB(kpiValue= 1200, timestamp= "2025-07-07 10:00:00", kpi_id=kpiMoney_Differdange.id)
try:
    session.add(moneyValue1)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 33")


tempValue1 = session.query(KPIValueDB).filter_by(kpiValue= 22, timestamp= "2025-07-07 10:00:00").first()

if tempValue1 is None:
    tempValue1 = KPIValueDB(kpiValue= 22, timestamp= "2025-07-07 10:00:00", kpi_id=kpiTemp_Differdange.id)
try:
    session.add(tempValue1)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 34")


           
city_alias = aliased(CityDB)
           
tablecolumn_alias = aliased(TableColumnDB)
           
dashboard_alias = aliased(DashboardDB)
           
kpi_alias = aliased(KPIDB)
           
visualisation_alias = aliased(VisualisationDB)
           
statchart_alias = aliased(StatChartDB)
           
linechart_alias = aliased(LineChartDB)
           
map_alias = aliased(MapDB)
           
piechart_alias = aliased(PieChartDB)
           
table_alias = aliased(TableDB)
           
barchart_alias = aliased(BarChartDB)
           
kpivalue_alias = aliased(KPIValueDB)
           
mapdata_alias = aliased(MapDataDB)
           
wms_alias = aliased(WMSDB)
           
geojson_alias = aliased(GeoJsonDB)
  



    

# KPI

@app.post("/city/{city_name}/kpi/create", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Create a new KPI",description="", tags=["KPI"])
async def create_kpi(
    city_name: str,
    kpi: KPI = Body(...),
):
    """
    Create a new Key Performance Indicator (KPI) for a specified city.

    This endpoint creates a generic KPI record in the database. All KPIs use the same structure
    with common fields for provider, name, category, thresholds, etc.

    Authentication:
    - Requires JWT token in the header: `Authorization: Bearer <token>`

    Path Parameters:
    - city_name (str): The name of the city (case-insensitive). Must already exist in the system. Supported cities include:
    Torino, Cascais, Differdange, Sofia, Athens, Grenoble-Alpes, Maribor, Ioannina

    Request Body Fields (KPI):
    - name (str, required): The name of the KPI.
    - description (str, required): A detailed description of the KPI.
    - unitText (str, required): The unit of measurement for the KPI (e.g., 'kWh', 'kg', '%').
    - id_kpi (str, required): A unique identifier string for the KPI.
    - provider (str, Optional): The organization or system providing the KPI data.
    - category (str, Optional): The category/domain of the KPI (e.g., 'energy', 'waste', 'transport').
    - calculationFrequency (str, Optional): How often the KPI is calculated (e.g., 'daily', 'monthly', 'yearly').
    - minThreshold (float, Optional): The minimum threshold value for the KPI.
    - maxThreshold (float, Optional): The maximum threshold value for the KPI.
    - hasCategoryLabel (bool, required): Whether the KPI has category labels (default: False).
    - categoryLabelDictionary (dict, optional): A dictionary mapping category labels to their meanings (e.g., {1: "Low", 2: "Medium", 3: "High"}).

    Returns:
    - The ID (int) of the newly created KPI in the database.

    Errors:
    - 404: City not found
    - 400: Duplicate ID (integrity error) or invalid data
    - 500: Internal server error
    """
    # Get city object
    city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower(city_name)).first()
    if not city:
        raise HTTPException(status_code=404, detail=f"City {city_name} not found")
    
    # Create the generic KPI DB object
    try:
        kpi_db = KPIDB(
            id_kpi=kpi.id_kpi,
            name=kpi.name,
            category=kpi.category,
            description=kpi.description,
            provider=kpi.provider,
            calculationFrequency=kpi.calculationFrequency,
            unitText=kpi.unitText,
            minThreshold=kpi.minThreshold,
            maxThreshold=kpi.maxThreshold,
            hasCategoryLabel=kpi.hasCategoryLabel,
            categoryLabelDictionary=kpi.categoryLabelDictionary,
            city_id=city.id
        )
        
        session.add(kpi_db)
        session.commit()
        session.refresh(kpi_db)
        return kpi_db.id
    
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Integrity error occurred. KPI with this ID might already exist.")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/city/{city_name}/kpi/{kpi_id}", dependencies=[Depends(KeycloakBearer())], response_model=List[KPIValue], summary="Add KPI values", tags=["KPI"])
async def add_kpi_values(
    city_name: str,
    kpi_id: int,
    kpis: List[KPIValue] = Body(...),
):
    """
    Add or update KPI values for a specified city and KPI.
    
    This endpoint allows adding or updating time-series data for an existing KPI. If values already 
    exist for the specified timestamps, they will be updated; otherwise, new entries will be created.
    
    Authentication:
    - Requires JWT token in the header: `Authorization: Bearer <token>`
    
    Path Parameters:
    - city_name (str): The name of the city (case-insensitive). Must already exist in the system. Supported cities include:
    Torino, Cascais, Differdange, Sofia, Athens, Grenoble-Alpes, Maribor, Ioannina
    - kpi_id (int): The ID of the KPI to update with new values.
    
    Request Body Fields:
    - List of KPIValue objects, each containing:
      - kpiValue (float, required): The measured value for the KPI at the specified timestamp.
      - timestamp (datetime, required): The date/time for the KPI measurement.
      - categoryLabel (str, required): The category label for the KPI measurement.
    
    Returns:
    - List of created or updated KPIValue objects.
    
    Errors:
    - 404: City or KPI not found
    - 400: Integrity error or invalid data format
    - 500: Internal server error
    """
    # Get city object
    city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower(city_name)).first()
    if not city:
        raise HTTPException(status_code=404, detail=f"City {city_name} not found")
    # Get KPI object
    kpi = session.query(KPIDB).filter_by(id=kpi_id, city_id=city.id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail=f"KPI {kpi_id} not found for city {city_name}")
    db_entries = []
    for kpi_value in kpis:
        try:
            existing_entry = session.query(KPIValueDB).filter_by(
                timestamp=kpi_value.timestamp,
                kpi_id=kpi.id
            ).first()
            
            if existing_entry:
                existing_entry.kpiValue = kpi_value.kpiValue
                existing_entry.categoryLabel = kpi_value.categoryLabel
                session.commit()
                session.refresh(existing_entry)
                db_entries.append(existing_entry)
            else:
                db_entry = KPIValueDB(**kpi_value.dict())
                db_entry.kpi_id = kpi.id
                session.add(db_entry)
                session.commit()
                session.refresh(db_entry)
                db_entries.append(db_entry)
                
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400, detail="Integrity error occurred")
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
            
    return db_entries

@app.delete("/city/{city_name}/kpi/{kpi_id}", dependencies=[Depends(KeycloakBearer())], summary="Delete a KPI", tags=["KPI"])
async def delete_kpi(
    city_name: str,
    kpi_id: int
):
    """
    Delete a KPI and all its associated values for a specified city.
    
    This endpoint deletes a KPI record and all associated KPI values from the database.
    It also handles any visualizations that reference this KPI by setting their kpi_id to NULL.
    This operation is irreversible.
    
    Authentication:
    - Requires JWT token in the header: `Authorization: Bearer <token>`
    
    Path Parameters:
    - city_name (str): The name of the city (case-insensitive). Must already exist in the system. Supported cities include:
    Torino, Cascais, Differdange, Sofia, Athens, Grenoble-Alpes, Maribor, Ioannina
    - kpi_id (int): The ID of the KPI to delete.
    
    Returns:
    - Success message confirming deletion.
    
    Errors:
    - 404: City or KPI not found
    - 500: Internal server error
    """
    try:
        # Get city object
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower(city_name)).first()
        if not city:
            raise HTTPException(status_code=404, detail=f"City {city_name} not found")
        
        # Get KPI object
        kpi = session.query(KPIDB).filter_by(id=kpi_id, city_id=city.id).first()
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI {kpi_id} not found for city {city_name}")
        
        # First, delete all visualizations that reference this KPI
        # This prevents foreign key constraint violations
        session.query(VisualisationDB).filter_by(kpi_id=kpi.id).delete()
        
        # Delete all KPI values (due to foreign key constraint)
        session.query(KPIValueDB).filter_by(kpi_id=kpi.id).delete()
        
        # Delete the KPI itself
        session.delete(kpi)
        session.commit()
        
        return {"message": f"KPI {kpi_id} and all associated values and visualizations deleted successfully from city {city_name}"}
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/city/{city_name}/kpis", response_model=list[object], summary="Get all KPI objects, Value: Torino,Cascais,Differdange,Sofia,Athens,Grenoble-Alpes,Maribor,Ioannina", tags=["KPI"])
async def get_kpis(city_name: str):
    """
    Retrieve all KPIs for a specific city.
    
    This endpoint returns a list of all Key Performance Indicators (KPIs) configured for the specified city.
    The response includes all KPI metadata (name, category, description, thresholds, etc.) but does not include time-series data.
    
    Path Parameters:
    - city_name (str): The name of the city (case-insensitive). Supported cities include:
      Torino, Cascais, Differdange, Sofia, Athens, Grenoble-Alpes, Maribor, Ioannina
    
    Returns:
    - A list of KPI objects, each containing all metadata fields.
      An empty list will be returned if the city exists but has no KPIs.
    
    Errors:
    - 404: City not found
    - 500: Internal server error
    """
    try:
        # Get city object
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower(city_name)).first()
        if not city:
            raise HTTPException(status_code=404, detail=f"City {city_name} not found")
            
        # Query for all KPIs for this city
        kpis = session.query(KPIDB).filter(KPIDB.city_id == city.id).all()
        
        # Convert SQLAlchemy objects to dictionaries
        results_list = []
        for kpi in kpis:
            kpi_dict = {
                "id": kpi.id,
                "id_kpi": kpi.id_kpi,
                "name": kpi.name,
                "category": kpi.category,
                "description": kpi.description,
                "provider": kpi.provider,
                "calculationFrequency": kpi.calculationFrequency,
                "unitText": kpi.unitText,
                "minThreshold": kpi.minThreshold,
                "maxThreshold": kpi.maxThreshold,
                "hasCategoryLabel": kpi.hasCategoryLabel,
                "categoryLabelDictionary": kpi.categoryLabelDictionary
            }
            results_list.append(kpi_dict)
            
        return results_list
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Visualisations

            
@app.post("/ioannina/visualization/BarChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_BarChart_ioannina(id: int, chart: BarChart= Body(..., description="Chart object to add")):
    db_entry = BarChartDB(**chart.dict())
    existing_chart = session.query(BarChartDB).filter(BarChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = BarChartDB(**chart.dict())
        db_entry.consistOf = dashboard_ioannina
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/ioannina/visualization/Map/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Map_ioannina(id: int, chart: Map= Body(..., description="Chart object to add")):
    db_entry = MapDB(**chart.dict())
    existing_chart = session.query(MapDB).filter(MapDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = MapDB(**chart.dict())
        db_entry.consistOf = dashboard_ioannina
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/ioannina/visualization/LineChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_LineChart_ioannina(id: int, chart: LineChart= Body(..., description="Chart object to add")):
    db_entry = LineChartDB(**chart.dict())
    existing_chart = session.query(LineChartDB).filter(LineChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = LineChartDB(**chart.dict())
        db_entry.consistOf = dashboard_ioannina
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/ioannina/visualization/Table/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Table_ioannina(id: int, chart: Table= Body(..., description="Chart object to add")):
    db_entry = TableDB(**chart.dict())
    existing_chart = session.query(TableDB).filter(TableDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = TableDB(**chart.dict())
        db_entry.consistOf = dashboard_ioannina
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/ioannina/visualization/StatChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_StatChart_ioannina(id: int, chart: StatChart= Body(..., description="Chart object to add")):
    db_entry = StatChartDB(**chart.dict())
    existing_chart = session.query(StatChartDB).filter(StatChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = StatChartDB(**chart.dict())
        db_entry.consistOf = dashboard_ioannina
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/ioannina/visualization/PieChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_PieChart_ioannina(id: int, chart: PieChart= Body(..., description="Chart object to add")):
    db_entry = PieChartDB(**chart.dict())
    existing_chart = session.query(PieChartDB).filter(PieChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = PieChartDB(**chart.dict())
        db_entry.consistOf = dashboard_ioannina
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
        
@app.delete("/ioannina/visualizations")
async def delete_visualizations_ioannina(ids: List[int], dependencies=[Depends(KeycloakBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            if row.consistOf and row.consistOf.code == "ioannina":
                session.delete(row)
        # Delete the row
        session.commit()
        return {"message": "Records deleted successfully"}
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Close the session
        print("COOL")

                
@app.post("/maribor/visualization/BarChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_BarChart_maribor(id: int, chart: BarChart= Body(..., description="Chart object to add")):
    db_entry = BarChartDB(**chart.dict())
    existing_chart = session.query(BarChartDB).filter(BarChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = BarChartDB(**chart.dict())
        db_entry.consistOf = dashboard_maribor
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/maribor/visualization/Map/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Map_maribor(id: int, chart: Map= Body(..., description="Chart object to add")):
    db_entry = MapDB(**chart.dict())
    existing_chart = session.query(MapDB).filter(MapDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = MapDB(**chart.dict())
        db_entry.consistOf = dashboard_maribor
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/maribor/visualization/LineChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_LineChart_maribor(id: int, chart: LineChart= Body(..., description="Chart object to add")):
    db_entry = LineChartDB(**chart.dict())
    existing_chart = session.query(LineChartDB).filter(LineChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = LineChartDB(**chart.dict())
        db_entry.consistOf = dashboard_maribor
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/maribor/visualization/Table/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Table_maribor(id: int, chart: Table= Body(..., description="Chart object to add")):
    db_entry = TableDB(**chart.dict())
    existing_chart = session.query(TableDB).filter(TableDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = TableDB(**chart.dict())
        db_entry.consistOf = dashboard_maribor
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/maribor/visualization/StatChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_StatChart_maribor(id: int, chart: StatChart= Body(..., description="Chart object to add")):
    db_entry = StatChartDB(**chart.dict())
    existing_chart = session.query(StatChartDB).filter(StatChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = StatChartDB(**chart.dict())
        db_entry.consistOf = dashboard_maribor
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/maribor/visualization/PieChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_PieChart_maribor(id: int, chart: PieChart= Body(..., description="Chart object to add")):
    db_entry = PieChartDB(**chart.dict())
    existing_chart = session.query(PieChartDB).filter(PieChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = PieChartDB(**chart.dict())
        db_entry.consistOf = dashboard_maribor
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
        
@app.delete("/maribor/visualizations")
async def delete_visualizations_maribor(ids: List[int], dependencies=[Depends(KeycloakBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:

            if row.consistOf and row.consistOf.code == "maribor":
                session.delete(row)
        # Delete the row
        session.commit()
        return {"message": "Records deleted successfully"}
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Close the session
        print("COOL")

                
@app.post("/grenoble/visualization/BarChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_BarChart_grenoble(id: int, chart: BarChart= Body(..., description="Chart object to add")):
    db_entry = BarChartDB(**chart.dict())
    existing_chart = session.query(BarChartDB).filter(BarChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = BarChartDB(**chart.dict())
        db_entry.consistOf = dashboard_grenoble
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/grenoble/visualization/Map/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Map_grenoble(id: int, chart: Map= Body(..., description="Chart object to add")):
    db_entry = MapDB(**chart.dict())
    existing_chart = session.query(MapDB).filter(MapDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = MapDB(**chart.dict())
        db_entry.consistOf = dashboard_grenoble
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/grenoble/visualization/LineChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_LineChart_grenoble(id: int, chart: LineChart= Body(..., description="Chart object to add")):
    db_entry = LineChartDB(**chart.dict())
    existing_chart = session.query(LineChartDB).filter(LineChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = LineChartDB(**chart.dict())
        db_entry.consistOf = dashboard_grenoble
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/grenoble/visualization/Table/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Table_grenoble(id: int, chart: Table= Body(..., description="Chart object to add")):
    db_entry = TableDB(**chart.dict())
    existing_chart = session.query(TableDB).filter(TableDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = TableDB(**chart.dict())
        db_entry.consistOf = dashboard_grenoble
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/grenoble/visualization/StatChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_StatChart_grenoble(id: int, chart: StatChart= Body(..., description="Chart object to add")):
    db_entry = StatChartDB(**chart.dict())
    existing_chart = session.query(StatChartDB).filter(StatChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = StatChartDB(**chart.dict())
        db_entry.consistOf = dashboard_grenoble
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/grenoble/visualization/PieChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_PieChart_grenoble(id: int, chart: PieChart= Body(..., description="Chart object to add")):
    db_entry = PieChartDB(**chart.dict())
    existing_chart = session.query(PieChartDB).filter(PieChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = PieChartDB(**chart.dict())
        db_entry.consistOf = dashboard_grenoble
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
        
@app.delete("/grenoble/visualizations")
async def delete_visualizations_grenoble(ids: List[int], dependencies=[Depends(KeycloakBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:

            if row.consistOf and row.consistOf.code == "grenoble":
                session.delete(row)
        # Delete the row
        session.commit()
        return {"message": "Records deleted successfully"}
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Close the session
        print("COOL")

                
@app.post("/athens/visualization/BarChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_BarChart_athens(id: int, chart: BarChart= Body(..., description="Chart object to add")):
    db_entry = BarChartDB(**chart.dict())
    existing_chart = session.query(BarChartDB).filter(BarChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = BarChartDB(**chart.dict())
        db_entry.consistOf = dashboard_athens
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/athens/visualization/Map/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Map_athens(id: int, chart: Map= Body(..., description="Chart object to add")):
    db_entry = MapDB(**chart.dict())
    existing_chart = session.query(MapDB).filter(MapDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = MapDB(**chart.dict())
        db_entry.consistOf = dashboard_athens
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/athens/visualization/LineChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_LineChart_athens(id: int, chart: LineChart= Body(..., description="Chart object to add")):
    db_entry = LineChartDB(**chart.dict())
    existing_chart = session.query(LineChartDB).filter(LineChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = LineChartDB(**chart.dict())
        db_entry.consistOf = dashboard_athens
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/athens/visualization/Table/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Table_athens(id: int, chart: Table= Body(..., description="Chart object to add")):
    db_entry = TableDB(**chart.dict())
    existing_chart = session.query(TableDB).filter(TableDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = TableDB(**chart.dict())
        db_entry.consistOf = dashboard_athens
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/athens/visualization/StatChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_StatChart_athens(id: int, chart: StatChart= Body(..., description="Chart object to add")):
    db_entry = StatChartDB(**chart.dict())
    existing_chart = session.query(StatChartDB).filter(StatChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = StatChartDB(**chart.dict())
        db_entry.consistOf = dashboard_athens
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/athens/visualization/PieChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_PieChart_athens(id: int, chart: PieChart= Body(..., description="Chart object to add")):
    db_entry = PieChartDB(**chart.dict())
    existing_chart = session.query(PieChartDB).filter(PieChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = PieChartDB(**chart.dict())
        db_entry.consistOf = dashboard_athens
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
        
@app.delete("/athens/visualizations")
async def delete_visualizations_athens(ids: List[int], dependencies=[Depends(KeycloakBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:

            if row.consistOf and row.consistOf.code == "athens":
                session.delete(row)
        # Delete the row
        session.commit()
        return {"message": "Records deleted successfully"}
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Close the session
        print("COOL")

                
@app.post("/differdange/visualization/BarChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_BarChart_differdange(id: int, chart: BarChart= Body(..., description="Chart object to add")):
    db_entry = BarChartDB(**chart.dict())
    existing_chart = session.query(BarChartDB).filter(BarChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = BarChartDB(**chart.dict())
        db_entry.consistOf = dashboard_differdange
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/differdange/visualization/Map/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Map_differdange(id: int, chart: Map= Body(..., description="Chart object to add")):
    db_entry = MapDB(**chart.dict())
    existing_chart = session.query(MapDB).filter(MapDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = MapDB(**chart.dict())
        db_entry.consistOf = dashboard_differdange
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/differdange/visualization/LineChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_LineChart_differdange(id: int, chart: LineChart= Body(..., description="Chart object to add")):
    db_entry = LineChartDB(**chart.dict())
    existing_chart = session.query(LineChartDB).filter(LineChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = LineChartDB(**chart.dict())
        db_entry.consistOf = dashboard_differdange
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/differdange/visualization/Table/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Table_differdange(id: int, chart: Table= Body(..., description="Chart object to add")):
    db_entry = TableDB(**chart.dict())
    existing_chart = session.query(TableDB).filter(TableDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = TableDB(**chart.dict())
        db_entry.consistOf = dashboard_differdange
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/differdange/visualization/StatChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_StatChart_differdange(id: int, chart: StatChart= Body(..., description="Chart object to add")):
    db_entry = StatChartDB(**chart.dict())
    existing_chart = session.query(StatChartDB).filter(StatChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = StatChartDB(**chart.dict())
        db_entry.consistOf = dashboard_differdange
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/differdange/visualization/PieChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_PieChart_differdange(id: int, chart: PieChart= Body(..., description="Chart object to add")):
    db_entry = PieChartDB(**chart.dict())
    existing_chart = session.query(PieChartDB).filter(PieChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = PieChartDB(**chart.dict())
        db_entry.consistOf = dashboard_differdange
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
        
@app.delete("/differdange/visualizations")
async def delete_visualizations_differdange(ids: List[int], dependencies=[Depends(KeycloakBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:

            if row.consistOf and row.consistOf.code == "differdange":
                session.delete(row)
        # Delete the row
        session.commit()
        return {"message": "Records deleted successfully"}
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Close the session
        print("COOL")

                
@app.post("/torino/visualization/BarChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_BarChart_torino(id: int, chart: BarChart= Body(..., description="Chart object to add")):
    db_entry = BarChartDB(**chart.dict())
    existing_chart = session.query(BarChartDB).filter(BarChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = BarChartDB(**chart.dict())
        db_entry.consistOf = dashboard_torino
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/torino/visualization/Map/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Map_torino(id: int, chart: Map= Body(..., description="Chart object to add")):
    db_entry = MapDB(**chart.dict())
    existing_chart = session.query(MapDB).filter(MapDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = MapDB(**chart.dict())
        db_entry.consistOf = dashboard_torino
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/torino/visualization/LineChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_LineChart_torino(id: int, chart: LineChart= Body(..., description="Chart object to add")):
    db_entry = LineChartDB(**chart.dict())
    existing_chart = session.query(LineChartDB).filter(LineChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = LineChartDB(**chart.dict())
        db_entry.consistOf = dashboard_torino
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/torino/visualization/Table/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Table_torino(id: int, chart: Table= Body(..., description="Chart object to add")):
    db_entry = TableDB(**chart.dict())
    existing_chart = session.query(TableDB).filter(TableDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = TableDB(**chart.dict())
        db_entry.consistOf = dashboard_torino
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/torino/visualization/StatChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_StatChart_torino(id: int, chart: StatChart= Body(..., description="Chart object to add")):
    db_entry = StatChartDB(**chart.dict())
    existing_chart = session.query(StatChartDB).filter(StatChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = StatChartDB(**chart.dict())
        db_entry.consistOf = dashboard_torino
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/torino/visualization/PieChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_PieChart_torino(id: int, chart: PieChart= Body(..., description="Chart object to add")):
    db_entry = PieChartDB(**chart.dict())
    existing_chart = session.query(PieChartDB).filter(PieChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = PieChartDB(**chart.dict())
        db_entry.consistOf = dashboard_torino
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
        
@app.delete("/torino/visualizations")
async def delete_visualizations_torino(ids: List[int], dependencies=[Depends(KeycloakBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:

            if row.consistOf and row.consistOf.code == "torino":
                session.delete(row)
        # Delete the row
        session.commit()
        return {"message": "Records deleted successfully"}
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Close the session
        print("COOL")

                
@app.post("/cascais/visualization/BarChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_BarChart_cascais(id: int, chart: BarChart= Body(..., description="Chart object to add")):
    db_entry = BarChartDB(**chart.dict())
    existing_chart = session.query(BarChartDB).filter(BarChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = BarChartDB(**chart.dict())
        db_entry.consistOf = dashboard_cascais
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/cascais/visualization/Map/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Map_cascais(id: int, chart: Map= Body(..., description="Chart object to add")):
    db_entry = MapDB(**chart.dict())
    existing_chart = session.query(MapDB).filter(MapDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = MapDB(**chart.dict())
        db_entry.consistOf = dashboard_cascais
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/cascais/visualization/LineChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_LineChart_cascais(id: int, chart: LineChart= Body(..., description="Chart object to add")):
    db_entry = LineChartDB(**chart.dict())
    existing_chart = session.query(LineChartDB).filter(LineChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = LineChartDB(**chart.dict())
        db_entry.consistOf = dashboard_cascais
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/cascais/visualization/Table/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Table_cascais(id: int, chart: Table= Body(..., description="Chart object to add")):
    db_entry = TableDB(**chart.dict())
    existing_chart = session.query(TableDB).filter(TableDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = TableDB(**chart.dict())
        db_entry.consistOf = dashboard_cascais
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/cascais/visualization/StatChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_StatChart_cascais(id: int, chart: StatChart= Body(..., description="Chart object to add")):
    db_entry = StatChartDB(**chart.dict())
    existing_chart = session.query(StatChartDB).filter(StatChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = StatChartDB(**chart.dict())
        db_entry.consistOf = dashboard_cascais
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/cascais/visualization/PieChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_PieChart_cascais(id: int, chart: PieChart= Body(..., description="Chart object to add")):
    db_entry = PieChartDB(**chart.dict())
    existing_chart = session.query(PieChartDB).filter(PieChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = PieChartDB(**chart.dict())
        db_entry.consistOf = dashboard_cascais
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
        
@app.delete("/cascais/visualizations")
async def delete_visualizations_cascais(ids: List[int], dependencies=[Depends(KeycloakBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            print({key: value for key, value in row.__dict__.items() if not key.startswith('_')})
            if row.consistOf and row.consistOf.code == "cascais":
                session.delete(row)
        # Delete the row
        session.commit()
        return {"message": "Records deleted successfully"}
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Close the session
        print("COOL")

                
@app.post("/sofia/visualization/BarChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_BarChart_sofia(id: int, chart: BarChart= Body(..., description="Chart object to add")):
    db_entry = BarChartDB(**chart.dict())
    existing_chart = session.query(BarChartDB).filter(BarChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = BarChartDB(**chart.dict())
        db_entry.consistOf = dashboard_sofia
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/sofia/visualization/Map/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Map_sofia(id: int, chart: Map= Body(..., description="Chart object to add")):
    db_entry = MapDB(**chart.dict())
    existing_chart = session.query(MapDB).filter(MapDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = MapDB(**chart.dict())
        db_entry.consistOf = dashboard_sofia
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
                        
@app.post("/sofia/visualization/LineChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_LineChart_sofia(id: int, chart: LineChart= Body(..., description="Chart object to add")):
    db_entry = LineChartDB(**chart.dict())
    existing_chart = session.query(LineChartDB).filter(LineChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = LineChartDB(**chart.dict())
        db_entry.consistOf = dashboard_sofia
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/sofia/visualization/Table/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_Table_sofia(id: int, chart: Table= Body(..., description="Chart object to add")):
    db_entry = TableDB(**chart.dict())
    existing_chart = session.query(TableDB).filter(TableDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = TableDB(**chart.dict())
        db_entry.consistOf = dashboard_sofia
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/sofia/visualization/StatChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_StatChart_sofia(id: int, chart: StatChart= Body(..., description="Chart object to add")):
    db_entry = StatChartDB(**chart.dict())
    existing_chart = session.query(StatChartDB).filter(StatChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = StatChartDB(**chart.dict())
        db_entry.consistOf = dashboard_sofia
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
                        
@app.post("/sofia/visualization/PieChart/{id}", dependencies=[Depends(KeycloakBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_PieChart_sofia(id: int, chart: PieChart= Body(..., description="Chart object to add")):
    db_entry = PieChartDB(**chart.dict())
    existing_chart = session.query(PieChartDB).filter(PieChartDB.i == db_entry.i).first()
    if existing_chart:
        # If the chart already exists, update it with the new data
        existing_chart_data = chart.dict(exclude_unset=True)
        for key, value in existing_chart_data.items():
            setattr(existing_chart, key, value)
        session.commit()
        session.refresh(existing_chart)
        return existing_chart.id
    else:
        # If the chart does not exist, create a new one
        db_entry = PieChartDB(**chart.dict())
        db_entry.consistOf = dashboard_sofia
        db_entry.kpi_id = id
        try:
            session.add(db_entry)
            session.commit()
            session.refresh(db_entry)
        except IntegrityError: 
            session.rollback()
            raise HTTPException(status_code=400, detail="Error integrity")
        except:
            session.rollback()
            raise HTTPException(status_code=400, detail="Error")
        return db_entry.id
                
            
        
@app.delete("/sofia/visualizations")
async def delete_visualizations_sofia(ids: List[int], dependencies=[Depends(KeycloakBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:

            if row.consistOf and row.consistOf.code == "sofia":
                session.delete(row)
        # Delete the row
        session.commit()
        return {"message": "Records deleted successfully"}
    except Exception as e:
        # Rollback in case of error
        session.rollback()
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")
    finally:
        # Close the session
        print("COOL")

    


     
@app.get("/ioannina/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI_Info"])
async def get_kpis_ioannina():
    try:
        # Query for all KPIs for this specific city
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower("ioannina")).first()
        if not city:
            return []
        
        kpis = session.query(KPIDB).filter(KPIDB.city_id == city.id).all()
        
        # Convert SQLAlchemy objects to dictionaries
        results_list = []
        for kpi in kpis:
            kpi_dict = {
                "id": kpi.id,
                "id_kpi": kpi.id_kpi,
                "name": kpi.name,
                "category": kpi.category,
                "description": kpi.description,
                "provider": kpi.provider,
                "calculationFrequency": kpi.calculationFrequency,
                "unitText": kpi.unitText,
                "minThreshold": kpi.minThreshold,
                "maxThreshold": kpi.maxThreshold,
                "hasCategoryLabel": kpi.hasCategoryLabel,
                "categoryLabelDictionary": kpi.categoryLabelDictionary
            }
            results_list.append(kpi_dict)
            
        return results_list
    except Exception as e:
        return [{"error": str(e)}]
    
@app.post("/ioannina/geojson/")
async def upload_geojson_ioannina(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(KeycloakBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
    try:
        # Create a new GeoJson entry
        new_data = GeoJsonDB(
            title=title,
            data=json.dumps(geojson_data),
            hasMapData=ioannina
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/ioannina/geojson/")
async def get_geojson_for_ioannina():
    results = []
    try:
        # Query the database for geospatial data for the given city
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == ioannina.id).all()

        # Check if data exists for the city
        if not geojson_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in geojson_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/ioannina/wms/")
async def upload_wms_ioannina(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(KeycloakBearer())], name: str = Query(..., description="Name of the wms artifact")):
    try:
        
        # Create a new GeoJson entry
        new_data = WMSDB(
            title=title,
            url=url,
            name=name,
            hasMapData=ioannina
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/ioannina/wms/")
async def get_wms_for_ioannina():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == ioannina.id).all()

        # Check if data exists for the city
        if not wms_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in wms_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/ioannina/mapdata/")    
async def get_mapdata_for_ioannina():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == ioannina.id).all()

        # Check if data exists for the city
        if not wms_data:
            print("sucks")
        for result in wms_data: 
            results.append(result)
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == ioannina.id).all()

        # Check if data exists for the city
        if not geojson_data:
            print("sucks")
        for result in geojson_data: 
            results.append(result)
        return results            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")     
        
@app.get("/ioannina/visualizations", response_model=list[object], summary="get visualization objects", tags = ["Visualisation"])
async def get_visualizations_ioannina():
    try:
        results_list = []
                    
        query = session.query(visualisation_alias, barchart_alias).\
            join(barchart_alias, visualisation_alias.id == barchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("ioannina"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, map_alias).\
            join(map_alias, visualisation_alias.id == map_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("ioannina"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, linechart_alias).\
            join(linechart_alias, visualisation_alias.id == linechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("ioannina"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, table_alias).\
            join(table_alias, visualisation_alias.id == table_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("ioannina"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, statchart_alias).\
            join(statchart_alias, visualisation_alias.id == statchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("ioannina"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, piechart_alias).\
            join(piechart_alias, visualisation_alias.id == piechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("ioannina"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/maribor/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI_Info"])
async def get_kpis_maribor():
    try:
        # Query for all KPIs for this specific city
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower("maribor")).first()
        if not city:
            return []
        
        kpis = session.query(KPIDB).filter(KPIDB.city_id == city.id).all()
        
        # Convert SQLAlchemy objects to dictionaries
        results_list = []
        for kpi in kpis:
            kpi_dict = {
                "id": kpi.id,
                "id_kpi": kpi.id_kpi,
                "name": kpi.name,
                "category": kpi.category,
                "description": kpi.description,
                "provider": kpi.provider,
                "calculationFrequency": kpi.calculationFrequency,
                "unitText": kpi.unitText,
                "minThreshold": kpi.minThreshold,
                "maxThreshold": kpi.maxThreshold,
                "hasCategoryLabel": kpi.hasCategoryLabel,
                "categoryLabelDictionary": kpi.categoryLabelDictionary
            }
            results_list.append(kpi_dict)
            
        return results_list
    except Exception as e:
        return [{"error": str(e)}]
    
@app.post("/maribor/geojson/")
async def upload_geojson_maribor(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(KeycloakBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
    try:
        # Create a new GeoJson entry
        new_data = GeoJsonDB(
            title=title,
            data=json.dumps(geojson_data),
            hasMapData=maribor
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/maribor/geojson/")
async def get_geojson_for_maribor():
    results = []
    try:
        # Query the database for geospatial data for the given city
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == maribor.id).all()

        # Check if data exists for the city
        if not geojson_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in geojson_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/maribor/wms/")
async def upload_wms_maribor(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(KeycloakBearer())], name: str = Query(..., description="Name of the wms artifact")):
    try:
        
        # Create a new GeoJson entry
        new_data = WMSDB(
            title=title,
            url=url,
            name=name,
            hasMapData=maribor
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/maribor/wms/")
async def get_wms_for_maribor():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == maribor.id).all()

        # Check if data exists for the city
        if not wms_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in wms_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/maribor/mapdata/")    
async def get_mapdata_for_maribor():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == maribor.id).all()

        # Check if data exists for the city
        if not wms_data:
            print("sucks")
        for result in wms_data: 
            results.append(result)
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == maribor.id).all()

        # Check if data exists for the city
        if not geojson_data:
            print("sucks")
        for result in geojson_data: 
            results.append(result)
        return results            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")     
        
@app.get("/maribor/visualizations", response_model=list[object], summary="get visualization objects", tags = ["Visualisation"])
async def get_visualizations_maribor():
    try:
        results_list = []
                    
        query = session.query(visualisation_alias, barchart_alias).\
            join(barchart_alias, visualisation_alias.id == barchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("maribor"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, map_alias).\
            join(map_alias, visualisation_alias.id == map_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("maribor"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, linechart_alias).\
            join(linechart_alias, visualisation_alias.id == linechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("maribor"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, table_alias).\
            join(table_alias, visualisation_alias.id == table_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("maribor"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, statchart_alias).\
            join(statchart_alias, visualisation_alias.id == statchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("maribor"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, piechart_alias).\
            join(piechart_alias, visualisation_alias.id == piechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("maribor"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/grenoble/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI_Info"])
async def get_kpis_grenoble():
    try:
        # Query for all KPIs for this specific city
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower("grenoble")).first()
        if not city:
            return []
        
        kpis = session.query(KPIDB).filter(KPIDB.city_id == city.id).all()
        
        # Convert SQLAlchemy objects to dictionaries
        results_list = []
        for kpi in kpis:
            kpi_dict = {
                "id": kpi.id,
                "id_kpi": kpi.id_kpi,
                "name": kpi.name,
                "category": kpi.category,
                "description": kpi.description,
                "provider": kpi.provider,
                "calculationFrequency": kpi.calculationFrequency,
                "unitText": kpi.unitText,
                "minThreshold": kpi.minThreshold,
                "maxThreshold": kpi.maxThreshold,
                "hasCategoryLabel": kpi.hasCategoryLabel,
                "categoryLabelDictionary": kpi.categoryLabelDictionary
            }
            results_list.append(kpi_dict)
            
        return results_list
    except Exception as e:
        return [{"error": str(e)}]
    
@app.post("/grenoble/geojson/")
async def upload_geojson_grenoble(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(KeycloakBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
    try:
        # Create a new GeoJson entry
        new_data = GeoJsonDB(
            title=title,
            data=json.dumps(geojson_data),
            hasMapData=grenoble
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/grenoble/geojson/")
async def get_geojson_for_grenoble():
    results = []
    try:
        # Query the database for geospatial data for the given city
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == grenoble.id).all()

        # Check if data exists for the city
        if not geojson_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in geojson_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/grenoble/wms/")
async def upload_wms_grenoble(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(KeycloakBearer())], name: str = Query(..., description="Name of the wms artifact")):
    try:
        
        # Create a new GeoJson entry
        new_data = WMSDB(
            title=title,
            url=url,
            name=name,
            hasMapData=grenoble
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/grenoble/wms/")
async def get_wms_for_grenoble():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == grenoble.id).all()

        # Check if data exists for the city
        if not wms_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in wms_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/grenoble/mapdata/")    
async def get_mapdata_for_grenoble():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == grenoble.id).all()

        # Check if data exists for the city
        if not wms_data:
            print("sucks")
        for result in wms_data: 
            results.append(result)
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == grenoble.id).all()

        # Check if data exists for the city
        if not geojson_data:
            print("sucks")
        for result in geojson_data: 
            results.append(result)
        return results            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")     
        
@app.get("/grenoble/visualizations", response_model=list[object], summary="get visualization objects", tags = ["Visualisation"])
async def get_visualizations_grenoble():
    try:
        results_list = []
                    
        query = session.query(visualisation_alias, barchart_alias).\
            join(barchart_alias, visualisation_alias.id == barchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("grenoble"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, map_alias).\
            join(map_alias, visualisation_alias.id == map_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("grenoble"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, linechart_alias).\
            join(linechart_alias, visualisation_alias.id == linechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("grenoble"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, table_alias).\
            join(table_alias, visualisation_alias.id == table_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("grenoble"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, statchart_alias).\
            join(statchart_alias, visualisation_alias.id == statchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("grenoble"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, piechart_alias).\
            join(piechart_alias, visualisation_alias.id == piechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("grenoble"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/athens/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI_Info"])
async def get_kpis_athens():
    try:
        # Query for all KPIs for this specific city
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower("athens")).first()
        if not city:
            return []
        
        kpis = session.query(KPIDB).filter(KPIDB.city_id == city.id).all()
        
        # Convert SQLAlchemy objects to dictionaries
        results_list = []
        for kpi in kpis:
            kpi_dict = {
                "id": kpi.id,
                "id_kpi": kpi.id_kpi,
                "name": kpi.name,
                "category": kpi.category,
                "description": kpi.description,
                "provider": kpi.provider,
                "calculationFrequency": kpi.calculationFrequency,
                "unitText": kpi.unitText,
                "minThreshold": kpi.minThreshold,
                "maxThreshold": kpi.maxThreshold,
                "hasCategoryLabel": kpi.hasCategoryLabel,
                "categoryLabelDictionary": kpi.categoryLabelDictionary
            }
            results_list.append(kpi_dict)
            
        return results_list
    except Exception as e:
        return [{"error": str(e)}]
    
@app.post("/athens/geojson/")
async def upload_geojson_athens(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(KeycloakBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
    try:
        # Create a new GeoJson entry
        new_data = GeoJsonDB(
            title=title,
            data=json.dumps(geojson_data),
            hasMapData=athens
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/athens/geojson/")
async def get_geojson_for_athens():
    results = []
    try:
        # Query the database for geospatial data for the given city
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == athens.id).all()

        # Check if data exists for the city
        if not geojson_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in geojson_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/athens/wms/")
async def upload_wms_athens(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(KeycloakBearer())], name: str = Query(..., description="Name of the wms artifact")):
    try:
        
        # Create a new GeoJson entry
        new_data = WMSDB(
            title=title,
            url=url,
            name=name,
            hasMapData=athens
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/athens/wms/")
async def get_wms_for_athens():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == athens.id).all()

        # Check if data exists for the city
        if not wms_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in wms_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/athens/mapdata/")    
async def get_mapdata_for_athens():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == athens.id).all()

        # Check if data exists for the city
        if not wms_data:
            print("sucks")
        for result in wms_data: 
            results.append(result)
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == athens.id).all()

        # Check if data exists for the city
        if not geojson_data:
            print("sucks")
        for result in geojson_data: 
            results.append(result)
        return results            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")     
        
@app.get("/athens/visualizations", response_model=list[object], summary="get visualization objects", tags = ["Visualisation"])
async def get_visualizations_athens():
    try:
        results_list = []
                    
        query = session.query(visualisation_alias, barchart_alias).\
            join(barchart_alias, visualisation_alias.id == barchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("athens"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, map_alias).\
            join(map_alias, visualisation_alias.id == map_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("athens"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, linechart_alias).\
            join(linechart_alias, visualisation_alias.id == linechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("athens"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, table_alias).\
            join(table_alias, visualisation_alias.id == table_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("athens"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, statchart_alias).\
            join(statchart_alias, visualisation_alias.id == statchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("athens"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, piechart_alias).\
            join(piechart_alias, visualisation_alias.id == piechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("athens"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/differdange/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI_Info"])
async def get_kpis_differdange():
    try:
        # Query for all KPIs for this specific city
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower("differdange")).first()
        if not city:
            return []
        
        kpis = session.query(KPIDB).filter(KPIDB.city_id == city.id).all()
        
        # Convert SQLAlchemy objects to dictionaries
        results_list = []
        for kpi in kpis:
            kpi_dict = {
                "id": kpi.id,
                "id_kpi": kpi.id_kpi,
                "name": kpi.name,
                "category": kpi.category,
                "description": kpi.description,
                "provider": kpi.provider,
                "calculationFrequency": kpi.calculationFrequency,
                "unitText": kpi.unitText,
                "minThreshold": kpi.minThreshold,
                "maxThreshold": kpi.maxThreshold,
                "hasCategoryLabel": kpi.hasCategoryLabel,
                "categoryLabelDictionary": kpi.categoryLabelDictionary
            }
            results_list.append(kpi_dict)
            
        return results_list
    except Exception as e:
        return [{"error": str(e)}]
    
@app.post("/differdange/geojson/")
async def upload_geojson_differdange(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(KeycloakBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
    try:
        # Create a new GeoJson entry
        new_data = GeoJsonDB(
            title=title,
            data=json.dumps(geojson_data),
            hasMapData=differdange
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/differdange/geojson/")
async def get_geojson_for_differdange():
    results = []
    try:
        # Query the database for geospatial data for the given city
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == differdange.id).all()

        # Check if data exists for the city
        if not geojson_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in geojson_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/differdange/wms/")
async def upload_wms_differdange(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(KeycloakBearer())], name: str = Query(..., description="Name of the wms artifact")):
    try:
        
        # Create a new GeoJson entry
        new_data = WMSDB(
            title=title,
            url=url,
            name=name,
            hasMapData=differdange
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/differdange/wms/")
async def get_wms_for_differdange():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == differdange.id).all()

        # Check if data exists for the city
        if not wms_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in wms_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/differdange/mapdata/")    
async def get_mapdata_for_differdange():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == differdange.id).all()

        # Check if data exists for the city
        if not wms_data:
            print("sucks")
        for result in wms_data: 
            results.append(result)
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == differdange.id).all()

        # Check if data exists for the city
        if not geojson_data:
            print("sucks")
        for result in geojson_data: 
            results.append(result)
        return results            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")     
        
@app.get("/differdange/visualizations", response_model=list[object], summary="get visualization objects", tags = ["Visualisation"])
async def get_visualizations_differdange():
    try:
        results_list = []
                    
        query = session.query(visualisation_alias, barchart_alias).\
            join(barchart_alias, visualisation_alias.id == barchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("differdange"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, map_alias).\
            join(map_alias, visualisation_alias.id == map_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("differdange"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, linechart_alias).\
            join(linechart_alias, visualisation_alias.id == linechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("differdange"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, table_alias).\
            join(table_alias, visualisation_alias.id == table_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("differdange"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, statchart_alias).\
            join(statchart_alias, visualisation_alias.id == statchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("differdange"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, piechart_alias).\
            join(piechart_alias, visualisation_alias.id == piechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("differdange"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/torino/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI_Info"])
async def get_kpis_torino():
    try:
        # Query for all KPIs for this specific city
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower("torino")).first()
        if not city:
            return []
        
        kpis = session.query(KPIDB).filter(KPIDB.city_id == city.id).all()
        
        # Convert SQLAlchemy objects to dictionaries
        results_list = []
        for kpi in kpis:
            kpi_dict = {
                "id": kpi.id,
                "id_kpi": kpi.id_kpi,
                "name": kpi.name,
                "category": kpi.category,
                "description": kpi.description,
                "provider": kpi.provider,
                "calculationFrequency": kpi.calculationFrequency,
                "unitText": kpi.unitText,
                "minThreshold": kpi.minThreshold,
                "maxThreshold": kpi.maxThreshold,
                "hasCategoryLabel": kpi.hasCategoryLabel,
                "categoryLabelDictionary": kpi.categoryLabelDictionary
            }
            results_list.append(kpi_dict)
            
        return results_list
    except Exception as e:
        return [{"error": str(e)}]
    
@app.post("/torino/geojson/")
async def upload_geojson_torino(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(KeycloakBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
    try:
        # Create a new GeoJson entry
        new_data = GeoJsonDB(
            title=title,
            data=json.dumps(geojson_data),
            hasMapData=torino
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/torino/geojson/")
async def get_geojson_for_torino():
    results = []
    try:
        # Query the database for geospatial data for the given city
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == torino.id).all()

        # Check if data exists for the city
        if not geojson_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in geojson_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/torino/wms/")
async def upload_wms_torino(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(KeycloakBearer())], name: str = Query(..., description="Name of the wms artifact")):
    try:
        
        # Create a new GeoJson entry
        new_data = WMSDB(
            title=title,
            url=url,
            name=name,
            hasMapData=torino
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/torino/wms/")
async def get_wms_for_torino():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == torino.id).all()

        # Check if data exists for the city
        if not wms_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in wms_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/torino/mapdata/")    
async def get_mapdata_for_torino():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == torino.id).all()

        # Check if data exists for the city
        if not wms_data:
            print("sucks")
        for result in wms_data: 
            results.append(result)
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == torino.id).all()

        # Check if data exists for the city
        if not geojson_data:
            print("sucks")
        for result in geojson_data: 
            results.append(result)
        return results            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")     
        
@app.get("/torino/visualizations", response_model=list[object], summary="get visualization objects", tags = ["Visualisation"])
async def get_visualizations_torino():
    try:
        results_list = []
                    
        query = session.query(visualisation_alias, barchart_alias).\
            join(barchart_alias, visualisation_alias.id == barchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("torino"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, map_alias).\
            join(map_alias, visualisation_alias.id == map_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("torino"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, linechart_alias).\
            join(linechart_alias, visualisation_alias.id == linechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("torino"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, table_alias).\
            join(table_alias, visualisation_alias.id == table_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("torino"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, statchart_alias).\
            join(statchart_alias, visualisation_alias.id == statchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("torino"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, piechart_alias).\
            join(piechart_alias, visualisation_alias.id == piechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("torino"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/cascais/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI_Info"])
async def get_kpis_cascais():
    try:
        # Query for all KPIs for this specific city
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower("cascais")).first()
        if not city:
            return []
        
        kpis = session.query(KPIDB).filter(KPIDB.city_id == city.id).all()
        
        # Convert SQLAlchemy objects to dictionaries
        results_list = []
        for kpi in kpis:
            kpi_dict = {
                "id": kpi.id,
                "id_kpi": kpi.id_kpi,
                "name": kpi.name,
                "category": kpi.category,
                "description": kpi.description,
                "provider": kpi.provider,
                "calculationFrequency": kpi.calculationFrequency,
                "unitText": kpi.unitText,
                "minThreshold": kpi.minThreshold,
                "maxThreshold": kpi.maxThreshold,
                "hasCategoryLabel": kpi.hasCategoryLabel,
                "categoryLabelDictionary": kpi.categoryLabelDictionary
            }
            results_list.append(kpi_dict)
            
        return results_list
    except Exception as e:
        return [{"error": str(e)}]
    
@app.post("/cascais/geojson/")
async def upload_geojson_cascais(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(KeycloakBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
    try:
        # Create a new GeoJson entry
        new_data = GeoJsonDB(
            title=title,
            data=json.dumps(geojson_data),
            hasMapData=cascais
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/cascais/geojson/")
async def get_geojson_for_cascais():
    results = []
    try:
        # Query the database for geospatial data for the given city
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == cascais.id).all()

        # Check if data exists for the city
        if not geojson_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in geojson_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/cascais/wms/")
async def upload_wms_cascais(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(KeycloakBearer())], name: str = Query(..., description="Name of the wms artifact")):
    try:
        
        # Create a new GeoJson entry
        new_data = WMSDB(
            title=title,
            url=url,
            name=name,
            hasMapData=cascais
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/cascais/wms/")
async def get_wms_for_cascais():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == cascais.id).all()

        # Check if data exists for the city
        if not wms_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in wms_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/cascais/mapdata/")    
async def get_mapdata_for_cascais():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == cascais.id).all()

        # Check if data exists for the city
        if not wms_data:
            print("sucks")
        for result in wms_data: 
            results.append(result)
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == cascais.id).all()

        # Check if data exists for the city
        if not geojson_data:
            print("sucks")
        for result in geojson_data: 
            results.append(result)
        return results            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")     
        
@app.get("/cascais/visualizations", response_model=list[object], summary="get visualization objects", tags = ["Visualisation"])
async def get_visualizations_cascais():
    try:
        results_list = []
                    
        query = session.query(visualisation_alias, barchart_alias).\
            join(barchart_alias, visualisation_alias.id == barchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("cascais"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, map_alias).\
            join(map_alias, visualisation_alias.id == map_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("cascais"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, linechart_alias).\
            join(linechart_alias, visualisation_alias.id == linechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("cascais"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, table_alias).\
            join(table_alias, visualisation_alias.id == table_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("cascais"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, statchart_alias).\
            join(statchart_alias, visualisation_alias.id == statchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("cascais"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, piechart_alias).\
            join(piechart_alias, visualisation_alias.id == piechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("cascais"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/sofia/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI_Info"])
async def get_kpis_sofia():
    try:
        # Query for all KPIs for this specific city
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower("sofia")).first()
        if not city:
            return []
        
        kpis = session.query(KPIDB).filter(KPIDB.city_id == city.id).all()
        
        # Convert SQLAlchemy objects to dictionaries
        results_list = []
        for kpi in kpis:
            kpi_dict = {
                "id": kpi.id,
                "id_kpi": kpi.id_kpi,
                "name": kpi.name,
                "category": kpi.category,
                "description": kpi.description,
                "provider": kpi.provider,
                "calculationFrequency": kpi.calculationFrequency,
                "unitText": kpi.unitText,
                "minThreshold": kpi.minThreshold,
                "maxThreshold": kpi.maxThreshold,
                "hasCategoryLabel": kpi.hasCategoryLabel,
                "categoryLabelDictionary": kpi.categoryLabelDictionary
            }
            results_list.append(kpi_dict)
            
        return results_list
    except Exception as e:
        return [{"error": str(e)}]
    
@app.post("/sofia/geojson/")
async def upload_geojson_sofia(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(KeycloakBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
    try:
        # Create a new GeoJson entry
        new_data = GeoJsonDB(
            title=title,
            data=json.dumps(geojson_data),
            hasMapData=sofia
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/sofia/geojson/")
async def get_geojson_for_sofia():
    results = []
    try:
        # Query the database for geospatial data for the given city
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == sofia.id).all()

        # Check if data exists for the city
        if not geojson_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in geojson_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/sofia/wms/")
async def upload_wms_sofia(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(KeycloakBearer())], name: str = Query(..., description="Name of the wms artifact")):
    try:
        
        # Create a new GeoJson entry
        new_data = WMSDB(
            title=title,
            url=url,
            name=name,
            hasMapData=sofia
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/sofia/wms/")
async def get_wms_for_sofia():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == sofia.id).all()

        # Check if data exists for the city
        if not wms_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in wms_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/sofia/mapdata/")    
async def get_mapdata_for_sofia():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == sofia.id).all()

        # Check if data exists for the city
        if not wms_data:
            print("sucks")
        for result in wms_data: 
            results.append(result)
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == sofia.id).all()

        # Check if data exists for the city
        if not geojson_data:
            print("sucks")
        for result in geojson_data: 
            results.append(result)
        return results            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")     
        
@app.get("/sofia/visualizations", response_model=list[object], summary="get visualization objects", tags = ["Visualisation"])
async def get_visualizations_sofia():
    try:
        results_list = []
                    
        query = session.query(visualisation_alias, barchart_alias).\
            join(barchart_alias, visualisation_alias.id == barchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("sofia"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, map_alias).\
            join(map_alias, visualisation_alias.id == map_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("sofia"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, linechart_alias).\
            join(linechart_alias, visualisation_alias.id == linechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("sofia"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, table_alias).\
            join(table_alias, visualisation_alias.id == table_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("sofia"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, statchart_alias).\
            join(statchart_alias, visualisation_alias.id == statchart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("sofia"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                            
        query = session.query(visualisation_alias, piechart_alias).\
            join(piechart_alias, visualisation_alias.id == piechart_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("sofia"))

        # Execute the query to get the results
        results = query.all()
        # Convert SQLAlchemy objects to dictionaries
        for result in results:
            result_dict = {}
            for table in result: 
                for key in table.__dict__.keys():
                    if not key.startswith('_'):
                        result_dict[key] = getattr(table, key)
            results_list.append(result_dict)
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
@app.get("/ioannina/kpi/", response_model=List[KPIValue], summary="get a KPI object", tags = ["KPI_Info"])
async def get_kpi_ioannina(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("ioannina"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        
        # Convert SQLAlchemy objects to Pydantic models
        kpi_values = []
        for result in results:
            kpi_value = KPIValue(
                kpiValue=result.kpiValue,
                timestamp=result.timestamp,
                categoryLabel=result.categoryLabel if hasattr(result, 'categoryLabel') else ""
            )
            kpi_values.append(kpi_value)
        
        return kpi_values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/maribor/kpi/", response_model=List[KPIValue], summary="get a KPI object", tags = ["KPI_Info"])
async def get_kpi_maribor(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("maribor"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        
        # Convert SQLAlchemy objects to Pydantic models
        kpi_values = []
        for result in results:
            kpi_value = KPIValue(
                kpiValue=result.kpiValue,
                timestamp=result.timestamp,
                categoryLabel=result.categoryLabel if hasattr(result, 'categoryLabel') else ""
            )
            kpi_values.append(kpi_value)
        
        return kpi_values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/grenoble/kpi/", response_model=List[KPIValue], summary="get a KPI object", tags = ["KPI_Info"])
async def get_kpi_grenoble(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("grenoble"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        
        # Convert SQLAlchemy objects to Pydantic models
        kpi_values = []
        for result in results:
            kpi_value = KPIValue(
                kpiValue=result.kpiValue,
                timestamp=result.timestamp,
                categoryLabel=result.categoryLabel if hasattr(result, 'categoryLabel') else ""
            )
            kpi_values.append(kpi_value)
        
        return kpi_values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/athens/kpi/", response_model=List[KPIValue], summary="get a KPI object", tags = ["KPI_Info"])
async def get_kpi_athens(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("athens"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        
        # Convert SQLAlchemy objects to Pydantic models
        kpi_values = []
        for result in results:
            kpi_value = KPIValue(
                kpiValue=result.kpiValue,
                timestamp=result.timestamp,
                categoryLabel=result.categoryLabel if hasattr(result, 'categoryLabel') else ""
            )
            kpi_values.append(kpi_value)
        
        return kpi_values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/differdange/kpi/", response_model=List[KPIValue], summary="get a KPI object", tags = ["KPI_Info"])
async def get_kpi_differdange(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("differdange"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        
        # Convert SQLAlchemy objects to Pydantic models
        kpi_values = []
        for result in results:
            kpi_value = KPIValue(
                kpiValue=result.kpiValue,
                timestamp=result.timestamp,
                categoryLabel=result.categoryLabel if hasattr(result, 'categoryLabel') else ""
            )
            kpi_values.append(kpi_value)
        
        return kpi_values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/torino/kpi/", response_model=List[KPIValue], summary="get a KPI object", tags = ["KPI_Info"])
async def get_kpi_torino(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("torino"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        
        # Convert SQLAlchemy objects to Pydantic models
        kpi_values = []
        for result in results:
            kpi_value = KPIValue(
                kpiValue=result.kpiValue,
                timestamp=result.timestamp,
                categoryLabel=result.categoryLabel if hasattr(result, 'categoryLabel') else ""
            )
            kpi_values.append(kpi_value)
        
        return kpi_values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/cascais/kpi/", response_model=List[KPIValue], summary="get a KPI object", tags = ["KPI_Info"])
async def get_kpi_cascais(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("cascais"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        
        # Convert SQLAlchemy objects to Pydantic models
        kpi_values = []
        for result in results:
            kpi_value = KPIValue(
                kpiValue=result.kpiValue,
                timestamp=result.timestamp,
                categoryLabel=result.categoryLabel if hasattr(result, 'categoryLabel') else ""
            )
            kpi_values.append(kpi_value)
        
        return kpi_values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/sofia/kpi/", response_model=List[KPIValue], summary="get a KPI object", tags = ["KPI_Info"])
async def get_kpi_sofia(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("sofia"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        
        # Convert SQLAlchemy objects to Pydantic models
        kpi_values = []
        for result in results:
            kpi_value = KPIValue(
                kpiValue=result.kpiValue,
                timestamp=result.timestamp,
                categoryLabel=result.categoryLabel if hasattr(result, 'categoryLabel') else ""
            )
            kpi_values.append(kpi_value)
        
        return kpi_values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.delete("/", dependencies=[Depends(KeycloakBearer())],  summary="Delete everything from the database, please never use this")
async def delete_all(dependencies=[Depends(KeycloakBearer())]):
    # Create a session
    from sqlalchemy import MetaData
    # Step 2: Reflect the existing tables from the database into SQLAlchemy metadata
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Step 3: Drop all tables from the metadata
    metadata.drop_all(bind=engine)
    return {"msg":"deleted all"}


# Optional: Swagger UI metadata
tags_metadata = [
    {
        "name": "Authentication",
        "description": "Authentication endpoints for obtaining and managing access tokens",
    },
    {
        "name": "KPI",
        "description": "Operations related to KPI objects",
    },
    {
        "name": "KPI_Info",
        "description": "Operations related to KPI information retrieval",
    },
]

origins = [
    "http://localhost",
    "http://localhost:3002",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.openapi_tags = tags_metadata


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
