# scripts/fix_backend_portal_final.py
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

CLIENT_PATH = Path("app/services/lemonsqueezy_client.py")
BILLING_PATH = Path("app/api/v1/endpoints/billing.py")

# ---------------- 1. lemonsqueezy_client.py 에 함수 추가 ----------------
if CLIENT_PATH.exists():
    txt = CLIENT_PATH.read_text(encoding="utf-8")
    if "def get_customer_portal_url" not in txt:
        func_code = '''

async def get_customer_portal_url(email: str) -> str | None:
    """이메일로 구독을 찾아 고객 포털(Signed URL)을 반환합니다."""
    headers = {
        "Accept": "application/vnd.api+json",
        "Authorization": f"Bearer {os.environ['LEMONSQUEEZY_API_KEY']}",
    }
    params = {"filter[user_email]": email}
    
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{LS_API}/subscriptions", headers=headers, params=params)
        
    if resp.status_code >= 400:
        log.error("LemonSqueezy Portal Error %s: %s", resp.status_code, resp.text)
        return None
        
    data = resp.json().get("data", [])
    if not data:
        return None
        
    # 가장 최근 구독의 고객 포털 URL 반환
    return data[0].get("attributes", {}).get("urls", {}).get("customer_portal")
'''
        txt += func_code
        print("✅ [백엔드] lemonsqueezy_client.py에 get_customer_portal_url 함수 추가 완료")
        if APPLY:
            CLIENT_PATH.write_text(txt, encoding="utf-8")
    else:
        print("ℹ️ [백엔드] lemonsqueezy_client.py에 이미 함수가 존재합니다.")

# ---------------- 2. billing.py 의 깨진 /portal 엔드포인트 교체 ----------------
if BILLING_PATH.exists():
    txt = BILLING_PATH.read_text(encoding="utf-8")
    
    # 이전 스크립트가 잘못 주입한 부분부터 끝까지 잘라냄
    broken_marker = '@router.get("/portal")'
    if broken_marker in txt:
        txt = txt.split(broken_marker)[0].rstrip()
        
    # 올바른 /portal 엔드포인트 추가
    correct_endpoint = '''


@router.get("/portal")
async def get_customer_portal(user: dict = Depends(get_current_user)):
    """Lemon Squeezy 고객 포털(Signed URL) 반환"""
    from app.services.lemonsqueezy_client import get_customer_portal_url
    
    email = user.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="User email required")
    
    portal_url = await get_customer_portal_url(email)
    if not portal_url:
        raise HTTPException(status_code=404, detail="No active subscription found")
        
    return {"url": portal_url}
'''
    txt = txt.rstrip() + correct_endpoint
    
    print("✅ [백엔드] billing.py의 /portal 엔드포인트 수정 완료")
    if APPLY:
        BILLING_PATH.write_text(txt, encoding="utf-8")

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
else:
    print("\n🎉 백엔드 패치가 모두 완료되었습니다.")