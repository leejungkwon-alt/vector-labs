# -*- coding: utf-8 -*-
"""
SAJU_ENV fail-closed 패치 (v2: 파일이 덤프 이후 바뀌어 있어도 적용되도록 표현식 단위로 치환).

목적: SAJU_ENV 가 빠지거나 오타여도 mock 영수증 / mock 소셜 토큰 / 개발용 JWT 기본 키가
      열리지 않게 한다. SAJU_ENV 가 development/dev/local/test/testing 중 하나일 때만
      "개발 모드"이고, 그 외(미설정 포함)는 전부 production 으로 취급한다.

사용법 (프로젝트 루트에서):
    python apply_env_failclosed.py            # 적용 (v1 을 이미 실행했어도 안전하게 이어서 적용)
    python apply_env_failclosed.py --check    # 파일을 바꾸지 않고 상태/남은 참조만 확인

마지막의 "남은 SAJU_ENV 직접 참조" 목록에 production 비교가 보이면 그 줄은 수동 수정이 필요하다.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECK_ONLY = "--check" in sys.argv
IMPORT_LINE = "from app.ops.env import is_production"


def read(path):
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    return raw.replace("\r\n", "\n"), crlf


def write(path, text, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))


def create(rel, content):
    path = ROOT / rel
    if path.exists():
        print(f"  = {rel} (이미 존재, 건너뜀)")
        return True
    if not CHECK_ONLY:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8"))
    print(f"  + {rel} (새 파일)")
    return True


ENV_PY = '''# app/ops/env.py
"""
실행 환경 판정 (fail-closed).

SAJU_ENV 가 development / dev / local / test / testing 중 하나로 "명시"되어 있을 때만
개발 모드다. 미설정, 빈 문자열, 오타, staging 등 그 외 모든 값은 production 으로 취급한다.
(이전에는 SAJU_ENV == "production" 일 때만 보호가 켜져서, 환경변수가 빠지면
 mock 영수증/토큰과 개발용 JWT 기본 키가 열렸다.)
