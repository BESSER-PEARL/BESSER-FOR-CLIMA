from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

{% for class in classes %}class {{ class.name }}(BaseModel):
        {% for attribute in class.all_attributes() %}{{ attribute.name }}: {{ attribute.type.name }}
        {% endfor %}
{% endfor %}
Base = declarative_base()

{% for class in classes %}
class {{ class.name }}DB(Base):
    __tablename__ = '{{ class.name }}'.lower()

    id = Column(Integer, primary_key=True, autoincrement=True)

    {% for attribute in class.all_attributes() %}
    {{- attribute.name }} = Column(
        {%- if attribute.type.name == 'str' %}String{%- endif %}
        {%- if attribute.type.name == 'int' %}Integer{%- endif %}
        {%- if attribute.type.name == 'date' %}TIMESTAMP{%- endif %}
        {%- if attribute.type.name == 'time' %}TIMESTAMP{%- endif %}
        {%- if attribute.type.name == 'datetime' %}TIMESTAMP{%- endif %})
    {% endfor %}
{% endfor %}


def create_all(engine):
    Base.metadata.create_all(bind=engine)