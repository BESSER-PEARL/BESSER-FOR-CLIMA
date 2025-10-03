"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas import TokenRequest, TokenResponse, RefreshTokenRequest
from ..services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=TokenResponse, summary="Get access token")
async def get_token(request: TokenRequest):
    """
    Get an access token using username and password.
    
    This token can be used in the Authorization header for protected endpoints.
    
    Example usage:
    1. Call this endpoint with your username and password
    2. Copy the access_token from the response  
    3. Use it in the Authorization header: 'Bearer <access_token>'
    4. In Swagger UI, click 'Authorize' and enter: 'Bearer <access_token>'
    """
    return await auth_service.get_access_token(request)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh an access token using a refresh token.
    
    Use this endpoint to get a new access token when your current one expires.
    """
    return await auth_service.refresh_access_token(request)


@router.get("/info", summary="Authentication Information")
async def auth_info():
    """
    Get authentication configuration information.
    
    Returns the Keycloak configuration details for this API.
    """
    return auth_service.get_auth_info()