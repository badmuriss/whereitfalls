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
    email_host: str | None = None
    email_port: int = 587
    email_user: str | None = None
    email_pass: str | None = None
    email_from: str = "alertas@whereitfalls.app"
    resend_api_key: str | None = None
    ingest_interval_hours: int = Field(default=6, ge=1, le=24)

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
