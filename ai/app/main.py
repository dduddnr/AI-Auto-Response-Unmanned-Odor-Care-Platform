from fastapi import FastAPI

from app.api import health

app = FastAPI(title="악취 근거기반 자동응답 AI (RAG·멀티모달)", version="0.1.0")

app.include_router(health.router)
