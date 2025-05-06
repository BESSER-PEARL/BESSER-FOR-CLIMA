# Python standard library imports
import os
import json
import logging

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
from passlib.context import CryptContext
from auth.auth_handler import sign_jwt, refresh_jwt
from auth.auth_model import UserSchema, UserLoginSchema, TokenSchema
from auth.auth_bearer import JWTBearer

# Local application imports
from pydantic_classes import KPIValue, User, CityUser, Admin, SolutionProvider, KPI, KPITemp, KPISecondHandCustomers, KPIMoney, CityAngel, KPITraffic, KPITotalRenewableEnergy, Visualisation, LineChart, BarChart, PieChart, StatChart, City, TableColumn, KPICollectedWaste, Table, KPITextileWastePerPerson, KPINumberHouseholdRenewableEnergy, MapData, GeoJson, WMS, Citizen, KPIWasteSorted, Map, KPICo2Avoided, KPIPeakSolarEnergy, Dashboard, KPIParticipants, KPIWasteAvoided
from sql_alchemy import Base
from sql_alchemy import KPIValue as KPIValueDB, User as UserDB, CityUser as CityUserDB, Admin as AdminDB, SolutionProvider as SolutionProviderDB, KPI as KPIDB, KPITemp as KPITempDB, KPISecondHandCustomers as KPISecondHandCustomersDB, KPIMoney as KPIMoneyDB, CityAngel as CityAngelDB, KPITraffic as KPITrafficDB, KPITotalRenewableEnergy as KPITotalRenewableEnergyDB, Visualisation as VisualisationDB, LineChart as LineChartDB, BarChart as BarChartDB, PieChart as PieChartDB, StatChart as StatChartDB, City as CityDB, TableColumn as TableColumnDB, KPICollectedWaste as KPICollectedWasteDB, Table as TableDB, KPITextileWastePerPerson as KPITextileWastePerPersonDB, KPINumberHouseholdRenewableEnergy as KPINumberHouseholdRenewableEnergyDB, MapData as MapDataDB, GeoJson as GeoJsonDB, WMS as WMSDB, Citizen as CitizenDB, KPIWasteSorted as KPIWasteSortedDB, Map as MapDB, KPICo2Avoided as KPICo2AvoidedDB, KPIPeakSolarEnergy as KPIPeakSolarEnergyDB, Dashboard as DashboardDB, KPIParticipants as KPIParticipantsDB, KPIWasteAvoided as KPIWasteAvoidedDB
from sql_alchemy import KPI as KPIDB

import logging

from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)


app = FastAPI()

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

admin = (
    session.query(UserDB)
    .filter_by(email="admin@gmail.com")
    .first()
)
if admin is None:
    admin = AdminDB(
        email="admin@gmail.com",
        password=pwd_context.hash("adminpw"),
        firstName="admin",
        lastName="admin",
    )
try:
    session.add(admin)
    session.commit()
except IntegrityError:
    session.rollback()
    print("error integrity")
except Exception as e:
    session.rollback()
    print(e)


@app.post("/user/signup", dependencies=[Depends(JWTBearer())], tags=["user"])
async def create_user(user: User = Body(...), city_id: Optional[int] = None):
    # Check if user already exists
    user_db = session.query(UserDB).filter_by(email=user.email).first()
    if user_db is not None:
        return {"error": "User with email address '" + user.email + "' already registered!"}
    
    # Hash password
    hashed_password = pwd_context.hash(user.password)
    
    # Create appropriate user type based on discriminator
    user_types = {
        "admin": AdminDB,
        "cityuser": CityUserDB,
        "cityangel": CityAngelDB,
        "solutionprovider": SolutionProviderDB,
        "citizen": CitizenDB
    }
    
    UserClass = user_types.get(user.type_spec)
    if not UserClass:
        return {"error": f"Invalid user type: {user.type_spec}"}
    
    # For cityuser, verify city exists
    if user.type_spec == "cityuser":
        if not city_id:
            return {"error": "City ID is required for city users"}
        city = session.query(CityDB).filter_by(id=city_id).first()
        if not city:
            return {"error": "Invalid city ID"}
            
    # Create user object
    statement = UserClass(
        email=user.email,
        password=hashed_password,
        firstName=user.firstName,
        lastName=user.lastName
    )
    
    # Set city for cityuser
    if user.type_spec == "cityuser":
        statement.city_id = city_id
        
    try:
        session.add(statement)
        session.commit()
        return sign_jwt(user.email)
    except IntegrityError:
        session.rollback()
        return {"error": "Integrity error"}
    except Exception as e:
        session.rollback()
        return {"error": f"Exception: {str(e)}"}

@app.post("/user/refresh", dependencies=[Depends(JWTBearer())], tags=["user"])
async def refresh_token(token: TokenSchema = Body(...)):
    try:
        return refresh_jwt(token.access_token)
    except Exception as e:
        print(e)
        print("added user")
        return {"error": "Exception " + e}

def check_user_api(data: UserLoginSchema):
    try:
        user = session.query(UserDB).filter_by(email=data.email).first()
        if user is None:
            return None
        if pwd_context.verify(data.password, user.password):
            return user
        return None
    except Exception as e:
        session.rollback()
        return {"error": "Exception " + e}


