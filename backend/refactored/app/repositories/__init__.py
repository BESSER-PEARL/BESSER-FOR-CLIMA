"""
Specific repositories for each model.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from .base import BaseRepository
from ..models import (
    City, Dashboard, DashboardSection, KPI, KPIValue, Visualization,
    LineChart, BarChart, PieChart, StatChart, Table, Map,
    TableColumn, MapData, WMS, GeoJson
)
from ..schemas import (
    CityCreate, CityUpdate, DashboardCreate, DashboardUpdate,
    DashboardSectionCreate, DashboardSectionUpdate,
    KPICreate, KPIUpdate, KPIValueCreate, VisualizationCreate, VisualizationUpdate
)


class CityRepository(BaseRepository[City, CityCreate, CityUpdate]):
    """Repository for City model."""
    
    def __init__(self):
        super().__init__(City)
    
    def get_by_code(self, db: Session, *, code: str) -> Optional[City]:
        """Get city by code."""
        return db.query(City).filter(City.code == code).first()
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[City]:
        """Get city by name (case insensitive)."""
        return db.query(City).filter(func.lower(City.name) == func.lower(name)).first()
    
    def get_with_stats(self, db: Session, *, city_id: int) -> Optional[Dict[str, Any]]:
        """Get city with dashboard and KPI counts."""
        city = self.get(db, city_id)
        if not city:
            return None
        
        dashboard_count = db.query(func.count(Dashboard.id)).filter(
            Dashboard.city_id == city_id
        ).scalar()
        
        kpi_count = db.query(func.count(KPI.id)).filter(
            and_(KPI.city_id == city_id, KPI.is_active == True)
        ).scalar()
        
        return {
            "city": city,
            "dashboard_count": dashboard_count,
            "kpi_count": kpi_count
        }


class DashboardRepository(BaseRepository[Dashboard, DashboardCreate, DashboardUpdate]):
    """Repository for Dashboard model."""
    
    def __init__(self):
        super().__init__(Dashboard)
    
    def get_by_city_and_code(self, db: Session, *, city_id: int, code: str) -> Optional[Dashboard]:
        """Get dashboard by city and code."""
        return db.query(Dashboard).filter(
            and_(Dashboard.city_id == city_id, Dashboard.code == code)
        ).first()
    
    def get_by_city_code(self, db: Session, *, city_code: str) -> Optional[Dashboard]:
        """Get dashboard by city code."""
        return db.query(Dashboard).join(City).filter(
            City.code == city_code
        ).first()
    
    def get_public_by_city(self, db: Session, *, city_id: int) -> List[Dashboard]:
        """Get all public dashboards for a city."""
        return db.query(Dashboard).filter(
            and_(Dashboard.city_id == city_id, Dashboard.is_public == True)
        ).all()
    
    def get_with_sections(self, db: Session, *, dashboard_id: int) -> Optional[Dashboard]:
        """Get dashboard with all its sections."""
        return db.query(Dashboard).options(
            joinedload(Dashboard.sections)
        ).filter(Dashboard.id == dashboard_id).first()


class SectionRepository(BaseRepository[DashboardSection, DashboardSectionCreate, DashboardSectionUpdate]):
    """Repository for DashboardSection model."""
    
    def __init__(self):
        super().__init__(DashboardSection)
    
    def get_by_dashboard(self, db: Session, *, dashboard_id: int) -> List[DashboardSection]:
        """Get all sections for a dashboard ordered by order."""
        return db.query(DashboardSection).filter(
            DashboardSection.dashboard_id == dashboard_id
        ).order_by(DashboardSection.order, DashboardSection.id).all()
    
    def get_by_dashboard_and_name(self, db: Session, *, dashboard_id: int, name: str) -> Optional[DashboardSection]:
        """Get section by dashboard and name."""
        return db.query(DashboardSection).filter(
            and_(
                DashboardSection.dashboard_id == dashboard_id,
                DashboardSection.name == name
            )
        ).first()
    
    def get_max_order(self, db: Session, *, dashboard_id: int) -> Optional[int]:
        """Get the maximum order value for sections in a dashboard."""
        return db.query(func.max(DashboardSection.order)).filter(
            DashboardSection.dashboard_id == dashboard_id
        ).scalar()
    
    def update_order(self, db: Session, *, section_id: int, order: int) -> None:
        """Update section order."""
        db.query(DashboardSection).filter(
            DashboardSection.id == section_id
        ).update({"order": order})
        db.commit()


class KPIRepository(BaseRepository[KPI, KPICreate, KPIUpdate]):
    """Repository for KPI model."""
    
    def __init__(self):
        super().__init__(KPI)
    
    def get_by_kpi_id(self, db: Session, *, id_kpi: str) -> Optional[KPI]:
        """Get KPI by its unique ID."""
        return db.query(KPI).filter(KPI.id_kpi == id_kpi).first()
    
    def get_by_city_and_category(
        self, 
        db: Session, 
        *, 
        city_id: int, 
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[KPI]:
        """Get KPIs by city and optionally category."""
        query = db.query(KPI).filter(KPI.city_id == city_id)
        
        if active_only:
            query = query.filter(KPI.is_active == True)
        
        if category:
            query = query.filter(KPI.category == category)
        
        return query.all()
    
    def get_categories_by_city(self, db: Session, *, city_id: int) -> List[str]:
        """Get all KPI categories for a city."""
        result = db.query(KPI.category).filter(
            and_(KPI.city_id == city_id, KPI.is_active == True)
        ).distinct().all()
        
        return [row[0] for row in result]
    
    def get_with_latest_value(self, db: Session, *, kpi_id: int) -> Optional[Dict[str, Any]]:
        """Get KPI with its latest value."""
        kpi = self.get(db, kpi_id)
        if not kpi:
            return None
        
        latest_value = db.query(KPIValue).filter(
            KPIValue.kpi_id == kpi_id
        ).order_by(KPIValue.timestamp.desc()).first()
        
        return {
            "kpi": kpi,
            "latest_value": latest_value
        }


class KPIValueRepository(BaseRepository[KPIValue, KPIValueCreate, None]):
    """Repository for KPIValue model."""
    
    def __init__(self):
        super().__init__(KPIValue)
    
    def get_by_kpi_and_timerange(
        self,
        db: Session,
        *,
        kpi_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category_label: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[KPIValue]:
        """Get KPI values within time range."""
        query = db.query(KPIValue).filter(KPIValue.kpi_id == kpi_id)
        
        if start_date:
            query = query.filter(KPIValue.timestamp >= start_date)
        
        if end_date:
            query = query.filter(KPIValue.timestamp <= end_date)
        
        if category_label:
            query = query.filter(KPIValue.category_label == category_label)
        
        return query.order_by(KPIValue.timestamp).offset(offset).limit(limit).all()
    
    def get_latest_by_kpi(self, db: Session, *, kpi_id: int) -> Optional[KPIValue]:
        """Get the latest value for a KPI."""
        return db.query(KPIValue).filter(
            KPIValue.kpi_id == kpi_id
        ).order_by(KPIValue.timestamp.desc()).first()
    
    def get_aggregated_by_period(
        self,
        db: Session,
        *,
        kpi_id: int,
        period: str = "day",  # day, week, month, year
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get aggregated KPI values by time period."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # PostgreSQL date_trunc function
        if period == "day":
            trunc_field = func.date_trunc('day', KPIValue.timestamp)
        elif period == "week":
            trunc_field = func.date_trunc('week', KPIValue.timestamp)
        elif period == "month":
            trunc_field = func.date_trunc('month', KPIValue.timestamp)
        elif period == "year":
            trunc_field = func.date_trunc('year', KPIValue.timestamp)
        else:
            trunc_field = func.date_trunc('day', KPIValue.timestamp)
        
        result = db.query(
            trunc_field.label('period'),
            func.avg(KPIValue.value).label('avg_value'),
            func.min(KPIValue.value).label('min_value'),
            func.max(KPIValue.value).label('max_value'),
            func.count(KPIValue.id).label('count')
        ).filter(
            and_(
                KPIValue.kpi_id == kpi_id,
                KPIValue.timestamp >= start_date,
                KPIValue.timestamp <= end_date
            )
        ).group_by(trunc_field).order_by(trunc_field).all()
        
        return [
            {
                "period": row.period,
                "avg_value": float(row.avg_value) if row.avg_value else 0,
                "min_value": float(row.min_value) if row.min_value else 0,
                "max_value": float(row.max_value) if row.max_value else 0,
                "count": row.count
            }
            for row in result
        ]
    
    def bulk_create(self, db: Session, *, values: List[KPIValueCreate]) -> int:
        """Bulk create KPI values."""
        db_objects = [KPIValue(**value.dict()) for value in values]
        db.add_all(db_objects)
        db.commit()
        return len(db_objects)


class VisualizationRepository(BaseRepository[Visualization, VisualizationCreate, VisualizationUpdate]):
    """Repository for Visualization model."""
    
    def __init__(self):
        super().__init__(Visualization)
    
    def get_by_dashboard(self, db: Session, *, dashboard_id: int) -> List[Visualization]:
        """Get all visualizations for a dashboard."""
        return db.query(Visualization).filter(
            Visualization.dashboard_id == dashboard_id
        ).all()
    
    def get_by_city_code(self, db: Session, *, city_code: str) -> List[Visualization]:
        """Get all visualizations for a city by city code."""
        return db.query(Visualization).join(Dashboard).join(City).filter(
            City.code == city_code
        ).all()
    
    def get_by_section(self, db: Session, *, section_id: int) -> List[Visualization]:
        """Get all visualizations for a section."""
        return db.query(Visualization).filter(
            Visualization.section_id == section_id
        ).all()
    
    def move_to_section(self, db: Session, *, from_section_id: int, to_section_id: int) -> None:
        """Move all visualizations from one section to another."""
        db.query(Visualization).filter(
            Visualization.section_id == from_section_id
        ).update({"section_id": to_section_id})
        db.commit()
    
    def delete_multiple(self, db: Session, *, ids: List[int]) -> int:
        """Delete multiple visualizations by IDs."""
        count = db.query(Visualization).filter(Visualization.id.in_(ids)).delete()
        db.commit()
        return count


# Specific visualization repositories
class LineChartRepository(BaseRepository[LineChart, None, None]):
    def __init__(self):
        super().__init__(LineChart)


class BarChartRepository(BaseRepository[BarChart, None, None]):
    def __init__(self):
        super().__init__(BarChart)


class PieChartRepository(BaseRepository[PieChart, None, None]):
    def __init__(self):
        super().__init__(PieChart)


class StatChartRepository(BaseRepository[StatChart, None, None]):
    def __init__(self):
        super().__init__(StatChart)


class TableRepository(BaseRepository[Table, None, None]):
    def __init__(self):
        super().__init__(Table)
    
    def get_with_columns(self, db: Session, *, table_id: int) -> Optional[Table]:
        """Get table with its columns."""
        return db.query(Table).options(
            joinedload(Table.columns)
        ).filter(Table.id == table_id).first()


class MapRepository(BaseRepository[Map, None, None]):
    def __init__(self):
        super().__init__(Map)
    
    def get_with_map_data(self, db: Session, *, map_id: int) -> Optional[Map]:
        """Get map with its data."""
        return db.query(Map).options(
            joinedload(Map.map_data)
        ).filter(Map.id == map_id).first()


class MapDataRepository(BaseRepository[MapData, None, None]):
    def __init__(self):
        super().__init__(MapData)
    
    def get_by_city(self, db: Session, *, city_id: int, active_only: bool = True) -> List[MapData]:
        """Get map data by city."""
        query = db.query(MapData).filter(MapData.city_id == city_id)
        
        if active_only:
            query = query.filter(MapData.is_active == True)
        
        return query.all()


# Repository instances (singletons)
city_repo = CityRepository()
dashboard_repo = DashboardRepository()
section_repo = SectionRepository()
kpi_repo = KPIRepository()
kpi_value_repo = KPIValueRepository()
visualization_repo = VisualizationRepository()
line_chart_repo = LineChartRepository()
bar_chart_repo = BarChartRepository()
pie_chart_repo = PieChartRepository()
stat_chart_repo = StatChartRepository()
table_repo = TableRepository()
map_repo = MapRepository()
map_data_repo = MapDataRepository()