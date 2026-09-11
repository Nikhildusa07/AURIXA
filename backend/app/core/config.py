from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================
    # APPLICATION
    # ==========================================

    APP_NAME: str = "AURIXA"
    ENVIRONMENT: str = "development"

    # ==========================================
    # DATABASE
    # ==========================================

    DATABASE_URL: str

    # ==========================================
    # SECURITY
    # ==========================================

    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    # Access token expiration time in minutes
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ==========================================
    # CONFIGURATION
    # ==========================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()