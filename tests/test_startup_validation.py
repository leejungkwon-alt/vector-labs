"""앱 부팅 시 validate_startup() fail-closed 동작 검증."""
import importlib

import pytest
from fastapi.testclient import TestClient


def test_app_boot_fails_without_secret_in_production(monkeypatch):
    """SAJU_ENV=production + SAJU_JWT_SECRET 미설정 → 앱 부팅 실패."""
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.delenv("SAJU_JWT_SECRET", raising=False)

    import app.main
    importlib.reload(app.main)

    with pytest.raises(RuntimeError, match="SAJU_JWT_SECRET is not set in production"):
        with TestClient(app.main.app):
            pass


def test_app_boot_ok_in_development(monkeypatch):
    """SAJU_ENV=development 면 부팅 성공."""
    monkeypatch.setenv("SAJU_ENV", "development")
    monkeypatch.delenv("SAJU_JWT_SECRET", raising=False)

    import app.main
    importlib.reload(app.main)

    with TestClient(app.main.app) as client:
        r = client.get("/health")
        assert r.status_code == 200


def test_app_boot_ok_with_secret_in_production(monkeypatch):
    """SAJU_ENV=production + 32자 이상 secret → 부팅 성공."""
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.setenv("SAJU_JWT_SECRET", "x" * 32)
    monkeypatch.setenv("SAJU_AUTH_DB_PATH", ":memory:")  # Phase 4: prod requires DB config

    import app.main
    importlib.reload(app.main)

    with TestClient(app.main.app) as client:
        r = client.get("/health")
        assert r.status_code == 200