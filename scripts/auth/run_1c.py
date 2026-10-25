#!/usr/bin/env python3
"""1-C: Apple JWKS 실제 검증 (함수 전체 교체, robust)."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _common import ROOT, run  # noqa: E402

sys.path.insert(0, str(ROOT))


NEW_VERIFY_APPLE = '''def _verify_apple(token: str) -> dict:
    claims = _decode_oidc_token("apple", token)
    return {"provider": "apple", "subject": claims["sub"]}'''

NEW_DECODE_FN = '''def _decode_oidc_token(provider: str, token: str, *, verify_aud: bool = True) -> dict:
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
    return claims'''


def _replace_function(src: str, fn_name: str, new_body: str) -> str:
    """파일에서 `def <fn_name>(`부터 다음 `\\ndef ` 직전까지를 new_body로 교체."""
    pattern = re.compile(
        r"^def " + re.escape(fn_name) + r"\(.*?(?=\ndef |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    m = pattern.search(src)
    if not m:
        # 디버그용 컨텍스트
        idx = src.find(f"def {fn_name}")
        raise RuntimeError(
            f"함수 '{fn_name}' 못 찾음 (find idx={idx}). "
            f"파일 앞 100자: {src[:100]!r}"
        )
    return src[:m.start()] + new_body.rstrip() + "\n\n\n" + src[m.end():]


def patch_providers() -> None:
    p = ROOT / "app/auth/providers.py"
    src = p.read_text(encoding="utf-8")
    changed = False

    if 'claims = _decode_oidc_token("apple", token)' in src:
        print("ℹ️  _verify_apple 이미 구현됨 — skip")
    else:
        try:
            src = _replace_function(src, "_verify_apple", NEW_VERIFY_APPLE)
            print("✅ _verify_apple 구현 완료")
            changed = True
        except RuntimeError as e:
            print(f"❌ {e}")
            raise

    if "헤더 파싱 먼저" in src:
        print("ℹ️  _decode_oidc_token 이미 재정렬됨 — skip")
    else:
        try:
            src = _replace_function(src, "_decode_oidc_token", NEW_DECODE_FN)
            print("✅ _decode_oidc_token 재정렬 (header → env → JWKS)")
            changed = True
        except RuntimeError as e:
            print(f"❌ {e}")
            raise

    if changed:
        p.write_text(src, encoding="utf-8")
        print("✅ providers.py 저장 완료")
    else:
        print("ℹ️  providers.py 변경 없음")


# test_social_link.py의 "mock:" assert 완화
OLD_TEST_INVALID = '''def test_link_invalid_token_format(fresh_auth):
    a = _anon()
    r = client.post(
        "/api/v1/auth/link/apple",
        headers=_h(a["access_token"]),
        json={"provider_token": "eyJhbGciOi.something.else"},
    )
    assert r.status_code == 400
    assert "mock:" in r.json()["detail"]'''

NEW_TEST_INVALID = '''def test_link_invalid_token_format(fresh_auth):
    a = _anon()
    r = client.post(
        "/api/v1/auth/link/apple",
        headers=_h(a["access_token"]),
        json={"provider_token": "eyJhbGciOi.something.else"},
    )
    assert r.status_code == 400
    # 1-C 이후: mock 이외 토큰은 Apple 검증기로 넘어가며
    # malformed 또는 env 미설정으로 fail-closed → 400.
    assert r.json()["detail"]'''


def patch_social_link_test() -> None:
    p = ROOT / "tests/test_social_link.py"
    src = p.read_text(encoding="utf-8")
    if "1-C 이후" in src:
        print("ℹ️  test_social_link.py 이미 갱신됨 — skip")
        return
    if OLD_TEST_INVALID not in src:
        i = src.find("def test_link_invalid_token_format")
        print("⚠️  test_link_invalid_token_format 블록 매칭 실패")
        print("   현재 블록 (repr):")
        print(repr(src[i:i + 400]))
        print("   → 매칭 실패해도 진행 (pytest가 있으면 재확인)")
        return
    src = src.replace(OLD_TEST_INVALID, NEW_TEST_INVALID, 1)
    p.write_text(src, encoding="utf-8")
    print("✅ test_social_link.py: 'mock:' assert → 400 + non-empty detail")


TEST_FILE = '''"""OIDC 실제 검증 유닛테스트 (Apple)."""
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
'''


def create_oidc_test() -> None:
    p = ROOT / "tests/test_oidc_verification.py"
    status = "갱신" if p.exists() else "생성"
    p.write_text(TEST_FILE, encoding="utf-8")
    print(f"✅ tests/test_oidc_verification.py {status}")


def main() -> int:
    print("[1-C] Apple JWKS 실제 검증")
    print("=" * 62)
    try:
        patch_providers()
        patch_social_link_test()
        create_oidc_test()
    except Exception as e:
        print(f"❌ 중단: {e}")
        return 1
    print("-" * 62)

    rc, out = run(
        [
            sys.executable, "-m", "pytest",
            "tests/test_oidc_verification.py",
            "tests/test_social_link.py",
            "-q",
        ],
        cwd=ROOT,
    )
    print(out[-3000:])
    if rc != 0:
        print("❌ 테스트 실패")
        return 1

    print("=" * 62)
    print("🎉 1-C 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())