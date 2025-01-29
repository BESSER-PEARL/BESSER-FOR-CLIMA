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
{% set ns = namespace(first_object_added=false) -%}
from pydantic_classes import {% for object in classes %}{% if not ns.first_object_added -%}{% set ns.first_object_added = true -%}{% else -%}, {% endif -%} {{object.name}}{% endfor %}
{% set ns.first_object_added=false -%}
from sql_alchemy import Base
from sql_alchemy import {% for object in classes %}{% if not ns.first_object_added -%}{% set ns.first_object_added = true -%}{% else -%}, {% endif -%} {{object.name}} as {{object.name}}DB{% endfor %}
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
    
    

{% for object in objects -%}




{{ object.className.name }} = session.query({{ object.name }}DB).filter_by(  
    {%- for attribute in object.attributes -%}
    {{ attribute.name -}} = {% for class in classes -%}
        {% if class.name == object.name -%}
            {% for attr in class.all_attributes() -%}
                {% if attr.name == attribute.name -%}
                    {%- if attr.type.name == "str" -%}
                        "{{- attribute.value -}}"
                    {%- else -%}
                        {{- attribute.value -}}
                    {%- endif -%}
                {% endif -%}
            {% endfor -%}
        {% endif -%}
    {% endfor -%}
    {% if not loop.last -%}
    {{-", "-}}   
    {% endif -%}
{%- endfor -%}   ).first()

if {{ object.className.name }} is None:
    {{ object.className.name }} = {{ object.name -}}
DB({% for attribute in object.attributes -%}
    {{ attribute.name -}} = {% for class in classes -%}
        {% if class.name == object.name -%}
            {% for attr in class.all_attributes() -%}
                {% if attr.name == attribute.name -%}
                    {%- if attr.type.name == "str" -%}
                        "{{- attribute.value -}}"
                    {%- else -%}
                        {{- attribute.value -}}
                    {%- endif -%}
                {% endif -%}
            {% endfor -%}
        {% endif -%}
    {% endfor -%}
    {% if not loop.last -%}
    {{-", "-}}   
    {% endif -%}
{%- endfor -%}
{%- for obj in object.dep_from -%}
    {%- for cls in classes -%}
        {% if obj.name == cls.name %}
            {%- for end in cls.all_association_ends()-%}
                {%- if end.type.name == object.name -%}
                    {{", "}}  {{- end.name -}} = {{- obj.className.name -}}
                {%- else -%}                    
                    {%- for cls in classes -%}
                        {%- if cls.name == object.name -%}
                            {%- for parent in cls.all_parents() -%}
                                {%- if end.type.name == parent.name -%}
                                    {{", "}}  {{- end.name -}} = {{- obj.className.name -}}
                                {%- endif -%}      
                            {%- endfor -%}
                        {%- endif -%}
                    {%- endfor-%}
                {%- endif -%}
            {%- endfor -%}
        {% endif %}
    {%- endfor -%}

{%- endfor -%})
try:
    session.add({{ object.className.name }})
    session.commit()
except IntegrityError: 
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? {{loop.index}}")


{% if object.name == "City" -%}
dashboard_{{object.className.name}} = session.query(DashboardDB).filter_by(code="{{object.className.name}}").first()
if dashboard_{{object.className.name}} is None:
    dashboard_{{object.className.name}} = DashboardDB(code="{{object.className.name}}", has={{object.className.name}})

try:
    session.add(dashboard_{{object.className.name}})
    session.commit()
except IntegrityError:
    session.rollback()
    print("error integrity")
except:
    session.rollback()
    print("error already added? {{loop.index}}")


{% endif %}

{%- endfor -%}

{% for class in classes %}           
{{class.name | lower}}_alias = aliased({{class.name}}DB)
{% endfor %}  
    
{% set is_active = false %}

{% set city_object = objects | selectattr("name", "equalto", "City") | first %}

