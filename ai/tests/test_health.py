from fastapi.testclient import TestClient

from app.api import health as health_module
from app.main import app

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

client = TestClient(app)


def test_health_ok_when_db_ok(monkeypatch):
    monkeypatch.setattr(health_module, "check_db", lambda: {"status": "ok", "pgvector": "0.8.0"})
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "db": {"status": "ok", "pgvector": "0.8.0"}}


def test_health_degraded_when_db_down(monkeypatch):
    monkeypatch.setattr(health_module, "check_db", lambda: {"status": "error", "detail": "OperationalError"})
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "degraded"

@pytest.mark.parametrize(
    "row, expected_status",
    [
        (("0.8.6",), "ok"),
        (None, "degraded"),
    ],
)
def test_health_checks_pgvector_presence(monkeypatch, row, expected_status):
    # 실제 DB 대신 확장 조회 결과만 모의 처리한다.
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.execute.return_value.fetchone.return_value = row

    monkeypatch.setattr(
        health_module.psycopg,
        "connect",
        lambda *args, **kwargs: connection,
    )
    monkeypatch.setattr(
        health_module,
        "get_settings",
        lambda: SimpleNamespace(database_url="mock"),
    )

    # check_db 자체는 대체하지 않으므로 실제 판정 로직을 검증한다.
    response = client.get("/health")
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == expected_status
    connection.execute.assert_called_once()

    if row is None:
        assert body["db"]["status"] == "error"
        assert body["db"]["pgvector"] is None
        assert body["db"]["detail"] == "PgvectorExtensionMissing"
    else:
        assert body["db"]["status"] == "ok"
        assert body["db"]["pgvector"] == row[0]