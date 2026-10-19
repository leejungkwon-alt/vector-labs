# tests/test_ops.py
"""운영 계층 테스트: 로깅, 요청 ID, rate limit, CORS, 헬스체크."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app
from app.ops.rate_limit import RateLimitMiddleware

client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_ready_endpoint():
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}


def test_request_id_header_present():
    r = client.get("/health")
    assert "x-request-id" in {k.lower() for k in r.headers.keys()}


def test_request_id_propagated_from_input():
    r = client.get("/health", headers={"x-request-id": "abc123def456"})
    assert r.headers["x-request-id"] == "abc123def456"


def test_rate_limit_headers_present():
    payload = {
        "birth_date": "1974-02-24",
        "birth_time": "05:30:00",
        "birth_location": "seoul",
        "lang": "en",
    }
    r = client.post("/api/v1/saju/report", json=payload)
    assert r.status_code == 200
    headers = {k.lower() for k in r.headers.keys()}
    assert "x-ratelimit-limit" in headers
    assert "x-ratelimit-remaining" in headers


def test_cors_preflight_allowed():
    r = client.options(
        "/api/v1/saju/report",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert r.status_code in (200, 204)
    assert "access-control-allow-origin" in {k.lower() for k in r.headers.keys()}


# ---- RateLimitMiddleware 단독 유닛 테스트 ----
def _mini_app(max_requests: int):
    mini = FastAPI()
    mini.add_middleware(
        RateLimitMiddleware, max_requests=max_requests, window_seconds=60
    )

    @mini.get("/ping")
    def ping():
        return {"ok": True}

    return TestClient(mini)


def test_rate_limit_rejects_over_limit():
    c = _mini_app(max_requests=2)
    assert c.get("/ping").status_code == 200
    assert c.get("/ping").status_code == 200
    r = c.get("/ping")
    assert r.status_code == 429
    assert "retry-after" in {k.lower() for k in r.headers.keys()}


def test_rate_limit_exempts_health_path():
    mini = FastAPI()
    mini.add_middleware(RateLimitMiddleware, max_requests=1, window_seconds=60)

    @mini.get("/health")
    def health():
        return {"ok": True}

    @mini.get("/ping")
    def ping():
        return {"ok": True}

    c = TestClient(mini)
    for _ in range(5):
        assert c.get("/health").status_code == 200
    assert c.get("/ping").status_code == 200
    assert c.get("/ping").status_code == 429


def test_rate_limit_disabled_when_max_zero():
    c = _mini_app(max_requests=0)
    for _ in range(10):
        assert c.get("/ping").status_code == 200
