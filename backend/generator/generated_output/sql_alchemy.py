from typing import List
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.orm import column_property
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, String, Date, Time, DateTime, Float, Integer
from datetime import datetime, time, date

class Base(DeclarativeBase):
    pass

# Tables definition for many-to-many relationships

# Tables definition
class Visualisation(Base):
    
    __tablename__ = "visualisation"
    id: Mapped[int] = mapped_column(primary_key=True)
    xposition: Mapped[int] = mapped_column(Integer)
    yposition: Mapped[int] = mapped_column(Integer)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    chartType: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(100))
    i: Mapped[str] = mapped_column(String(100))
    section: Mapped[str] = mapped_column(String(100))
    type_spec: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "visualisation",
        "polymorphic_on": "type_spec",
    }

class Table(Visualisation):
        
    __tablename__ = "table"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "table",
    }

class PieChart(Visualisation):
        
    __tablename__ = "piechart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "piechart",
    }

class BarChart(Visualisation):
        
    __tablename__ = "barchart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "barchart",
    }

class StatChart(Visualisation):
        
    __tablename__ = "statchart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    unit: Mapped[str] = mapped_column(String(100))
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "statchart",
    }

class LineChart(Visualisation):
        
    __tablename__ = "linechart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    ytitle: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(100))
    xtitle: Mapped[str] = mapped_column(String(100))
    __mapper_args__ = {
        "polymorphic_identity": "linechart",
    }

class TableColumn(Base):
    
    __tablename__ = "tablecolumn"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

class Map(Visualisation):
        
    __tablename__ = "map"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "map",
    }

class User(Base):
    
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100))
    firstName: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(100))
    lastName: Mapped[str] = mapped_column(String(100))
    type_spec: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": "type_spec",
    }

class Admin(User):
        
    __tablename__ = "admin"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

class CityUser(User):
        
    __tablename__ = "cityuser"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "cityuser",
    }

class CityAngel(User):
        
    __tablename__ = "cityangel"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "cityangel",
    }

class SolutionProvider(User):
        
    __tablename__ = "solutionprovider"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "solutionprovider",
    }

class Citizen(User):
        
    __tablename__ = "citizen"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "citizen",
    }

class Dashboard(Base):
    
    __tablename__ = "dashboard"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100))

class MapData(Base):
    
    __tablename__ = "mapdata"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    type_spec: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "mapdata",
        "polymorphic_on": "type_spec",
    }

class GeoJson(MapData):
        
    __tablename__ = "geojson"
    id: Mapped[int] = mapped_column(ForeignKey("mapdata.id"), primary_key=True)
    data: Mapped[str] = mapped_column(String(100))
    __mapper_args__ = {
        "polymorphic_identity": "geojson",
    }

class WMS(MapData):
        
    __tablename__ = "wms"
    id: Mapped[int] = mapped_column(ForeignKey("mapdata.id"), primary_key=True)
    url: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    __mapper_args__ = {
        "polymorphic_identity": "wms",
    }

class City(Base):
    
    __tablename__ = "city"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

class KPI(Base):
    
    __tablename__ = "kpi"
    id: Mapped[int] = mapped_column(primary_key=True)
    id_kpi: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(100))
    calculationFrequency: Mapped[str] = mapped_column(String(100))
    unitText: Mapped[str] = mapped_column(String(100))
    type_spec: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "kpi",
        "polymorphic_on": "type_spec",
    }

class KPIValue(Base):
    
    __tablename__ = "kpivalue"
    id: Mapped[int] = mapped_column(primary_key=True)
    kpiValue: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    currentStanding: Mapped[str] = mapped_column(String(100))

class KPITemp(KPI):
        
    __tablename__ = "kpitemp"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    threshold: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpitemp",
    }

class KPITraffic(KPI):
        
    __tablename__ = "kpitraffic"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpitraffic",
    }

class KPICollectedWaste(KPI):
        
    __tablename__ = "kpicollectedwaste"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpicollectedwaste",
    }

class KPISecondHandCustomers(KPI):
        
    __tablename__ = "kpisecondhandcustomers"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpisecondhandcustomers",
    }

class KPIMoney(KPI):
        
    __tablename__ = "kpimoney"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpimoney",
    }

