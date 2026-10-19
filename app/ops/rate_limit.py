# app/ops/rate_limit.py
"""
IP 기반 슬라이딩 윈도우 rate limit (인메모리, 단일 프로세스용).

SAJU_RATE_LIMIT_MAX=0 이면 비활성화.
"""
from collections import defaultdict, deque
from time import monotonic

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


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

        ip = request.client.host if request.client else "unknown"
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
