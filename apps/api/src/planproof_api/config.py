from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPIK_API_KEY: str | None = None
    OPIK_PROJECT_NAME: str = "Hackaton"
    OPIK_WORKSPACE: str = "silviu-druma"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
