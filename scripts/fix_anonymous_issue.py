# scripts/fix_anonymous_issue.py
from pathlib import Path
import sys
import re

# ==========================================
# 1. 백엔드 repository.py에 유저 등급 업데이트 함수 추가
# ==========================================
repo_path = Path("app/auth/repository.py")
if repo_path.exists():
    src = repo_path.read_text(encoding="utf-8")
    if "def set_user_not_anonymous" not in src:
        # create_anonymous_user 함수 바로 아래에 추가
        old_func = '    def get_user(self, user_id: str) -> Optional[dict]:\n        return self._one("SELECT * FROM users WHERE id = ?", (user_id,))'
        new_func = '''    def set_user_not_anonymous(self, user_id: str) -> None:
        self._run("UPDATE users SET is_anonymous = 0 WHERE id = ?", (user_id,))

    def get_user(self, user_id: str) -> Optional[dict]:
        return self._one("SELECT * FROM users WHERE id = ?", (user_id,))'''
        
        if old_func in src:
            src = src.replace(old_func, new_func, 1)
            repo_path.write_text(src, encoding="utf-8")
            print("✅ repository.py에 set_user_not_anonymous 함수 추가 완료")

# ==========================================
# 2. 백엔드 router.py의 login_telegram 함수 수정
# ==========================================
router_path = Path("app/auth/router.py")
if router_path.exists():
    src = router_path.read_text(encoding="utf-8")
    
    # 텔레그램 로그인 시 익명 해제 로직 추가
    old_login = '''    if not user:
        user = repo.create_anonymous_user()
        repo.upsert_telegram_subscriber(tg_id, user["id"], payload.lang or "ko")'''
    
    new_login = '''    if not user:
        user = repo.create_anonymous_user()
        repo.upsert_telegram_subscriber(tg_id, user["id"], payload.lang or "ko")
    
    # 텔레그램 로그인을 했으므로 익명 상태 해제
    if user.get("is_anonymous"):
        repo.set_user_not_anonymous(user["id"])
        user = repo.get_user(user["id"]) # 최신 유저 정보 다시 가져오기'''
    
    if old_login in src:
        src = src.replace(old_login, new_login, 1)
        router_path.write_text(src, encoding="utf-8")
        print("✅ router.py의 login_telegram 함수 수정 완료")

# ==========================================
# 3. 프론트엔드 settings.tsx 방어 코드 추가 (!isTgEnv)
# ==========================================
settings_path = Path("frontend/app/(tabs)/settings.tsx")
if settings_path.exists():
    src = settings_path.read_text(encoding="utf-8")
    
    old_ui = '{user?.is_anonymous && ('
    new_ui = '{user?.is_anonymous && !isTgEnv && ('
    
    if old_ui in src and '!isTgEnv' not in src:
        src = src.replace(old_ui, new_ui, 1)
        settings_path.write_text(src, encoding="utf-8")
        print("✅ settings.tsx에 텔레그램 환경 시 연동 버튼 숨김 방어 코드 추가 완료")