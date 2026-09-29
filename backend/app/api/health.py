import psycopg
from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


def check_db() -> dict:
    """DB 연결과 pgvector 확장 설치 여부를 확인한다."""
    try:
        with psycopg.connect(get_settings().database_url, connect_timeout=3) as conn:
            row = conn.execute(
                "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
            ).fetchone()
        return {"status": "ok", "pgvector": row[0] if row else None}
    except Exception as e:  # 헬스체크는 예외를 던지지 않고 상태로 보고한다
        return {"status": "error", "detail": type(e).__name__}


@router.get("/health")
def health() -> dict:
    db = check_db()
    return {"status": "ok" if db["status"] == "ok" else "degraded", "db": db}
