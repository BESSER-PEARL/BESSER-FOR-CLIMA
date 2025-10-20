"""
Service layer for business logic and data operations.
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from ..repositories import (
    city_repo, dashboard_repo, section_repo, kpi_repo, kpi_value_repo, 
    visualization_repo
)
from ..schemas import (
    CityCreate, CityUpdate, City,
    DashboardCreate, DashboardUpdate, Dashboard, DashboardWithSections,
    DashboardSection, DashboardSectionCreate, DashboardSectionUpdate,
    KPICreate, KPIUpdate, KPI, KPIQueryParams,
    KPIValueCreate, KPIValue, KPIValueQueryParams, KPIValueBulkCreate,
    VisualizationCreate, VisualizationUpdate, Visualization,
    PaginatedResponse
)


class CityService:
    """Service for city operations."""
    
    def get_city(self, db: Session, city_id: int) -> City:
        """Get city by ID."""
        city = city_repo.get(db, city_id)
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        return city
    
    def get_city_by_code(self, db: Session, code: str) -> City:
        """Get city by code."""
        city = city_repo.get_by_code(db, code=code)
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"City with code '{code}' not found"
            )
        return city
    
    def list_cities(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[City], int]:
        """List cities with pagination."""
        cities = city_repo.get_multi(db, skip=skip, limit=limit)
        total = city_repo.count(db)
        return cities, total
    
    def create_city(self, db: Session, city_in: CityCreate) -> City:
        """Create new city."""
        # Check if city with same code already exists
        existing = city_repo.get_by_code(db, code=city_in.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"City with code '{city_in.code}' already exists"
            )
        
        # Check if city with same name already exists
        existing = city_repo.get_by_name(db, name=city_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"City with name '{city_in.name}' already exists"
            )
        
        return city_repo.create(db, obj_in=city_in)
    
    def update_city(self, db: Session, city_id: int, city_in: CityUpdate) -> City:
        """Update existing city."""
        city = self.get_city(db, city_id)
        return city_repo.update(db, db_obj=city, obj_in=city_in)
    
    def delete_city(self, db: Session, city_id: int) -> City:
        """Delete city."""
        city = self.get_city(db, city_id)
        return city_repo.delete(db, id=city_id)
    
    def get_city_stats(self, db: Session, city_id: int) -> Dict[str, Any]:
        """Get city statistics."""
        stats = city_repo.get_with_stats(db, city_id=city_id)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        return stats


class DashboardService:
    """Service for dashboard operations."""
    
    def get_dashboard(self, db: Session, dashboard_id: int) -> Dashboard:
        """Get dashboard by ID."""
        dashboard = dashboard_repo.get(db, dashboard_id)
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        return dashboard
    
    def get_dashboard_by_city_code(self, db: Session, city_code: str) -> Dashboard:
        """Get dashboard by city code."""
        dashboard = dashboard_repo.get_by_city_code(db, city_code=city_code)
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dashboard for city '{city_code}' not found"
            )
        return dashboard
    
    def list_dashboards_by_city(
        self, 
        db: Session, 
        city_id: int,
        skip: int = 0,
        limit: int = 100,
        public_only: bool = True
    ) -> Tuple[List[Dashboard], int]:
        """List dashboards for a city."""
        filters = {"city_id": city_id}
        if public_only:
            filters["is_public"] = True
        
        dashboards = dashboard_repo.get_multi(db, skip=skip, limit=limit, filters=filters)
        total = dashboard_repo.count(db, filters=filters)
        return dashboards, total
    
    def create_dashboard(self, db: Session, dashboard_in: DashboardCreate) -> Dashboard:
        """Create new dashboard."""
        # Verify city exists
        city = city_repo.get(db, dashboard_in.city_id)
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        
        # Check if dashboard with same code exists for this city
        existing = dashboard_repo.get_by_city_and_code(
            db, city_id=dashboard_in.city_id, code=dashboard_in.code
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dashboard with code '{dashboard_in.code}' already exists for this city"
            )
        
        return dashboard_repo.create(db, obj_in=dashboard_in)
    
    def update_dashboard(self, db: Session, dashboard_id: int, dashboard_in: DashboardUpdate) -> Dashboard:
        """Update existing dashboard."""
        dashboard = self.get_dashboard(db, dashboard_id)
        return dashboard_repo.update(db, db_obj=dashboard, obj_in=dashboard_in)
    
    def delete_dashboard(self, db: Session, dashboard_id: int) -> Dashboard:
        """Delete dashboard."""
        dashboard = self.get_dashboard(db, dashboard_id)
        return dashboard_repo.delete(db, id=dashboard_id)
    
    def get_dashboard_with_sections_and_visualizations(self, db: Session, dashboard_id: int) -> DashboardWithSections:
        """Get dashboard with all its sections and visualizations."""
        dashboard = dashboard_repo.get_with_sections(db, dashboard_id=dashboard_id)
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        return dashboard


class SectionService:
    """Service for dashboard section operations."""
    
    def get_section(self, db: Session, section_id: int) -> DashboardSection:
        """Get section by ID."""
        section = section_repo.get(db, section_id)
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found"
            )
        return section
    
    def list_sections_by_dashboard(self, db: Session, dashboard_id: int) -> List[DashboardSection]:
        """List sections for a dashboard."""
        # Verify dashboard exists
        dashboard = dashboard_repo.get(db, dashboard_id)
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        return section_repo.get_by_dashboard(db, dashboard_id=dashboard_id)
    
    def create_section(self, db: Session, section_in: DashboardSectionCreate) -> DashboardSection:
        """Create new section."""
        # Verify dashboard exists
        dashboard = dashboard_repo.get(db, section_in.dashboard_id)
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Check if section with same name exists for this dashboard
        existing = section_repo.get_by_dashboard_and_name(
            db, dashboard_id=section_in.dashboard_id, name=section_in.name
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Section with name '{section_in.name}' already exists for this dashboard"
            )
        
        # Set order to be last if not specified
        if section_in.order == 0:
            max_order = section_repo.get_max_order(db, dashboard_id=section_in.dashboard_id)
            section_in.order = (max_order or 0) + 1
        
        return section_repo.create(db, obj_in=section_in)
    
    def update_section(self, db: Session, section_id: int, section_in: DashboardSectionUpdate) -> DashboardSection:
        """Update existing section."""
        section = self.get_section(db, section_id)
        
        # Check for name conflicts if name is being changed
        if section_in.name and section_in.name != section.name:
            existing = section_repo.get_by_dashboard_and_name(
                db, dashboard_id=section.dashboard_id, name=section_in.name
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Section with name '{section_in.name}' already exists for this dashboard"
                )
        
        return section_repo.update(db, db_obj=section, obj_in=section_in)
    
    def delete_section(self, db: Session, section_id: int) -> DashboardSection:
        """Delete section and move its visualizations to the first section."""
        section = self.get_section(db, section_id)
        
        # Check if this is the only section for the dashboard
        sections = section_repo.get_by_dashboard(db, dashboard_id=section.dashboard_id)
        if len(sections) <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last section of a dashboard"
            )
        
        # Move visualizations to the first remaining section
        target_section = next((s for s in sections if s.id != section_id), None)
        if target_section:
            visualization_repo.move_to_section(db, from_section_id=section_id, to_section_id=target_section.id)
        
        return section_repo.delete(db, id=section_id)
    
    def reorder_sections(self, db: Session, dashboard_id: int, section_ids: List[int]) -> Dict[str, Any]:
        """Reorder sections by providing a list of section IDs in desired order."""
        # Verify dashboard exists
        dashboard = dashboard_repo.get(db, dashboard_id)
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Get existing sections
        existing_sections = section_repo.get_by_dashboard(db, dashboard_id=dashboard_id)
        existing_ids = {s.id for s in existing_sections}
        
        # Validate all section IDs belong to this dashboard
        if set(section_ids) != existing_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid section IDs provided"
            )
        
        # Update order for each section
        for order, section_id in enumerate(section_ids, 1):
            section_repo.update_order(db, section_id=section_id, order=order)
        
        return {"message": f"Reordered {len(section_ids)} sections"}
    
    def duplicate_section(self, db: Session, section_id: int, new_name: str) -> DashboardSection:
        """Duplicate a section with all its visualizations."""
        section = self.get_section(db, section_id)
        
        # Create new section
        section_data = DashboardSectionCreate(
            name=new_name,
            description=f"Copy of {section.name}",
            dashboard_id=section.dashboard_id
        )
        new_section = self.create_section(db, section_data)
        
        # Duplicate visualizations
        visualizations = visualization_repo.get_by_section(db, section_id=section_id)
        for vis in visualizations:
            vis_data = VisualizationCreate(
                type=vis.type,
                title=f"{vis.title} (Copy)",
                width=vis.width,
                height=vis.height,
                x_position=vis.x_position,
                y_position=vis.y_position,
                i=f"{vis.i}_copy_{new_section.id}",
                dashboard_id=vis.dashboard_id,
                section_id=new_section.id,
                kpi_id=vis.kpi_id
            )
            visualization_repo.create(db, obj_in=vis_data)
        
        return new_section


class KPIService:
    """Service for KPI operations."""
    
    def get_kpi(self, db: Session, kpi_id: int) -> KPI:
        """Get KPI by ID."""
        kpi = kpi_repo.get(db, kpi_id)
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        return kpi
    
    def get_kpi_by_kpi_id(self, db: Session, id_kpi: str) -> KPI:
        """Get KPI by its unique ID."""
        kpi = kpi_repo.get_by_kpi_id(db, id_kpi=id_kpi)
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"KPI with ID '{id_kpi}' not found"
            )
        return kpi
    
    def list_kpis_by_city(
        self, 
        db: Session, 
        city_id: int,
        params: KPIQueryParams
    ) -> Tuple[List[KPI], int]:
        """List KPIs for a city with filtering."""
        kpis = kpi_repo.get_by_city_and_category(
            db, 
            city_id=city_id, 
            category=params.category,
            active_only=params.active_only
        )
        
        # Apply additional filters
        if params.provider:
            kpis = [kpi for kpi in kpis if kpi.provider == params.provider]
        
        # Apply pagination
        total = len(kpis)
        kpis = kpis[params.offset:params.offset + params.limit]
        
        return kpis, total
    
    def get_kpi_categories(self, db: Session, city_id: int) -> List[str]:
        """Get all KPI categories for a city."""
        return kpi_repo.get_categories_by_city(db, city_id=city_id)
    
    def create_kpi(self, db: Session, kpi_in: KPICreate) -> KPI:
        """Create new KPI."""
        # Verify city exists
        city = city_repo.get(db, kpi_in.city_id)
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )
        
        # Check if KPI with same id_kpi already exists
        existing = kpi_repo.get_by_kpi_id(db, id_kpi=kpi_in.id_kpi)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"KPI with ID '{kpi_in.id_kpi}' already exists"
            )
        
        return kpi_repo.create(db, obj_in=kpi_in)
    
    def update_kpi(self, db: Session, kpi_id: int, kpi_in: KPIUpdate) -> KPI:
        """Update existing KPI."""
        kpi = self.get_kpi(db, kpi_id)
        return kpi_repo.update(db, db_obj=kpi, obj_in=kpi_in)
    
    def delete_kpi(self, db: Session, kpi_id: int) -> KPI:
        """Delete KPI."""
        kpi = self.get_kpi(db, kpi_id)
        return kpi_repo.delete(db, id=kpi_id)
    
    def get_kpi_with_latest_value(self, db: Session, kpi_id: int) -> Dict[str, Any]:
        """Get KPI with its latest value."""
        result = kpi_repo.get_with_latest_value(db, kpi_id=kpi_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        return result


class KPIValueService:
    """Service for KPI value operations."""
    
    def get_kpi_values(
        self, 
        db: Session, 
        kpi_id: int, 
        params: KPIValueQueryParams
    ) -> Tuple[List[KPIValue], int]:
        """Get KPI values with filtering."""
        # Verify KPI exists
        kpi = kpi_repo.get(db, kpi_id)
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        
        values = kpi_value_repo.get_by_kpi_and_timerange(
            db,
            kpi_id=kpi_id,
            start_date=params.start_date,
            end_date=params.end_date,
            category_label=params.category_label,
            limit=params.limit,
            offset=params.offset
        )
        
        # Count total for pagination
        total_filters = {"kpi_id": kpi_id}
        if params.category_label:
            total_filters["category_label"] = params.category_label
        total = kpi_value_repo.count(db, filters=total_filters)
        
        return values, total
    
    def get_kpi_values_aggregated(
        self,
        db: Session,
        kpi_id: int,
        period: str = "day",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get aggregated KPI values by period."""
        # Verify KPI exists
        kpi = kpi_repo.get(db, kpi_id)
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        
        if period not in ["day", "week", "month", "year"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Period must be one of: day, week, month, year"
            )
        
        return kpi_value_repo.get_aggregated_by_period(
            db,
            kpi_id=kpi_id,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
    
    def create_kpi_value(self, db: Session, value_in: KPIValueCreate) -> KPIValue:
        """Create new KPI value."""
        # Verify KPI exists
        kpi = kpi_repo.get(db, value_in.kpi_id)
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        
        return kpi_value_repo.create(db, obj_in=value_in)
    
    def bulk_create_kpi_values(self, db: Session, bulk_in: KPIValueBulkCreate) -> int:
        """Bulk create KPI values."""
        # Verify KPI exists
        kpi = kpi_repo.get(db, bulk_in.kpi_id)
        if not kpi:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="KPI not found"
            )
        
        # Add kpi_id to all values
        values_with_kpi = []
        for value in bulk_in.values:
            value_dict = value.dict()
            value_dict["kpi_id"] = bulk_in.kpi_id
            values_with_kpi.append(KPIValueCreate(**value_dict))
        
        return kpi_value_repo.bulk_create(db, values=values_with_kpi)
    
    def get_latest_kpi_value(self, db: Session, kpi_id: int) -> Optional[KPIValue]:
        """Get the latest KPI value."""
        return kpi_value_repo.get_latest_by_kpi(db, kpi_id=kpi_id)


