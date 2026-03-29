"""Configuration module for FastAPI application"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    database_url: str = "postgresql+asyncpg://benchmark:benchmark@postgres:5432/benchmark"
    app_name: str = "Benchmark API - FastAPI"
    app_version: str = "1.0.0"
    debug: bool = False
    pool_size: int = 20
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()