"""1-H: add regression tests — mock:<subject> rejected when SAJU_ENV=production."""
from pathlib import Path
import sys

TARGET = Path("tests/test_oidc_verification.py")

APPEND = '''

def test_mock_token_rejected_in_production(monkeypatch):
    """SAJU_ENV=production 이면 mock:<subject> 토큰이 거부되어야 한다."""
    import app.auth.providers as prov

    monkeypatch.setenv("SAJU_ENV", "production")
    with pytest.raises(
        prov.ProviderTokenError, match="not allowed in production"
    ):
        prov.verify_provider_token("apple", "mock:alice")


def test_mock_token_accepted_in_dev(monkeypatch):
    """SAJU_ENV != production 이면 mock:<subject> 가 정상 통과해야 한다."""
    import app.auth.providers as prov

    monkeypatch.delenv("SAJU_ENV", raising=False)
    out = prov.verify_provider_token("google", "mock:bob")
    assert out == {"provider": "google", "subject": "bob"}
'''


def main() -> int:
    if not TARGET.is_file():
        print(f"[fail] not found: {TARGET}", file=sys.stderr)
        return 1
    src = TARGET.read_text(encoding="utf-8")
    if "test_mock_token_rejected_in_production" in src:
        print("[skip] already present")
        return 0
    if "import pytest" not in src:
        print("[fail] pytest import missing in target", file=sys.stderr)
        return 1
    # prov 관련 import 는 함수 내부 local import 로 넣으므로 파일 상단 검사 불필요
    TARGET.write_text(src.rstrip() + APPEND, encoding="utf-8")
    print(f"[ok] appended 2 tests to {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())