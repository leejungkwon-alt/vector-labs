#!/usr/bin/env python3
"""1-B 적용 러너 (단일 파일)."""
import importlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _common import ROOT, append_env_example, run  # noqa: E402


NEW_PROVIDERS_PY = '''"""
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
    aud_env = _AUDIENCE_ENV.get(provider)
    audience = _env(aud_env) if aud_env else None
    if verify_aud and not audience:
        raise ProviderTokenError(
            f"{aud_env} is not configured on the server; "
            f"cannot verify {provider} ID tokens."
        )
    keys = _fetch_jwks(provider)
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise ProviderTokenError(f"Malformed {provider} token: {exc}") from exc
    kid = header.get("kid")
    if not kid or kid not in keys:
        _JWKS_CACHE.pop(provider, None)
        keys = _fetch_jwks(provider)
        if not kid or kid not in keys:
            raise ProviderTokenError(f"Unknown signing key id for {provider} token.")
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
    raise ProviderTokenError(
        "Apple OIDC verifier not configured yet. "
        "Use 'mock:<subject>' in non-production, or configure "
        "SAJU_APPLE_CLIENT_ID and complete step 1-C."
    )


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
'''


def _patch_requirements() -> None:
    req_path = ROOT / "requirements.txt"
    req = req_path.read_text(encoding="utf-8")
    changed = False
    if "pyjwt[crypto]" not in req:
        new_req, n = re.subn(
            r"^pyjwt(\[[^\]]*\])?[^\n]*$",
            "pyjwt[crypto]>=2.8.0",
            req, count=1, flags=re.MULTILINE,
        )
        if n == 0:
            new_req = req.rstrip() + "\npyjwt[crypto]>=2.8.0\n"
            print("  · pyjwt 라인 없음 → append")
        else:
            print("  · pyjwt → pyjwt[crypto]>=2.8.0")
        req, changed = new_req, True
    if not re.search(r"^cryptography([\[>=<\s]|$)", req, re.MULTILINE):
        req = req.rstrip() + "\ncryptography>=42.0.0\n"
        print("  · cryptography>=42.0.0 append")
        changed = True
    if changed:
        req_path.write_text(req, encoding="utf-8")
        print("✅ requirements.txt 갱신")
    else:
        print("ℹ️  requirements.txt 이미 최신")


def _patch_providers() -> None:
    p = ROOT / "app/auth/providers.py"
    existing = p.read_text(encoding="utf-8") if p.exists() else ""
    if "_VERIFIERS" in existing and "_verify_mock" in existing:
        print("ℹ️  providers.py 이미 리팩터됨 — skip")
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(NEW_PROVIDERS_PY, encoding="utf-8")
    print(f"✅ providers.py {'교체' if existing else '생성'}")


def _patch_env() -> None:
    append_env_example({
        "SAJU_APPLE_CLIENT_ID": "Apple Service ID (Apple Developer Console)",
        "SAJU_GOOGLE_CLIENT_ID": "Google OAuth 2.0 Client ID",
        "SAJU_KAKAO_APP_KEY": "Kakao REST API key",
    })
    print("✅ .env.example 3키 반영")


def _smoke() -> None:
    import app.auth.providers as prov
    importlib.reload(prov)
    r = prov.verify_provider_token("apple", "mock:smoke")
    assert r == {"provider": "apple", "subject": "smoke"}, r
    try:
        prov.verify_provider_token("apple", "eyJhbGciOi.xx.yy")
    except prov.ProviderTokenError as exc:
        assert "mock:" in str(exc), str(exc)
    else:
        raise AssertionError("real token이 스텁을 통과함")
    try:
        prov.verify_provider_token("facebook", "mock:x")
    except prov.ProviderTokenError as exc:
        assert "Unsupported provider" in str(exc), str(exc)
    else:
        raise AssertionError("unsupported provider가 통과함")
    print("✅ providers 스모크 통과")


def main() -> int:
    print("[1-B] providers.py 리팩터 + deps + env")
    print("=" * 62)
    _patch_requirements()
    _patch_providers()
    _patch_env()
    print("-" * 62)
    _smoke()
    print("-" * 62)
    rc, out = run(
        [sys.executable, "-m", "pytest", "tests/test_social_link.py", "-q"],
        cwd=ROOT,
    )
    print(out[-1500:])
    if rc != 0:
        print("❌ test_social_link.py 실패")
        return 1
    print("=" * 62)
    print("🎉 1-B 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())