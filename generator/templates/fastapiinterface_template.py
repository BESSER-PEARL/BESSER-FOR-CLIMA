from fastapi import FastAPI, HTTPException, Body
import psycopg2
from pydantic import BaseModel
from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Union
import pydantic_classes as py_classes
from pydantic_classes import {% for class in classes %}{% if not loop.last %}{{class.name}}, {{class.name}}DB,{% else %}{{class.name}}, {{class.name}}DB{% endif %}{% endfor %}
app = FastAPI()

engine = create_engine("postgresql://127.0.0.1/aaron?user=aaron&password=aaron")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

py_classes.create_all(engine)

# In-memory storage for KPI objects
kpi_objects = []
{% for class in classes %}
@app.post("/kpi/{{ class.name }}", response_model={{ class.name }}, summary="Add a KPI object")
async def create_kpi_{{ class.name }}(kpi: {{ class.name }}= Body(..., description="KPI object to add")):
    db_entry = {{ class.name }}DB(**kpi.model_dump())
    db = SessionLocal()
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    db.close()   
    return {"message": "KPI added to the database"}
{% endfor %}

# Optional: Swagger UI metadata
tags_metadata = [
    {
        "name": "KPI",
        "description": "Operations related to KPI objects",
    },
]

app.openapi_tags = tags_metadata


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
