# scripts/fix_account_merge.py
from pathlib import Path
import sys

# ==========================================
# 1. repository.py에 텔레그램 ID로 유저를 정확히 찾는 함수 추가
# ==========================================
repo_path = Path("app/auth/repository.py")
if not repo_path.exists():
    print("❌ repository.py 없음"); sys.exit(1)

src = repo_path.read_text(encoding="utf-8")

if "def get_user_by_telegram_id" not in src:
    # get_user 함수 근처에 추가
    target_func = "    def get_user(self, user_id: str) -> Optional[dict]:"
    new_func = '''    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[dict]:
        """텔레그램 ID로 유저 정보를 정확히 조회합니다 (계정 통합용)."""
        return self._one(
            "SELECT u.* FROM users u "
            "JOIN telegram_subscribers t ON u.id = t.user_id "
            "WHERE t.telegram_id = ?",
            (telegram_id,)
        )

    def get_user(self, user_id: str) -> Optional[dict]:'''
    
    if target_func in src:
        src = src.replace(target_func, new_func, 1)
        repo_path.write_text(src, encoding="utf-8")
        print("✅ repository.py에 get_user_by_telegram_id 함수 추가 완료")

# ==========================================
# 2. router.py의 login_telegram 함수 전면 수정
# ==========================================
router_path = Path("app/auth/router.py")
if not router_path.exists():
    print("❌ router.py 없음"); sys.exit(1)

src = router_path.read_text(encoding="utf-8")

old_login_logic = '''    tg_id = _verified_telegram_id(payload)
    repo = get_repository()
    
    # 1. 기존 텔레그램 구독자 목록에서 유저 찾기
    user = None
    try:
        subs = repo.list_telegram_subscribers()
        existing = next((s for s in subs if s["telegram_id"] == tg_id), None)
        if existing:
            user = repo.get_user_by_id(existing["user_id"])
    except Exception:
        pass
    
    # 2. 없으면 새 계정 생성
    if not user:
        user = repo.create_anonymous_user()
        repo.upsert_telegram_subscriber(tg_id, user["id"], payload.lang or "ko")
    
    # 텔레그램 로그인을 했으므로 익명 상태 해제
    if user.get("is_anonymous"):
        repo.set_user_not_anonymous(user["id"])
        user = repo.get_user(user["id"]) # 최신 유저 정보 다시 가져오기
    
    # 3. JWT 토큰 발급 (기존 프로젝트 방식)
    token = encode_token(user["id"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ttl_seconds(),
        "user": _user_public(user),
    }'''

new_login_logic = '''    tg_id = _verified_telegram_id(payload)
    repo = get_repository()
    
    # 1. 텔레그램 ID로 기존 유저가 있는지 1:1 매칭 (계정 통합 핵심)
    user = repo.get_user_by_telegram_id(tg_id)
    
    # 2. 없으면 새 계정 생성 및 구독자 등록
    if not user:
        user = repo.create_anonymous_user()
        repo.upsert_telegram_subscriber(tg_id, user["id"], payload.lang or "ko")
    
    # 3. 텔레그램 로그인이므로 익명 상태 해제
    if user.get("is_anonymous"):
        repo.set_user_not_anonymous(user["id"])
        user = repo.get_user(user["id"]) # 최신 정보 갱신
    
    # 4. JWT 토큰 발급
    token = encode_token(user["id"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ttl_seconds(),
        "user": _user_public(user),
    }'''

if old_login_logic in src:
    src = src.replace(old_login_logic, new_login_logic, 1)
    router_path.write_text(src, encoding="utf-8")
    print("✅ router.py의 login_telegram 로직 전면 수정 완료 (1:1 매칭)")
else:
    print("⚠️ login_telegram 로직 패턴을 찾지 못했습니다. 수동 확인 필요.")