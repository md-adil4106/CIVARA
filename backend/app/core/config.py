from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CIVARA (MOOLKARAN Engine)"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/civara_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI API Keys
    AI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
