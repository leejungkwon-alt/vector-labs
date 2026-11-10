# scripts/fix_telegram_login_backend.py
from pathlib import Path
import sys

PATH = Path("app/auth/router.py")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 기존 login_telegram 함수 전체를 찾아서 새로운 코드로 교체
import re
pattern = r'(@router\.post\("/login/telegram"\)[\s\S]*?)(?=@router\.post|\Z)'
match = re.search(pattern, src)

if not match:
    print("❌ 텔레그램 로그인 함수를 찾을 수 없습니다."); sys.exit(1)

new_func = '''@router.post("/login/telegram")
def login_telegram(payload: TelegramInitData):
    from app.auth.jwt_utils import encode_token, ttl_seconds
    from app.auth.repository import get_repository
    
    tg_id = _verified_telegram_id(payload)
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
    
    # 3. JWT 토큰 발급 (기존 프로젝트 방식)
    token = encode_token(user["id"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ttl_seconds(),
        "user": _user_public(user),
    }
'''

src = src.replace(match.group(1), new_func)
PATH.write_text(src, encoding="utf-8")
print("✅ 백엔드 login_telegram 함수 수정 완료")