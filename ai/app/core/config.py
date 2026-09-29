from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """서버 설정. 값은 환경변수에서만 읽는다 (키를 코드에 넣지 않는다)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    database_url: str = "postgresql://odor:odor@localhost:5432/odor"
    llm_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
