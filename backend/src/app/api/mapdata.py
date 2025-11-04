"""
Map Data API routes with Keycloak authentication.
Handles WMS layers and GeoJSON data for city maps.
"""
from typing import List, Union
from fastapi import APIRouter, Depends, Query, HTTPException, status, Path, Body
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import KeycloakBearer
from ..schemas import WMS, WMSCreate, GeoJson, GeoJsonCreate
from ..services import map_data_service

router = APIRouter(
    prefix="/mapdata", 
    tags=["Map Data"],
    dependencies=[Depends(KeycloakBearer())]
)


@router.get("/city/{city_id}", response_model=List[Union[WMS, GeoJson]], summary="Get map data for city")
def get_city_map_data(
    city_id: int = Path(..., description="City ID"),
    active_only: bool = Query(True, description="Return only active layers"),
    db: Session = Depends(get_db)
):
    """
    Get all map layers (WMS and GeoJSON) for a specific city.
    
    **City IDs:**
    - 1: Torino | 2: Cascais | 3: Differdange | 4: Sofia
    - 5: Athens | 6: Grenoble | 7: Maribor | 8: Ioannina
    
    **Parameters:**
    - `city_id`: The ID of the city
    - `active_only`: If true, only return active/visible layers
    
    **Returns:**
    - List of map layers (mix of WMS and GeoJSON)
    
    **Example:**
    - `/mapdata/city/8?active_only=true` - Get active layers for Ioannina
    """
    return map_data_service.get_map_data_by_city(db, city_id, active_only)


@router.get("/city/code/{city_code}", response_model=List[Union[WMS, GeoJson]], summary="Get map data by city code")
def get_city_map_data_by_code(
    city_code: str = Path(..., description="City code (e.g., 'ioannina', 'cascais')"),
    active_only: bool = Query(True, description="Return only active layers"),
    db: Session = Depends(get_db)
):
    """
    Get all map layers for a city by its code.
    
    **City Codes:**
    - torino, cascais, differdange, sofia, athens, grenoble, maribor, ioannina
    
    **Example:**
    - `/mapdata/city/code/ioannina` - Get map layers for Ioannina
    """
    return map_data_service.get_map_data_by_city_code(db, city_code, active_only)


@router.get("/{map_data_id}", response_model=Union[WMS, GeoJson], summary="Get map data by ID")
def get_map_data(
    map_data_id: int = Path(..., description="Map data ID"),
    db: Session = Depends(get_db)
):
    """Get a specific map layer by ID."""
    return map_data_service.get_map_data(db, map_data_id)


@router.post("/wms", response_model=WMS, status_code=status.HTTP_201_CREATED, summary="Create WMS layer")
def create_wms_layer(
    wms_in: WMSCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new WMS (Web Map Service) layer.
    
    **WMS layers** display map tiles from external services (e.g., GeoServer, MapServer).
    
    **Request Body:**
    ```json
    {
      "title": "Building Footprints",
      "description": "All building polygons in the city",
      "url": "https://geoserver.example.com/wms",
      "layer_name": "buildings",
      "format": "image/png",
      "transparent": true,
      "city_id": 8,
      "is_active": true
    }
    ```
    
    **Required Fields:**
    - `title`: Display name for the layer
    - `url`: WMS service endpoint URL
    - `layer_name`: Name of the layer on the WMS server
    - `city_id`: ID of the city (1-8)
    
    **Optional Fields:**
    - `description`: Layer description
    - `format`: Image format (default: "image/png")
    - `transparent`: Whether to request transparent images (default: true)
    - `is_active`: Whether layer is active (default: true)
    """
    return map_data_service.create_wms_layer(db, wms_in)


@router.post("/geojson", response_model=GeoJson, status_code=status.HTTP_201_CREATED, summary="Create GeoJSON layer")
def create_geojson_layer(
    geojson_in: GeoJsonCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new GeoJSON layer.
    
    **GeoJSON layers** store vector data (points, lines, polygons) directly in the database.
    
    **Request Body:**
    ```json
    {
      "title": "Bike Stations",
      "description": "Public bicycle sharing stations",
      "data": {
        "type": "FeatureCollection",
        "features": [
          {
            "type": "Feature",
            "geometry": {
              "type": "Point",
              "coordinates": [20.8509, 39.6679]
            },
            "properties": {
              "name": "Central Station",
              "capacity": 20
            }
          }
        ]
      },
      "style": {
        "color": "#FF0000",
        "weight": 2,
        "opacity": 1
      },
      "city_id": 8,
      "is_active": true
    }
    ```
    
    **Required Fields:**
    - `title`: Display name for the layer
    - `data`: Valid GeoJSON object (FeatureCollection, Feature, or Geometry)
    - `city_id`: ID of the city (1-8)
    
    **Optional Fields:**
    - `description`: Layer description
    - `is_active`: Whether layer is active (default: true)
    """
    return map_data_service.create_geojson_layer(db, geojson_in)


@router.put("/wms/{map_data_id}", response_model=WMS, summary="Update WMS layer")
def update_wms_layer(
    map_data_id: int = Path(..., description="Map data ID"),
    wms_in: WMSCreate = Body(...),
    db: Session = Depends(get_db)
):
    """Update an existing WMS layer."""
    return map_data_service.update_wms_layer(db, map_data_id, wms_in)


@router.put("/geojson/{map_data_id}", response_model=GeoJson, summary="Update GeoJSON layer")
def update_geojson_layer(
    map_data_id: int = Path(..., description="Map data ID"),
    geojson_in: GeoJsonCreate = Body(...),
    db: Session = Depends(get_db)
):
    """Update an existing GeoJSON layer."""
    return map_data_service.update_geojson_layer(db, map_data_id, geojson_in)


@router.delete("/{map_data_id}", summary="Delete map data")
def delete_map_data(
    map_data_id: int = Path(..., description="Map data ID"),
    db: Session = Depends(get_db)
):
    """
    Delete a map layer (WMS or GeoJSON).
    
    **Returns:**
    - Success message with deleted layer info
    """
    return map_data_service.delete_map_data(db, map_data_id)


@router.post("/geojson/upload-file", response_model=GeoJson, status_code=status.HTTP_201_CREATED, summary="Upload GeoJSON file")
def upload_geojson_file(
    title: str = Body(..., embed=True),
    city_id: int = Body(..., embed=True),
    geojson_data: dict = Body(..., embed=True),
    description: str = Body(None, embed=True),
    style: dict = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """
    Upload a GeoJSON file as a new layer.
    
    **This endpoint accepts the entire GeoJSON file content.**
    
    **Request Body:**
    ```json
    {
      "title": "City Parks",
      "city_id": 8,
      "description": "All public parks",
      "geojson_data": {
        "type": "FeatureCollection",
        "features": [...]
      },
      "style": {
        "color": "#00FF00",
        "fillOpacity": 0.5
      }
    }
    ```
    """
    geojson_in = GeoJsonCreate(
        title=title,
        description=description,
        data=geojson_data,
        style=style,
        city_id=city_id
    )
    return map_data_service.create_geojson_layer(db, geojson_in)


# Legacy endpoint for backward compatibility
@router.get("/{city_code}/mapdata/", response_model=List[Union[WMS, GeoJson]], summary="Get map data (legacy)")
def get_map_data_legacy(
    city_code: str = Path(..., description="City code"),
    db: Session = Depends(get_db)
):
    """
    **Legacy endpoint** for backward compatibility with old frontend code.
    
    Maps to the new endpoint: `/mapdata/city/code/{city_code}`
    """
    return map_data_service.get_map_data_by_city_code(db, city_code.lower(), active_only=True)
