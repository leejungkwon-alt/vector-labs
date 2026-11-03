# tests/test_env_failclosed.py
"""SAJU_ENV fail-closed 동작 검증: 환경변수가 빠져도 mock 경로가 열리지 않아야 한다."""
import pytest

from app.ops.env import is_production, validate_startup


@pytest.mark.parametrize("value", ["", "   ", "prod", "Production", "PRODUCTION", "staging", "prodction", "stage"])
def test_non_dev_values_are_production(monkeypatch, value):
    monkeypatch.setenv("SAJU_ENV", value)
    assert is_production() is True


def test_unset_is_production(monkeypatch):
    monkeypatch.delenv("SAJU_ENV", raising=False)
    assert is_production() is True


@pytest.mark.parametrize("value", ["development", "dev", "local", "test", "testing", " DEV ", "Development"])
def test_explicit_dev_values_are_not_production(monkeypatch, value):
    monkeypatch.setenv("SAJU_ENV", value)
    assert is_production() is False


def test_mock_receipt_rejected_when_env_unset(monkeypatch):
    monkeypatch.delenv("SAJU_ENV", raising=False)
    from app.services.iap import verify_and_grant, IAPVerificationError

    with pytest.raises(IAPVerificationError, match="Mock receipts"):
        verify_and_grant("u1", "ios", "mock_valid_receipt", "sub_monthly_299")


def test_mock_provider_token_rejected_when_env_unset(monkeypatch):
    monkeypatch.delenv("SAJU_ENV", raising=False)
    from app.auth.providers import verify_provider_token, ProviderTokenError

    with pytest.raises(ProviderTokenError):
        verify_provider_token("apple", "mock:someone")


def test_dev_jwt_secret_not_used_when_env_unset(monkeypatch):
    monkeypatch.delenv("SAJU_ENV", raising=False)
    monkeypatch.delenv("SAJU_JWT_SECRET", raising=False)
    from app.auth.jwt_utils import _secret

    with pytest.raises(RuntimeError, match="SAJU_JWT_SECRET"):
        _secret()


def test_validate_startup_fails_without_secret(monkeypatch):
    monkeypatch.delenv("SAJU_ENV", raising=False)
    monkeypatch.delenv("SAJU_JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        validate_startup()


def test_validate_startup_rejects_short_secret(monkeypatch):
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.setenv("SAJU_JWT_SECRET", "too-short")
    with pytest.raises(RuntimeError, match="at least"):
        validate_startup()


def test_validate_startup_ok_with_strong_secret(monkeypatch):
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.setenv("SAJU_JWT_SECRET", "x" * 40)
    validate_startup()  # 예외 없음


def test_validate_startup_ok_in_dev(monkeypatch):
    monkeypatch.setenv("SAJU_ENV", "development")
    monkeypatch.delenv("SAJU_JWT_SECRET", raising=False)
    validate_startup()  # 예외 없음