@app.post("/user/login", response_model=dict, tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    session.rollback()
    user_db = check_user_api(user)
    if user_db:
        token_response = sign_jwt(user.email)
        token_response["firstName"] = user_db.firstName
        token_response["type_spec"] = user_db.type_spec

        if user_db.type_spec == "cityuser":
            if user_db.city_id:
                city_record = session.query(CityDB).filter_by(id=user_db.city_id).first()
                if city_record:
                    city_name = city_record.name
                    token_response["city"] = user_db.city_id
                    token_response["city_name"] = city_name
                    print(f"User city name: {city_name}")

        return token_response
    
    return {"error": "Wrong login details!"}
    
    

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
    print("error already added? 5")


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
    print("error already added? 5")


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
    print("error already added? 6")


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
    print("error already added? 6")


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
    print("error already added? 7")


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


kpiCollectedClothes2 = session.query(KPICollectedWasteDB).filter_by(id_kpi= "waste_015", name= "Amount of collected textile clothes", category= "Waste", description= "Amount of collected textile clothes", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", target= 100).first()

if kpiCollectedClothes2 is None:
    kpiCollectedClothes2 = KPICollectedWasteDB(id_kpi= "waste_015", name= "Amount of collected textile clothes", category= "Waste", description= "Amount of collected textile clothes", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", target= 100, KPI=torino)
try:
    session.add(kpiCollectedClothes2)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 9")


kpiHouseholdInvolvedThreeBagCollection = session.query(KPIParticipantsDB).filter_by(id_kpi= "participants_006", name= "Households participating in the three bags collection", category= "Waste", description= "Households participating in the three bags collection", provider= "Torino", calculationFrequency= "Monthly", unitText= "Households", target= 100).first()

if kpiHouseholdInvolvedThreeBagCollection is None:
    kpiHouseholdInvolvedThreeBagCollection = KPIParticipantsDB(id_kpi= "participants_006", name= "Households participating in the three bags collection", category= "Waste", description= "Households participating in the three bags collection", provider= "Torino", calculationFrequency= "Monthly", unitText= "Households", target= 100, KPI=torino)
try:
    session.add(kpiHouseholdInvolvedThreeBagCollection)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 10")


kpiTextileWastePerPerson = session.query(KPITextileWastePerPersonDB).filter_by(id_kpi= "waste_010", name= "Amount of yearly textile waste per person", category= "Waste", description= "Amount of yearly textile waste per person", provider= "City", calculationFrequency= "Yearly", unitText= "Kg").first()

if kpiTextileWastePerPerson is None:
    kpiTextileWastePerPerson = KPITextileWastePerPersonDB(id_kpi= "waste_010", name= "Amount of yearly textile waste per person", category= "Waste", description= "Amount of yearly textile waste per person", provider= "City", calculationFrequency= "Yearly", unitText= "Kg", KPI=torino)
try:
    session.add(kpiTextileWastePerPerson)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 11")


kpiCollectedWaste = session.query(KPICollectedWasteDB).filter_by(id_kpi= "waste_007", name= "Amount of collected textile waste", category= "Waste", description= "Amount of collected textile waste", provider= "ReLearn", calculationFrequency= "Monthly", unitText= "Kg", target= 6000).first()

if kpiCollectedWaste is None:
    kpiCollectedWaste = KPICollectedWasteDB(id_kpi= "waste_007", name= "Amount of collected textile waste", category= "Waste", description= "Amount of collected textile waste", provider= "ReLearn", calculationFrequency= "Monthly", unitText= "Kg", target= 6000, KPI=torino)
try:
    session.add(kpiCollectedWaste)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 12")


kpiWasteSorted = session.query(KPIWasteSortedDB).filter_by(id_kpi= "waste_006", name= "Amount of correctly sorted waste in bins using ReLearn sensors", category= "Waste", description= "Amount of correctly sorted waste in bins using ReLearn sensors", provider= "ReLearn", calculationFrequency= "Monthly", unitText= "Kg", target= 1000).first()

if kpiWasteSorted is None:
    kpiWasteSorted = KPIWasteSortedDB(id_kpi= "waste_006", name= "Amount of correctly sorted waste in bins using ReLearn sensors", category= "Waste", description= "Amount of correctly sorted waste in bins using ReLearn sensors", provider= "ReLearn", calculationFrequency= "Monthly", unitText= "Kg", target= 1000, KPI=torino)
try:
    session.add(kpiWasteSorted)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 13")


kpiCo2Avoided = session.query(KPICo2AvoidedDB).filter_by(id_kpi= "co2_001", name= "Co2 avoided through collection of waste through Re4Circular", category= "Waste", description= "Co2 avoided through collection of waste through Re4Circular", provider= "DKSR", calculationFrequency= "Monthly", unitText= "Tons", target= 1).first()

if kpiCo2Avoided is None:
    kpiCo2Avoided = KPICo2AvoidedDB(id_kpi= "co2_001", name= "Co2 avoided through collection of waste through Re4Circular", category= "Waste", description= "Co2 avoided through collection of waste through Re4Circular", provider= "DKSR", calculationFrequency= "Monthly", unitText= "Tons", target= 1, KPI=torino)
try:
    session.add(kpiCo2Avoided)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 14")


kpiWasteAvoided = session.query(KPIWasteAvoidedDB).filter_by(id_kpi= "waste_001", name= "Waste avoided through Re4Circular", category= "Waste", description= "Waste avoided through Re4Circular (collecting material before it becomes waste)", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Tons", target= 10).first()

if kpiWasteAvoided is None:
    kpiWasteAvoided = KPIWasteAvoidedDB(id_kpi= "waste_001", name= "Waste avoided through Re4Circular", category= "Waste", description= "Waste avoided through Re4Circular (collecting material before it becomes waste)", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Tons", target= 10, KPI=torino)
try:
    session.add(kpiWasteAvoided)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 15")


kpiReuseBusinesses = session.query(KPIParticipantsDB).filter_by(id_kpi= "participants_005", name= "Businesses re-using textiles through Re4Circular", category= "Waste", description= "Businesses re-using textiles through Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of businesses", target= 10).first()

if kpiReuseBusinesses is None:
    kpiReuseBusinesses = KPIParticipantsDB(id_kpi= "participants_005", name= "Businesses re-using textiles through Re4Circular", category= "Waste", description= "Businesses re-using textiles through Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of businesses", target= 10, KPI=torino)
try:
    session.add(kpiReuseBusinesses)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 16")


kpiInvolvedBusinesses = session.query(KPIParticipantsDB).filter_by(id_kpi= "participants_004", name= "Businesses active on Re4Circular", category= "Waste", description= "Businesses active on Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of businesses", target= 20).first()

if kpiInvolvedBusinesses is None:
    kpiInvolvedBusinesses = KPIParticipantsDB(id_kpi= "participants_004", name= "Businesses active on Re4Circular", category= "Waste", description= "Businesses active on Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of businesses", target= 20, KPI=torino)
try:
    session.add(kpiInvolvedBusinesses)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 17")


kpiInformedBusinesses = session.query(KPIParticipantsDB).filter_by(id_kpi= "participants_003", name= "Businesses informed through Re4Circular", category= "Waste", description= "Businesses informed through Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of businesses", target= 50).first()

if kpiInformedBusinesses is None:
    kpiInformedBusinesses = KPIParticipantsDB(id_kpi= "participants_003", name= "Businesses informed through Re4Circular", category= "Waste", description= "Businesses informed through Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of businesses", target= 50, KPI=torino)
try:
    session.add(kpiInformedBusinesses)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 18")


kpiInvolvedCitizens = session.query(KPIParticipantsDB).filter_by(id_kpi= "participants_002", name= "Citizens active on Re4Circular", category= "Waste", description= "Citizens active on Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of people", target= 500).first()

if kpiInvolvedCitizens is None:
    kpiInvolvedCitizens = KPIParticipantsDB(id_kpi= "participants_002", name= "Citizens active on Re4Circular", category= "Waste", description= "Citizens active on Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of people", target= 500, KPI=torino)
try:
    session.add(kpiInvolvedCitizens)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 19")


kpiDiscardedWaste = session.query(KPICollectedWasteDB).filter_by(id_kpi= "waste_013", name= "Amount of textile waste discarded from the differentiated share", category= "Waste", description= "Amount of textile waste discarded from the differentiated share", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", target= 50).first()

if kpiDiscardedWaste is None:
    kpiDiscardedWaste = KPICollectedWasteDB(id_kpi= "waste_013", name= "Amount of textile waste discarded from the differentiated share", category= "Waste", description= "Amount of textile waste discarded from the differentiated share", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", target= 50, KPI=torino)
try:
    session.add(kpiDiscardedWaste)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 20")


kpiInformedCitizens = session.query(KPIParticipantsDB).filter_by(id_kpi= "participants_001", name= "Citizens informed through Re4Circular", category= "Waste", description= "Citizens informed through Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of people", target= 1000).first()

if kpiInformedCitizens is None:
    kpiInformedCitizens = KPIParticipantsDB(id_kpi= "participants_001", name= "Citizens informed through Re4Circular", category= "Waste", description= "Citizens informed through Re4Circular", provider= "Re4Circular", calculationFrequency= "Monthly", unitText= "Number of people", target= 1000, KPI=torino)
try:
    session.add(kpiInformedCitizens)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 21")


kpiCollectedTextileWasteEcoIsole = session.query(KPICollectedWasteDB).filter_by(id_kpi= "waste_014", name= "Amount of textile left in the indifferentiated waste (Eco-Isole)", category= "Waste", description= "Amount of textile left in the indifferentiated waste (Eco-Isole)", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", target= 3000).first()

if kpiCollectedTextileWasteEcoIsole is None:
    kpiCollectedTextileWasteEcoIsole = KPICollectedWasteDB(id_kpi= "waste_014", name= "Amount of textile left in the indifferentiated waste (Eco-Isole)", category= "Waste", description= "Amount of textile left in the indifferentiated waste (Eco-Isole)", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", target= 3000, KPI=torino)
try:
    session.add(kpiCollectedTextileWasteEcoIsole)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 22")


kpiCollectedTextileWaste = session.query(KPICollectedWasteDB).filter_by(id_kpi= "waste_012", name= "Amount of other types of textiles collected", category= "Waste", description= "Amount of other types of textiles collected", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", target= 5000).first()

if kpiCollectedTextileWaste is None:
    kpiCollectedTextileWaste = KPICollectedWasteDB(id_kpi= "waste_012", name= "Amount of other types of textiles collected", category= "Waste", description= "Amount of other types of textiles collected", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", target= 5000, KPI=torino)
try:
    session.add(kpiCollectedTextileWaste)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 23")


kpiCollectedClothes = session.query(KPICollectedWasteDB).filter_by(id_kpi= "waste_011", name= "Amount of collected textile clothes", category= "Waste", description= "Amount of collected textile clothes", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", target= 6000).first()

if kpiCollectedClothes is None:
    kpiCollectedClothes = KPICollectedWasteDB(id_kpi= "waste_011", name= "Amount of collected textile clothes", category= "Waste", description= "Amount of collected textile clothes", provider= "City of Torino", calculationFrequency= "Monthly", unitText= "Kg", target= 6000, KPI=torino)
try:
    session.add(kpiCollectedClothes)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 24")


kpiCSecondHandCustomers_Cascais = session.query(KPISecondHandCustomersDB).filter_by(id_kpi= "waste002", name= "Customers in second hand shops", category= "Waste", description= "Daily number of customers in second hand shops", provider= "Shops", calculationFrequency= "Daily", unitText= "Number of people", target= 1000).first()

if kpiCSecondHandCustomers_Cascais is None:
    kpiCSecondHandCustomers_Cascais = KPISecondHandCustomersDB(id_kpi= "waste002", name= "Customers in second hand shops", category= "Waste", description= "Daily number of customers in second hand shops", provider= "Shops", calculationFrequency= "Daily", unitText= "Number of people", target= 1000, KPI=cascais)
try:
    session.add(kpiCSecondHandCustomers_Cascais)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 25")


kpiCollectedWaste_Cascais = session.query(KPICollectedWasteDB).filter_by(id_kpi= "waste001", name= "Collected Textile Waste in Ton", category= "Waste", description= "Total textile waste collected in Cascais", provider= "WasteDepartment", calculationFrequency= "Weekly", unitText= "Tons", target= 10).first()

if kpiCollectedWaste_Cascais is None:
    kpiCollectedWaste_Cascais = KPICollectedWasteDB(id_kpi= "waste001", name= "Collected Textile Waste in Ton", category= "Waste", description= "Total textile waste collected in Cascais", provider= "WasteDepartment", calculationFrequency= "Weekly", unitText= "Tons", target= 10, KPI=cascais)
try:
    session.add(kpiCollectedWaste_Cascais)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 26")


kpiPeakSolarEnergy_Differdange = session.query(KPIPeakSolarEnergyDB).filter_by(id_kpi= "energy003", name= "Peak solar energy", category= "Energy", description= "Peak solar energy in Differdange", provider= "Differdange", calculationFrequency= "Monthly", unitText= "KW peak", target= 1000).first()

if kpiPeakSolarEnergy_Differdange is None:
    kpiPeakSolarEnergy_Differdange = KPIPeakSolarEnergyDB(id_kpi= "energy003", name= "Peak solar energy", category= "Energy", description= "Peak solar energy in Differdange", provider= "Differdange", calculationFrequency= "Monthly", unitText= "KW peak", target= 1000, KPI=differdange)
try:
    session.add(kpiPeakSolarEnergy_Differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 27")


kpiNumberHouseholdRenewableEnergy_Differdange = session.query(KPINumberHouseholdRenewableEnergyDB).filter_by(id_kpi= "energy002", name= "Household with renewable energy", category= "Energy", description= "Number of households producing any kind of renewable energy", provider= "Citizens", calculationFrequency= "Monthly", unitText= "Number", target= 500).first()

if kpiNumberHouseholdRenewableEnergy_Differdange is None:
    kpiNumberHouseholdRenewableEnergy_Differdange = KPINumberHouseholdRenewableEnergyDB(id_kpi= "energy002", name= "Household with renewable energy", category= "Energy", description= "Number of households producing any kind of renewable energy", provider= "Citizens", calculationFrequency= "Monthly", unitText= "Number", target= 500, KPI=differdange)
try:
    session.add(kpiNumberHouseholdRenewableEnergy_Differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 28")


kpiTotalRenewableEnergy_Differdange = session.query(KPITotalRenewableEnergyDB).filter_by(id_kpi= "energy001", name= "Percentage of renewable energy in Differdange", category= "Energy", description= "Percentage of renewable energy in Differdange based on total amount of energy", provider= "Solution Provider", calculationFrequency= "Monthly", unitText= "Percentage", target= 20).first()

if kpiTotalRenewableEnergy_Differdange is None:
    kpiTotalRenewableEnergy_Differdange = KPITotalRenewableEnergyDB(id_kpi= "energy001", name= "Percentage of renewable energy in Differdange", category= "Energy", description= "Percentage of renewable energy in Differdange based on total amount of energy", provider= "Solution Provider", calculationFrequency= "Monthly", unitText= "Percentage", target= 20, KPI=differdange)
try:
    session.add(kpiTotalRenewableEnergy_Differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 29")


kpiTrafficCongestion_Sofia = session.query(KPITrafficDB).filter_by(id_kpi= "traffic001", name= "Traffic Congestion Level", category= "Transport", description= "Measures the level of traffic congestion", provider= "TransportDepartment", calculationFrequency= "Hourly", unitText= "Number of Cars", target= 30).first()

if kpiTrafficCongestion_Sofia is None:
    kpiTrafficCongestion_Sofia = KPITrafficDB(id_kpi= "traffic001", name= "Traffic Congestion Level", category= "Transport", description= "Measures the level of traffic congestion", provider= "TransportDepartment", calculationFrequency= "Hourly", unitText= "Number of Cars", target= 30, KPI=sofia)
try:
    session.add(kpiTrafficCongestion_Sofia)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 30")


kpiMoney_Differdange = session.query(KPIMoneyDB).filter_by(id_kpi= "money001", name= "Money Invested", category= "Environment", description= "Measures the money invested in green stuff", provider= "BankService", calculationFrequency= "Weekly", unitText= "Euros", target= 1000).first()

if kpiMoney_Differdange is None:
    kpiMoney_Differdange = KPIMoneyDB(id_kpi= "money001", name= "Money Invested", category= "Environment", description= "Measures the money invested in green stuff", provider= "BankService", calculationFrequency= "Weekly", unitText= "Euros", target= 1000, KPI=differdange)
try:
    session.add(kpiMoney_Differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 31")


kpiTemp_Differdange = session.query(KPITempDB).filter_by(id_kpi= "temp001", name= "Average Temperature", category= "Environment", description= "Measures the average temperature of the city", provider= "WeatherService", calculationFrequency= "Daily", unitText= "Celsius", threshold= 25).first()

if kpiTemp_Differdange is None:
    kpiTemp_Differdange = KPITempDB(id_kpi= "temp001", name= "Average Temperature", category= "Environment", description= "Measures the average temperature of the city", provider= "WeatherService", calculationFrequency= "Daily", unitText= "Celsius", threshold= 25, KPI=differdange)
try:
    session.add(kpiTemp_Differdange)
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? 32")


           
kpivalue_alias = aliased(KPIValueDB)
           
user_alias = aliased(UserDB)
           
cityuser_alias = aliased(CityUserDB)
           
admin_alias = aliased(AdminDB)
           
solutionprovider_alias = aliased(SolutionProviderDB)
           
kpi_alias = aliased(KPIDB)
           
kpitemp_alias = aliased(KPITempDB)
           
kpisecondhandcustomers_alias = aliased(KPISecondHandCustomersDB)
           
kpimoney_alias = aliased(KPIMoneyDB)
           
cityangel_alias = aliased(CityAngelDB)
           
kpitraffic_alias = aliased(KPITrafficDB)
           
kpitotalrenewableenergy_alias = aliased(KPITotalRenewableEnergyDB)
           
visualisation_alias = aliased(VisualisationDB)
           
linechart_alias = aliased(LineChartDB)
           
barchart_alias = aliased(BarChartDB)
           
piechart_alias = aliased(PieChartDB)
           
statchart_alias = aliased(StatChartDB)
           
city_alias = aliased(CityDB)
           
tablecolumn_alias = aliased(TableColumnDB)
           
kpicollectedwaste_alias = aliased(KPICollectedWasteDB)
           
table_alias = aliased(TableDB)
           
kpitextilewasteperperson_alias = aliased(KPITextileWastePerPersonDB)
           
kpinumberhouseholdrenewableenergy_alias = aliased(KPINumberHouseholdRenewableEnergyDB)
           
mapdata_alias = aliased(MapDataDB)
           
geojson_alias = aliased(GeoJsonDB)
           
wms_alias = aliased(WMSDB)
           
citizen_alias = aliased(CitizenDB)
           
kpiwastesorted_alias = aliased(KPIWasteSortedDB)
           
map_alias = aliased(MapDB)
           
kpico2avoided_alias = aliased(KPICo2AvoidedDB)
           
kpipeaksolarenergy_alias = aliased(KPIPeakSolarEnergyDB)
           
dashboard_alias = aliased(DashboardDB)
           
kpiparticipants_alias = aliased(KPIParticipantsDB)
           
kpiwasteavoided_alias = aliased(KPIWasteAvoidedDB)
  
    




# KPI

@app.post("/city/{city_name}/kpi/{kpi_id}", dependencies=[Depends(JWTBearer())], response_model=List[KPIValue], summary="Add KPI values", tags=["KPI"])
async def add_kpi_values(
    city_name: str,
    kpi_id: int,
    kpis: List[KPIValue] = Body(...),
):
    """Add KPI values for any city"""
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
                existing_entry.currentStanding = kpi_value.currentStanding
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


@app.get("/city/{city_name}/kpis", response_model=list[object], summary="Get all KPI objects", tags=["KPI"])
async def get_kpis(city_name: str):
    """Get all KPIs for a specific city"""
    try:
        # Get city object
        city = session.query(CityDB).filter(func.lower(CityDB.name) == func.lower(city_name)).first()
        if not city:
            raise HTTPException(status_code=404, detail=f"City {city_name} not found")
            
        results_list = []
                    
        query = session.query(kpi_alias, kpitemp_alias).\
            join(kpitemp_alias, kpi_alias.id == kpitemp_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpisecondhandcustomers_alias).\
            join(kpisecondhandcustomers_alias, kpi_alias.id == kpisecondhandcustomers_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpimoney_alias).\
            join(kpimoney_alias, kpi_alias.id == kpimoney_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpitraffic_alias).\
            join(kpitraffic_alias, kpi_alias.id == kpitraffic_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpitotalrenewableenergy_alias).\
            join(kpitotalrenewableenergy_alias, kpi_alias.id == kpitotalrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpicollectedwaste_alias).\
            join(kpicollectedwaste_alias, kpi_alias.id == kpicollectedwaste_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpitextilewasteperperson_alias).\
            join(kpitextilewasteperperson_alias, kpi_alias.id == kpitextilewasteperperson_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpinumberhouseholdrenewableenergy_alias).\
            join(kpinumberhouseholdrenewableenergy_alias, kpi_alias.id == kpinumberhouseholdrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpiwastesorted_alias).\
            join(kpiwastesorted_alias, kpi_alias.id == kpiwastesorted_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpico2avoided_alias).\
            join(kpico2avoided_alias, kpi_alias.id == kpico2avoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpipeaksolarenergy_alias).\
            join(kpipeaksolarenergy_alias, kpi_alias.id == kpipeaksolarenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpiparticipants_alias).\
            join(kpiparticipants_alias, kpi_alias.id == kpiparticipants_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
                            
        query = session.query(kpi_alias, kpiwasteavoided_alias).\
            join(kpiwasteavoided_alias, kpi_alias.id == kpiwasteavoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(city_alias.id == city.id)

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
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Visualisations


            
            
            
            
            
            
            
            
                        
@app.post("/ioannina/visualization/LineChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_ioannina
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
                
                        
@app.post("/ioannina/visualization/BarChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_ioannina
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
                
                        
@app.post("/ioannina/visualization/PieChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_ioannina
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
                
                        
@app.post("/ioannina/visualization/StatChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_ioannina
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
                
            
                        
@app.post("/ioannina/visualization/Table/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_ioannina
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
                
            
            
            
            
            
            
                        
@app.post("/ioannina/visualization/Map/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_ioannina
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
async def delete_visualizations_ioannina(ids: List[int], dependencies=[Depends(JWTBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            
            if (row.consistsOf.code == "ioannina"):
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

    
            
            
            
            
            
            
            
            
                        
@app.post("/maribor/visualization/LineChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_maribor
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
                
                        
@app.post("/maribor/visualization/BarChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_maribor
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
                
                        
@app.post("/maribor/visualization/PieChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_maribor
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
                
                        
@app.post("/maribor/visualization/StatChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_maribor
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
                
            
                        
@app.post("/maribor/visualization/Table/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_maribor
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
                
            
            
            
            
            
            
                        
@app.post("/maribor/visualization/Map/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_maribor
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
async def delete_visualizations_maribor(ids: List[int], dependencies=[Depends(JWTBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            
            if (row.consistsOf.code == "maribor"):
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

    
            
            
            
            
            
            
            
            
                        
@app.post("/grenoble/visualization/LineChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_grenoble
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
                
                        
@app.post("/grenoble/visualization/BarChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_grenoble
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
                
                        
@app.post("/grenoble/visualization/PieChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_grenoble
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
                
                        
@app.post("/grenoble/visualization/StatChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_grenoble
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
                
            
                        
@app.post("/grenoble/visualization/Table/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_grenoble
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
                
            
            
            
            
            
            
                        
@app.post("/grenoble/visualization/Map/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_grenoble
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
async def delete_visualizations_grenoble(ids: List[int], dependencies=[Depends(JWTBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            
            if (row.consistsOf.code == "grenoble"):
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

    
            
            
            
            
            
            
            
            
                        
@app.post("/athens/visualization/LineChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_athens
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
                
                        
@app.post("/athens/visualization/BarChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_athens
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
                
                        
@app.post("/athens/visualization/PieChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_athens
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
                
                        
@app.post("/athens/visualization/StatChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_athens
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
                
            
                        
@app.post("/athens/visualization/Table/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_athens
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
                
            
            
            
            
            
            
                        
@app.post("/athens/visualization/Map/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_athens
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
async def delete_visualizations_athens(ids: List[int], dependencies=[Depends(JWTBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            
            if (row.consistsOf.code == "athens"):
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

    
            
            
            
            
            
            
            
            
                        
@app.post("/torino/visualization/LineChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_torino
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
                
                        
@app.post("/torino/visualization/BarChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_torino
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
                
                        
@app.post("/torino/visualization/PieChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_torino
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
                
                        
@app.post("/torino/visualization/StatChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_torino
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
                
            
                        
@app.post("/torino/visualization/Table/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_torino
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
                
            
            
            
            
            
            
                        
@app.post("/torino/visualization/Map/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_torino
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
async def delete_visualizations_torino(ids: List[int], dependencies=[Depends(JWTBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            
            if (row.consistsOf.code == "torino"):
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

    
            
            
            
            
            
            
            
            
                        
@app.post("/cascais/visualization/LineChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_cascais
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
                
                        
@app.post("/cascais/visualization/BarChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_cascais
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
                
                        
@app.post("/cascais/visualization/PieChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_cascais
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
                
                        
@app.post("/cascais/visualization/StatChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_cascais
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
                
            
                        
@app.post("/cascais/visualization/Table/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_cascais
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
                
            
            
            
            
            
            
                        
@app.post("/cascais/visualization/Map/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_cascais
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
async def delete_visualizations_cascais(ids: List[int], dependencies=[Depends(JWTBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            
            if (row.consistsOf.code == "cascais"):
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

    
            
            
            
            
            
            
            
            
                        
@app.post("/differdange/visualization/LineChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_differdange
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
                
                        
@app.post("/differdange/visualization/BarChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_differdange
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
                
                        
@app.post("/differdange/visualization/PieChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_differdange
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
                
                        
@app.post("/differdange/visualization/StatChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_differdange
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
                
            
                        
@app.post("/differdange/visualization/Table/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_differdange
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
                
            
            
            
            
            
            
                        
@app.post("/differdange/visualization/Map/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_differdange
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
async def delete_visualizations_differdange(ids: List[int], dependencies=[Depends(JWTBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            
            if (row.consistsOf.code == "differdange"):
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

    
            
            
            
            
            
            
            
            
                        
@app.post("/sofia/visualization/LineChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_sofia
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
                
                        
@app.post("/sofia/visualization/BarChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_sofia
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
                
                        
@app.post("/sofia/visualization/PieChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_sofia
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
                
                        
@app.post("/sofia/visualization/StatChart/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_sofia
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
                
            
                        
@app.post("/sofia/visualization/Table/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_sofia
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
                
            
            
            
            
            
            
                        
@app.post("/sofia/visualization/Map/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
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
        db_entry.consistsOf = dashboard_sofia
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
async def delete_visualizations_sofia(ids: List[int], dependencies=[Depends(JWTBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            
            if (row.consistsOf.code == "sofia"):
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

    


     
@app.get("/ioannina/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI"])
async def get_kpis_ioannina():
    try:
        results_list = []
                    
        query = session.query(kpi_alias, kpitemp_alias).\
            join(kpitemp_alias, kpi_alias.id == kpitemp_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpisecondhandcustomers_alias).\
            join(kpisecondhandcustomers_alias, kpi_alias.id == kpisecondhandcustomers_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpimoney_alias).\
            join(kpimoney_alias, kpi_alias.id == kpimoney_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpitraffic_alias).\
            join(kpitraffic_alias, kpi_alias.id == kpitraffic_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpitotalrenewableenergy_alias).\
            join(kpitotalrenewableenergy_alias, kpi_alias.id == kpitotalrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpicollectedwaste_alias).\
            join(kpicollectedwaste_alias, kpi_alias.id == kpicollectedwaste_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpitextilewasteperperson_alias).\
            join(kpitextilewasteperperson_alias, kpi_alias.id == kpitextilewasteperperson_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpinumberhouseholdrenewableenergy_alias).\
            join(kpinumberhouseholdrenewableenergy_alias, kpi_alias.id == kpinumberhouseholdrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpiwastesorted_alias).\
            join(kpiwastesorted_alias, kpi_alias.id == kpiwastesorted_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpico2avoided_alias).\
            join(kpico2avoided_alias, kpi_alias.id == kpico2avoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpipeaksolarenergy_alias).\
            join(kpipeaksolarenergy_alias, kpi_alias.id == kpipeaksolarenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpiparticipants_alias).\
            join(kpiparticipants_alias, kpi_alias.id == kpiparticipants_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
                            
        query = session.query(kpi_alias, kpiwasteavoided_alias).\
            join(kpiwasteavoided_alias, kpi_alias.id == kpiwasteavoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("ioannina"))

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
        return [e]
    
@app.post("/ioannina/geojson/")
async def upload_geojson_ioannina(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(JWTBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
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
async def upload_wms_ioannina(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(JWTBearer())], name: str = Query(..., description="Name of the wms artifact")):
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
        
@app.get("/ioannina/visualizations", response_model=list[object], summary="get a KPI object", tags = ["Visualisation"])
async def get_visualizations_ioannina():
    try:
        results_list = []
                    
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
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/maribor/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI"])
async def get_kpis_maribor():
    try:
        results_list = []
                    
        query = session.query(kpi_alias, kpitemp_alias).\
            join(kpitemp_alias, kpi_alias.id == kpitemp_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpisecondhandcustomers_alias).\
            join(kpisecondhandcustomers_alias, kpi_alias.id == kpisecondhandcustomers_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpimoney_alias).\
            join(kpimoney_alias, kpi_alias.id == kpimoney_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpitraffic_alias).\
            join(kpitraffic_alias, kpi_alias.id == kpitraffic_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpitotalrenewableenergy_alias).\
            join(kpitotalrenewableenergy_alias, kpi_alias.id == kpitotalrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpicollectedwaste_alias).\
            join(kpicollectedwaste_alias, kpi_alias.id == kpicollectedwaste_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpitextilewasteperperson_alias).\
            join(kpitextilewasteperperson_alias, kpi_alias.id == kpitextilewasteperperson_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpinumberhouseholdrenewableenergy_alias).\
            join(kpinumberhouseholdrenewableenergy_alias, kpi_alias.id == kpinumberhouseholdrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpiwastesorted_alias).\
            join(kpiwastesorted_alias, kpi_alias.id == kpiwastesorted_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpico2avoided_alias).\
            join(kpico2avoided_alias, kpi_alias.id == kpico2avoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpipeaksolarenergy_alias).\
            join(kpipeaksolarenergy_alias, kpi_alias.id == kpipeaksolarenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpiparticipants_alias).\
            join(kpiparticipants_alias, kpi_alias.id == kpiparticipants_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
                            
        query = session.query(kpi_alias, kpiwasteavoided_alias).\
            join(kpiwasteavoided_alias, kpi_alias.id == kpiwasteavoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("maribor"))

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
        return [e]
    
@app.post("/maribor/geojson/")
async def upload_geojson_maribor(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(JWTBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
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
async def upload_wms_maribor(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(JWTBearer())], name: str = Query(..., description="Name of the wms artifact")):
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
        
@app.get("/maribor/visualizations", response_model=list[object], summary="get a KPI object", tags = ["Visualisation"])
async def get_visualizations_maribor():
    try:
        results_list = []
                    
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
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/grenoble/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI"])
async def get_kpis_grenoble():
    try:
        results_list = []
                    
        query = session.query(kpi_alias, kpitemp_alias).\
            join(kpitemp_alias, kpi_alias.id == kpitemp_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpisecondhandcustomers_alias).\
            join(kpisecondhandcustomers_alias, kpi_alias.id == kpisecondhandcustomers_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpimoney_alias).\
            join(kpimoney_alias, kpi_alias.id == kpimoney_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpitraffic_alias).\
            join(kpitraffic_alias, kpi_alias.id == kpitraffic_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpitotalrenewableenergy_alias).\
            join(kpitotalrenewableenergy_alias, kpi_alias.id == kpitotalrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpicollectedwaste_alias).\
            join(kpicollectedwaste_alias, kpi_alias.id == kpicollectedwaste_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpitextilewasteperperson_alias).\
            join(kpitextilewasteperperson_alias, kpi_alias.id == kpitextilewasteperperson_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpinumberhouseholdrenewableenergy_alias).\
            join(kpinumberhouseholdrenewableenergy_alias, kpi_alias.id == kpinumberhouseholdrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpiwastesorted_alias).\
            join(kpiwastesorted_alias, kpi_alias.id == kpiwastesorted_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpico2avoided_alias).\
            join(kpico2avoided_alias, kpi_alias.id == kpico2avoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpipeaksolarenergy_alias).\
            join(kpipeaksolarenergy_alias, kpi_alias.id == kpipeaksolarenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpiparticipants_alias).\
            join(kpiparticipants_alias, kpi_alias.id == kpiparticipants_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
                            
        query = session.query(kpi_alias, kpiwasteavoided_alias).\
            join(kpiwasteavoided_alias, kpi_alias.id == kpiwasteavoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("grenoble"))

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
        return [e]
    
@app.post("/grenoble/geojson/")
async def upload_geojson_grenoble(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(JWTBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
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
async def upload_wms_grenoble(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(JWTBearer())], name: str = Query(..., description="Name of the wms artifact")):
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
        
@app.get("/grenoble/visualizations", response_model=list[object], summary="get a KPI object", tags = ["Visualisation"])
async def get_visualizations_grenoble():
    try:
        results_list = []
                    
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
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/athens/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI"])
async def get_kpis_athens():
    try:
        results_list = []
                    
        query = session.query(kpi_alias, kpitemp_alias).\
            join(kpitemp_alias, kpi_alias.id == kpitemp_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpisecondhandcustomers_alias).\
            join(kpisecondhandcustomers_alias, kpi_alias.id == kpisecondhandcustomers_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpimoney_alias).\
            join(kpimoney_alias, kpi_alias.id == kpimoney_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpitraffic_alias).\
            join(kpitraffic_alias, kpi_alias.id == kpitraffic_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpitotalrenewableenergy_alias).\
            join(kpitotalrenewableenergy_alias, kpi_alias.id == kpitotalrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpicollectedwaste_alias).\
            join(kpicollectedwaste_alias, kpi_alias.id == kpicollectedwaste_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpitextilewasteperperson_alias).\
            join(kpitextilewasteperperson_alias, kpi_alias.id == kpitextilewasteperperson_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpinumberhouseholdrenewableenergy_alias).\
            join(kpinumberhouseholdrenewableenergy_alias, kpi_alias.id == kpinumberhouseholdrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpiwastesorted_alias).\
            join(kpiwastesorted_alias, kpi_alias.id == kpiwastesorted_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpico2avoided_alias).\
            join(kpico2avoided_alias, kpi_alias.id == kpico2avoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpipeaksolarenergy_alias).\
            join(kpipeaksolarenergy_alias, kpi_alias.id == kpipeaksolarenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpiparticipants_alias).\
            join(kpiparticipants_alias, kpi_alias.id == kpiparticipants_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
                            
        query = session.query(kpi_alias, kpiwasteavoided_alias).\
            join(kpiwasteavoided_alias, kpi_alias.id == kpiwasteavoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("athens"))

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
        return [e]
    
@app.post("/athens/geojson/")
async def upload_geojson_athens(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(JWTBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
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
async def upload_wms_athens(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(JWTBearer())], name: str = Query(..., description="Name of the wms artifact")):
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
        
@app.get("/athens/visualizations", response_model=list[object], summary="get a KPI object", tags = ["Visualisation"])
async def get_visualizations_athens():
    try:
        results_list = []
                    
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
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/torino/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI"])
async def get_kpis_torino():
    try:
        results_list = []
                    
        query = session.query(kpi_alias, kpitemp_alias).\
            join(kpitemp_alias, kpi_alias.id == kpitemp_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpisecondhandcustomers_alias).\
            join(kpisecondhandcustomers_alias, kpi_alias.id == kpisecondhandcustomers_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpimoney_alias).\
            join(kpimoney_alias, kpi_alias.id == kpimoney_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpitraffic_alias).\
            join(kpitraffic_alias, kpi_alias.id == kpitraffic_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpitotalrenewableenergy_alias).\
            join(kpitotalrenewableenergy_alias, kpi_alias.id == kpitotalrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpicollectedwaste_alias).\
            join(kpicollectedwaste_alias, kpi_alias.id == kpicollectedwaste_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpitextilewasteperperson_alias).\
            join(kpitextilewasteperperson_alias, kpi_alias.id == kpitextilewasteperperson_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpinumberhouseholdrenewableenergy_alias).\
            join(kpinumberhouseholdrenewableenergy_alias, kpi_alias.id == kpinumberhouseholdrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpiwastesorted_alias).\
            join(kpiwastesorted_alias, kpi_alias.id == kpiwastesorted_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpico2avoided_alias).\
            join(kpico2avoided_alias, kpi_alias.id == kpico2avoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpipeaksolarenergy_alias).\
            join(kpipeaksolarenergy_alias, kpi_alias.id == kpipeaksolarenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpiparticipants_alias).\
            join(kpiparticipants_alias, kpi_alias.id == kpiparticipants_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
                            
        query = session.query(kpi_alias, kpiwasteavoided_alias).\
            join(kpiwasteavoided_alias, kpi_alias.id == kpiwasteavoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("torino"))

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
        return [e]
    
@app.post("/torino/geojson/")
async def upload_geojson_torino(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(JWTBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
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
async def upload_wms_torino(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(JWTBearer())], name: str = Query(..., description="Name of the wms artifact")):
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
        
@app.get("/torino/visualizations", response_model=list[object], summary="get a KPI object", tags = ["Visualisation"])
async def get_visualizations_torino():
    try:
        results_list = []
                    
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
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/cascais/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI"])
async def get_kpis_cascais():
    try:
        results_list = []
                    
        query = session.query(kpi_alias, kpitemp_alias).\
            join(kpitemp_alias, kpi_alias.id == kpitemp_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpisecondhandcustomers_alias).\
            join(kpisecondhandcustomers_alias, kpi_alias.id == kpisecondhandcustomers_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpimoney_alias).\
            join(kpimoney_alias, kpi_alias.id == kpimoney_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpitraffic_alias).\
            join(kpitraffic_alias, kpi_alias.id == kpitraffic_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpitotalrenewableenergy_alias).\
            join(kpitotalrenewableenergy_alias, kpi_alias.id == kpitotalrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpicollectedwaste_alias).\
            join(kpicollectedwaste_alias, kpi_alias.id == kpicollectedwaste_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpitextilewasteperperson_alias).\
            join(kpitextilewasteperperson_alias, kpi_alias.id == kpitextilewasteperperson_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpinumberhouseholdrenewableenergy_alias).\
            join(kpinumberhouseholdrenewableenergy_alias, kpi_alias.id == kpinumberhouseholdrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpiwastesorted_alias).\
            join(kpiwastesorted_alias, kpi_alias.id == kpiwastesorted_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpico2avoided_alias).\
            join(kpico2avoided_alias, kpi_alias.id == kpico2avoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpipeaksolarenergy_alias).\
            join(kpipeaksolarenergy_alias, kpi_alias.id == kpipeaksolarenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpiparticipants_alias).\
            join(kpiparticipants_alias, kpi_alias.id == kpiparticipants_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
                            
        query = session.query(kpi_alias, kpiwasteavoided_alias).\
            join(kpiwasteavoided_alias, kpi_alias.id == kpiwasteavoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("cascais"))

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
        return [e]
    
@app.post("/cascais/geojson/")
async def upload_geojson_cascais(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(JWTBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
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
async def upload_wms_cascais(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(JWTBearer())], name: str = Query(..., description="Name of the wms artifact")):
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
        
@app.get("/cascais/visualizations", response_model=list[object], summary="get a KPI object", tags = ["Visualisation"])
async def get_visualizations_cascais():
    try:
        results_list = []
                    
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
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/differdange/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI"])
async def get_kpis_differdange():
    try:
        results_list = []
                    
        query = session.query(kpi_alias, kpitemp_alias).\
            join(kpitemp_alias, kpi_alias.id == kpitemp_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpisecondhandcustomers_alias).\
            join(kpisecondhandcustomers_alias, kpi_alias.id == kpisecondhandcustomers_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpimoney_alias).\
            join(kpimoney_alias, kpi_alias.id == kpimoney_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpitraffic_alias).\
            join(kpitraffic_alias, kpi_alias.id == kpitraffic_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpitotalrenewableenergy_alias).\
            join(kpitotalrenewableenergy_alias, kpi_alias.id == kpitotalrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpicollectedwaste_alias).\
            join(kpicollectedwaste_alias, kpi_alias.id == kpicollectedwaste_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpitextilewasteperperson_alias).\
            join(kpitextilewasteperperson_alias, kpi_alias.id == kpitextilewasteperperson_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpinumberhouseholdrenewableenergy_alias).\
            join(kpinumberhouseholdrenewableenergy_alias, kpi_alias.id == kpinumberhouseholdrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpiwastesorted_alias).\
            join(kpiwastesorted_alias, kpi_alias.id == kpiwastesorted_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpico2avoided_alias).\
            join(kpico2avoided_alias, kpi_alias.id == kpico2avoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpipeaksolarenergy_alias).\
            join(kpipeaksolarenergy_alias, kpi_alias.id == kpipeaksolarenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpiparticipants_alias).\
            join(kpiparticipants_alias, kpi_alias.id == kpiparticipants_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
                            
        query = session.query(kpi_alias, kpiwasteavoided_alias).\
            join(kpiwasteavoided_alias, kpi_alias.id == kpiwasteavoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("differdange"))

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
        return [e]
    
@app.post("/differdange/geojson/")
async def upload_geojson_differdange(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(JWTBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
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
async def upload_wms_differdange(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(JWTBearer())], name: str = Query(..., description="Name of the wms artifact")):
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
        
@app.get("/differdange/visualizations", response_model=list[object], summary="get a KPI object", tags = ["Visualisation"])
async def get_visualizations_differdange():
    try:
        results_list = []
                    
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
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
     
@app.get("/sofia/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI"])
async def get_kpis_sofia():
    try:
        results_list = []
                    
        query = session.query(kpi_alias, kpitemp_alias).\
            join(kpitemp_alias, kpi_alias.id == kpitemp_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpisecondhandcustomers_alias).\
            join(kpisecondhandcustomers_alias, kpi_alias.id == kpisecondhandcustomers_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpimoney_alias).\
            join(kpimoney_alias, kpi_alias.id == kpimoney_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpitraffic_alias).\
            join(kpitraffic_alias, kpi_alias.id == kpitraffic_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpitotalrenewableenergy_alias).\
            join(kpitotalrenewableenergy_alias, kpi_alias.id == kpitotalrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpicollectedwaste_alias).\
            join(kpicollectedwaste_alias, kpi_alias.id == kpicollectedwaste_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpitextilewasteperperson_alias).\
            join(kpitextilewasteperperson_alias, kpi_alias.id == kpitextilewasteperperson_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpinumberhouseholdrenewableenergy_alias).\
            join(kpinumberhouseholdrenewableenergy_alias, kpi_alias.id == kpinumberhouseholdrenewableenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpiwastesorted_alias).\
            join(kpiwastesorted_alias, kpi_alias.id == kpiwastesorted_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpico2avoided_alias).\
            join(kpico2avoided_alias, kpi_alias.id == kpico2avoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpipeaksolarenergy_alias).\
            join(kpipeaksolarenergy_alias, kpi_alias.id == kpipeaksolarenergy_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpiparticipants_alias).\
            join(kpiparticipants_alias, kpi_alias.id == kpiparticipants_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
                            
        query = session.query(kpi_alias, kpiwasteavoided_alias).\
            join(kpiwasteavoided_alias, kpi_alias.id == kpiwasteavoided_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("sofia"))

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
        return [e]
    
@app.post("/sofia/geojson/")
async def upload_geojson_sofia(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(JWTBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
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
async def upload_wms_sofia(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(JWTBearer())], name: str = Query(..., description="Name of the wms artifact")):
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
        
@app.get("/sofia/visualizations", response_model=list[object], summary="get a KPI object", tags = ["Visualisation"])
async def get_visualizations_sofia():
    try:
        results_list = []
                    
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
                
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
@app.get("/ioannina/kpi/", response_model=list[object], summary="get a KPI object", tags = ["KPI"])
async def get_kpi_ioannina(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("ioannina"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        results_list = []
        for result in results:
            res = dict()
            attributes = inspect(result).attrs
            for attr in attributes:
                if attr.key.lower() == "values" or attr.key.lower() == "value":
                    continue
                res[attr.key] = getattr(result, attr.key)
            results_list.append(res)

        return results_list
    except Exception as e:
        return [{'err': e}]
    
@app.get("/maribor/kpi/", response_model=list[object], summary="get a KPI object", tags = ["KPI"])
async def get_kpi_maribor(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("maribor"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        results_list = []
        for result in results:
            res = dict()
            attributes = inspect(result).attrs
            for attr in attributes:
                if attr.key.lower() == "values" or attr.key.lower() == "value":
                    continue
                res[attr.key] = getattr(result, attr.key)
            results_list.append(res)

        return results_list
    except Exception as e:
        return [{'err': e}]
    
@app.get("/grenoble/kpi/", response_model=list[object], summary="get a KPI object", tags = ["KPI"])
async def get_kpi_grenoble(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("grenoble"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        results_list = []
        for result in results:
            res = dict()
            attributes = inspect(result).attrs
            for attr in attributes:
                if attr.key.lower() == "values" or attr.key.lower() == "value":
                    continue
                res[attr.key] = getattr(result, attr.key)
            results_list.append(res)

        return results_list
    except Exception as e:
        return [{'err': e}]
    
@app.get("/athens/kpi/", response_model=list[object], summary="get a KPI object", tags = ["KPI"])
async def get_kpi_athens(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("athens"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        results_list = []
        for result in results:
            res = dict()
            attributes = inspect(result).attrs
            for attr in attributes:
                if attr.key.lower() == "values" or attr.key.lower() == "value":
                    continue
                res[attr.key] = getattr(result, attr.key)
            results_list.append(res)

        return results_list
    except Exception as e:
        return [{'err': e}]
    
@app.get("/torino/kpi/", response_model=list[object], summary="get a KPI object", tags = ["KPI"])
async def get_kpi_torino(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("torino"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        results_list = []
        for result in results:
            res = dict()
            attributes = inspect(result).attrs
            for attr in attributes:
                if attr.key.lower() == "values" or attr.key.lower() == "value":
                    continue
                res[attr.key] = getattr(result, attr.key)
            results_list.append(res)

        return results_list
    except Exception as e:
        return [{'err': e}]
    
@app.get("/cascais/kpi/", response_model=list[object], summary="get a KPI object", tags = ["KPI"])
async def get_kpi_cascais(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("cascais"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        results_list = []
        for result in results:
            res = dict()
            attributes = inspect(result).attrs
            for attr in attributes:
                if attr.key.lower() == "values" or attr.key.lower() == "value":
                    continue
                res[attr.key] = getattr(result, attr.key)
            results_list.append(res)

        return results_list
    except Exception as e:
        return [{'err': e}]
    
@app.get("/differdange/kpi/", response_model=list[object], summary="get a KPI object", tags = ["KPI"])
async def get_kpi_differdange(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("differdange"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        results_list = []
        for result in results:
            res = dict()
            attributes = inspect(result).attrs
            for attr in attributes:
                if attr.key.lower() == "values" or attr.key.lower() == "value":
                    continue
                res[attr.key] = getattr(result, attr.key)
            results_list.append(res)

        return results_list
    except Exception as e:
        return [{'err': e}]
    
@app.get("/sofia/kpi/", response_model=list[object], summary="get a KPI object", tags = ["KPI"])
async def get_kpi_sofia(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("sofia"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
        results_list = []
        for result in results:
            res = dict()
            attributes = inspect(result).attrs
            for attr in attributes:
                if attr.key.lower() == "values" or attr.key.lower() == "value":
                    continue
                res[attr.key] = getattr(result, attr.key)
            results_list.append(res)

        return results_list
    except Exception as e:
        return [{'err': e}]
    


@app.delete("/", dependencies=[Depends(JWTBearer())],  summary="Delete everything from the database, please never use this")
async def delete_all(dependencies=[Depends(JWTBearer())]):
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
        "name": "KPI",
        "description": "Operations related to KPI objects",
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