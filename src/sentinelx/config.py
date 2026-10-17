"""Runtime configuration, loaded from environment / .env.

Secrets are read from the environment only; nothing is hard-coded. The default
configuration (deterministic LLM provider, in-memory knowledge store) runs with
no secrets at all.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SENTINELX_", env_file=".env", extra="ignore"
    )

    # LLM
    llm_provider: str = "deterministic"
    llm_api_key: str | None = None
    llm_model: str | None = None
    llm_temperature: float = 0.0
    llm_seed: int = 7

    # Retrieval
    retrieval_top_k: int = 5

    # DB (scaffold; unused by the default in-memory store)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "sentinelx"
    db_user: str = "sentinelx"
    db_password: str | None = None


def load_settings() -> Settings:
    return Settings()
