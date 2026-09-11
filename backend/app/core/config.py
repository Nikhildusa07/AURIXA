from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AURIXA"
    app_description: str = "Autonomous Enterprise AI Platform"
    app_version: str = "0.1.0"

    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="sqlite+aiosqlite:///./aurixa.db"
    )

    secret_key: str = "aurixa-dev-secret-key-2026"
    access_token_expire_minutes: int = 60

    frontend_url: str = "http://localhost:5173"
    redis_url: str = "redis://localhost:6379/0"

    llm_provider: str = "local"
    llm_model: str = "default"
    embedding_model: str = "default"

    upload_directory: str = "data/documents"
    max_upload_size_mb: int = 25

    max_agent_steps: int = 10
    workflow_timeout_seconds: int = 300
    tool_timeout_seconds: int = 30
    max_retry_attempts: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()