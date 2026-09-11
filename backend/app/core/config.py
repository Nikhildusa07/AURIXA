from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AURIXA"
    APP_DESCRIPTION: str = "Autonomous Enterprise AI Platform"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI
    LLM_PROVIDER: str = "local"
    LLM_MODEL: str = "default"
    EMBEDDING_MODEL: str = "default"

    # File Storage
    UPLOAD_DIRECTORY: str = "data/documents"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Workflow
    MAX_AGENT_STEPS: int = 10
    WORKFLOW_TIMEOUT_SECONDS: int = 300
    TOOL_TIMEOUT_SECONDS: int = 30
    MAX_RETRY_ATTEMPTS: int = 3

    # Email
    BREVO_API_KEY: str = ""
    BREVO_SENDER_EMAIL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()