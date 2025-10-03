"""
Improved database models with proper relationships and constraints.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from ..core.database import Base


class TimestampMixin:
    """Mixin for adding created/updated timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )


class City(Base, TimestampMixin):
    """City model with improved constraints."""
    __tablename__ = "cities"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(100))
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationships
    dashboards: Mapped[List["Dashboard"]] = relationship(
        "Dashboard", back_populates="city", cascade="all, delete-orphan"
    )
    kpis: Mapped[List["KPI"]] = relationship(
        "KPI", back_populates="city", cascade="all, delete-orphan"
    )
    map_data: Mapped[List["MapData"]] = relationship(
        "MapData", back_populates="city", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<City(id={self.id}, name='{self.name}', code='{self.code}')>"


class Dashboard(Base, TimestampMixin):
    """Dashboard model with better organization."""
    __tablename__ = "dashboards"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False, index=True)
    
    # Relationships
    city: Mapped["City"] = relationship("City", back_populates="dashboards")
    sections: Mapped[List["DashboardSection"]] = relationship(
        "DashboardSection", back_populates="dashboard", cascade="all, delete-orphan",
        order_by="DashboardSection.order"
    )
    visualizations: Mapped[List["Visualization"]] = relationship(
        "Visualization", back_populates="dashboard", cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("code", "city_id", name="unique_dashboard_code_per_city"),
        Index("idx_dashboard_city_code", "city_id", "code"),
    )


class DashboardSection(Base, TimestampMixin):
    """Dashboard section model for organizing visualizations."""
    __tablename__ = "dashboard_sections"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    dashboard_id: Mapped[int] = mapped_column(ForeignKey("dashboards.id"), nullable=False, index=True)
    
    # Relationships
    dashboard: Mapped["Dashboard"] = relationship("Dashboard", back_populates="sections")
    visualizations: Mapped[List["Visualization"]] = relationship(
        "Visualization", back_populates="section", cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("name", "dashboard_id", name="unique_section_name_per_dashboard"),
        Index("idx_section_dashboard_order", "dashboard_id", "order"),
    )


class KPI(Base, TimestampMixin):
    """Improved KPI model with better categorization."""
    __tablename__ = "kpis"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_kpi: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    unit_text: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(100))
    calculation_frequency: Mapped[Optional[str]] = mapped_column(String(50))
    min_threshold: Mapped[Optional[float]] = mapped_column(Float)
    max_threshold: Mapped[Optional[float]] = mapped_column(Float)
    has_category_label: Mapped[bool] = mapped_column(Boolean, default=False)
    category_label_dictionary: Mapped[Optional[Dict[int, str]]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False, index=True)
    
    # Relationships
    city: Mapped["City"] = relationship("City", back_populates="kpis")
    values: Mapped[List["KPIValue"]] = relationship(
        "KPIValue", back_populates="kpi", cascade="all, delete-orphan"
    )
    visualizations: Mapped[List["Visualization"]] = relationship(
        "Visualization", back_populates="kpi"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_kpi_city_category", "city_id", "category"),
        Index("idx_kpi_active", "is_active"),
    )


class KPIValue(Base):
    """KPI values with proper indexing for time series data."""
    __tablename__ = "kpi_values"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    category_label: Mapped[Optional[str]] = mapped_column(String(100))
    kpi_id: Mapped[int] = mapped_column(ForeignKey("kpis.id"), nullable=False, index=True)
    
    # Relationship
    kpi: Mapped["KPI"] = relationship("KPI", back_populates="values")
    
    # Composite indexes for efficient time series queries
    __table_args__ = (
        Index("idx_kpivalue_kpi_timestamp", "kpi_id", "timestamp"),
        Index("idx_kpivalue_timestamp_desc", "timestamp", postgresql_using="btree"),
    )


class Visualization(Base, TimestampMixin):
    """Base visualization model using table per class inheritance."""
    __tablename__ = "visualizations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    width: Mapped[int] = mapped_column(Integer, default=4)
    height: Mapped[int] = mapped_column(Integer, default=8)
    x_position: Mapped[int] = mapped_column(Integer, default=0)
    y_position: Mapped[int] = mapped_column(Integer, default=0)
    i: Mapped[str] = mapped_column(String(100), nullable=False)  # Grid layout ID
    dashboard_id: Mapped[int] = mapped_column(ForeignKey("dashboards.id"), nullable=False, index=True)
    section_id: Mapped[Optional[int]] = mapped_column(ForeignKey("dashboard_sections.id"), index=True)
    kpi_id: Mapped[Optional[int]] = mapped_column(ForeignKey("kpis.id"), index=True)
    
    # Relationships
    dashboard: Mapped["Dashboard"] = relationship("Dashboard", back_populates="visualizations")
    section: Mapped[Optional["DashboardSection"]] = relationship("DashboardSection", back_populates="visualizations")
    kpi: Mapped[Optional["KPI"]] = relationship("KPI", back_populates="visualizations")
    
    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "visualization",
        "polymorphic_on": "type",
    }
    
    __table_args__ = (
        Index("idx_visualization_dashboard", "dashboard_id"),
        Index("idx_visualization_section", "section_id"),
        Index("idx_visualization_type", "type"),
    )


