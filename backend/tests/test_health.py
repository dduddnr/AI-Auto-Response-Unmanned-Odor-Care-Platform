from fastapi.testclient import TestClient

from app.api import health as health_module
from app.main import app

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
