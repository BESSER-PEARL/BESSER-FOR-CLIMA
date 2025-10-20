"""
Authentication service for handling Keycloak integration.
"""
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from ..core.config import settings
from ..schemas import TokenRequest, TokenResponse, RefreshTokenRequest


class AuthenticationService:
    """Service for handling authentication with Keycloak."""
    
    def __init__(self):
        self.token_url = f"{settings.KEYCLOAK_AUTH_URL}/protocol/openid-connect/token"
        self.userinfo_url = f"{settings.KEYCLOAK_AUTH_URL}/protocol/openid-connect/userinfo"
    
    async def get_access_token(self, request: TokenRequest) -> TokenResponse:
        """
        Get access token using username and password.
        """
        try:
            data = {
                'grant_type': 'password',
                'client_id': settings.KEYCLOAK_CLIENT_ID,
                'username': request.username,
                'password': request.password,
                'scope': 'openid'
            }
            
            response = requests.post(self.token_url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                return TokenResponse(
                    access_token=token_data["access_token"],
                    token_type="bearer",
                    expires_in=token_data["expires_in"],
                    refresh_token=token_data.get("refresh_token")
                )
            else:
                error_detail = "Invalid credentials"
                try:
                    error_data = response.json()
                    error_detail = error_data.get("error_description", error_detail)
                except:
                    pass
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error_detail
                )
                
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed"
            )
    
    async def refresh_access_token(self, request: RefreshTokenRequest) -> TokenResponse:
        """
        Refresh access token using refresh token.
        """
        try:
            data = {
                'grant_type': 'refresh_token',
                'client_id': settings.KEYCLOAK_CLIENT_ID,
                'refresh_token': request.refresh_token,
            }
            
            response = requests.post(self.token_url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                return TokenResponse(
                    access_token=token_data["access_token"],
                    token_type="bearer",
                    expires_in=token_data["expires_in"],
                    refresh_token=token_data.get("refresh_token")
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
                
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed"
            )
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information using access token.
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(self.userinfo_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token"
                )
                
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user info"
            )
    
    def get_auth_info(self) -> Dict[str, Any]:
        """
        Get authentication configuration information.
        """
        return {
            "server_url": settings.KEYCLOAK_SERVER_URL,
            "realm": settings.KEYCLOAK_REALM,
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "auth_url": settings.KEYCLOAK_AUTH_URL,
            "token_endpoint": self.token_url,
            "userinfo_endpoint": self.userinfo_url
        }


# Service instance
auth_service = AuthenticationService()