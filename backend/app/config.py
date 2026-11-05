"""Application settings, read from the repo-root .env (or the process environment)."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT / ".env", ROOT / "backend" / ".env"), extra="ignore"
    )

    database_url: str = "postgresql+psycopg://civic:civic@localhost:5433/civicflow"
    test_database_url: str = "postgresql+psycopg://civic:civic@localhost:5433/civicflow_test"
    jwt_secret: str = "change-me"
    jwt_hours: int = 8
    media_dir: str = str(ROOT / "media")
    media_url_secret: str = "change-me-too"
    cors_origins: str = "http://localhost:5173"

    seed_admin_mobile: str = ""
    seed_admin_password: str = ""
    seed_staff_password: str = ""

    ingest_key_oem_sim: str = ""
    ingest_key_weather: str = ""
    weather_lat: float = 12.9081
    weather_lon: float = 77.4874
    weather_poll_minutes: int = 30

    time_scale: float = 1.0
    agent_mode: str = "rules"  # live | record | replay | rules
    llm_providers: str = ""
    scheduler_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