class VisualizationService:
    """Service for visualization operations."""
    
    def get_visualization(self, db: Session, vis_id: int) -> Visualization:
        """Get visualization by ID."""
        vis = visualization_repo.get(db, vis_id)
        if not vis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visualization not found"
            )
        return vis
    
    def list_visualizations_by_dashboard(
        self, 
        db: Session, 
        dashboard_id: int
    ) -> List[Visualization]:
        """List visualizations for a dashboard."""
        # Verify dashboard exists
        dashboard = dashboard_repo.get(db, dashboard_id)
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        return visualization_repo.get_by_dashboard(db, dashboard_id=dashboard_id)
    
    def list_visualizations_by_city(
        self, 
        db: Session, 
        city_code: str
    ) -> List[Dict[str, Any]]:
        """List all visualizations for a city by code."""
        # Verify city exists
        city = city_repo.get_by_code(db, code=city_code)
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"City with code '{city_code}' not found"
            )
        
        return visualization_repo.get_by_city_code(db, city_code=city_code)
    
    def create_visualization(self, db: Session, vis_in: VisualizationCreate) -> Visualization:
        """Create new visualization."""
        # Verify dashboard exists
        dashboard = dashboard_repo.get(db, vis_in.dashboard_id)
        if not dashboard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dashboard not found"
            )
        
        # Verify KPI exists if provided
        if vis_in.kpi_id:
            kpi = kpi_repo.get(db, vis_in.kpi_id)
            if not kpi:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="KPI not found"
                )
        
        return visualization_repo.create(db, obj_in=vis_in)
    
    def update_visualization(self, db: Session, vis_id: int, vis_in: VisualizationUpdate) -> Visualization:
        """Update existing visualization."""
        vis = self.get_visualization(db, vis_id)
        
        # Verify KPI exists if provided
        if vis_in.kpi_id:
            kpi = kpi_repo.get(db, vis_in.kpi_id)
            if not kpi:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="KPI not found"
                )
        
        return visualization_repo.update(db, db_obj=vis, obj_in=vis_in)
    
    def delete_visualization(self, db: Session, vis_id: int) -> Visualization:
        """Delete visualization."""
        vis = self.get_visualization(db, vis_id)
        return visualization_repo.delete(db, id=vis_id)
    
    def delete_multiple_visualizations(self, db: Session, vis_ids: List[int]) -> int:
        """Delete multiple visualizations."""
        return visualization_repo.delete_multiple(db, ids=vis_ids)


# Service instances
city_service = CityService()
dashboard_service = DashboardService()
section_service = SectionService()
kpi_service = KPIService()
kpi_value_service = KPIValueService()
visualization_service = VisualizationService()