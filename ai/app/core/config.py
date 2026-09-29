from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """서버 설정. 값은 환경변수에서만 읽는다 (키를 코드에 넣지 않는다)."""

    # hide_input_in_errors: 설정 누락 에러 메시지에 다른 키 값이 찍히지 않게 한다
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    app_env: str = "local"
    database_url: str  # 필수. 기본값을 두지 않아 누락 시 공개 비밀번호로 뜨지 않게 한다
    llm_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
