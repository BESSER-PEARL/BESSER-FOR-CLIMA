from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from abc import ABC, abstractmethod


class User(ABC, BaseModel):
    firstName: str
    password: str
    email: str
    lastName: str
    
class CityAngel(User):
    pass 
    
class KPIValue(BaseModel):
    kpiValue: int
    timestamp: datetime
    currentStanding: str
    
class Visualisation(ABC, BaseModel):
    title: str
    width: int
    chartType: str
    xposition: int
    yposition: int
    section: str
    i: str
    height: int
    
class PieChart(Visualisation):
    pass 
    
class Table(Visualisation):
    pass 
    
class LineChart(Visualisation):
    ytitle: str
    color: str
    target: int
    xtitle: str
    
class TableColumn(BaseModel):
    name: str
    
class StatChart(Visualisation):
    unit: str
    target: int
    
class Dashboard(BaseModel):
    code: str
    
class Map(Visualisation):
    pass 
    
class Admin(User):
    pass 
    
class Citizen(User):
    pass 
    
class City(BaseModel):
    name: str
    
class BarChart(Visualisation):
    pass 
    
class CityUser(User):
    pass 
    
class MapData(ABC, BaseModel):
    title: str
    
class GeoJson(MapData):
    data: str
    
class WMS(MapData):
    name: str
    url: str
    
class KPI(ABC, BaseModel):
    description: str
    provider: str
    name: str
    id_kpi: str
    calculationFrequency: str
    unitText: str
    category: str
    
class KPIWasteSorted(KPI):
    target: int
    
class KPISecondHandCustomers(KPI):
    target: int
    
class KPITraffic(KPI):
    target: int
    
class KPICo2Avoided(KPI):
    target: int
    
class KPITemp(KPI):
    threshold: int
    
class KPINumberHouseholdRenewableEnergy(KPI):
    target: int
    
class KPIParticipants(KPI):
    target: int
    
class KPIWasteAvoided(KPI):
    target: int
    
class KPITotalRenewableEnergy(KPI):
    target: int
    
class KPICollectedWaste(KPI):
    target: int
    
class SolutionProvider(User):
    pass 
    
class KPITextileWastePerPerson(KPI):
    pass 
    
class KPIMoney(KPI):
    target: int
    
class KPIPeakSolarEnergy(KPI):
    target: int
    