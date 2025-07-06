from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://llm_user:llm_password@localhost:5433/llm_platform"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Authentication
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "LLM Development Platform"
    version: str = "1.0.0"
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # File upload
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_dir: str = "uploads"
    
    # TimescaleDB
    timescale_enabled: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings() 