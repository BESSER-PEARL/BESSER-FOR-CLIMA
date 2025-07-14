from typing import List, Optional
from sqlalchemy import (
    create_engine, Column, ForeignKey, Table, Text, Boolean, String, Date, 
    Time, DateTime, Float, Integer, Enum, JSON
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
class City(Base):
    
    __tablename__ = "city"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

class TableColumn(Base):
    
    __tablename__ = "tablecolumn"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

class Dashboard(Base):
    
    __tablename__ = "dashboard"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100))

class KPI(Base):
    
    __tablename__ = "kpi"
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(100))
    unitText: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(100))
    id_kpi: Mapped[str] = mapped_column(String(100))
    provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    calculationFrequency: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    minThreshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    maxThreshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hasCategoryLabel: Mapped[bool] = mapped_column(Boolean, default=False)
    categoryLabelDictionary: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

class Visualisation(Base):
    
    __tablename__ = "visualisation"
    id: Mapped[int] = mapped_column(primary_key=True)
    section: Mapped[str] = mapped_column(String(100))
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(100))
    chartType: Mapped[str] = mapped_column(String(100))
    i: Mapped[str] = mapped_column(String(100))
    yposition: Mapped[int] = mapped_column(Integer)
    xposition: Mapped[int] = mapped_column(Integer)
    type_spec: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "visualisation",
        "polymorphic_on": "type_spec",
    }

class StatChart(Visualisation):
        
    __tablename__ = "statchart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    unit: Mapped[str] = mapped_column(String(100))
    __mapper_args__ = {
        "polymorphic_identity": "statchart",
    }

class LineChart(Visualisation):
        
    __tablename__ = "linechart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    xtitle: Mapped[str] = mapped_column(String(100))
    ytitle: Mapped[str] = mapped_column(String(100))
    color: Mapped[str] = mapped_column(String(100))
    __mapper_args__ = {
        "polymorphic_identity": "linechart",
    }

class Map(Visualisation):
        
    __tablename__ = "map"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "map",
    }

class PieChart(Visualisation):
        
    __tablename__ = "piechart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "piechart",
    }

class Table(Visualisation):
        
    __tablename__ = "table"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "table",
    }

class BarChart(Visualisation):
        
    __tablename__ = "barchart"
    id: Mapped[int] = mapped_column(ForeignKey("visualisation.id"), primary_key=True)
    __mapper_args__ = {
        "polymorphic_identity": "barchart",
    }

class KPIValue(Base):
    
    __tablename__ = "kpivalue"
    id: Mapped[int] = mapped_column(primary_key=True)
    kpiValue: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    categoryLabel: Mapped[str] = mapped_column(String(100))

class MapData(Base):
    
    __tablename__ = "mapdata"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    type_spec: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "mapdata",
        "polymorphic_on": "type_spec",
    }

class WMS(MapData):
        
    __tablename__ = "wms"
    id: Mapped[int] = mapped_column(ForeignKey("mapdata.id"), primary_key=True)
    url: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    __mapper_args__ = {
        "polymorphic_identity": "wms",
    }

class GeoJson(MapData):
        
    __tablename__ = "geojson"
    id: Mapped[int] = mapped_column(ForeignKey("mapdata.id"), primary_key=True)
    data: Mapped[str] = mapped_column(String(100))
    __mapper_args__ = {
        "polymorphic_identity": "geojson",
    }


#--- Foreign keys and relationships of the city table
City.MapData: Mapped[List["MapData"]] = relationship("MapData", back_populates="City")
City.Dashboard: Mapped[List["Dashboard"]] = relationship("Dashboard", back_populates="City")
City.KPI: Mapped[List["KPI"]] = relationship("KPI", back_populates="City")

#--- Foreign keys and relationships of the tablecolumn table
TableColumn.table_id: Mapped["Table"] = mapped_column(ForeignKey("table.id"), nullable=False)
TableColumn.Table: Mapped["Table"] = relationship("Table", back_populates="TableColumn")

#--- Foreign keys and relationships of the dashboard table
Dashboard.consistOf: Mapped[List["Visualisation"]] = relationship("Visualisation", back_populates="consistOf")
Dashboard.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
Dashboard.City: Mapped["City"] = relationship("City", back_populates="Dashboard")

#--- Foreign keys and relationships of the kpi table
KPI.KPIValue: Mapped[List["KPIValue"]] = relationship("KPIValue", back_populates="KPI")
KPI.Visualisation: Mapped[List["Visualisation"]] = relationship("Visualisation", back_populates="KPI")
KPI.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
KPI.City: Mapped["City"] = relationship("City", back_populates="KPI")

#--- Foreign keys and relationships of the visualisation table
Visualisation.dashboard_id: Mapped["Dashboard"] = mapped_column(ForeignKey("dashboard.id"), nullable=False)
Visualisation.consistOf: Mapped["Dashboard"] = relationship("Dashboard", back_populates="consistOf")
Visualisation.kpi_id: Mapped["KPI"] = mapped_column(ForeignKey("kpi.id"), nullable=False)
Visualisation.KPI: Mapped["KPI"] = relationship("KPI", back_populates="Visualisation")

#--- Foreign keys and relationships of the map table
Map.mapdata_id: Mapped["MapData"] = mapped_column(ForeignKey("mapdata.id"), nullable=False)
Map.MapData: Mapped["MapData"] = relationship("MapData", back_populates="Map")

#--- Foreign keys and relationships of the table table
Table.TableColumn: Mapped[List["TableColumn"]] = relationship("TableColumn", back_populates="Table")

#--- Foreign keys and relationships of the kpivalue table
KPIValue.kpi_id: Mapped["KPI"] = mapped_column(ForeignKey("kpi.id"), nullable=False)
KPIValue.KPI: Mapped["KPI"] = relationship("KPI", back_populates="KPIValue")

#--- Foreign keys and relationships of the mapdata table
MapData.Map: Mapped[List["Map"]] = relationship("Map", back_populates="MapData")
MapData.city_id: Mapped["City"] = mapped_column(ForeignKey("city.id"), nullable=False)
MapData.City: Mapped["City"] = relationship("City", back_populates="MapData")