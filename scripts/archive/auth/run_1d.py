#!/usr/bin/env python3
"""1-D: Google JWKS 실제 검증."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _common import ROOT, run  # noqa: E402

sys.path.insert(0, str(ROOT))


NEW_VERIFY_GOOGLE = '''def _verify_google(token: str) -> dict:
    claims = _decode_oidc_token("google", token)
    return {"provider": "google", "subject": claims["sub"]}'''


def _replace_function(src: str, fn_name: str, new_body: str) -> str:
    """파일에서 `def <fn_name>(`부터 다음 `\\ndef ` 직전까지를 new_body로 교체."""
    pattern = re.compile(
        r"^def " + re.escape(fn_name) + r"\(.*?(?=\ndef |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    m = pattern.search(src)
    if not m:
        idx = src.find(f"def {fn_name}")
        raise RuntimeError(
            f"함수 '{fn_name}' 못 찾음 (find idx={idx})."
        )
    return src[:m.start()] + new_body.rstrip() + "\n\n\n" + src[m.end():]


def patch_providers() -> None:
    p = ROOT / "app/auth/providers.py"
    src = p.read_text(encoding="utf-8")

    if 'claims = _decode_oidc_token("google", token)' in src:
        print("ℹ️  _verify_google 이미 구현됨 — skip")
        return

    src = _replace_function(src, "_verify_google", NEW_VERIFY_GOOGLE)
    p.write_text(src, encoding="utf-8")
    print("✅ _verify_google 구현 완료")


GOOGLE_TESTS_BLOCK = '''

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
'''


def extend_oidc_test() -> None:
    p = ROOT / "tests/test_oidc_verification.py"
    if not p.exists():
        raise SystemExit(
            "❌ tests/test_oidc_verification.py 없음. 1-C 먼저 실행하세요."
        )
    src = p.read_text(encoding="utf-8")
    if "google_setup" in src:
        print("ℹ️  Google 테스트 이미 존재 — skip")
        return
    p.write_text(src.rstrip() + GOOGLE_TESTS_BLOCK, encoding="utf-8")
    print("✅ tests/test_oidc_verification.py: Google 8 테스트 추가")


def main() -> int:
    print("[1-D] Google JWKS 실제 검증")
    print("=" * 62)
    try:
        patch_providers()
        extend_oidc_test()
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
    print("🎉 1-D 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())