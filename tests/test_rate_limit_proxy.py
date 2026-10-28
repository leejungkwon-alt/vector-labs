# tests/test_rate_limit_proxy.py
"""X-Forwarded-For 지원 회귀 테스트."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.ops.rate_limit import RateLimitMiddleware


def _make_app(max_requests=1, window_seconds=60):
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware, max_requests=max_requests, window_seconds=window_seconds
    )

    @app.get("/ping")
    def ping():
        return {"ok": True}

    return app


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("SAJU_TRUST_PROXY", raising=False)


def test_xff_ignored_when_trust_proxy_off(monkeypatch):
    """SAJU_TRUST_PROXY 미설정 시 XFF 무시 — XFF 회전으로 rate limit 우회 불가."""
    monkeypatch.delenv("SAJU_TRUST_PROXY", raising=False)
    app = _make_app(max_requests=1)
    client = TestClient(app)
    r1 = client.get("/ping", headers={"X-Forwarded-For": "1.1.1.1"})
    r2 = client.get("/ping", headers={"X-Forwarded-For": "2.2.2.2"})
    assert r1.status_code == 200
    assert r2.status_code == 429, "XFF 미신뢰 시 IP 회전 우회가 발생하면 안 됨"


def test_xff_trusted_when_env_set(monkeypatch):
    """SAJU_TRUST_PROXY=1 시 XFF leftmost IP 로 별도 버킷."""
    monkeypatch.setenv("SAJU_TRUST_PROXY", "1")
    app = _make_app(max_requests=1)
    client = TestClient(app)
    r1 = client.get("/ping", headers={"X-Forwarded-For": "1.1.1.1"})
    r2 = client.get("/ping", headers={"X-Forwarded-For": "2.2.2.2"})
    assert r1.status_code == 200
    assert r2.status_code == 200, "XFF 신뢰 시 서로 다른 IP 는 별도 버킷"


def test_xff_multiple_entries_uses_leftmost(monkeypatch):
    """XFF 여러 IP → leftmost(원 클라이언트) 사용."""
    monkeypatch.setenv("SAJU_TRUST_PROXY", "1")
    app = _make_app(max_requests=1)
    client = TestClient(app)
    h1 = {"X-Forwarded-For": "1.1.1.1, 10.0.0.1, 10.0.0.2"}
    h2 = {"X-Forwarded-For": "1.1.1.1, 10.0.0.3"}
    r1 = client.get("/ping", headers=h1)
    r2 = client.get("/ping", headers=h2)
    assert r1.status_code == 200
    assert r2.status_code == 429, "leftmost IP 동일 → 같은 버킷"


def test_xff_missing_falls_back_to_client_host(monkeypatch):
    """XFF 헤더 없으면 client.host 로 폴백."""
    monkeypatch.setenv("SAJU_TRUST_PROXY", "1")
    app = _make_app(max_requests=1)
    client = TestClient(app)
    r1 = client.get("/ping")
    r2 = client.get("/ping")
    assert r1.status_code == 200
    assert r2.status_code == 429


def test_xff_empty_string_falls_back(monkeypatch):
    """빈 XFF 헤더는 client.host 폴백."""
    monkeypatch.setenv("SAJU_TRUST_PROXY", "1")
    app = _make_app(max_requests=1)
    client = TestClient(app)
    r1 = client.get("/ping", headers={"X-Forwarded-For": ""})
    r2 = client.get("/ping", headers={"X-Forwarded-For": ""})
    assert r1.status_code == 200
    assert r2.status_code == 429