class KPITotalRenewableEnergy(KPI):
        
    __tablename__ = "kpitotalrenewableenergy"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpitotalrenewableenergy",
    }

class KPINumberHouseholdRenewableEnergy(KPI):
        
    __tablename__ = "kpinumberhouseholdrenewableenergy"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpinumberhouseholdrenewableenergy",
    }

class KPIPeakSolarEnergy(KPI):
        
    __tablename__ = "kpipeaksolarenergy"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpipeaksolarenergy",
    }

class KPIParticipants(KPI):
        
    __tablename__ = "kpiparticipants"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpiparticipants",
    }

class KPIWasteAvoided(KPI):
        
    __tablename__ = "kpiwasteavoided"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpiwasteavoided",
    }

class KPICo2Avoided(KPI):
        
    __tablename__ = "kpico2avoided"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpico2avoided",
    }

class KPIWasteSorted(KPI):
        
    __tablename__ = "kpiwastesorted"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpiwastesorted",
    }

class KPITextileWastePerPerson(KPI):
        
    __tablename__ = "kpitextilewasteperperson"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "kpitextilewasteperperson",
    }


#--- Foreign keys and relationships of the visualisation table
Visualisation.kpi_id: Mapped["KPI"] = mapped_column(ForeignKey("kpi.id"), nullable=False)
Visualisation.visualizedBy: Mapped["KPI"] = relationship("KPI", back_populates="visualizedBy")
Visualisation.dashboard_id: Mapped["Dashboard"] = mapped_column(ForeignKey("dashboard.id"), nullable=False)
Visualisation.consistsOf: Mapped["Dashboard"] = relationship("Dashboard", back_populates="consistsOf")

#--- Foreign keys and relationships of the table table
Table.shows: Mapped[List["TableColumn"]] = relationship("TableColumn", back_populates="shows")

#--- Foreign keys and relationships of the tablecolumn table
TableColumn.table_id: Mapped["Table"] = mapped_column(ForeignKey("table.id"), nullable=False)
TableColumn.shows: Mapped["Table"] = relationship("Table", back_populates="shows")

#--- Foreign keys and relationships of the map table
Map.mapdata_id: Mapped["MapData"] = mapped_column(ForeignKey("mapdata.id"), nullable=False)
Map.isDisplayedOnMap: Mapped["MapData"] = relationship("MapData", back_populates="isDisplayedOnMap")

#--- Foreign keys and relationships of the user table
User.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
User.operatedBy: Mapped["City"] = relationship("City", back_populates="operatedBy")

#--- Foreign keys and relationships of the dashboard table
Dashboard.consistsOf: Mapped[List["Visualisation"]] = relationship("Visualisation", back_populates="consistsOf")
Dashboard.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
Dashboard.has: Mapped["City"] = relationship("City", back_populates="has")

#--- Foreign keys and relationships of the mapdata table
MapData.isDisplayedOnMap: Mapped[List["Map"]] = relationship("Map", back_populates="isDisplayedOnMap")
MapData.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
MapData.hasMapData: Mapped["City"] = relationship("City", back_populates="hasMapData")

#--- Foreign keys and relationships of the city table
City.hasMapData: Mapped[List["MapData"]] = relationship("MapData", back_populates="hasMapData")
City.operatedBy: Mapped[List["User"]] = relationship("User", back_populates="operatedBy")
City.has: Mapped[List["Dashboard"]] = relationship("Dashboard", back_populates="has")
City.kpis: Mapped[List["KPI"]] = relationship("KPI", back_populates="kpis")

#--- Foreign keys and relationships of the kpi table
KPI.visualizedBy: Mapped[List["Visualisation"]] = relationship("Visualisation", back_populates="visualizedBy")
KPI.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
KPI.kpis: Mapped["City"] = relationship("City", back_populates="kpis")
KPI.values: Mapped[List["KPIValue"]] = relationship("KPIValue", back_populates="values")

#--- Foreign keys and relationships of the kpivalue table
KPIValue.kpi_id: Mapped["KPI"] = mapped_column(ForeignKey("kpi.id"), nullable=False)
KPIValue.values: Mapped["KPI"] = relationship("KPI", back_populates="values")