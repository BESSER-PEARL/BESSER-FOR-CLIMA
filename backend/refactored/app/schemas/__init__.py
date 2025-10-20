"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union, Literal, Literal
from datetime import datetime
from enum import Enum


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True
        use_enum_values = True


# Enums
class VisualizationType(str, Enum):
    LINECHART = "linechart"
    BARCHART = "barchart" 
    PIECHART = "piechart"
    STATCHART = "statchart"
    TABLE = "table"
    MAP = "map"
    FREETEXTFIELD = "freetextfield"
    TIMELINE = "timeline"


class KPICategory(str, Enum):
    ENVIRONMENT = "Environment"
    ENERGY = "Energy"
    WASTE = "Waste"
    TRANSPORT = "Transport"
    WATER = "Water"
    PARTICIPANTS = "Participants"


# City schemas
class CityBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)


class CityCreate(CityBase):
    pass


class CityUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)


class City(CityBase):
    id: int
    created_at: datetime
    updated_at: datetime


# Dashboard schemas
class DashboardSectionBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    order: int = Field(0, ge=0)
    is_active: bool = True


class DashboardSectionCreate(DashboardSectionBase):
    dashboard_id: int = Field(..., gt=0)


class DashboardSectionUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class DashboardSection(DashboardSectionBase):
    id: int
    dashboard_id: int
    created_at: datetime
    updated_at: datetime


class DashboardBase(BaseSchema):
    code: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    is_public: bool = True


class DashboardCreate(DashboardBase):
    city_id: int = Field(..., gt=0)


class DashboardUpdate(BaseSchema):
    code: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_public: Optional[bool] = None


class Dashboard(DashboardBase):
    id: int
    city_id: int
    created_at: datetime
    updated_at: datetime
    city: City
    sections: List[DashboardSection] = []


class DashboardWithSections(Dashboard):
    """Dashboard with sections populated."""
    sections: List[DashboardSection]


class DashboardSummary(BaseSchema):
    """Lightweight dashboard info without relations."""
    id: int
    code: str
    title: str
    city_id: int
    is_public: bool


# KPI schemas
class KPIBase(BaseSchema):
    id_kpi: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=100)
    unit_text: str = Field(..., min_length=1, max_length=50)
    provider: Optional[str] = Field(None, max_length=100)
    calculation_frequency: Optional[str] = Field(None, max_length=50)
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None
    has_category_label: bool = False
    category_label_dictionary: Optional[Dict[int, str]] = None
    is_active: bool = True

    @field_validator('max_threshold')
    @classmethod
    def validate_thresholds(cls, v, info):
        if v is not None and info.data.get('min_threshold') is not None:
            if v <= info.data['min_threshold']:
                raise ValueError('max_threshold must be greater than min_threshold')
        return v


class KPICreate(KPIBase):
    city_id: int = Field(..., gt=0)


class KPIUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    unit_text: Optional[str] = Field(None, min_length=1, max_length=50)
    provider: Optional[str] = Field(None, max_length=100)
    calculation_frequency: Optional[str] = Field(None, max_length=50)
    min_threshold: Optional[float] = None
    max_threshold: Optional[float] = None
    has_category_label: Optional[bool] = None
    category_label_dictionary: Optional[Dict[int, str]] = None
    is_active: Optional[bool] = None


class KPI(KPIBase):
    id: int
    city_id: int
    created_at: datetime
    updated_at: datetime
    city: City


class KPISummary(BaseSchema):
    """Lightweight KPI info without relations."""
    id: int
    id_kpi: str
    name: str
    category: str
    unit_text: str
    city_id: int


# KPI Value schemas
class KPIValueBase(BaseSchema):
    value: float
    timestamp: datetime
    category_label: Optional[str] = Field(None, max_length=100)


class KPIValueCreate(KPIValueBase):
    kpi_id: int = Field(..., gt=0)


