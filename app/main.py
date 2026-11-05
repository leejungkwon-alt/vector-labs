# app/main.py
"""
FastAPI 진입점 — 운영 계층 포함.
"""
import os
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints import saju, report, compatibility, daily, telegram
from app.auth.router import router as auth_router
from app.ops.logging_config import configure_logging
from app.ops.middleware import RequestContextMiddleware
from app.ops.env import is_production, validate_startup
from app.ops.rate_limit import RateLimitMiddleware

configure_logging()


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    """앱 부팅 시 프로덕션 필수 환경변수 검증 (fail-closed)."""
    validate_startup()
    yield


app = FastAPI(
    title="Gyeol API",
    version="1.0.0",
    description="Deterministic Four Pillars engine for Gyeol (Read the grain of your life).",
    lifespan=_lifespan,
)

# Starlette: 마지막에 add 한 미들웨어가 가장 바깥(outermost).
# 요청 흐름: CORS -> RequestContext -> RateLimit -> 라우터
# (그래서 429/500 응답에도 CORS 헤더가 붙는다.)
app.add_middleware(
    RateLimitMiddleware,
    max_requests=int(os.getenv("SAJU_RATE_LIMIT_MAX", "120")),
    window_seconds=int(os.getenv("SAJU_RATE_LIMIT_WINDOW", "60")),
)

app.add_middleware(RequestContextMiddleware)

_cors_origins = [
    o.strip()
    for o in os.getenv("SAJU_CORS_ORIGINS", "*").split(",")
    if o.strip()
]
if "*" in _cors_origins and is_production():
    logging.getLogger("saju.security").warning(
        "SAJU_CORS_ORIGINS=* in production. Set explicit origins."
    )

# 미리보기 배포(*.vercel.app) 허용 정규식. 빈 문자열이면 비활성화.
_cors_regex = os.getenv("SAJU_CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app").strip() or None

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

app.include_router(saju.router, prefix="/api/v1/saju", tags=["Saju"])
app.include_router(report.router, prefix="/api/v1/saju", tags=["Report"])
app.include_router(compatibility.router, prefix="/api/v1/saju", tags=["Compatibility"])
app.include_router(daily.router, prefix="/api/v1/saju", tags=["Daily"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(telegram.router, prefix="/api/v1/telegram", tags=["Telegram"])


@app.get("/")
def root():
    return {"message": "Saju Engine API is running successfully!"}


@app.get("/healthz")
def healthz():
    """Startup/liveness probe — 외부 의존성 없음 (즉시 200)."""
    return {"status": "ok"}


@app.get("/health")  # 기존 경로 유지 (클라이언트 호환)
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    """Readiness probe — DB(SELECT 1) 까지 확인. 실패 시 503.

    Cloud Run startup probe 에는 연결하지 않는다 (Neon 콜드 스타트 시
    재시작 루프 방지). deploy.ps1 스모크 테스트 + 모니터링 용.
    """
    from app.auth.repository import get_repository

    try:
        get_repository().ping()
        return {"status": "ready", "db": "ok"}
    except Exception as e:
        logging.getLogger("saju.ops").error("readiness check failed: %s", e)
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "db": "error",
                "error": type(e).__name__,
            },
        )