# KPI
{% if city_object %}
@app.post("/city/{city_name}/kpi/{kpi_id}", dependencies=[Depends(JWTBearer())], response_model=List[KPIValue], summary="Add KPI values", tags=["KPI"])
async def add_kpi_values(
    city_name: str,
    kpi_id: str,
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
{% endif %}

# Visualisations

{% for object in objects -%}
    {% if object.name == "City" -%}
        {% for class in classes -%}
            {% for parent in class.parents() -%}
                {% if parent.name == "Visualisation" %}            
@app.post("/{{object.className.name}}/visualization/{{class.name}}/{id}", dependencies=[Depends(JWTBearer())], response_model=int, summary="Add a Chart object", tags = ["Visualisation"])
async def add_or_update_{{class.name}}_{{object.className.name}}(id: int, chart: {{class.name}}= Body(..., description="Chart object to add")):
    db_entry = {{class.name}}DB(**chart.dict())
    existing_chart = session.query({{class.name}}DB).filter({{class.name}}DB.i == db_entry.i).first()
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
        db_entry = {{class.name}}DB(**chart.dict())
        db_entry.consistsOf = dashboard_{{object.className.name}}
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
                {% endif %}
            {% endfor %}
        {%- endfor %}
        
@app.delete("/{{object.className.name}}/visualizations")
async def delete_visualizations_{{object.className.name}}(ids: List[int], dependencies=[Depends(JWTBearer())], tags = ["Visualisation"]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualisationDB).filter(~VisualisationDB.id.in_(ids)).all()
        for row in rows_to_delete:
            
            if (row.consistsOf.code == "{{object.className.name}}"):
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

    {% endif %}
{%- endfor %}

{% for object in objects %}
    {% if object.name == "City" %} 
@app.get("/{{object.className.name}}/kpis", response_model=list[object], summary="get all KPI object",  tags=["KPI"])
async def get_kpis_{{object.className.name}}():
    try:
        results_list = []
        {% for class in classes -%}
            {% for parent in class.parents() -%}
                {% if parent.name == "KPI" %}            
        query = session.query(kpi_alias, {{class.name | lower }}_alias).\
            join({{class.name | lower }}_alias, kpi_alias.id == {{class.name | lower}}_alias.id).\
            join(city_alias, city_alias.id == kpi_alias.city_id).\
            filter(func.lower(city_alias.name) == func.lower("{{object.className.name}}"))

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
                {% endif -%}
            {% endfor -%}
        {%- endfor %}
        return results_list
    except Exception as e:
        return [e]
    
@app.post("/{{object.className.name}}/geojson/")
async def upload_geojson_{{object.className.name}}(title: str = Query(..., description="Title of the GeoJSON data"), dependencies=[Depends(JWTBearer())], geojson_data: dict = Body(..., description="GeoJSON data")):
    try:
        # Create a new GeoJson entry
        new_data = GeoJsonDB(
            title=title,
            data=json.dumps(geojson_data),
            hasMapData={{object.className.name}}
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/{{object.className.name}}/geojson/")
async def get_geojson_for_{{object.className.name}}():
    results = []
    try:
        # Query the database for geospatial data for the given city
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == {{object.className.name}}.id).all()

        # Check if data exists for the city
        if not geojson_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in geojson_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/{{object.className.name}}/wms/")
async def upload_wms_{{object.className.name}}(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), dependencies=[Depends(JWTBearer())], name: str = Query(..., description="Name of the wms artifact")):
    try:
        
        # Create a new GeoJson entry
        new_data = WMSDB(
            title=title,
            url=url,
            name=name,
            hasMapData={{object.className.name}}
        )
        session.add(new_data)
        session.commit()
        
        return {"status": "success", "message": "GeoJSON file processed and data stored in the database."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/{{object.className.name}}/wms/")
async def get_wms_for_{{object.className.name}}():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == {{object.className.name}}.id).all()

        # Check if data exists for the city
        if not wms_data:
            raise HTTPException(status_code=404, detail=f"No geospatial data found for city: torino")
        for result in wms_data: 
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/{{object.className.name}}/mapdata/")    
async def get_mapdata_for_{{object.className.name}}():
    results = []
    try:
        # Query the database for geospatial data for the given city
        wms_data = session.query(WMSDB).filter(WMSDB.city_id == {{object.className.name}}.id).all()

        # Check if data exists for the city
        if not wms_data:
            print("sucks")
        for result in wms_data: 
            results.append(result)
        geojson_data = session.query(GeoJsonDB).filter(GeoJsonDB.city_id == {{object.className.name}}.id).all()

        # Check if data exists for the city
        if not geojson_data:
            print("sucks")
        for result in geojson_data: 
            results.append(result)
        return results            
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")     
        
@app.get("/{{object.className.name}}/visualizations", response_model=list[object], summary="get a KPI object", tags = ["Visualisation"])
async def get_visualizations_{{object.className.name}}():
    try:
        results_list = []
        {% for class in classes -%}
            {% for parent in class.parents() -%}
                {% if parent.name == "Visualisation" %}            
        query = session.query(visualisation_alias, {{class.name | lower }}_alias).\
            join({{class.name | lower}}_alias, visualisation_alias.id == {{class.name | lower}}_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualisation_alias.dashboard_id).\
            filter(func.lower(dashboard_alias.code) == func.lower("{{object.className.name}}"))

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
                {% endif -%}
            {% endfor -%}
        {%- endfor %}
        return results_list
    except Exception as e:
        session.rollback()
        return [{"error": str(e)}]
    {% endif -%}
{%- endfor -%}

{%- for object in objects -%}
    {%- if object.name == "City" %}
@app.get("/{{object.className.name}}/kpi/", response_model=list[object], summary="get a KPI object", tags = ["KPI"])
async def get_kpi_{{object.className.name}}(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("{{object.className.name}}"), KPIDB.id == id).order_by(KPIValueDB.timestamp).all()
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
    {% endif %}
{%- endfor %}


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
