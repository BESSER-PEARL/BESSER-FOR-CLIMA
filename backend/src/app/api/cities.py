"""
City API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas import (
    City, CityCreate, CityUpdate, 
    PaginatedResponse, ErrorResponse
)
from ..services import city_service

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("/", response_model=List[City], summary="List cities")
def list_cities(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """List all cities with pagination."""
    cities, total = city_service.list_cities(db, skip=skip, limit=limit)
    return cities


@router.get("/{city_id}", response_model=City, summary="Get city by ID")
def get_city(
    city_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific city by ID."""
    return city_service.get_city(db, city_id)


@router.get("/code/{city_code}", response_model=City, summary="Get city by code")
def get_city_by_code(
    city_code: str,
    db: Session = Depends(get_db)
):
    """Get a specific city by its code."""
    return city_service.get_city_by_code(db, city_code)


@router.get("/{city_id}/stats", summary="Get city statistics")
def get_city_stats(
    city_id: int,
    db: Session = Depends(get_db)
):
    """Get statistics for a specific city (dashboard count, KPI count, etc.)."""
    return city_service.get_city_stats(db, city_id)


@router.post("/", response_model=City, status_code=status.HTTP_201_CREATED, summary="Create city")
def create_city(
    city_in: CityCreate,
    db: Session = Depends(get_db)
):
    """Create a new city."""
    return city_service.create_city(db, city_in)


@router.put("/{city_id}", response_model=City, summary="Update city")
def update_city(
    city_id: int,
    city_in: CityUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing city."""
    return city_service.update_city(db, city_id, city_in)


@router.delete("/{city_id}", response_model=City, summary="Delete city")
def delete_city(
    city_id: int,
    db: Session = Depends(get_db)
):
    """Delete a city and all its related data."""
    return city_service.delete_city(db, city_id)