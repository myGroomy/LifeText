"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application configuration."""
    
    # Database
    database_url: str = "postgresql://lifetext:password@localhost:5432/lifetext"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # LLM Provider Configuration
    llm_provider: str = "anthropic"  # openai, anthropic, gemini, deepseek, openai-compatible
    llm_api_key: str
    llm_model: str = "claude-sonnet-4-20250514"
    llm_base_url: Optional[str] = None  # For openai-compatible providers
    
    # Whisper
    whisper_model_size: str = "base"
    
    # App settings
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    
    # Development user (for MVP, no auth yet)
    development_user_id: str = "dev-user-123"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