class LineChart(Visualization):
    """Line chart visualization."""
    __tablename__ = "line_charts"
    
    id: Mapped[int] = mapped_column(ForeignKey("visualizations.id"), primary_key=True)
    x_title: Mapped[str] = mapped_column(String(100), nullable=False)
    y_title: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(50), default="#3498db")
    
    __mapper_args__ = {"polymorphic_identity": "linechart"}


class BarChart(Visualization):
    """Bar chart visualization."""
    __tablename__ = "bar_charts"
    
    id: Mapped[int] = mapped_column(ForeignKey("visualizations.id"), primary_key=True)
    orientation: Mapped[str] = mapped_column(String(20), default="vertical")
    
    __mapper_args__ = {"polymorphic_identity": "barchart"}


class PieChart(Visualization):
    """Pie chart visualization."""
    __tablename__ = "pie_charts"
    
    id: Mapped[int] = mapped_column(ForeignKey("visualizations.id"), primary_key=True)
    show_legend: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __mapper_args__ = {"polymorphic_identity": "piechart"}


class StatChart(Visualization):
    """Stat/metric chart visualization."""
    __tablename__ = "stat_charts"
    
    id: Mapped[int] = mapped_column(ForeignKey("visualizations.id"), primary_key=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    show_trend: Mapped[bool] = mapped_column(Boolean, default=False)
    
    __mapper_args__ = {"polymorphic_identity": "statchart"}


class Table(Visualization):
    """Table visualization."""
    __tablename__ = "tables"
    
    id: Mapped[int] = mapped_column(ForeignKey("visualizations.id"), primary_key=True)
    pagination_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    page_size: Mapped[int] = mapped_column(Integer, default=10)
    
    # Relationship
    columns: Mapped[List["TableColumn"]] = relationship(
        "TableColumn", back_populates="table", cascade="all, delete-orphan"
    )
    
    __mapper_args__ = {"polymorphic_identity": "table"}


class Map(Visualization):
    """Map visualization."""
    __tablename__ = "maps"
    
    id: Mapped[int] = mapped_column(ForeignKey("visualizations.id"), primary_key=True)
    default_zoom: Mapped[int] = mapped_column(Integer, default=10)
    center_lat: Mapped[Optional[float]] = mapped_column(Float)
    center_lon: Mapped[Optional[float]] = mapped_column(Float)
    
    # Relationship
    map_data: Mapped[List["MapData"]] = relationship("MapData", back_populates="map")
    
    __mapper_args__ = {"polymorphic_identity": "map"}


class TableColumn(Base):
    """Table column configuration."""
    __tablename__ = "table_columns"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    header: Mapped[str] = mapped_column(String(100), nullable=False)
    data_type: Mapped[str] = mapped_column(String(50), default="string")
    sortable: Mapped[bool] = mapped_column(Boolean, default=True)
    filterable: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"), nullable=False, index=True)
    
    # Relationship
    table: Mapped["Table"] = relationship("Table", back_populates="columns")


class MapData(Base, TimestampMixin):
    """Base map data model."""
    __tablename__ = "map_data"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False, index=True)
    map_id: Mapped[Optional[int]] = mapped_column(ForeignKey("maps.id"), index=True)
    
    # Relationships
    city: Mapped["City"] = relationship("City", back_populates="map_data")
    map: Mapped[Optional["Map"]] = relationship("Map", back_populates="map_data")
    
    # Polymorphic configuration
    __mapper_args__ = {
        "polymorphic_identity": "mapdata",
        "polymorphic_on": "type",
    }


class WMS(MapData):
    """WMS layer data."""
    __tablename__ = "wms_layers"
    
    id: Mapped[int] = mapped_column(ForeignKey("map_data.id"), primary_key=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    layer_name: Mapped[str] = mapped_column(String(200), nullable=False)
    format: Mapped[str] = mapped_column(String(50), default="image/png")
    transparent: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __mapper_args__ = {"polymorphic_identity": "wms"}


class GeoJson(MapData):
    """GeoJSON data."""
    __tablename__ = "geojson_data"
    
    id: Mapped[int] = mapped_column(ForeignKey("map_data.id"), primary_key=True)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    style: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    __mapper_args__ = {"polymorphic_identity": "geojson"}