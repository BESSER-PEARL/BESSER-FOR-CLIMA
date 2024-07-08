from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, func 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import Union
import os
from sqlalchemy import inspect, MetaData
{% set ns = namespace(first_object_added=false) -%}
from pydantic_classes import {% for object in classes %}{% if not ns.first_object_added -%}{% set ns.first_object_added = true -%}{% else -%}, {% endif -%} {{object.name}}{% endfor %}
{% set ns.first_object_added=false -%}
from sql_alchemy import Base
from sql_alchemy import {% for object in classes %}{% if not ns.first_object_added -%}{% set ns.first_object_added = true -%}{% else -%}, {% endif -%} {{object.name}} as {{object.name}}DB{% endfor %}
from sql_alchemy import KPI as KPIDB
from sqlalchemy.orm import aliased

from fastapi import File, UploadFile, HTTPException
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
import json


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
{% for object in objects -%}
{%- if object.name != "KPIValue" -%}

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
    print("error already added? {{loop.index}}")


{% endif %}

{%- if object.name == "City" -%}
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
    print("error already added? {{loop.index}}")


{% endif %}

{%- endfor -%}



@app.post("/admin", response_model=Admin, summary="Add an admin")
async def add_admin(user: Admin= Body(..., description="Admin to add")):
    db_entry = AdminDB(**user.dict())
    try:
        session.add(db_entry)
        session.commit()
        session.refresh(db_entry)   
    except IntegrityError: 
        session.rollback()
        print("Error integrity")
    except:
        session.rollback()
        print("Error")
    return user

# Define the Pydantic models
class UserCredentials(BaseModel):
    email: str
    password: str

@app.post("/check_user", response_model=bool, summary="Check if user in database")
def check_user(credentials: UserCredentials):
    user = session.query(UserDB).filter(UserDB.email == credentials.email, UserDB.password == credentials.password).first()
    if user:
        return user
    else:
        return {}


{% for object in objects %}
    {%- if object.name == "KPIValue" -%}
        {%- for parent in object.dep_from -%}
            {%- for grandparent in parent.dep_from -%}
                {%- if grandparent.name == "City" %}
                
@app.post("/{{grandparent.className.name}}/kpi/{{parent.className.name}}", response_model=KPIValue, summary="Add a KPI object")
async def add_kpi_value_{{-parent.className.name-}}(kpi: KPIValue= Body(..., description="KPI object to add")):
    db_entry = KPIValueDB(**kpi.dict())
    db_entry.values = {{parent.className.name}}
    try:
        session.add(db_entry)
        session.commit()
        session.refresh(db_entry)   
    except IntegrityError: 
        session.rollback()
        print("Error integrity")
    except:
        session.rollback()
        print("Error")
    return kpi 

                {%- endif -%}
            {%- endfor -%}
        {%- endfor -%}  
    {%- endif -%}
{%- endfor %}

{% for object in objects %}
    {% if object.name == "City" %}
        {% for class in classes %}
            {% for parent in class.parents() %}
                {% if parent.name == "Visualization" %}            
@app.post("/{{object.className.name}}/visualization/{{class.name}}/{id}", response_model=int, summary="Add a Chart object")
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
async def delete_visualizations_{{object.className.name}}(ids: List[int]):
    # Create a session
    try:
        # Delete rows using ORM
        rows_to_delete = session.query(VisualizationDB).filter(~VisualizationDB.id.in_(ids)).all()
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
@app.get("/{{object.className.name}}/kpis", response_model=list[object], summary="get a KPI object")
async def get_kpis_{{object.className.name}}():
    try:
        results = session.query(KPIDB.name, KPIDB.id).join(CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("{{object.className.name}}")).all()
        results_list = []
        for result in results:
            results_list.append({'name': result[0], 'id': result[1]})
        return results_list
    except Exception as e:
        return [e]
    
@app.post("/{{object.className.name}}/geojson/")
async def upload_geojson_{{object.className.name}}(title: str = Query(..., description="Title of the GeoJSON data"), file: UploadFile = File(...)):
    try:
        contents = await file.read()
        geojson_data = json.loads(contents)
        
        # Create a new GeoJson entry
        new_data = GeoJsonDB(
            title=title,
            data=geojson_data,
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
async def upload_wms_{{object.className.name}}(title: str = Query(..., description="Title of the WMS data"), url: str = Query(..., description="URL of the WMS data"), name: str = Query(..., description="Name of the wms artifact")):
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
    
    
dashboard_alias = aliased(DashboardDB)
visualization_alias = aliased(VisualizationDB)
        {%- for class in classes -%}
            {%- for parent in class.parents() -%}
                {% if parent.name == "Visualization" %}            
{{class.name}}_alias = aliased({{class.name}}DB)
                {%- endif -%}
            {%- endfor -%}
        {%- endfor %}
        
@app.get("/{{object.className.name}}/visualizations", response_model=list[object], summary="get a KPI object")
async def get_visualizations_{{object.className.name}}():
    try:
        results_list = []
        {% for class in classes -%}
            {% for parent in class.parents() -%}
                {% if parent.name == "Visualization" %}            
        query = session.query(visualization_alias, {{class.name}}_alias).\
            join({{class.name}}_alias, visualization_alias.id == {{class.name}}_alias.id).\
            join(dashboard_alias, dashboard_alias.id == visualization_alias.dashboard_id).\
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
@app.get("/{{object.className.name}}/kpi/", response_model=list[object], summary="get a KPI object")
async def get_kpi_{{object.className.name}}(id: int):
    try:
        results = session.query(KPIValueDB).join(KPIDB, KPIValueDB.kpi_id == KPIDB.id).join(
            CityDB, KPIDB.city_id == CityDB.id).filter(func.lower(CityDB.name) == func.lower("{{object.className.name}}"), KPIDB.id == id).all()
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


@app.delete("/")
async def delete_all():
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
