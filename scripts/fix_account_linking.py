import os
import re
import shutil
import subprocess

print("🚀 계정 파편화 방지(텔레그램 계정 통합) 패치를 시작합니다...\n")

# 1. 백엔드: login_telegram 함수 수정 (기존 유저 정보 병합)
router_path = "app/auth/router.py"
if os.path.exists(router_path):
    shutil.copy2(router_path, router_path + ".bak")
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()

    # login_telegram 함수 전체 교체 (기존 토큰이 있으면 그 계정에 텔레그램 연동)
    old_func_pattern = r"@router.post\(\"/login/telegram\".*?\n(?:.*?\n)*?    return \{[\s\S]*?\n    \}"
    
    new_func = '''@router.post("/login/telegram", response_model=TokenResponse)
def login_telegram(payload: TelegramInitData, authorization: str | None = Header(default=None)):
    from app.auth.jwt_utils import encode_token, ttl_seconds
    from app.auth.repository import get_repository
    
    tg_id = _verified_telegram_id(payload)
    repo = get_repository()
    
    # 1. 텔레그램 ID로 기존 유저 찾기
    user = repo.get_user_by_telegram_id(tg_id)
    
    # 2. 기존 텔레그램 유저가 없다면, 현재 접속 중인(익명) 유저가 있는지 확인
    current_user = None
    token = _extract_bearer(authorization)
    if token:
        try:
            claims = decode_token(token)
            current_user = repo.get_user(claims.get("sub"))
        except Exception:
            pass

    # 3. 처리 분기
    if user:
        # 이미 텔레그램 연동된 계정이 있음 (정상 로그인)
        pass
    elif current_user:
        # 텔레그램 연동은 안 되어 있지만, 현재 게스트 세션이 있음 -> 이 계정에 텔레그램 연동!
        user = current_user
        repo.upsert_telegram_subscriber(tg_id, user["id"], payload.lang or "ko")
        repo.set_user_not_anonymous(user["id"])
    else:
        # 텔레그램도 없고 게스트도 없음 -> 완전 신규 생성
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
    
    # 필요한 임포트 추가
    if "from fastapi import Header" not in content:
        content = content.replace("from fastapi import APIRouter, Depends, HTTPException", "from fastapi import APIRouter, Depends, HTTPException, Header")

    with open(router_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 백엔드: 텔레그램 로그인 시 기존 계정 통합 로직 적용 완료")


# 2. 프론트엔드: loginWithTelegram 호출 시 현재 토큰 헤더에 포함
auth_store_path = "frontend/src/store/authStore.ts"
if os.path.exists(auth_store_path):
    shutil.copy2(auth_store_path, auth_store_path + ".bak")
    with open(auth_store_path, "r", encoding="utf-8") as f:
        content = f.read()

    # api.loginTelegram 함수에 토큰 전달
    content = content.replace(
        "const res = await api.loginTelegram(tg.initData);",
        "const currentToken = await storage.getItem(TOKEN_KEY);\n    const res = await api.loginTelegram(tg.initData, currentToken);"
    )
    with open(auth_store_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 프론트엔드: loginWithTelegram 시 현재 토큰 전달하도록 수정 완료")

# 3. 프론트엔드: api/client.ts 수정
client_path = "frontend/src/api/client.ts"
if os.path.exists(client_path):
    shutil.copy2(client_path, client_path + ".bak")
    with open(client_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # loginTelegram 함수 수정
    content = re.sub(
        r"loginTelegram:\s*\(initData:\s*string\)\s*=>\s*request<AuthResponse>\('/auth/login/telegram',\s*\{\s*method:\s*'POST',\s*body:\s*JSON\.stringify\(\{\s*init_data:\s*initData\s*\}\)\s*\}\)",
        "loginTelegram: (initData: string, currentToken?: string | null) => request<AuthResponse>('/auth/login/telegram', { method: 'POST', body: JSON.stringify({ init_data: initData }), headers: currentToken ? { Authorization: `Bearer ${currentToken}` } : {} })",
        content
    )
    with open(client_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 프론트엔드: api/client.ts 수정 완료")

print("\n4. 백엔드 배포 및 프론트엔드 푸시...")
try:
    subprocess.run(".\\deploy.ps1", shell=True, check=True)
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "fix: 텔레그램 로그인 시 계정 파편화 방지 및 기존 계정 통합"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("🎉 모든 패치 및 배포가 완료되었습니다!")
except Exception as e:
    print(f"⚠️ 배포 실패: {e}")