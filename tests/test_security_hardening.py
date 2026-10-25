"""Step 4-B 보안 강화 회귀 테스트."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# /report 전용 (lang 포함)
BASE_PAYLOAD = {
    "birth_date": "1974-02-24",
    "birth_time": "05:30:00",
    "timezone_str": "Asia/Seoul",
    "longitude": 126.9780,
    "correction_mode": "lmt",
    "jasi_boundary": 23,
    "gender": "M",
    "lang": "en",
}

# /calculate 전용 (SajuRequest는 extra=forbid이므로 lang 금지)
CALC_PAYLOAD = {
    "birth_date": "1974-02-24",
    "birth_time": "05:30:00",
    "timezone_str": "Asia/Seoul",
    "longitude": 126.9780,
    "correction_mode": "lmt",
    "jasi_boundary": 23,
    "gender": "M",
}


# ---- /interpret 게이팅 ----
def test_interpret_works_by_default(monkeypatch):
    monkeypatch.delenv("SAJU_REQUIRE_AUTH_FOR_INTERPRET", raising=False)
    resp = client.post(
        "/api/v1/saju/interpret",
        json={"saju_data": {"day_pillar": "庚午"}, "lang": "en"},
    )
    assert resp.status_code == 200


def test_interpret_requires_auth_when_enabled(monkeypatch):
    monkeypatch.setenv("SAJU_REQUIRE_AUTH_FOR_INTERPRET", "true")
    resp = client.post(
        "/api/v1/saju/interpret",
        json={"saju_data": {"day_pillar": "庚午"}, "lang": "en"},
    )
    assert resp.status_code == 401


# ---- /calculate 게이팅 ----
def test_calculate_works_by_default(monkeypatch):
    monkeypatch.delenv("SAJU_REQUIRE_AUTH_FOR_CALCULATE", raising=False)
    resp = client.post("/api/v1/saju/calculate", json=CALC_PAYLOAD)
    assert resp.status_code == 200


def test_calculate_requires_auth_when_enabled(monkeypatch):
    monkeypatch.setenv("SAJU_REQUIRE_AUTH_FOR_CALCULATE", "true")
    resp = client.post("/api/v1/saju/calculate", json=CALC_PAYLOAD)
    assert resp.status_code == 401


# ---- mock: 토큰 프로덕션 가드 ----
def test_mock_token_works_in_development(monkeypatch):
    monkeypatch.delenv("SAJU_ENV", raising=False)
    from app.auth.providers import verify_provider_token
    identity = verify_provider_token("apple", "mock:dev-user-1")
    assert identity["subject"] == "dev-user-1"


def test_mock_token_rejected_in_production(monkeypatch):
    monkeypatch.setenv("SAJU_ENV", "production")
    from app.auth.providers import verify_provider_token, ProviderTokenError
    with pytest.raises(ProviderTokenError, match="not allowed in production"):
        verify_provider_token("apple", "mock:prod-user")


# ---- JWT 시크릿 프로덕션 가드 ----
def test_jwt_default_secret_works_in_dev(monkeypatch):
    monkeypatch.delenv("SAJU_ENV", raising=False)
    monkeypatch.delenv("SAJU_JWT_SECRET", raising=False)
    from app.auth.jwt_utils import _secret
    s = _secret()
    assert s


def test_jwt_default_secret_rejected_in_production(monkeypatch):
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.delenv("SAJU_JWT_SECRET", raising=False)
    from app.auth.jwt_utils import _secret
    with pytest.raises(RuntimeError, match="SAJU_JWT_SECRET"):
        _secret()


def test_jwt_explicit_secret_works_in_production(monkeypatch):
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.setenv("SAJU_JWT_SECRET", "explicit-prod-secret-32-chars-minimum-xyz")
    from app.auth.jwt_utils import _secret
    assert _secret() == "explicit-prod-secret-32-chars-minimum-xyz"


# ---- IAP mock 영수증 프로덕션 가드 ----
def test_iap_mock_receipt_works_in_dev(monkeypatch, tmp_path):
    monkeypatch.delenv("SAJU_ENV", raising=False)
    monkeypatch.setenv("SAJU_AUTH_DB_PATH", str(tmp_path / "auth.db"))
    from app.auth.repository import reset_repository
    reset_repository()

    a = client.post("/api/v1/auth/anonymous").json()
    from app.services.iap import verify_and_grant
    result = verify_and_grant(
        a["user"]["id"], "ios", "mock_valid_receipt", "sub_monthly_299"
    )
    assert result["status"] == "success"


def test_iap_mock_receipt_rejected_in_production(monkeypatch, tmp_path):
    """production에서 mock 영수증 거부. JWT 시크릿도 함께 설정해야 auth 통과."""
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.setenv("SAJU_JWT_SECRET", "test-secret-for-iap-production-32chars!")
    monkeypatch.setenv("SAJU_AUTH_DB_PATH", str(tmp_path / "auth.db"))
    from app.auth.repository import reset_repository
    reset_repository()

    a_resp = client.post("/api/v1/auth/anonymous")
    assert a_resp.status_code == 200, f"auth failed: {a_resp.text}"
    a = a_resp.json()

    from app.services.iap import verify_and_grant, IAPVerificationError
    with pytest.raises(IAPVerificationError, match="not allowed in production"):
        verify_and_grant(
            a["user"]["id"], "ios", "mock_valid_receipt", "sub_monthly_299"
        )

def test_jwt_short_secret_rejected_in_production(monkeypatch):
    """production + 짧은 시크릿 → RuntimeError (최소 32자)."""
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.setenv("SAJU_JWT_SECRET", "too-short")
    from app.auth.jwt_utils import _secret
    with pytest.raises(RuntimeError, match="at least 32"):
        _secret()


def test_jwt_exactly_min_length_ok_in_production(monkeypatch):
    """production + 정확히 32자 → 통과 (경계값)."""
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.setenv("SAJU_JWT_SECRET", "x" * 32)
    from app.auth.jwt_utils import _secret
    assert _secret() == "x" * 32


def test_jwt_short_secret_ok_in_development(monkeypatch):
    """dev는 짧은 커스텀 시크릿 허용 (기존 동작 보존)."""
    monkeypatch.delenv("SAJU_ENV", raising=False)
    monkeypatch.setenv("SAJU_JWT_SECRET", "short-dev")
    from app.auth.jwt_utils import _secret
    assert _secret() == "short-dev"

