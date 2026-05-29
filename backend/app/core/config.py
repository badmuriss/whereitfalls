from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WhereItFalls"
    app_env: str = "local"
    database_url: str = "sqlite:///./whereitfalls.db"
    spacetrack_user: str | None = None
    spacetrack_pass: str | None = None
    celestrak_base: AnyHttpUrl = "https://celestrak.org"
    ingest_interval_hours: int = Field(default=6, ge=1, le=24)

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
