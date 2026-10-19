# app/ops/middleware.py
"""
Request ID + duration logging 미들웨어.
"""
import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

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
                raise

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