class KPIValueBulkCreate(BaseSchema):
    """For bulk inserting KPI values."""
    kpi_id: int = Field(..., gt=0)
    values: List[KPIValueBase] = Field(..., min_items=1, max_items=1000)


class KPIValue(KPIValueBase):
    id: int
    kpi_id: int


class KPIValueWithKPI(KPIValue):
    kpi: KPISummary


# Visualization schemas
class VisualizationBase(BaseSchema):
    type: VisualizationType
    title: str = Field(..., min_length=1, max_length=200)
    width: int = Field(4, ge=1, le=12)
    height: int = Field(8, ge=1, le=20)
    x_position: int = Field(0, ge=0)
    y_position: int = Field(0, ge=0)
    i: str = Field(..., min_length=1, max_length=100)


class VisualizationCreate(VisualizationBase):
    dashboard_id: int = Field(..., gt=0)
    section_id: Optional[int] = Field(None, gt=0)
    kpi_id: Optional[int] = Field(None, gt=0)


class VisualizationUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    width: Optional[int] = Field(None, ge=1, le=12)
    height: Optional[int] = Field(None, ge=1, le=20)
    x_position: Optional[int] = Field(None, ge=0)
    y_position: Optional[int] = Field(None, ge=0)
    section_id: Optional[int] = Field(None, gt=0)
    kpi_id: Optional[int] = Field(None, gt=0)


class Visualization(VisualizationBase):
    id: int
    dashboard_id: int
    section_id: Optional[int]
    kpi_id: Optional[int]
    created_at: datetime
    updated_at: datetime


# Specific visualization schemas
class LineChartCreate(VisualizationCreate):
    type: Literal[VisualizationType.LINECHART] = VisualizationType.LINECHART
    x_title: str = Field(..., min_length=1, max_length=100)
    y_title: str = Field(..., min_length=1, max_length=100)
    color: str = Field("#3498db", pattern=r'^#[0-9A-Fa-f]{6}$')


class LineChart(Visualization):
    x_title: str
    y_title: str
    color: str


class BarChartCreate(VisualizationCreate):
    type: Literal[VisualizationType.BARCHART] = VisualizationType.BARCHART
    orientation: str = Field("vertical", pattern=r'^(vertical|horizontal)$')


class BarChart(Visualization):
    orientation: str


class PieChartCreate(VisualizationCreate):
    type: Literal[VisualizationType.PIECHART] = VisualizationType.PIECHART
    show_legend: bool = True


class PieChart(Visualization):
    show_legend: bool


class StatChartCreate(VisualizationCreate):
    type: Literal[VisualizationType.STATCHART] = VisualizationType.STATCHART
    unit: str = Field(..., min_length=1, max_length=50)
    show_trend: bool = False


class StatChart(Visualization):
    unit: str
    show_trend: bool


class TableColumnBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    header: str = Field(..., min_length=1, max_length=100)
    data_type: str = Field("string", pattern=r'^(string|number|date|boolean)$')
    sortable: bool = True
    filterable: bool = False
    order: int = Field(0, ge=0)


class TableColumnCreate(TableColumnBase):
    pass


class TableColumn(TableColumnBase):
    id: int
    table_id: int


class TableCreate(VisualizationCreate):
    type: Literal[VisualizationType.TABLE] = VisualizationType.TABLE
    pagination_enabled: bool = True
    page_size: int = Field(10, ge=1, le=100)
    columns: List[TableColumnCreate] = Field(..., min_items=1)


class Table(Visualization):
    pagination_enabled: bool
    page_size: int
    columns: List[TableColumn]


class MapCreate(VisualizationCreate):
    type: Literal[VisualizationType.MAP] = VisualizationType.MAP
    default_zoom: int = Field(10, ge=1, le=20)
    center_lat: Optional[float] = Field(None, ge=-90, le=90)
    center_lon: Optional[float] = Field(None, ge=-180, le=180)


