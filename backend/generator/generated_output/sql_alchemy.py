from typing import List, Optional
from sqlalchemy import (
    create_engine, Column, ForeignKey, Table, Text, Boolean, String, Date, 
    Time, DateTime, Float, Integer, Enum
)
from sqlalchemy.orm import (
    column_property, DeclarativeBase, Mapped, mapped_column, relationship
)
from datetime import datetime, time, date

class Base(DeclarativeBase):
    pass

# Enum definitions


# Tables definition for many-to-many relationships

# Tables definition
class KPIValue(Base):
    
    __tablename__ = "kpivalue"
    id: Mapped[int] = mapped_column(primary_key=True)
    currentStanding: Mapped[str] = mapped_column(String(100))
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    kpiValue: Mapped[int] = mapped_column(Integer)

class User(Base):
    
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(100))
    lastName: Mapped[str] = mapped_column(String(100))
    firstName: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(100))
    type_spec: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": "type_spec",
    }

class CityUser(User):
        
    __tablename__ = "cityuser"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "cityuser",
    }

class Admin(User):
        
    __tablename__ = "admin"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

class SolutionProvider(User):
        
    __tablename__ = "solutionprovider"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "solutionprovider",
    }

class KPI(Base):
    
    __tablename__ = "kpi"
    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    id_kpi: Mapped[str] = mapped_column(String(100))
    calculationFrequency: Mapped[str] = mapped_column(String(100))
    unitText: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(100))
    type_spec: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "kpi",
        "polymorphic_on": "type_spec",
    }

class KPITemp(KPI):
        
    __tablename__ = "kpitemp"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    threshold: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpitemp",
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

class CityAngel(User):
        
    __tablename__ = "cityangel"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "cityangel",
    }

class KPITraffic(KPI):
        
    __tablename__ = "kpitraffic"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpitraffic",
    }

class KPITotalRenewableEnergy(KPI):
        
    __tablename__ = "kpitotalrenewableenergy"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpitotalrenewableenergy",
    }

class Visualisation(Base):
    
    __tablename__ = "visualisation"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    width: Mapped[int] = mapped_column(Integer)
    chartType: Mapped[str] = mapped_column(String(100))
    xposition: Mapped[int] = mapped_column(Integer)
    yposition: Mapped[int] = mapped_column(Integer)
    section: Mapped[str] = mapped_column(String(100))
    i: Mapped[str] = mapped_column(String(100))
    height: Mapped[int] = mapped_column(Integer)
    type_spec: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "visualisation",
        "polymorphic_on": "type_spec",
    }

class LineChart(Visualisation):
        
    __tablename__ = "linechart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    xtitle: Mapped[str] = mapped_column(String(100))
    ytitle: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(100))
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "linechart",
    }

class BarChart(Visualisation):
        
    __tablename__ = "barchart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "barchart",
    }

class PieChart(Visualisation):
        
    __tablename__ = "piechart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "piechart",
    }

class StatChart(Visualisation):
        
    __tablename__ = "statchart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    unit: Mapped[str] = mapped_column(String(100))
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "statchart",
    }

class City(Base):
    
    __tablename__ = "city"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

class TableColumn(Base):
    
    __tablename__ = "tablecolumn"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

class KPICollectedWaste(KPI):
        
    __tablename__ = "kpicollectedwaste"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpicollectedwaste",
    }

class Table(Visualisation):
        
    __tablename__ = "table"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "table",
    }

class KPITextileWastePerPerson(KPI):
        
    __tablename__ = "kpitextilewasteperperson"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "kpitextilewasteperperson",
    }

class KPINumberHouseholdRenewableEnergy(KPI):
        
    __tablename__ = "kpinumberhouseholdrenewableenergy"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpinumberhouseholdrenewableenergy",
    }

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
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(100))
    __mapper_args__ = {
        "polymorphic_identity": "wms",
    }

class Citizen(User):
        
    __tablename__ = "citizen"
    id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "citizen",
    }

class KPIWasteSorted(KPI):
        
    __tablename__ = "kpiwastesorted"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpiwastesorted",
    }

class Map(Visualisation):
        
    __tablename__ = "map"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "map",
    }

class KPICo2Avoided(KPI):
        
    __tablename__ = "kpico2avoided"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpico2avoided",
    }

class KPIPeakSolarEnergy(KPI):
        
    __tablename__ = "kpipeaksolarenergy"
    id: Mapped[int] = mapped_column(ForeignKey("kpi.id"), primary_key=True)
    target: Mapped[int] = mapped_column(Integer)
    __mapper_args__ = {
        "polymorphic_identity": "kpipeaksolarenergy",
    }

class Dashboard(Base):
    
    __tablename__ = "dashboard"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100))

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


#--- Foreign keys and relationships of the kpivalue table
KPIValue.kpi_id: Mapped["KPI"] = mapped_column(ForeignKey("kpi.id"), nullable=False)
KPIValue.KPI: Mapped["KPI"] = relationship("KPI", back_populates="KPIValue")

#--- Foreign keys and relationships of the user table
User.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
User.City: Mapped["City"] = relationship("City", back_populates="User")

#--- Foreign keys and relationships of the kpi table
KPI.Visualisation: Mapped[List["Visualisation"]] = relationship("Visualisation", back_populates="KPI")
KPI.KPIValue: Mapped[List["KPIValue"]] = relationship("KPIValue", back_populates="KPI")
KPI.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
KPI.City: Mapped["City"] = relationship("City", back_populates="KPI")

#--- Foreign keys and relationships of the visualisation table
Visualisation.kpi_id: Mapped["KPI"] = mapped_column(ForeignKey("kpi.id"), nullable=False)
Visualisation.KPI: Mapped["KPI"] = relationship("KPI", back_populates="Visualisation")
Visualisation.dashboard_id: Mapped["Dashboard"] = mapped_column(ForeignKey("dashboard.id"), nullable=False)
Visualisation.Dashboard: Mapped["Dashboard"] = relationship("Dashboard", back_populates="Visualisation")

#--- Foreign keys and relationships of the city table
City.KPI: Mapped[List["KPI"]] = relationship("KPI", back_populates="City")
City.User: Mapped[List["User"]] = relationship("User", back_populates="City")
City.Dashboard: Mapped[List["Dashboard"]] = relationship("Dashboard", back_populates="City")
City.MapData: Mapped[List["MapData"]] = relationship("MapData", back_populates="City")

#--- Foreign keys and relationships of the tablecolumn table
TableColumn.table_id: Mapped["Table"] = mapped_column(ForeignKey("table.id"), nullable=False)
TableColumn.Table: Mapped["Table"] = relationship("Table", back_populates="TableColumn")

#--- Foreign keys and relationships of the table table
Table.TableColumn: Mapped[List["TableColumn"]] = relationship("TableColumn", back_populates="Table")

#--- Foreign keys and relationships of the mapdata table
MapData.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
MapData.City: Mapped["City"] = relationship("City", back_populates="MapData")
MapData.Map: Mapped[List["Map"]] = relationship("Map", back_populates="MapData")

#--- Foreign keys and relationships of the map table
Map.mapdata_id: Mapped["MapData"] = mapped_column(ForeignKey("mapdata.id"), nullable=False)
Map.MapData: Mapped["MapData"] = relationship("MapData", back_populates="Map")

#--- Foreign keys and relationships of the dashboard table
Dashboard.Visualisation: Mapped[List["Visualisation"]] = relationship("Visualisation", back_populates="Dashboard")
Dashboard.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
Dashboard.City: Mapped["City"] = relationship("City", back_populates="Dashboard")