from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from abc import ABC, abstractmethod
from typing import Dict, Optional


class City(BaseModel):
    name: str
    
class TableColumn(BaseModel):
    name: str
    
class Dashboard(BaseModel):
    code: str
    
class KPI(ABC, BaseModel):
    category: str
    unitText: str
    name: str
    description: str
    id_kpi: str
    provider: Optional[str] = None
    calculationFrequency: Optional[str] = None
    minThreshold: Optional[float] = None
    maxThreshold: Optional[float] = None
    hasCategoryLabel: bool
    categoryLabelDictionary: Optional[Dict[int, str]] = None
    
class Visualisation(ABC, BaseModel):
    section: str
    width: int
    height: int
    title: str
    chartType: str
    i: str
    yposition: int
    xposition: int
    
class StatChart(Visualisation):
    unit: str
    
class LineChart(Visualisation):
    xtitle: str
    ytitle: str
    color: str
    
class Map(Visualisation):
    pass 
    
class PieChart(Visualisation):
    pass 
    
class Table(Visualisation):
    pass 
    
class BarChart(Visualisation):
    pass 
    
class KPIValue(BaseModel):
    kpiValue: float
    timestamp: datetime
    categoryLabel: Optional[str] = None
    
class MapData(ABC, BaseModel):
    title: str
    
class WMS(MapData):
    url: str
    name: str
    
class GeoJson(MapData):
    data: str
    