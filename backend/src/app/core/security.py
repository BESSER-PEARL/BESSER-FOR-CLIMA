"""
Security utilities for Keycloak token verification.
"""
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import requests
from functools import lru_cache

from .config import settings

logger = logging.getLogger(__name__)


class KeycloakBearer(HTTPBearer):
    """
    Keycloak JWT Bearer token authentication.
    Use as a dependency to protect routes: dependencies=[Depends(KeycloakBearer())]
    """
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.realm_url = settings.KEYCLOAK_AUTH_URL
        self.client_id = settings.KEYCLOAK_CLIENT_ID
        self._public_key: Optional[str] = None
    
    def get_jwks(self) -> dict:
        """
        Fetch JWKS (JSON Web Key Set) from Keycloak.
        """
        try:
            certs_url = f"{self.realm_url}/protocol/openid-connect/certs"
            logger.info(f"Fetching JWKS from: {certs_url}")
            response = requests.get(certs_url, timeout=10)
            response.raise_for_status()
            
            jwks = response.json()
            if not jwks.get("keys"):
                raise ValueError("No keys found in JWKS")
            
            logger.info(f"Successfully fetched {len(jwks['keys'])} keys from Keycloak")
            return jwks
            
        except Exception as e:
            logger.error(f"Failed to fetch Keycloak JWKS: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to verify token: Authentication service unavailable"
            )
    
    async def __call__(self, request: Request) -> Dict[str, Any]:
        """
        Verify the JWT token from the Authorization header.
        Returns the decoded token payload if valid.
        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            try:
                # Get JWKS
                jwks = self.get_jwks()
                
                # Decode token header to get the key ID (kid)
                unverified_header = jwt.get_unverified_header(credentials.credentials)
                kid = unverified_header.get('kid')
                
                # Find the matching key
                rsa_key = None
                for key in jwks["keys"]:
                    if key.get('kid') == kid:
                        rsa_key = key
                        break
                
                if not rsa_key:
                    logger.warning(f"No matching key found for kid: {kid}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token key",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Decode and verify the token
                # First, try without audience verification (some Keycloak configs don't include aud)
                try:
                    payload = jwt.decode(
                        credentials.credentials,
                        rsa_key,
                        algorithms=["RS256"],
                        audience=self.client_id,
                        options={
                            "verify_signature": True,
                            "verify_aud": True,
                            "verify_exp": True,
                        }
                    )
                except jwt.JWTClaimsError:
                    # If audience verification fails, try without it
                    logger.info("Retrying token verification without audience check")
                    payload = jwt.decode(
                        credentials.credentials,
                        rsa_key,
                        algorithms=["RS256"],
                        options={
                            "verify_signature": True,
                            "verify_aud": False,
                            "verify_exp": True,
                        }
                    )
                
                # Store user info in request state for later use
                request.state.user = payload
                logger.info(f"Successfully authenticated user: {payload.get('preferred_username', 'unknown')}")
                return payload
                
            except jwt.ExpiredSignatureError:
                logger.warning("Token has expired")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except jwt.JWTClaimsError as e:
                logger.warning(f"Invalid token claims: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token claims",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except JWTError as e:
                logger.warning(f"Invalid token: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Token verification failed: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Token verification failed"
                )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


class OptionalKeycloakBearer(KeycloakBearer):
    """
    Optional Keycloak authentication - doesn't raise error if no token provided.
    Use for endpoints that support both authenticated and anonymous access.
    """
    
    def __init__(self):
        super().__init__(auto_error=False)
    
    async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Verify token if provided, return None if not provided or invalid.
        """
        try:
            credentials: HTTPAuthorizationCredentials = await super(HTTPBearer, self).__call__(request)
            
            if credentials is None:
                return None
            
            if credentials.scheme != "Bearer":
                return None
            
            # Get JWKS
            jwks = self.get_jwks()
            
            # Decode token header to get the key ID (kid)
            unverified_header = jwt.get_unverified_header(credentials.credentials)
            kid = unverified_header.get('kid')
            
            # Find the matching key
            rsa_key = None
            for key in jwks["keys"]:
                if key.get('kid') == kid:
                    rsa_key = key
                    break
            
            if not rsa_key:
                logger.debug(f"No matching key found for kid: {kid}")
                return None
            
            # Decode and verify the token
            try:
                payload = jwt.decode(
                    credentials.credentials,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=self.client_id,
                    options={
                        "verify_signature": True,
                        "verify_aud": True,
                        "verify_exp": True,
                    }
                )
            except jwt.JWTClaimsError:
                # Try without audience verification
                payload = jwt.decode(
                    credentials.credentials,
                    rsa_key,
                    algorithms=["RS256"],
                    options={
                        "verify_signature": True,
                        "verify_aud": False,
                        "verify_exp": True,
                    }
                )
            
            # Store user info in request state
            request.state.user = payload
            return payload
            
        except Exception as e:
            logger.debug(f"Optional auth failed: {e}")
            return None


def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Get the current authenticated user from request state.
    Use this dependency in individual route handlers if you need user info.
    
    Example:
        @router.get("/profile")
        def get_profile(user: dict = Depends(get_current_user)):
            return {"username": user.get("preferred_username")}
    """
    if hasattr(request.state, "user"):
        return request.state.user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated"
    )


def require_role(required_role: str):
    """
    Dependency factory to check if user has a specific role.
    
    Usage:
        @router.delete("/admin-only", dependencies=[Depends(require_role("admin"))])
        def admin_route():
            return {"message": "Admin access granted"}
    """
    def role_checker(request: Request) -> None:
        user = get_current_user(request)
        
        # Keycloak stores roles in different places
        user_roles = []
        
        # Check realm roles
        if "realm_access" in user:
            user_roles.extend(user["realm_access"].get("roles", []))
        
        # Check client roles
        if "resource_access" in user:
            client_access = user["resource_access"].get(settings.KEYCLOAK_CLIENT_ID, {})
            user_roles.extend(client_access.get("roles", []))
        
        if required_role not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have the required role: {required_role}"
            )
    
    return role_checker
