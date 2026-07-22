from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "Roleplay Chat API"
    app_version: str = "0.1.0"

    environment: str = "development"
    debug: bool = True


    # Local LLM Settings

    llm_provider: str = "local"

    local_api_url: str = (
        "http://127.0.0.1:8080"
    )

    base_url: str = "http://192.168.1.50:8000"

    # Generation Settings

    temperature: float = 0.9

    top_p: float = 0.95

    max_tokens: int = 128


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()