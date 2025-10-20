"""
KPI API routes with improved organization and no city-specific duplication.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas import (
    KPI, KPICreate, KPIUpdate, KPISummary,
    KPIValue, KPIValueCreate, KPIValueBulkCreate,
    KPIQueryParams, KPIValueQueryParams
)
from ..services import kpi_service, kpi_value_service

router = APIRouter(prefix="/kpis", tags=["KPIs"])


@router.get("/", response_model=List[KPI], summary="List KPIs")
def list_kpis(
    city_id: Optional[int] = Query(None, description="Filter by city ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    active_only: bool = Query(True, description="Show only active KPIs"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """
    List KPIs with optional filtering.
    
    Retrieves KPIs for a specific city with optional filters for category and provider.
    
    **City IDs:**
    - 1: Torino
    - 2: Cascais
    - 3: Differdange
    - 4: Sofia
    - 5: Athens
    - 6: Grenoble
    - 7: Maribor
    - 8: Ioannina
    
    **Parameters:**
    - `city_id` (required): The ID of the city to filter KPIs
    - `category`: Filter by KPI category (e.g., "Environment", "Energy", "Transport")
    - `provider`: Filter by data provider name
    - `active_only`: If true, only return active KPIs (default: true)
    - `limit`: Maximum number of results to return (1-1000)
    - `offset`: Number of records to skip for pagination
    
    **Returns:**
    - List of KPI objects matching the filters
    
    **Example:**
    - `/kpis?city_id=8&category=Environment&active_only=true`
    """
    if not city_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="city_id parameter is required"
        )
    
    params = KPIQueryParams(
        category=category,
        provider=provider,
        active_only=active_only,
        limit=limit,
        offset=offset
    )
    
    kpis, total = kpi_service.list_kpis_by_city(db, city_id, params)
    return kpis


@router.get("/categories", response_model=List[str], summary="Get KPI categories")
def get_kpi_categories(
    city_id: int = Query(..., description="City ID"),
    db: Session = Depends(get_db)
):
    """
    Get all available KPI categories for a city.
    
    Returns a list of unique KPI category names available for the specified city.
    
    **City IDs:**
    - 1: Torino | 2: Cascais | 3: Differdange | 4: Sofia
    - 5: Athens | 6: Grenoble | 7: Maribor | 8: Ioannina
    
    **Example:**
    - `/kpis/categories?city_id=8` - Get categories for Ioannina
    """
    return kpi_service.get_kpi_categories(db, city_id)


@router.get("/{kpi_id}", response_model=KPI, summary="Get KPI by ID")
def get_kpi(
    kpi_id: int = Path(..., description="KPI ID"),
    db: Session = Depends(get_db)
):
    """
    Get a specific KPI by its database ID.
    
    Retrieves detailed information about a KPI including its configuration,
    thresholds, and metadata.
    
    **Parameters:**
    - `kpi_id`: The numeric database ID of the KPI
    
    **Returns:**
    - Full KPI object with all properties
    
    **Example:**
    - `/kpis/123` - Get KPI with ID 123
    """
    return kpi_service.get_kpi(db, kpi_id)


@router.get("/by-kpi-id/{id_kpi}", response_model=KPI, summary="Get KPI by unique KPI ID")
def get_kpi_by_kpi_id(
    id_kpi: str = Path(..., description="Unique KPI identifier"),
    db: Session = Depends(get_db)
):
    """Get a specific KPI by its unique ID string."""
    return kpi_service.get_kpi_by_kpi_id(db, id_kpi)


@router.get("/{kpi_id}/with-latest-value", summary="Get KPI with latest value")
def get_kpi_with_latest_value(
    kpi_id: int = Path(..., description="KPI ID"),
    db: Session = Depends(get_db)
):
    """Get KPI information along with its latest value."""
    return kpi_service.get_kpi_with_latest_value(db, kpi_id)


@router.post("/", response_model=KPI, status_code=status.HTTP_201_CREATED, summary="Create KPI")
def create_kpi(
    kpi_in: KPICreate,
    db: Session = Depends(get_db)
):
    """
    Create a new KPI.
    
    Creates a new Key Performance Indicator with the specified configuration.
    
    **Required Fields:**
    - `id_kpi`: Unique string identifier (e.g., "TEMP_AVG_MONTHLY")
    - `name`: Human-readable name
    - `description`: Detailed description
    - `category`: KPI category (e.g., "Environment", "Energy")
    - `unit_text`: Unit of measurement (e.g., "°C", "kWh")
    - `city_id`: ID of the city this KPI belongs to (1-8, see list above)
    
    **Optional Fields:**
    - `provider`: Data provider name
    - `calculation_frequency`: How often calculated (e.g., "daily", "monthly")
    - `min_threshold`: Minimum threshold value
    - `max_threshold`: Maximum threshold value
    - `has_category_label`: Whether values have category labels
    - `category_label_dictionary`: A dictionary mapping category labels to their meanings (e.g., {1: "Low", 2: "Medium", 3: "High"}).
    - `is_active`: Whether the KPI is active (default: true)
    
    **Returns:**
    - The created KPI object with assigned ID
    """
    return kpi_service.create_kpi(db, kpi_in)


@router.put("/{kpi_id}", response_model=KPI, summary="Update KPI")
def update_kpi(
    kpi_id: int = Path(..., description="KPI ID"),
    kpi_in: KPIUpdate = ...,
    db: Session = Depends(get_db)
):
    """Update an existing KPI."""
    return kpi_service.update_kpi(db, kpi_id, kpi_in)


@router.delete("/{kpi_id}", response_model=KPI, summary="Delete KPI")
def delete_kpi(
    kpi_id: int = Path(..., description="KPI ID"),
    db: Session = Depends(get_db)
):
    """Delete a KPI and all its values."""
    return kpi_service.delete_kpi(db, kpi_id)


# KPI Values endpoints
@router.get("/{kpi_id}/values", response_model=List[KPIValue], summary="Get KPI values")
def get_kpi_values(
    kpi_id: int = Path(..., description="KPI ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    category_label: Optional[str] = Query(None, description="Filter by category label"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of values"),
    offset: int = Query(0, ge=0, description="Number of values to skip"),
    db: Session = Depends(get_db)
):
    """
    Get KPI values with optional time range and category filtering.
    
    Retrieves historical values for a specific KPI with optional date range
    and category label filters.
    
    **Parameters:**
    - `kpi_id`: The numeric database ID of the KPI
    - `start_date`: Start of date range (ISO 8601 format: 2024-01-01T00:00:00)
    - `end_date`: End of date range (ISO 8601 format: 2024-12-31T23:59:59)
    - `category_label`: Filter by category label (if KPI has category labels)
    - `limit`: Maximum number of values to return (1-10000)
    - `offset`: Number of values to skip for pagination
    
    **Returns:**
    - List of KPI values with timestamps and values
    
    **Examples:**
    - `/kpis/123/values` - All values for KPI 123
    - `/kpis/123/values?start_date=2024-01-01&end_date=2024-01-31` - January 2024 values
    - `/kpis/123/values?limit=100&offset=0` - First 100 values
    """
    params = KPIValueQueryParams(
        start_date=start_date,
        end_date=end_date,
        category_label=category_label,
        limit=limit,
        offset=offset
    )
    
    values, total = kpi_value_service.get_kpi_values(db, kpi_id, params)
    return values


@router.get("/{kpi_id}/values/latest", response_model=KPIValue, summary="Get latest KPI value")
def get_latest_kpi_value(
    kpi_id: int = Path(..., description="KPI ID"),
    db: Session = Depends(get_db)
):
    """Get the most recent value for a KPI."""
    value = kpi_value_service.get_latest_kpi_value(db, kpi_id)
    if not value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No values found for this KPI"
        )
    return value


@router.get("/{kpi_id}/values/aggregated", summary="Get aggregated KPI values")
def get_kpi_values_aggregated(
    kpi_id: int = Path(..., description="KPI ID"),
    period: str = Query("day", regex="^(day|week|month|year)$", description="Aggregation period"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db)
):
    """Get aggregated KPI values by time period (day, week, month, year)."""
    return kpi_value_service.get_kpi_values_aggregated(
        db, kpi_id, period, start_date, end_date
    )


@router.post("/{kpi_id}/values", response_model=KPIValue, status_code=status.HTTP_201_CREATED, summary="Add KPI value")
def create_kpi_value(
    kpi_id: int = Path(..., description="KPI ID"),
    value_in: KPIValueCreate = ...,
    db: Session = Depends(get_db)
):
    """Add a new value to a KPI."""
    # Ensure the KPI ID matches
    value_in.kpi_id = kpi_id
    return kpi_value_service.create_kpi_value(db, value_in)


@router.post("/{kpi_id}/values/bulk", status_code=status.HTTP_201_CREATED, summary="Bulk add KPI values")
def bulk_create_kpi_values(
    kpi_id: int = Path(..., description="KPI ID"),
    bulk_in: KPIValueBulkCreate = ...,
    db: Session = Depends(get_db)
):
    """
    Bulk add multiple KPI values for a KPI.
    
    This endpoint allows adding multiple time-series data points for an existing KPI 
    in a single request. Duplicate entries (same timestamp for the same KPI) will be 
    skipped to prevent integrity errors.
    
    **City IDs (for reference):**
    - 1: Torino | 2: Cascais | 3: Differdange | 4: Sofia
    - 5: Athens | 6: Grenoble | 7: Maribor | 8: Ioannina
    
    **Path Parameters:**
    - `kpi_id` (int): The database ID of the KPI to add values to
    
    **Request Body Fields:**
    - `values`: List of KPIValue objects, each containing:
      - `kpi_value` (float, required): The measured value for the KPI
      - `timestamp` (datetime, required): ISO 8601 format (e.g., "2024-01-15T10:30:00")
      - `category_label` (str, optional): Category label if KPI uses category labels
    
    **Returns:**
    - JSON object with:
      - `created` (int): Number of values successfully added
      - `message` (str): Summary message
    
    **Errors:**
    - 404: KPI not found
    - 400: Invalid data format or KPI configuration mismatch
    - 500: Internal server error
    
    **Example Request:**
    ```json
    {
      "values": [
        {"kpi_value": 25.5, "timestamp": "2024-01-01T00:00:00"},
        {"kpi_value": 26.2, "timestamp": "2024-01-02T00:00:00"}
      ]
    }
    ```
    """
    # Ensure the KPI ID matches
    bulk_in.kpi_id = kpi_id
    count = kpi_value_service.bulk_create_kpi_values(db, bulk_in)
    return {"created": count, "message": f"Successfully created {count} KPI values"}


# Legacy endpoint for backward compatibility - consolidated single endpoint instead of per-city
@router.get("/city/{city_code}/kpi/{kpi_db_id}", response_model=List[KPIValue], summary="Get KPI values by city (legacy)")
def get_kpi_values_by_city_legacy(
    city_code: str = Path(..., description="City code"),
    kpi_db_id: int = Path(..., description="KPI database ID"), 
    db: Session = Depends(get_db)
):
    """Legacy endpoint for getting KPI values by city code and KPI ID."""
    # This replaces all the individual city endpoints like /ioannina/kpi/, /maribor/kpi/, etc.
    params = KPIValueQueryParams(limit=1000, offset=0)
    values, _ = kpi_value_service.get_kpi_values(db, kpi_db_id, params)
    return values