# app/ops/middleware.py
"""
Request ID + duration logging 미들웨어.

주의: 처리되지 않은 예외를 그대로 raise 하면 Starlette 의 ServerErrorMiddleware 가
CORS 미들웨어 "바깥"에서 500 을 만들기 때문에 응답에 Access-Control-Allow-Origin 이
빠진다. 브라우저는 이를 "CORS 에러 / Failed to fetch" 로만 보여줘 원인 추적이 불가능해진다.
그래서 여기(CORS 안쪽)에서 직접 JSON 500 을 만들어 CORS 헤더가 붙도록 한다.
"""
import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.ops.logging_config import set_request_id

logger = logging.getLogger("saju.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        request.state.request_id = rid
        set_request_id(rid)

        start = time.perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception:
                duration_ms = (time.perf_counter() - start) * 1000
                logger.exception(
                    "unhandled",
                    extra={
                        "path": request.url.path,
                        "method": request.method,
                        "duration_ms": round(duration_ms, 2),
                    },
                )
                response = JSONResponse(
                    status_code=500,
                    content={"detail": "Internal server error.", "request_id": rid},
                )

            duration_ms = (time.perf_counter() - start) * 1000
            response.headers["X-Request-ID"] = rid
            logger.info(
                "request",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "status": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            return response
        finally:
            set_request_id(None)