"""
import logging
import os

_NON_PROD_ENVS = frozenset({"development", "dev", "local", "test", "testing"})


def current_env() -> str:
    return os.environ.get("SAJU_ENV", "").strip().lower()


def is_production() -> bool:
    """명시적으로 개발 계열이 아니면 모두 production."""
    return current_env() not in _NON_PROD_ENVS


def validate_startup() -> None:
    """
    프로세스 시작 시 1회 호출. production 으로 판정되면 필수 설정을 즉시 검사한다.
    (Cloud Run 에서는 시작 실패 revision 이 트래픽을 받지 않아 이전 revision 이 유지된다.)
    """
    log = logging.getLogger("saju.security")
    if not is_production():
        log.warning(
            "SAJU_ENV=%r: non-production mode "
            "(mock tokens/receipts and the dev JWT secret are allowed).",
            current_env(),
        )
        return
    if not current_env():
        log.warning("SAJU_ENV is not set; treating as production (fail-closed).")
    from app.auth.jwt_utils import _secret

    _secret()  # 시크릿 누락 / 32자 미만이면 여기서 RuntimeError
'''

TEST_PY = '''# tests/test_env_failclosed.py
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
'''

# os.environ.get("SAJU_ENV", "") / os.getenv('SAJU_ENV') + .strip()/.lower() 조합 + ==/!= "production"
_ENV_READ = r'''(?:os\.environ\.get|os\.getenv)\(\s*["']SAJU_ENV["'][^)]*\)(?:\s*\.\s*(?:strip|lower)\(\s*\))*'''
EQ_PROD = re.compile(_ENV_READ + r'''\s*==\s*["']production["']''', re.S)
NE_PROD = re.compile(_ENV_READ + r'''\s*!=\s*["']production["']''', re.S)

ok = True
changed_any = False


def patch_file(rel, extra=None):
    """표현식 단위 치환 + (필요하면) 모듈 상단 import 삽입. 반환: 이 파일에 production 판정이 남았는지."""
    global ok, changed_any
    path = ROOT / rel
    if not path.exists():
        print(f"  ! {rel}: 파일이 없습니다.")
        ok = False
        return
    text, crlf = read(path)
    orig = text
    n_eq = len(EQ_PROD.findall(text))
    n_ne = len(NE_PROD.findall(text))
    text = EQ_PROD.sub("is_production()", text)
    text = NE_PROD.sub("(not is_production())", text)

    if extra:
        text = extra(text)

    needs_import = ("is_production()" in text) and (IMPORT_LINE not in text)
    if needs_import:
        m = re.search(r"^import os[ \t]*$", text, flags=re.M) or re.search(
            r"^(?:import|from)\s+\S.*$", text, flags=re.M
        )
        if not m:
            print(f"  ! {rel}: import 삽입 위치를 찾지 못했습니다. 파일 상단에 '{IMPORT_LINE}' 를 직접 추가하세요.")
            ok = False
        else:
            text = text[: m.end()] + "\n" + IMPORT_LINE + text[m.end():]

    if text == orig:
        print(f"  = {rel} (변경 없음 / 이미 적용됨)")
        return
    if not CHECK_ONLY:
        write(path, text, crlf)
    changed_any = True
    print(f"  + {rel} (production 비교 {n_eq + n_ne}곳 교체)")


def main_extra(text):
    """main.py: validate_startup 임포트 + 호출."""
    if "validate_startup" in text:
        return text
    # 임포트: is_production import 가 이미 있어도 validate_startup 만 따로 추가
    m = re.search(r"^from app\.ops\.middleware import .*$", text, flags=re.M) or re.search(
        r"^(?:import|from)\s+\S.*$", text, flags=re.M
    )
    if m:
        text = text[: m.end()] + "\nfrom app.ops.env import validate_startup" + text[m.end():]
    call = re.search(r"^configure_logging\(\)[ \t]*$", text, flags=re.M)
    if call:
        text = (
            text[: call.end()]
            + "\nvalidate_startup()  # SAJU_ENV 가 개발 계열이 아니면(미설정 포함) JWT 시크릿 등을 즉시 검사"
            + text[call.end():]
        )
    else:
        print("  ! app/main.py: configure_logging() 호출을 찾지 못했습니다. 'validate_startup()' 호출을 직접 추가하세요.")
    return text


print("== 새 파일")
create("app/ops/env.py", ENV_PY)
create("tests/test_env_failclosed.py", TEST_PY)

print("== 코드 수정")
for rel in (
    "app/auth/jwt_utils.py",
    "app/auth/providers.py",
    "app/auth/repository.py",
    "app/services/visual_generator.py",
    "app/services/iap.py",
):
    patch_file(rel)
patch_file("app/main.py", extra=main_extra)

print("== 테스트 환경 고정")
conf = ROOT / "conftest.py"
text, crlf = read(conf)
if 'os.environ["SAJU_ENV"] = "development"' in text:
    print("  = conftest.py (이미 적용됨)")
else:
    m = re.search(r'^os\.environ\["SAJU_RATE_LIMIT_MAX"\][^\n]*$', text, flags=re.M)
    if m:
        ins = (
            '# 테스트는 항상 개발 모드로 고정 (SAJU_ENV 미설정은 이제 production 으로 취급됨)\n'
            'os.environ["SAJU_ENV"] = "development"\n'
        )
        text = text[: m.start()] + ins + text[m.start():]
        if not CHECK_ONLY:
            write(conf, text, crlf)
        print("  + conftest.py")
    else:
        print('  ! conftest.py: 위치를 찾지 못했습니다. os.environ["SAJU_ENV"] = "development" 를 직접 추가하세요.')
        ok = False

pat = re.compile(r'monkeypatch\.delenv\(\s*["\']SAJU_ENV["\']\s*,\s*raising\s*=\s*False\s*\)')
changed = 0
for path in sorted((ROOT / "tests").glob("*.py")):
    if path.name == "test_env_failclosed.py":
        continue
    text, crlf = read(path)
    new, n = pat.subn('monkeypatch.setenv("SAJU_ENV", "development")', text)
    if n:
        changed += n
        if not CHECK_ONLY:
            write(path, new, crlf)
        print(f"  + tests/{path.name} ({n}곳)")
if not changed:
    print("  = 교체할 delenv 없음(이미 적용됨)")

print("== 남은 SAJU_ENV 직접 참조 (app/ 아래, app/ops/env.py 제외)")
risky = 0
for path in sorted((ROOT / "app").rglob("*.py")):
    if path.name == "env.py" and path.parent.name == "ops":
        continue
    text, _ = read(path)
    for i, line in enumerate(text.split("\n"), 1):
        if "SAJU_ENV" in line:
            s = line.strip()
            code = line.split("#")[0]
            is_doc = (
                "SAJU_ENV" not in code            # 주석에만 등장
                or '"""' in s or s.startswith(("-", "*"))  # docstring / 목록 설명
                or "SAJU_ENV=" in s               # 문구/메시지
            )
            flag = "  " if is_doc else "!!"
            if flag == "!!":
                risky += 1
            print(f"  {flag} {path.relative_to(ROOT)}:{i}: {s[:120]}")
if risky:
    print(f"  → '!!' 표시 {risky}곳은 production 판정을 직접 하고 있을 수 있습니다. is_production() 으로 바꾸세요.")

print()
print("완료" if ok else "일부 항목은 수동 확인이 필요합니다. 위의 '!' 줄을 확인하세요.")
print("다음: python -m pytest -q")