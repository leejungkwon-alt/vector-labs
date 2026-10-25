"""OIDC 실제 검증 유닛테스트 (Apple)."""
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.auth import providers as prov

KID = "test-kid-1"
ISS = "https://appleid.apple.com"
AUD = "com.example.saju.test"


def _make_apple_token(private_key, **overrides):
    now = int(time.time())
    claims = {
        "iss": ISS,
        "aud": AUD,
        "sub": "apple-sub-1",
        "iat": now,
        "exp": now + 300,
    }
    claims.update(overrides)
    return jwt.encode(
        claims, private_key, algorithm="RS256", headers={"kid": KID}
    )


@pytest.fixture
def apple_setup(monkeypatch):
    from jwt.algorithms import RSAAlgorithm

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = RSAAlgorithm.to_jwk(key.public_key(), as_dict=True)
    jwk["kid"] = KID
    jwk["alg"] = "RS256"
    jwk["use"] = "sig"

    monkeypatch.setenv("SAJU_APPLE_CLIENT_ID", AUD)
    monkeypatch.delenv("SAJU_ENV", raising=False)

    prov._JWKS_CACHE.clear()

    def fake_fetch(_provider):
        return {KID: RSAAlgorithm.from_jwk(jwk)}

    monkeypatch.setattr(prov, "_fetch_jwks", fake_fetch)

    yield key

    prov._JWKS_CACHE.clear()


def test_apple_valid(apple_setup):
    token = _make_apple_token(apple_setup)
    result = prov.verify_provider_token("apple", token)
    assert result == {"provider": "apple", "subject": "apple-sub-1"}


def test_apple_expired(apple_setup):
    token = _make_apple_token(apple_setup, exp=int(time.time()) - 10)
    with pytest.raises(prov.ProviderTokenError):
        prov.verify_provider_token("apple", token)


def test_apple_wrong_audience(apple_setup):
    token = _make_apple_token(apple_setup, aud="wrong-audience")
    with pytest.raises(prov.ProviderTokenError):
        prov.verify_provider_token("apple", token)


def test_apple_wrong_issuer(apple_setup):
    token = _make_apple_token(apple_setup, iss="https://evil.example.com")
    with pytest.raises(prov.ProviderTokenError):
        prov.verify_provider_token("apple", token)


def test_apple_missing_kid(apple_setup):
    now = int(time.time())
    claims = {"iss": ISS, "aud": AUD, "sub": "x", "iat": now, "exp": now + 300}
    token = jwt.encode(claims, apple_setup, algorithm="RS256", headers={})
    with pytest.raises(prov.ProviderTokenError, match="Unknown signing key"):
        prov.verify_provider_token("apple", token)


def test_apple_bad_signature(apple_setup):
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = _make_apple_token(other_key)
    with pytest.raises(prov.ProviderTokenError):
        prov.verify_provider_token("apple", token)


def test_apple_missing_env(monkeypatch, apple_setup):
    monkeypatch.delenv("SAJU_APPLE_CLIENT_ID", raising=False)
    token = _make_apple_token(apple_setup)
    with pytest.raises(
        prov.ProviderTokenError, match="SAJU_APPLE_CLIENT_ID is not configured"
    ):
        prov.verify_provider_token("apple", token)


def test_mock_still_works_in_dev(apple_setup):
    result = prov.verify_provider_token("apple", "mock:dev-user")
    assert result == {"provider": "apple", "subject": "dev-user"}


def test_mock_rejected_in_production(monkeypatch, apple_setup):
    monkeypatch.setenv("SAJU_ENV", "production")
    with pytest.raises(prov.ProviderTokenError, match="production"):
        prov.verify_provider_token("apple", "mock:dev-user")

# =============================================================================
# Google OIDC (1-D)
# =============================================================================

GOOGLE_KID = "test-google-kid-1"
GOOGLE_ISS = "https://accounts.google.com"
GOOGLE_AUD = "com.example.saju.google.test"


def _make_google_token(private_key, **overrides):
    now = int(time.time())
    claims = {
        "iss": GOOGLE_ISS,
        "aud": GOOGLE_AUD,
        "sub": "google-sub-1",
        "iat": now,
        "exp": now + 300,
    }
    claims.update(overrides)
    return jwt.encode(
        claims, private_key, algorithm="RS256", headers={"kid": GOOGLE_KID}
    )


@pytest.fixture
def google_setup(monkeypatch):
    from jwt.algorithms import RSAAlgorithm

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = RSAAlgorithm.to_jwk(key.public_key(), as_dict=True)
    jwk["kid"] = GOOGLE_KID
    jwk["alg"] = "RS256"
    jwk["use"] = "sig"

    monkeypatch.setenv("SAJU_GOOGLE_CLIENT_ID", GOOGLE_AUD)
    monkeypatch.delenv("SAJU_ENV", raising=False)

    prov._JWKS_CACHE.clear()

    def fake_fetch(_provider):
        return {GOOGLE_KID: RSAAlgorithm.from_jwk(jwk)}

    monkeypatch.setattr(prov, "_fetch_jwks", fake_fetch)

    yield key

    prov._JWKS_CACHE.clear()


def test_google_valid(google_setup):
    token = _make_google_token(google_setup)
    result = prov.verify_provider_token("google", token)
    assert result == {"provider": "google", "subject": "google-sub-1"}


def test_google_expired(google_setup):
    token = _make_google_token(google_setup, exp=int(time.time()) - 10)
    with pytest.raises(prov.ProviderTokenError):
        prov.verify_provider_token("google", token)


def test_google_wrong_audience(google_setup):
    token = _make_google_token(google_setup, aud="wrong-audience")
    with pytest.raises(prov.ProviderTokenError):
        prov.verify_provider_token("google", token)


def test_google_wrong_issuer(google_setup):
    token = _make_google_token(google_setup, iss="https://evil.example.com")
    with pytest.raises(prov.ProviderTokenError):
        prov.verify_provider_token("google", token)


def test_google_bad_signature(google_setup):
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = _make_google_token(other_key)
    with pytest.raises(prov.ProviderTokenError):
        prov.verify_provider_token("google", token)


def test_google_missing_env(monkeypatch, google_setup):
    monkeypatch.delenv("SAJU_GOOGLE_CLIENT_ID", raising=False)
    token = _make_google_token(google_setup)
    with pytest.raises(
        prov.ProviderTokenError, match="SAJU_GOOGLE_CLIENT_ID is not configured"
    ):
        prov.verify_provider_token("google", token)


def test_google_mock_still_works_in_dev(google_setup):
    result = prov.verify_provider_token("google", "mock:dev-google")
    assert result == {"provider": "google", "subject": "dev-google"}


def test_google_mock_rejected_in_production(monkeypatch, google_setup):
    monkeypatch.setenv("SAJU_ENV", "production")
    with pytest.raises(prov.ProviderTokenError, match="production"):
        prov.verify_provider_token("google", "mock:dev-google")
