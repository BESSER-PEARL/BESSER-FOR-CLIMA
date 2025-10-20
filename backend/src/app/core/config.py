"""
Application configuration settings.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Climaborough API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "root"
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    
    # Keycloak
    KEYCLOAK_SERVER_URL: str = "https://auth.climaplatform.eu"
    KEYCLOAK_REALM: str = "climaborough"
    KEYCLOAK_CLIENT_ID: str = "climaborough-platform"
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3002", 
        "http://localhost:8080"
    ]
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL."""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    @property
    def KEYCLOAK_AUTH_URL(self) -> str:
        """Construct Keycloak auth URL."""
        return f"{self.KEYCLOAK_SERVER_URL}/realms/{self.KEYCLOAK_REALM}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()