from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum
from pathlib import Path


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    app_name: str = "Healthcare SaaS API"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    version: str = "1.0.0"
    
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "healthcare_saas"
    mysql_ssl: bool = False  # True para PlanetScale
    
    frontend_url: str = "http://localhost:5173"
    api_url: str = "http://localhost:8000"
    
    redis_url: Optional[str] = None
    cache_ttl: int = 300
    
    @property
    def database_url(self) -> str:
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
    
    @property
    def async_database_url(self) -> str:
        return f"mysql+asyncmy://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
    
    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"
        case_sensitive = False


settings = Settings()