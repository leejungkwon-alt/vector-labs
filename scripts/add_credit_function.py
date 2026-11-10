# scripts/add_credit_function.py
from pathlib import Path
import sys

PATH = Path("app/auth/repository.py")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

if "def add_onetime_credit" in src:
    print("⚠️ 이미 add_onetime_credit 함수가 존재합니다.")
    sys.exit(0)

# get_user 함수 근처에 추가
target = "    def get_user(self, user_id: str) -> Optional[dict]:"
new_func = '''    def add_onetime_credit(self, user_id: str) -> None:
        """일시불 결제 시 단품 이용권(크레딧) +1 증가"""
        # 크레딧 컬럼이 없으면 추가 (마이그레이션)
        try:
            self._run("ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0")
        except Exception:
            pass # 이미 컬럼이 있으면 무시
        self._run("UPDATE users SET onetime_credits = COALESCE(onetime_credits, 0) + 1 WHERE id = ?", (user_id,))

    def get_user(self, user_id: str) -> Optional[dict]:'''

if target in src:
    src = src.replace(target, new_func, 1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ repository.py에 add_onetime_credit 함수 추가 완료")
else:
    print("❌ 대상 위치를 찾지 못했습니다.")