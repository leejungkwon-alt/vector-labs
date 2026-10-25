"""
소셜 identity provider 토큰 검증.

인터페이스:
    verify_provider_token(provider: str, token: str) -> dict
        성공: {"provider": str, "subject": str}
        실패: ProviderTokenError (API 레이어에서 400 매핑)

모드:
  - 개발/스테이징 (SAJU_ENV != production): 'mock:<subject>' 허용
  - 프로덕션: 실제 OIDC ID 토큰 검증 (Apple / Google / Kakao)

1-B(이 파일): dispatch 구조 + mock 경로 보존 + verifier 스텁 + JWKS 캐시 스캐폴드
1-C: Apple 실제 검증 (_verify_apple)
1-D: Google 실제 검증 (_verify_google)
1-E: Kakao 토큰 조회 API (_verify_kakao)
"""

import os
import time

import httpx
import jwt

SUPPORTED_PROVIDERS = ("apple", "google", "kakao")
MOCK_PREFIX = "mock:"
_MAX_SUBJECT_LEN = 256

_JWKS_CACHE: dict = {}
_JWKS_TTL_SECONDS = 3600
_HTTP_TIMEOUT_SECONDS = 5.0

_JWKS_URLS = {
    "apple": "https://appleid.apple.com/auth/keys",
    "google": "https://www.googleapis.com/oauth2/v3/certs",
}

_ISSUERS = {
    "apple": "https://appleid.apple.com",
    "google": "https://accounts.google.com",
}

_AUDIENCE_ENV = {
    "apple": "SAJU_APPLE_CLIENT_ID",
    "google": "SAJU_GOOGLE_CLIENT_ID",
}


class ProviderTokenError(ValueError):
    """provider 또는 토큰이 유효하지 않음."""


def _is_production() -> bool:
    return os.environ.get("SAJU_ENV", "").lower() == "production"


def _env(name: str):
    v = os.environ.get(name)
    if v is None:
        return None
    v = v.strip()
    return v or None


def _verify_mock(provider: str, token: str) -> dict:
    if _is_production():
        raise ProviderTokenError(
            "Mock provider tokens are not allowed in production. "
            "Real OIDC verification must be implemented before deploying."
        )
    subject = token[len(MOCK_PREFIX):].strip()
    if not subject:
        raise ProviderTokenError("Empty subject after 'mock:'.")
    if len(subject) > _MAX_SUBJECT_LEN:
        raise ProviderTokenError("Subject too long.")
    return {"provider": provider, "subject": subject}


def _fetch_jwks(provider: str) -> dict:
    now = time.time()
    cached = _JWKS_CACHE.get(provider)
    if cached and now - cached[0] < _JWKS_TTL_SECONDS:
        return cached[1]
    url = _JWKS_URLS[provider]
    try:
        resp = httpx.get(url, timeout=_HTTP_TIMEOUT_SECONDS)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        raise ProviderTokenError(
            f"Failed to fetch JWKS for {provider}: {exc}"
        ) from exc
    keys = {}
    for jwk in payload.get("keys", []):
        kid = jwk.get("kid")
        if not kid:
            continue
        try:
            keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
        except Exception:
            continue
    if not keys:
        raise ProviderTokenError(f"Empty or invalid JWKS for {provider}.")
    _JWKS_CACHE[provider] = (now, keys)
    return keys


def _decode_oidc_token(provider: str, token: str, *, verify_aud: bool = True) -> dict:
    """ID 토큰 서명/issuer/audience/exp 검증 후 claims 반환."""
    # 1. 헤더 파싱 먼저 — malformed 토큰은 네트워크 없이 fail-fast
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise ProviderTokenError(f"Malformed {provider} token: {exc}") from exc

    # 2. audience(env) 확인 — 미설정이면 fail-closed
    aud_env = _AUDIENCE_ENV.get(provider)
    audience = _env(aud_env) if aud_env else None
    if verify_aud and not audience:
        raise ProviderTokenError(
            f"{aud_env} is not configured on the server; "
            f"cannot verify {provider} ID tokens."
        )

    # 3. JWKS fetch + kid lookup (kid 로테이션 시 캐시 1회 무효화 후 재시도)
    keys = _fetch_jwks(provider)
    kid = header.get("kid")
    if not kid or kid not in keys:
        _JWKS_CACHE.pop(provider, None)
        keys = _fetch_jwks(provider)
        if not kid or kid not in keys:
            raise ProviderTokenError(f"Unknown signing key id for {provider} token.")

    # 4. 서명 + 표준 클레임 검증
    options = {"require": ["exp", "iat", "iss", "aud", "sub"]}
    if not verify_aud:
        options["verify_aud"] = False

    try:
        claims = jwt.decode(
            token, key=keys[kid], algorithms=["RS256"],
            audience=audience if verify_aud else None,
            issuer=_ISSUERS[provider], options=options,
        )
    except jwt.PyJWTError as exc:
        raise ProviderTokenError(f"Invalid {provider} ID token: {exc}") from exc

    if not claims.get("sub"):
        raise ProviderTokenError(f"{provider} token missing 'sub'.")
    return claims



def _verify_apple(token: str) -> dict:
    claims = _decode_oidc_token("apple", token)
    return {"provider": "apple", "subject": claims["sub"]}



def _verify_google(token: str) -> dict:
    raise ProviderTokenError(
        "Google OIDC verifier not configured yet. "
        "Use 'mock:<subject>' in non-production, or configure "
        "SAJU_GOOGLE_CLIENT_ID and complete step 1-D."
    )


def _verify_kakao(token: str) -> dict:
    raise ProviderTokenError(
        "Kakao verifier not configured yet. "
        "Use 'mock:<subject>' in non-production, or configure "
        "SAJU_KAKAO_APP_KEY and complete step 1-E."
    )


_VERIFIERS: dict = {
    "apple": _verify_apple,
    "google": _verify_google,
    "kakao": _verify_kakao,
}


def verify_provider_token(provider: str, token: str) -> dict:
    if not isinstance(provider, str):
        raise ProviderTokenError("provider must be a string")
    p = provider.lower().strip()
    if p not in SUPPORTED_PROVIDERS:
        raise ProviderTokenError(
            f"Unsupported provider: {provider!r}. "
            f"Supported: {SUPPORTED_PROVIDERS}"
        )
    if not isinstance(token, str) or not token:
        raise ProviderTokenError(
            "provider_token must be a non-empty string. "
            "Use 'mock:<subject>' in dev or a real OIDC ID token."
        )
    if token.startswith(MOCK_PREFIX):
        return _verify_mock(p, token)
    return _VERIFIERS[p](token)
