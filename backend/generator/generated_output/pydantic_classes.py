from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from abc import ABC, abstractmethod


class City(BaseModel):
    name: str
    
class KPI(ABC, BaseModel):
    id_kpi: str
    name: str
    category: str
    description: str
    provider: str
    calculationFrequency: str
    unitText: str
    
class KPIValue(BaseModel):
    timestamp: datetime
    currentStanding: str
    kpiValue: int
    
class KPITemp(KPI):
    threshold: int
    
class KPITraffic(KPI):
    target: int
    
class KPICollectedWaste(KPI):
    target: int
    
class KPISecondHandCustomers(KPI):
    target: int
    
class KPIMoney(KPI):
    target: int
    
class KPITotalRenewableEnergy(KPI):
    target: int
    
class KPINumberHouseholdRenewableEnergy(KPI):
    target: int
    
class KPIPeakSolarEnergy(KPI):
    target: int
    
class Visualisation(ABC, BaseModel):
    xposition: int
    yposition: int
    width: int
    height: int
    chartType: str
    title: str
    i: str
    section: str
    
class Table(Visualisation):
    pass 
    
class PieChart(Visualisation):
    pass 
    
class StatChart(Visualisation):
    unit: str
    target: int
    
class LineChart(Visualisation):
    ytitle: str
    color: str
    xtitle: str
    target: int
    
class TableColumn(BaseModel):
    name: str
    
class Map(Visualisation):
    pass 
    
class User(ABC, BaseModel):
    email: str
    firstName: str
    password: str
    lastName: str
    
class Admin(User):
    pass 
    
class CityUser(User):
    pass 
    
class CityAngel(User):
    pass 
    
class SolutionProvider(User):
    pass 
    
class Citizen(User):
    pass 
    
class Dashboard(BaseModel):
    code: str
    
class MapData(ABC, BaseModel):
    title: str
    
class GeoJson(MapData):
    data: str
    
class WMS(MapData):
    url: str
    name: str
    
class KPIParticipants(KPI):
    target: int
    
class KPIWasteAvoided(KPI):
    target: int
    
class KPICo2Avoided(KPI):
    target: int
    
class KPIWasteSorted(KPI):
    target: int
    
class KPITextileWastePerPerson(KPI):
    pass 
    