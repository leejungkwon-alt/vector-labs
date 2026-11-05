# -*- coding: utf-8 -*-
"""
cleanup_project.py가 잘못 추가한 'staging' 환경을 원복합니다.
원래 설계대로 staging 은 production(fail-closed) 으로 취급되어야 합니다.

+ 보너스: JWT 개발용 기본 키가 32바이트 미만이라 나오는 경고도 함께 정리.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def revert_staging():
    path = ROOT / "app" / "ops" / "env.py"
    if not path.exists():
        print(f"❌ 파일 없음: {path}")
        return
    text = path.read_text(encoding="utf-8")

    old = '_NON_PROD_ENVS = frozenset({"development", "dev", "local", "test", "testing", "staging"})'
    new = '_NON_PROD_ENVS = frozenset({"development", "dev", "local", "test", "testing"})'

    if old in text:
        text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")
        print("✅ app/ops/env.py: 'staging' 제거 → 원래 fail-closed 설계로 복구")
    elif new in text:
        print("ℹ️ app/ops/env.py: 이미 원복된 상태 (staging 없음)")
    else:
        print("⚠️ app/ops/env.py: 예상한 패턴을 찾지 못했습니다. 수동 확인 필요")


def fix_dev_jwt_key_length():
    """개발용 JWT 기본 키를 32바이트 이상으로 늘려 InsecureKeyLengthWarning 제거."""
    path = ROOT / "app" / "auth" / "jwt_utils.py"
    if not path.exists():
        print(f"❌ 파일 없음: {path}")
        return
    text = path.read_text(encoding="utf-8")

    # 현재 개발용 기본 키 (29 bytes — 경고 원인)
    old = '_DEFAULT_SECRET = "dev-secret-key-for-local-only"'
    # 32 bytes 초과로 확장 (경고 해소)
    new = '_DEFAULT_SECRET = "dev-secret-key-for-local-only-do-not-use-in-prod"'

    if old in text:
        text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")
        print("✅ app/auth/jwt_utils.py: 개발용 JWT 기본 키를 32바이트 이상으로 확장 (경고 제거)")
    elif new in text:
        print("ℹ️ app/auth/jwt_utils.py: 이미 확장된 상태")
    else:
        print("⚠️ app/auth/jwt_utils.py: _DEFAULT_SECRET 패턴을 찾지 못했습니다")


if __name__ == "__main__":
    print("🚀 staging 원복 + JWT 기본 키 경고 정리...")
    revert_staging()
    fix_dev_jwt_key_length()
    print("🎉 완료. 다시 `python -m pytest -q` 실행해 주세요.")