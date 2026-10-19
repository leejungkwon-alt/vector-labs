# app/ops/logging_config.py
"""
구조적 로깅 설정 + request_id 전파.

- SAJU_LOG_FORMAT=json  → JSON 로그 (프로덕션)
- SAJU_LOG_FORMAT=text  → 사람이 읽기 좋은 텍스트 (개발, 기본)
"""
import contextvars
import json
import logging
import os
import sys
from datetime import datetime, timezone


_request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


def set_request_id(rid: str | None) -> None:
    _request_id_var.set(rid)


def current_request_id() -> str:
    return _request_id_var.get() or "-"


class RequestIdFilter(logging.Filter):
    """record.request_id가 비어 있으면 contextvar에서 채움."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not getattr(record, "request_id", None):
            record.request_id = current_request_id()
        return True


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(record, "request_id", "-"),
            "msg": record.getMessage(),
        }
        for key in ("path", "method", "status", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    level = os.getenv("SAJU_LOG_LEVEL", "INFO").upper()
    fmt = os.getenv("SAJU_LOG_FORMAT", "text").lower()

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())

    if fmt == "json":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)-7s [%(name)s] rid=%(request_id)s %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # uvicorn 로그도 동일 포맷으로 통일
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True
