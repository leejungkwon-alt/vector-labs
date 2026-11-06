# scripts/patch_billing_fixes.py
"""
Lemon Squeezy 연동 안정화 패치 (멱등성 보장)
1. lemonsqueezy_client.py: email Optional 처리 및 에러 로깅 추가
2. billing.py: user.get("email") 적용 및 웹훅 시크릿 누락 방어
"""
import ast
import re
import shutil
import sys
from pathlib import Path

# 패치할 파일 경로
CLIENT_PATH = Path("app/services/lemonsqueezy_client.py")
BILLING_PATH = Path("app/api/v1/endpoints/billing.py")

def patch_client():
    if not CLIENT_PATH.exists():
        print(f"⚠️ {CLIENT_PATH} 파일이 없습니다. 건너뜁니다.")
        return

    src = CLIENT_PATH.read_text(encoding="utf-8")
    if "log = logging.getLogger(\"saju.billing\")" in src:
        print("✅ lemonsqueezy_client.py 는 이미 패치되어 있습니다.")
        return

    backup = CLIENT_PATH.with_suffix(".py.bak")
    shutil.copy2(CLIENT_PATH, backup)
    print(f"백업 생성: {backup}")

    # 1) import logging 추가
    if "import logging" not in src:
        src = src.replace("import httpx", "import httpx\nimport logging")

    # 2) 로거 생성
    src = src.replace(
        'LS_API = "https://api.lemonsqueezy.com/v1"',
        'log = logging.getLogger("saju.billing")\nLS_API = "https://api.lemonsqueezy.com/v1"'
    )

    # 3) 함수 시그니처 변경 (email Optional)
    src = re.sub(
        r'async def create_checkout_url\(user_id: str, email: str\) -> str:',
        'async def create_checkout_url(user_id: str, email: str | None = None) -> str:',
        src
    )

    # 4) checkout_data 생성 로직 변경
    old_checkout = '''                "checkout_data": {
                    "email": email,
                    "custom": {"user_id": user_id},
                },'''
    new_checkout = '''                "checkout_data": checkout_data,'''
    
    if old_checkout in src:
        src = src.replace(old_checkout, new_checkout)
        # checkout_data 변수 생성 코드 삽입 (payload 직전)
        src = src.replace(
            '    payload = {',
            '    checkout_data = {"custom": {"user_id": user_id}}\n    if email:\n        checkout_data["email"] = email\n\n    payload = {'
        )

    # 5) httpx 타임아웃 및 에러 로깅 추가
    old_http = '''    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{LS_API}/checkouts", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["data"]["attributes"]["url"]'''
    new_http = '''    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{LS_API}/checkouts", headers=headers, json=payload)
        
    if resp.status_code >= 400:
        log.error("LemonSqueezy API Error %s: %s", resp.status_code, resp.text)
        resp.raise_for_status()
        
    return resp.json()["data"]["attributes"]["url"]'''
    
    src = src.replace(old_http, new_http)

    # 문법 검사
    try:
        ast.parse(src)
    except SyntaxError as e:
        print(f"❌ 문법 오류 발생: {e}")
        sys.exit(1)

    CLIENT_PATH.write_text(src, encoding="utf-8")
    print("✅ lemonsqueezy_client.py 패치 완료")


def patch_billing():
    if not BILLING_PATH.exists():
        print(f"⚠️ {BILLING_PATH} 파일이 없습니다. 건너뜁니다.")
        return

    src = BILLING_PATH.read_text(encoding="utf-8")
    if 'if not secret_str:' in src:
        print("✅ billing.py 는 이미 패치되어 있습니다.")
        return

    backup = BILLING_PATH.with_suffix(".py.bak")
    shutil.copy2(BILLING_PATH, backup)
    print(f"백업 생성: {backup}")

    # 1) user["email"] -> user.get("email")
    src = src.replace('email=user["email"]', 'email=user.get("email")')

    # 2) 웹훅 시크릿 누락 방어 로직 추가
    old_secret = '    secret = os.environ.get("LEMONSQUEEZY_WEBHOOK_SECRET", "").encode()'
    new_secret = '''    secret_str = os.environ.get("LEMONSQUEEZY_WEBHOOK_SECRET", "")
    if not secret_str:
        raise HTTPException(status_code=503, detail="Webhook not configured")
    secret = secret_str.encode()'''
    
    if old_secret in src:
        src = src.replace(old_secret, new_secret)

    # 문법 검사
    try:
        ast.parse(src)
    except SyntaxError as e:
        print(f"❌ 문법 오류 발생: {e}")
        sys.exit(1)

    BILLING_PATH.write_text(src, encoding="utf-8")
    print("✅ billing.py 패치 완료")


if __name__ == "__main__":
    print("🚀 Lemon Squeezy 안정화 패치를 시작합니다...\n")
    patch_client()
    patch_billing()
    print("\n🎉 모든 패치가 완료되었습니다. 서버를 재배포하세요!")