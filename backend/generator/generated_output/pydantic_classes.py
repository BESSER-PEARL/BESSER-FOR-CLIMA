from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from abc import ABC, abstractmethod


class KPIValue(BaseModel):
    currentStanding: str
    timestamp: datetime
    kpiValue: int
    
class User(ABC, BaseModel):
    email: str
    lastName: str
    firstName: str
    password: str
    
class CityUser(User):
    pass 
    
class Admin(User):
    pass 
    
class SolutionProvider(User):
    pass 
    
class KPI(ABC, BaseModel):
    provider: str
    name: str
    id_kpi: str
    calculationFrequency: str
    unitText: str
    category: str
    description: str
    
class KPITemp(KPI):
    threshold: int
    
class KPISecondHandCustomers(KPI):
    target: int
    
class KPIMoney(KPI):
    target: int
    
class CityAngel(User):
    pass 
    
class KPITraffic(KPI):
    target: int
    
class KPITotalRenewableEnergy(KPI):
    target: int
    
class Visualisation(ABC, BaseModel):
    title: str
    width: int
    chartType: str
    xposition: int
    yposition: int
    section: str
    i: str
    height: int
    
class LineChart(Visualisation):
    xtitle: str
    ytitle: str
    color: str
    target: int
    
class BarChart(Visualisation):
    pass 
    
class PieChart(Visualisation):
    pass 
    
class StatChart(Visualisation):
    unit: str
    target: int
    
class City(BaseModel):
    name: str
    
class TableColumn(BaseModel):
    name: str
    
class KPICollectedWaste(KPI):
    target: int
    
class Table(Visualisation):
    pass 
    
class KPITextileWastePerPerson(KPI):
    pass 
    
class KPINumberHouseholdRenewableEnergy(KPI):
    target: int
    
class MapData(ABC, BaseModel):
    title: str
    
class GeoJson(MapData):
    data: str
    
class WMS(MapData):
    name: str
    url: str
    
class Citizen(User):
    pass 
    
class KPIWasteSorted(KPI):
    target: int
    
class Map(Visualisation):
    pass 
    
class KPICo2Avoided(KPI):
    target: int
    
class KPIPeakSolarEnergy(KPI):
    target: int
    
class Dashboard(BaseModel):
    code: str
    
class KPIParticipants(KPI):
    target: int
    
class KPIWasteAvoided(KPI):
    target: int
    