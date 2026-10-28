# app/ops/rate_limit.py
"""
IP 기반 슬라이딩 윈도우 rate limit (인메모리, 단일 프로세스용).

SAJU_RATE_LIMIT_MAX=0 이면 비활성화.
"""
import os
from collections import defaultdict, deque
from time import monotonic

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse




_TRUTHY = ("1", "true", "yes", "on")


def _trust_proxy() -> bool:
    """SAJU_TRUST_PROXY=1/true/yes/on 일 때만 프록시 헤더 신뢰."""
    return os.environ.get("SAJU_TRUST_PROXY", "").strip().lower() in _TRUTHY


def _client_ip(request: Request) -> str:
    """클라이언트 IP 반환.

    - SAJU_TRUST_PROXY 활성 + X-Forwarded-For 존재:
      leftmost(원 클라이언트) IP 사용. Cloud Run/Vercel 등 프록시 뒤 배포용.
    - 그 외: request.client.host (기존 동작 유지, 스푸핑 방지).
    """
    if _trust_proxy():
        xff = request.headers.get("x-forwarded-for", "").strip()
        if xff:
            first = xff.split(",")[0].strip()
            if first:
                return first
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    # 헬스체크·프리플라이트는 우회
    EXEMPT_PATHS = {"/health", "/ready", "/"}

    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if self.max_requests <= 0:
            return await call_next(request)

        path = request.url.path
        if path in self.EXEMPT_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        ip = _client_ip(request)
        now = monotonic()
        bucket = self._hits[ip]
        cutoff = now - self.window
        while bucket and bucket[0] < cutoff:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Slow down."},
                headers={
                    "Retry-After": str(self.window),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        bucket.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.max_requests - len(bucket))
        )
        return response
