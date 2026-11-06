# scripts/fix_portal_integration.py
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ---------- 1. 프론트엔드 client.ts 수정 ----------
CLIENT_PATH = Path("frontend/src/api/client.ts")
if CLIENT_PATH.exists():
    txt = CLIENT_PATH.read_text(encoding="utf-8")
    
    # 기존 checkout 메서드 뒤에 getPortalUrl 추가
    old_checkout = 'checkout: () => request<{ url: string }>("/billing/checkout", { method: "POST" }),'
    new_checkout = 'checkout: () => request<{ url: string }>("/billing/checkout", { method: "POST" }),\n  getPortalUrl: () => request<{ url: string }>("/billing/portal"),'
    
    if 'getPortalUrl' not in txt:
        if old_checkout in txt:
            txt = txt.replace(old_checkout, new_checkout)
            print("✅ [프론트엔드] client.ts에 getPortalUrl 추가 완료")
        else:
            print("❌ client.ts에서 checkout 메서드 패턴을 찾지 못했습니다.")
    
    if APPLY:
        CLIENT_PATH.write_text(txt, encoding="utf-8")

# ---------- 2. 프론트엔드 settings.tsx 수정 ----------
SETTINGS_PATH = Path("frontend/app/(tabs)/settings.tsx")
if SETTINGS_PATH.exists():
    txt = SETTINGS_PATH.read_text(encoding="utf-8")
    
    # api.billing.getPortalUrl() -> api.getPortalUrl() 로 수정
    if "api.billing.getPortalUrl" in txt:
        txt = txt.replace("api.billing.getPortalUrl()", "api.getPortalUrl()")
        print("✅ [프론트엔드] settings.tsx API 호출부 수정 완료")
        
    if APPLY:
        SETTINGS_PATH.write_text(txt, encoding="utf-8")

# ---------- 3. 백엔드 라우터 파일 자동 탐색 및 패치 ----------
def find_and_patch_backend():
    # backend 폴더 내에서 checkout 엔드포인트가 있는 파이썬 파일 탐색
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ backend 폴더를 찾을 수 없습니다.")
        return

    target_files = []
    for p in backend_dir.rglob("*.py"):
        if "venv" in p.parts or "__pycache__" in p.parts:
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if "@router.post(\"/checkout\")" in txt or "def checkout(" in txt:
            target_files.append((p, txt))

    if not target_files:
        print("❌ 백엔드에서 '/checkout' 라우터를 찾지 못했습니다.")
        return

    for p, txt in target_files:
        if "@router.get(\"/portal\")" in txt:
            print(f"ℹ️ [백엔드] {p} 에 이미 /portal 엔드포인트가 존재합니다.")
            continue

        endpoint_code = '''
@router.get("/portal")
async def get_customer_portal(user=Depends(get_current_user)):
    """Lemon Squeezy 고객 포털(Signed URL) 반환"""
    if not user or not getattr(user, "email", None):
        raise HTTPException(status_code=400, detail="User email required")
    
    portal_url = lemonsqueezy_client.get_customer_portal_url(user.email)
    if not portal_url:
        raise HTTPException(status_code=404, detail="No active subscription found")
        
    return {"url": portal_url}
'''
        # 파일 끝에 엔드포인트 추가
        txt += endpoint_code
        if APPLY:
            p.write_text(txt, encoding="utf-8")
            print(f"✅ [백엔드] {p} 에 /portal 엔드포인트 추가 완료")
        else:
            print(f"🧪 [백엔드] {p} 에 /portal 엔드포인트 추가 예정")

    # get_customer_portal_url 메서드가 lemonsqueezy_client에 있는지 확인
    client_py = backend_dir / "app" / "services" / "lemonsqueezy_client.py"
    if client_py.exists():
        ctxt = client_py.read_text(encoding="utf-8")
        if "def get_customer_portal_url" not in ctxt:
            method_code = '''
    def get_customer_portal_url(self, email: str) -> str | None:
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
                with open(client_py, "a", encoding="utf-8") as f:
                    f.write(method_code)
                print(f"✅ [백엔드] {client_py} 에 get_customer_portal_url 추가 완료")
            else:
                print(f"🧪 [백엔드] {client_py} 에 get_customer_portal_url 추가 예정")

find_and_patch_backend()

if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")