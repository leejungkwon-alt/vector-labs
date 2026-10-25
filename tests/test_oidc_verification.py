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

# =============================================================================
# Kakao (1-E: /v2/user/me 토큰 조회)
# =============================================================================

class _FakeKakaoResp:
    def __init__(self, status_code, payload=None, bad_json=False):
        self.status_code = status_code
        self._payload = payload
        self._bad_json = bad_json

    def json(self):
        if self._bad_json:
            raise ValueError("not json")
        return self._payload


def _fake_kakao_get(resp):
    def fake_get(url, headers=None, timeout=None):
        return resp
    return fake_get


@pytest.fixture
def kakao_env(monkeypatch):
    monkeypatch.setenv("SAJU_KAKAO_APP_KEY", "test-kakao-key")
    monkeypatch.delenv("SAJU_ENV", raising=False)
    yield


def test_kakao_valid(monkeypatch, kakao_env):
    resp = _FakeKakaoResp(200, {"id": 123456789})
    monkeypatch.setattr(prov.httpx, "get", _fake_kakao_get(resp))
    result = prov.verify_provider_token("kakao", "kakao-access-token-xyz")
    assert result == {"provider": "kakao", "subject": "123456789"}


def test_kakao_unauthorized(monkeypatch, kakao_env):
    monkeypatch.setattr(prov.httpx, "get", _fake_kakao_get(_FakeKakaoResp(401)))
    with pytest.raises(prov.ProviderTokenError, match="Invalid Kakao"):
        prov.verify_provider_token("kakao", "bad-token")


def test_kakao_forbidden(monkeypatch, kakao_env):
    monkeypatch.setattr(prov.httpx, "get", _fake_kakao_get(_FakeKakaoResp(403)))
    with pytest.raises(prov.ProviderTokenError, match="Invalid Kakao"):
        prov.verify_provider_token("kakao", "bad-token")


def test_kakao_server_error(monkeypatch, kakao_env):
    monkeypatch.setattr(prov.httpx, "get", _fake_kakao_get(_FakeKakaoResp(500)))
    with pytest.raises(prov.ProviderTokenError, match="status 500"):
        prov.verify_provider_token("kakao", "some-token")


def test_kakao_non_json(monkeypatch, kakao_env):
    monkeypatch.setattr(
        prov.httpx, "get", _fake_kakao_get(_FakeKakaoResp(200, bad_json=True))
    )
    with pytest.raises(prov.ProviderTokenError, match="non-JSON"):
        prov.verify_provider_token("kakao", "some-token")


def test_kakao_missing_id(monkeypatch, kakao_env):
    monkeypatch.setattr(
        prov.httpx, "get", _fake_kakao_get(_FakeKakaoResp(200, {"nickname": "x"}))
    )
    with pytest.raises(prov.ProviderTokenError, match="missing 'id'"):
        prov.verify_provider_token("kakao", "some-token")


def test_kakao_network_error(monkeypatch, kakao_env):
    import httpx as real_httpx

    def fake_get(url, headers=None, timeout=None):
        raise real_httpx.ConnectError("boom")

    monkeypatch.setattr(prov.httpx, "get", fake_get)
    with pytest.raises(prov.ProviderTokenError, match="request failed"):
        prov.verify_provider_token("kakao", "some-token")


def test_kakao_missing_env(monkeypatch, kakao_env):
    monkeypatch.delenv("SAJU_KAKAO_APP_KEY", raising=False)

    def fake_get(*a, **k):
        raise AssertionError("should not call HTTP when env missing")

    monkeypatch.setattr(prov.httpx, "get", fake_get)
    with pytest.raises(
        prov.ProviderTokenError, match="SAJU_KAKAO_APP_KEY is not configured"
    ):
        prov.verify_provider_token("kakao", "some-token")


def test_kakao_mock_still_works_in_dev(kakao_env):
    result = prov.verify_provider_token("kakao", "mock:dev-kakao")
    assert result == {"provider": "kakao", "subject": "dev-kakao"}


def test_kakao_mock_rejected_in_production(monkeypatch, kakao_env):
    monkeypatch.setenv("SAJU_ENV", "production")
    with pytest.raises(prov.ProviderTokenError, match="production"):
        prov.verify_provider_token("kakao", "mock:dev-kakao")
