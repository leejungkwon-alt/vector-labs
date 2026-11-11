import os
import re
import shutil
import subprocess

print("🚀 계정 통합 로직의 Import 에러를 수정하고 안전하게 재배포합니다...\n")

router_path = "app/auth/router.py"
if os.path.exists(router_path):
    shutil.copy2(router_path, router_path + ".bak")
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. get_current_user_optional 임포트 추가
    if "from app.auth.dependencies import get_current_user_optional" not in content:
        # 기존 dependencies 임포트 확인
        if "from app.auth.dependencies import" in content:
            content = re.sub(r"from app\.auth\.dependencies import ([^\n]+)", r"from app.auth.dependencies import \1, get_current_user_optional", content)
        else:
            content = content.replace("from fastapi import APIRouter", "from app.auth.dependencies import get_current_user_optional\nfrom fastapi import APIRouter")

    # 2. login_telegram 함수를 get_current_user_optional을 쓰도록 안전하게 교체
    old_func_pattern = r"@router\.post\(\"/login/telegram\".*?\n(?:.*?\n)*?    return \{[\s\S]*?\n    \}"
    
    new_func = '''@router.post("/login/telegram", response_model=TokenResponse)
def login_telegram(
    payload: TelegramInitData, 
    current_user: dict | None = Depends(get_current_user_optional)
):
    from app.auth.jwt_utils import encode_token, ttl_seconds
    from app.auth.repository import get_repository
    
    tg_id = _verified_telegram_id(payload)
    repo = get_repository()
    
    # 1. 텔레그램 ID로 기존 유저 찾기
    user = repo.get_user_by_telegram_id(tg_id)
    
    # 2. 분기 처리
    if user:
        # 이미 텔레그램 연동된 계정이 있음 (정상 로그인)
        pass
    elif current_user:
        # 텔레그램 연동은 안 되어 있지만, 현재 로그인된(게스트/프리미엄) 계정이 있음 -> 이 계정에 연동!
        user = current_user
        repo.upsert_telegram_subscriber(tg_id, user["id"], payload.lang or "ko")
        repo.set_user_not_anonymous(user["id"])
    else:
        # 텔레그램도 없고 현재 세션도 없음 -> 완전 신규 생성
        user = repo.create_anonymous_user()
        repo.upsert_telegram_subscriber(tg_id, user["id"], payload.lang or "ko")
        repo.set_user_not_anonymous(user["id"])
        
    # 최신 정보 갱신
    user = repo.get_user(user["id"])
    token = encode_token(user["id"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ttl_seconds(),
        "user": _user_public(user),
    }'''

    content = re.sub(old_func_pattern, new_func, content, flags=re.DOTALL)

    with open(router_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ router.py 수정 완료 (의존성 주입 방식으로 안전하게 변경)")

# 백엔드 배포
print("\n2. 백엔드 배포 시작...")
try:
    subprocess.run(".\\deploy.ps1", shell=True, check=True)
    print("\n🎉 배포 완료! 이제 텔레그램 로그인을 다시 시도해 보세요.")
except subprocess.CalledProcessError:
    print("\n⚠️ 배포 실패! 에러를 확인해 주세요.")