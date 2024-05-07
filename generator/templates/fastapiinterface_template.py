from fastapi import FastAPI, HTTPException, Body
import psycopg2
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Union
import os
{% set ns = namespace(first_class_added=false) -%}
from pydantic_classes import {% for class in classes %}{% if not class.is_abstract %}{% if not ns.first_class_added -%}{% set ns.first_class_added = true -%}{% else -%}, {% endif -%} {{class.name}}{% endif %}{% endfor %}
{% set ns.first_class_added=false -%}
from sql_alchemy import Base
from sql_alchemy import {% for class in classes %}{% if not class.is_abstract %}{% if not ns.first_class_added -%}{% set ns.first_class_added = true -%}{% else -%}, {% endif -%} {{class.name}} as {{class.name}}DB{% endif %}{% endfor %}
app = FastAPI()

db_host = os.environ.get("DB_HOST")
if db_host is None:
    db_host = "127.0.0.1"

engine = create_engine("postgresql://" + db_host + "/aaron?user=aaron&password=aaron")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

{% for class in classes %}
    {% if not class.is_abstract %}
@app.post("/kpi/{{ class.name }}", response_model={{ class.name }}, summary="Add a KPI object")
async def create_kpi_{{ class.name }}(kpi: {{ class.name }}= Body(..., description="KPI object to add")):
    db_entry = {{ class.name }}DB(**kpi.model_dump())
    db = SessionLocal()
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    db.close()   
    return kpi
    {% endif %}
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
