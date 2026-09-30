import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_database_url_is_required(monkeypatch):
    # 기본값이 없어야 .env 누락 시 공개 비밀번호로 조용히 뜨지 않는다
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_config_error_does_not_leak_other_values(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("AIRKOREA_API_KEY", "FAKE-SECRET-123456")
    monkeypatch.setenv("LLM_API_KEY", "FAKE-SECRET-123456")
    with pytest.raises(ValidationError) as exc:
        Settings(_env_file=None)
    assert "FAKE-SECRET-123456" not in str(exc.value)
