# app/main.py
"""
FastAPI 진입점 — 운영 계층 포함.
"""
import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import saju, report, compatibility, daily, telegram
from app.auth.router import router as auth_router
from app.ops.logging_config import configure_logging
from app.ops.middleware import RequestContextMiddleware
from app.ops.rate_limit import RateLimitMiddleware

configure_logging()

app = FastAPI(
    title="Saju Engine API",
    version="1.0.0",
    description="Deterministic Four Pillars (Saju) engine.",
)

# Starlette: 마지막에 추가된 미들웨어가 outermost
app.add_middleware(
    RateLimitMiddleware,
    max_requests=int(os.getenv("SAJU_RATE_LIMIT_MAX", "120")),
    window_seconds=int(os.getenv("SAJU_RATE_LIMIT_WINDOW", "60")),
)

_cors_origins = [
    o.strip()
    for o in os.getenv("SAJU_CORS_ORIGINS", "*").split(",")
    if o.strip()
]
if "*" in _cors_origins and os.getenv("SAJU_ENV", "").lower() == "production":
    logging.getLogger("saju.security").warning(
        "SAJU_CORS_ORIGINS=* in production. Set explicit origins."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

app.add_middleware(RequestContextMiddleware)

app.include_router(saju.router, prefix="/api/v1/saju", tags=["Saju"])
app.include_router(report.router, prefix="/api/v1/saju", tags=["Report"])
app.include_router(compatibility.router, prefix="/api/v1/saju", tags=["Compatibility"])
app.include_router(daily.router, prefix="/api/v1/saju", tags=["Daily"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(telegram.router, prefix="/api/v1/telegram", tags=["Telegram"])


@app.get("/")
def root():
    return {"message": "Saju Engine API is running successfully!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}