class Map(Visualization):
    default_zoom: int
    center_lat: Optional[float]
    center_lon: Optional[float]


class FreeTextFieldCreate(VisualizationCreate):
    type: Literal[VisualizationType.FREETEXTFIELD] = VisualizationType.FREETEXTFIELD
    text: Optional[str] = None


class FreeTextField(Visualization):
    text: Optional[str]


# Timeline schemas
class TimelineEventBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    phase: str = Field(..., min_length=1, max_length=50)
    start_date: datetime
    end_date: Optional[datetime] = None
    is_ongoing: bool = False
    status: str = Field("active", pattern=r'^(active|completed|failed)$')
    kpi_references: Optional[str] = None  # JSON array of KPI IDs
    failure_reason: Optional[str] = None
    color: str = Field("#0177a9", pattern=r'^#[0-9A-Fa-f]{6}$')


class TimelineEventCreate(TimelineEventBase):
    pass


class TimelineEvent(TimelineEventBase):
    id: int
    timeline_id: int
    created_at: datetime
    updated_at: datetime


class TimelineCreate(VisualizationCreate):
    type: Literal[VisualizationType.TIMELINE] = VisualizationType.TIMELINE
    description: Optional[str] = None
    events: List[TimelineEventCreate] = Field(default_factory=list)


class Timeline(Visualization):
    description: Optional[str]
    events: List[TimelineEvent]


# Map Data schemas
class MapDataBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    is_active: bool = True


class WMSCreate(MapDataBase):
    url: str = Field(..., min_length=1, max_length=500)
    layer_name: str = Field(..., min_length=1, max_length=200)
    format: str = Field("image/png", max_length=50)
    transparent: bool = True
    city_id: int = Field(..., gt=0)
    map_id: Optional[int] = Field(None, gt=0)


class WMS(MapDataBase):
    id: int
    type: str
    url: str
    layer_name: str
    format: str
    transparent: bool
    city_id: int
    map_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class GeoJsonCreate(MapDataBase):
    data: Dict[str, Any]
    style: Optional[Dict[str, Any]] = None
    city_id: int = Field(..., gt=0)
    map_id: Optional[int] = Field(None, gt=0)


class GeoJson(MapDataBase):
    id: int
    type: str
    data: Dict[str, Any]
    style: Optional[Dict[str, Any]]
    city_id: int
    map_id: Optional[int]
    created_at: datetime
    updated_at: datetime


# Authentication schemas
class TokenRequest(BaseSchema):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class RefreshTokenRequest(BaseSchema):
    refresh_token: str = Field(..., min_length=1)


# Query parameter schemas
class KPIQueryParams(BaseSchema):
    """Query parameters for KPI filtering."""
    category: Optional[str] = None
    provider: Optional[str] = None
    active_only: bool = True
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class KPIValueQueryParams(BaseSchema):
    """Query parameters for KPI value filtering."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category_label: Optional[str] = None
    limit: int = Field(1000, ge=1, le=10000)
    offset: int = Field(0, ge=0)
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, info):
        if v is not None and info.data.get('start_date') is not None:
            if v <= info.data['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


# Response wrapper schemas
class PaginatedResponse(BaseSchema):
    """Generic paginated response."""
    items: List[Any]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_previous: bool


class ErrorResponse(BaseSchema):
    """Error response schema."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None


# Union type for all visualization creation schemas
AnyVisualizationCreate = Union[
    LineChartCreate,
    BarChartCreate,
    PieChartCreate,
    StatChartCreate,
    TableCreate,
    MapCreate,
    FreeTextFieldCreate,
    TimelineCreate,
    VisualizationCreate  # Fallback for generic visualizations
]

# Union type for all visualization response schemas
AnyVisualization = Union[
    LineChart,
    BarChart,
    PieChart,
    StatChart,
    Table,
    Map,
    FreeTextField,
    Timeline,
    Visualization  # Fallback for generic visualizations
]