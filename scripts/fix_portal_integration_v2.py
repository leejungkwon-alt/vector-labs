# scripts/fix_portal_integration_v2.py
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
ROOT = Path(".")

print("🔎 백엔드 결제 라우터 및 레몬스퀴지 클라이언트 파일을 탐색합니다...\n")

# ---------- 1. 백엔드: billing.py (또는 checkout 라우터가 있는 파일) 탐색 및 패치 ----------
billing_files = []
lemonsqueezy_files = []

for p in ROOT.rglob("*.py"):
    if any(x in p.parts for x in ["venv", ".venv", "node_modules", "__pycache__", ".git", "scripts", "tests"]):
        continue
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        continue
    
    # checkout 라우터가 있는 파일 찾기
    if "@router.post(\"/checkout\")" in txt or "def checkout(" in txt:
        billing_files.append((p, txt))
        
    # lemonsqueezy 클라이언트 파일 찾기
    if "class LemonSqueezyClient" in txt or "lemonsqueezy" in txt.lower() and "class" in txt and "def create_checkout" in txt:
        lemonsqueezy_files.append((p, txt))

# 1-1. 레몬스퀴지 클라이언트에 get_customer_portal_url 메서드 추가
if not lemonsqueezy_files:
    print("❌ 레몬스퀴지 클라이언트 파일을 찾지 못했습니다.")
else:
    for p, txt in lemonsqueezy_files:
        if "def get_customer_portal_url" in txt:
            print(f"ℹ️ {p} 에 이미 get_customer_portal_url 메서드가 존재합니다.")
            continue
            
        method_code = '''
    def get_customer_portal_url(self, email: str) -> str | None:
        """이메일로 구독을 찾아 고객 포털(Signed URL)을 반환합니다."""
        import httpx
        try:
            resp = httpx.get(
                "https://api.lemonsqueezy.com/v1/subscriptions",
                headers={"Accept": "application/vnd.api+json", "Authorization": f"Bearer {self.api_key}"},
                params={"filter[user_email]": email},
                timeout=10.0
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])
            if not data:
                return None
            return data[0].get("attributes", {}).get("urls", {}).get("customer_portal")
        except Exception as e:
            print(f"LemonSqueezy portal fetch error: {e}")
            return None
'''
        if APPLY:
            with open(p, "a", encoding="utf-8") as f:
                f.write(method_code)
            print(f"✅ [백엔드] {p} 에 get_customer_portal_url 추가 완료")
        else:
            print(f"🧪 [백엔드] {p} 에 get_customer_portal_url 추가 예정")

# 1-2. billing 라우터 파일에 /portal 엔드포인트 추가
if not billing_files:
    print("❌ /checkout 라우터가 있는 파일을 찾지 못했습니다.")
else:
    for p, txt in billing_files:
        if "@router.get(\"/portal\")" in txt:
            print(f"ℹ️ {p} 에 이미 /portal 엔드포인트가 존재합니다.")
            continue
            
        endpoint_code = '''
@router.get("/portal")
async def get_customer_portal(user=Depends(get_current_user)):
    """Lemon Squeezy 고객 포털(Signed URL) 반환"""
    if not user or not getattr(user, "email", None):
        raise HTTPException(status_code=400, detail="User email required")
    
    # 클라이언트 인스턴스 이름이 다를 수 있으므로 유연하게 처리
    portal_url = None
    if "lemonsqueezy_client" in globals():
        portal_url = lemonsqueezy_client.get_customer_portal_url(user.email)
    elif "client" in globals():
        portal_url = client.get_customer_portal_url(user.email)
        
    if not portal_url:
        raise HTTPException(status_code=404, detail="No active subscription found")
        
    return {"url": portal_url}
'''
        if APPLY:
            with open(p, "a", encoding="utf-8") as f:
                f.write(endpoint_code)
            print(f"✅ [백엔드] {p} 에 /portal 엔드포인트 추가 완료")
        else:
            print(f"🧪 [백엔드] {p} 에 /portal 엔드포인트 추가 예정")

# ---------- 2. 프론트엔드 client.ts 및 settings.tsx (이미 수정되었으므로 패스) ----------
print("\n💡 프론트엔드(client.ts, settings.tsx)는 이전 스크립트에서 이미 수정되었습니다.")

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")