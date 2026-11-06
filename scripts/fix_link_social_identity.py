# scripts/fix_link_social_identity.py
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
REPO_PATH = Path("app/auth/repository.py")

if not REPO_PATH.exists():
    print(f"❌ 파일을 찾을 수 없습니다: {REPO_PATH}")
    sys.exit(1)

txt = REPO_PATH.read_text(encoding="utf-8")
original = txt

# 1. email 매개변수에 기본값(None) 추가
txt = txt.replace(
    "self, user_id: str, provider: str, subject: str, email: str",
    "self, user_id: str, provider: str, subject: str, email: str | None = None"
)
print("✅ email 매개변수에 기본값(None) 추가")

# 2. UPDATE 쿼리에 email 저장 로직 추가
old_update = '''        try:
            self._run(
                "UPDATE users SET social_provider = ?, social_subject = ?, "
                "is_anonymous = 0 WHERE id = ?",
                (provider, subject, user_id),
            )'''
new_update = '''        try:
            if email:
                self._run(
                    "UPDATE users SET social_provider = ?, social_subject = ?, "
                    "is_anonymous = 0, email = ? WHERE id = ?",
                    (provider, subject, email, user_id),
                )
            else:
                self._run(
                    "UPDATE users SET social_provider = ?, social_subject = ?, "
                    "is_anonymous = 0 WHERE id = ?",
                    (provider, subject, user_id),
                )'''

if old_update in txt:
    txt = txt.replace(old_update, new_update, 1)
    print("✅ UPDATE 쿼리에 email 저장 로직 추가")
else:
    print("⚠️ UPDATE 쿼리 패턴을 찾지 못했습니다. 수동 확인 필요")

if txt == original:
    print("ℹ️ 변경 사항이 없습니다.")
    sys.exit(0)

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    sys.exit(0)

REPO_PATH.write_text(txt, encoding="utf-8")
print("🎉 repository.py 패치 완료")