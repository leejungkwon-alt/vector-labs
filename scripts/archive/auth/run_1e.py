#!/usr/bin/env python3
"""1-E: Kakao /v2/user/me 토큰 조회 검증."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _common import ROOT, run  # noqa: E402

sys.path.insert(0, str(ROOT))


NEW_VERIFY_KAKAO = '''def _verify_kakao(token: str) -> dict:
    # 정책적 fail-closed: 카카오 콘솔/서버 env 미설정이면 어떤 토큰도 수용 안 함.
    # (실제 /v2/user/me 호출에는 app key가 필요 없지만,
    #  운영 환경 셋업 의무를 강제하기 위해 요구.)
    if not _env("SAJU_KAKAO_APP_KEY"):
        raise ProviderTokenError(
            "SAJU_KAKAO_APP_KEY is not configured on the server; "
            "cannot verify Kakao tokens."
        )

    # Kakao /v2/user/me: 사용자 access token으로 프로필 조회.
    # Kakao user id는 앱별 스코프이므로 그대로 subject로 사용.
    try:
        resp = httpx.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=_HTTP_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        raise ProviderTokenError(
            f"Kakao API request failed: {exc}"
        ) from exc

    if resp.status_code in (401, 403):
        raise ProviderTokenError("Invalid Kakao access token.")
    if resp.status_code != 200:
        raise ProviderTokenError(
            f"Kakao API returned status {resp.status_code}."
        )

    try:
        payload = resp.json()
    except ValueError as exc:
        raise ProviderTokenError(
            "Kakao API returned non-JSON response."
        ) from exc

    kid = payload.get("id") if isinstance(payload, dict) else None
    if kid is None:
        raise ProviderTokenError("Kakao API response missing 'id'.")

    subject = str(kid).strip()
    if not subject:
        raise ProviderTokenError("Kakao returned empty user id.")
    if len(subject) > _MAX_SUBJECT_LEN:
        raise ProviderTokenError("Kakao user id too long.")

    return {"provider": "kakao", "subject": subject}'''


def _replace_function(src: str, fn_name: str, new_body: str) -> str:
    """`def <fn_name>(` 부터 첫 `\\n\\n\\n` 직전까지 교체.

    1-B 파일의 함수 구분자는 정확히 빈 두 줄(\\n\\n\\n)이므로 이에 앵커.
    `_VERIFIERS = {` 같은 dict 리터럴을 실수로 삼키지 않도록 `\\ndef ` 대신 사용.
    """
    pattern = re.compile(
        r"^def " + re.escape(fn_name) + r"\(.*?(?=\n\n\n|\Z)",
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

    if "kapi.kakao.com/v2/user/me" in src:
        print("ℹ️  _verify_kakao 이미 구현됨 — skip")
        return

    src = _replace_function(src, "_verify_kakao", NEW_VERIFY_KAKAO)
    p.write_text(src, encoding="utf-8")
    print("✅ _verify_kakao 구현 완료 (/v2/user/me)")


KAKAO_TESTS_BLOCK = '''

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
'''


def extend_oidc_test() -> None:
    p = ROOT / "tests/test_oidc_verification.py"
    if not p.exists():
        raise SystemExit(
            "❌ tests/test_oidc_verification.py 없음. 1-C 먼저."
        )
    src = p.read_text(encoding="utf-8")
    if "kakao_env" in src:
        print("ℹ️  Kakao 테스트 이미 존재 — skip")
        return
    p.write_text(src.rstrip() + KAKAO_TESTS_BLOCK, encoding="utf-8")
    print("✅ tests/test_oidc_verification.py: Kakao 10 테스트 추가")


def main() -> int:
    print("[1-E] Kakao /v2/user/me 토큰 조회 검증")
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
    print("🎉 1-E 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())