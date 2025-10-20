"""
Dashboard and Visualization API routes - consolidated and improved.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas import (
    Dashboard, DashboardCreate, DashboardUpdate, DashboardWithSections,
    DashboardSection, DashboardSectionCreate, DashboardSectionUpdate,
    Visualization, VisualizationCreate, VisualizationUpdate,
    LineChart, BarChart, PieChart, StatChart, Table, Map,
    AnyVisualizationCreate, AnyVisualization
)
from ..services import dashboard_service, visualization_service, section_service

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.get("/", response_model=List[Dashboard], summary="List dashboards")
def list_dashboards(
    city_id: Optional[int] = Query(None, description="Filter by city ID"),
    public_only: bool = Query(True, description="Show only public dashboards"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """List dashboards with optional filtering."""
    if city_id:
        dashboards, total = dashboard_service.list_dashboards_by_city(
            db, city_id, skip, limit, public_only
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="city_id parameter is required"
        )
    return dashboards


@router.get("/{dashboard_id}", response_model=Dashboard, summary="Get dashboard by ID")
def get_dashboard(
    dashboard_id: int = Path(..., description="Dashboard ID"),
    db: Session = Depends(get_db)
):
    """Get a specific dashboard by ID."""
    return dashboard_service.get_dashboard(db, dashboard_id)


@router.get("/city/{city_code}", response_model=Dashboard, summary="Get dashboard by city code")
def get_dashboard_by_city_code(
    city_code: str = Path(..., description="City code"),
    db: Session = Depends(get_db)
):
    """Get dashboard for a specific city by city code."""
    return dashboard_service.get_dashboard_by_city_code(db, city_code)


@router.get("/{dashboard_id}/with-visualizations", response_model=DashboardWithSections, summary="Get dashboard with visualizations")
def get_dashboard_with_visualizations(
    dashboard_id: int = Path(..., description="Dashboard ID"),
    db: Session = Depends(get_db)
):
    """Get dashboard with all its sections and visualizations."""
    return dashboard_service.get_dashboard_with_sections_and_visualizations(db, dashboard_id)


# Dashboard Section routes
@router.get("/{dashboard_id}/sections", response_model=List[DashboardSection], summary="Get dashboard sections")
def get_dashboard_sections(
    dashboard_id: int = Path(..., description="Dashboard ID"),
    db: Session = Depends(get_db)
):
    """Get all sections for a dashboard."""
    return section_service.list_sections_by_dashboard(db, dashboard_id)


@router.post("/{dashboard_id}/sections", response_model=DashboardSection, status_code=status.HTTP_201_CREATED, summary="Create section")
def create_section(
    dashboard_id: int = Path(..., description="Dashboard ID"),
    section_in: DashboardSectionCreate = ...,
    db: Session = Depends(get_db)
):
    """Create a new section for a dashboard."""
    # Override dashboard_id from path parameter
    section_data = section_in.dict()
    section_data['dashboard_id'] = dashboard_id
    section_in = DashboardSectionCreate(**section_data)
    return section_service.create_section(db, section_in)


@router.put("/sections/{section_id}", response_model=DashboardSection, summary="Update section")
def update_section(
    section_id: int = Path(..., description="Section ID"),
    section_in: DashboardSectionUpdate = ...,
    db: Session = Depends(get_db)
):
    """Update an existing section."""
    return section_service.update_section(db, section_id, section_in)


@router.delete("/sections/{section_id}", response_model=DashboardSection, summary="Delete section")
def delete_section(
    section_id: int = Path(..., description="Section ID"),
    db: Session = Depends(get_db)
):
    """Delete a section and move its visualizations to the first section."""
    return section_service.delete_section(db, section_id)


@router.put("/{dashboard_id}/sections/reorder", summary="Reorder sections")
def reorder_sections(
    dashboard_id: int = Path(..., description="Dashboard ID"),
    section_ids: List[int] = ...,
    db: Session = Depends(get_db)
):
    """Reorder sections by providing a list of section IDs in desired order."""
    return section_service.reorder_sections(db, dashboard_id, section_ids)


@router.post("/sections/{section_id}/duplicate", response_model=DashboardSection, summary="Duplicate section")
def duplicate_section(
    section_id: int = Path(..., description="Section ID"),
    new_name: str = ...,
    db: Session = Depends(get_db)
):
    """Duplicate a section with all its visualizations."""
    return section_service.duplicate_section(db, section_id, new_name)


@router.post("/", response_model=Dashboard, status_code=status.HTTP_201_CREATED, summary="Create dashboard")
def create_dashboard(
    dashboard_in: DashboardCreate,
    db: Session = Depends(get_db)
):
    """Create a new dashboard."""
    return dashboard_service.create_dashboard(db, dashboard_in)


@router.put("/{dashboard_id}", response_model=Dashboard, summary="Update dashboard")
def update_dashboard(
    dashboard_id: int = Path(..., description="Dashboard ID"),
    dashboard_in: DashboardUpdate = ...,
    db: Session = Depends(get_db)
):
    """Update an existing dashboard."""
    return dashboard_service.update_dashboard(db, dashboard_id, dashboard_in)


@router.delete("/{dashboard_id}", response_model=Dashboard, summary="Delete dashboard")
def delete_dashboard(
    dashboard_id: int = Path(..., description="Dashboard ID"),
    db: Session = Depends(get_db)
):
    """Delete a dashboard and all its visualizations."""
    return dashboard_service.delete_dashboard(db, dashboard_id)


# Visualization routes
@router.get("/{dashboard_id}/visualizations", response_model=List[AnyVisualization], summary="Get dashboard visualizations")
def get_dashboard_visualizations(
    dashboard_id: int = Path(..., description="Dashboard ID"),
    db: Session = Depends(get_db)
):
    """Get all visualizations for a dashboard."""
    return visualization_service.list_visualizations_by_dashboard(db, dashboard_id)


@router.post("/{dashboard_id}/visualizations", response_model=AnyVisualization, status_code=status.HTTP_201_CREATED, summary="Create visualization")
def create_visualization(
    dashboard_id: int = Path(..., description="Dashboard ID"),
    vis_in: AnyVisualizationCreate = ...,
    db: Session = Depends(get_db)
):
    """Create a new visualization for a dashboard."""
    # Ensure dashboard ID matches
    vis_in.dashboard_id = dashboard_id
    return visualization_service.create_visualization(db, vis_in)


# Visualization management routes
visualization_router = APIRouter(prefix="/visualizations", tags=["Visualizations"])


# Bulk operations must come before path parameters to avoid route conflicts
@visualization_router.delete("/bulk", summary="Delete multiple visualizations")
def delete_multiple_visualizations(
    ids: List[int] = Query(..., description="List of visualization IDs to delete"),
    db: Session = Depends(get_db)
):
    """Delete multiple visualizations by their IDs."""
    count = visualization_service.delete_multiple_visualizations(db, ids)
    return {"deleted": count, "message": f"Successfully deleted {count} visualizations"}


@visualization_router.get("/{vis_id}", response_model=AnyVisualization, summary="Get visualization")
def get_visualization(
    vis_id: int = Path(..., description="Visualization ID"),
    db: Session = Depends(get_db)
):
    """Get a specific visualization by ID."""
    return visualization_service.get_visualization(db, vis_id)


@visualization_router.put("/{vis_id}", response_model=AnyVisualization, summary="Update visualization")
def update_visualization(
    vis_id: int = Path(..., description="Visualization ID"),
    vis_in: VisualizationUpdate = ...,
    db: Session = Depends(get_db)
):
    """Update an existing visualization."""
    return visualization_service.update_visualization(db, vis_id, vis_in)


@visualization_router.delete("/{vis_id}", response_model=AnyVisualization, summary="Delete visualization")
def delete_visualization(
    vis_id: int = Path(..., description="Visualization ID"),
    db: Session = Depends(get_db)
):
    """Delete a visualization."""
    return visualization_service.delete_visualization(db, vis_id)


# Legacy endpoint for city-based visualization listing (consolidated)
@visualization_router.get("/city/{city_code}", summary="Get visualizations by city code (legacy)")
def get_visualizations_by_city(
    city_code: str = Path(..., description="City code"),
    db: Session = Depends(get_db)
):
    """Legacy endpoint for getting all visualizations for a city by code."""
    # This replaces individual city endpoints like /ioannina/visualizations, /maribor/visualizations, etc.
    return visualization_service.list_visualizations_by_city(db, city_code)


# Include the visualization router
router.include_router(visualization_router)