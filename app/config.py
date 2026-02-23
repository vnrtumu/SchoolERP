from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration"""
    
    # Application
    APP_NAME: str = "Mindwhile ERP"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Master Database (Control Plane)
    MASTER_DATABASE_URL: str
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TENANT_PASSWORD_ENCRYPTION_KEY: str
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000", 
        "http://localhost:8000", 
        "http://localhost:5173",
        "https://mindwhileerp.vercel.app"
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-fix Railway MySQL URL to use async driver
        if self.MASTER_DATABASE_URL and self.MASTER_DATABASE_URL.startswith("mysql://"):
            self.MASTER_DATABASE_URL = self.MASTER_DATABASE_URL.replace("mysql://", "mysql+aiomysql://")


settings = Settings()
