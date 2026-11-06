# scripts/patch_lemonsqueezy_portal.py
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
ROOT = Path(".")

# 대상 파일 경로 (프로젝트 구조에 맞게 수정 필요할 수 있음)
CLIENT_PATH = ROOT / "backend/app/services/lemonsqueezy_client.py"
BILLING_PATH = ROOT / "backend/app/api/v1/endpoints/billing.py"
SETTINGS_PATH = ROOT / "frontend/app/(tabs)/settings.tsx"
API_CLIENT_PATH = ROOT / "frontend/src/api/client.ts"

# 1. 백엔드 서비스 (lemonsqueezy_client.py)에 메서드 추가
if CLIENT_PATH.exists():
    txt = CLIENT_PATH.read_text(encoding="utf-8")
    if "def get_customer_portal_url" not in txt:
        method = '''
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
            # 가장 최근 구독의 고객 포털 URL 반환
            return data[0].get("attributes", {}).get("urls", {}).get("customer_portal")
        except Exception as e:
            print(f"LemonSqueezy portal fetch error: {e}")
            return None
'''
        txt += method
        print("✅ [백엔드] lemonsqueezy_client.py 메서드 추가 예정")

# 2. 백엔드 엔드포인트 (billing.py) 추가
if BILLING_PATH.exists():
    txt = BILLING_PATH.read_text(encoding="utf-8")
    if "/portal" not in txt:
        endpoint = '''
@router.get("/portal")
async def get_customer_portal(user=Depends(get_current_user)):
    """현재 로그인한 유저의 Lemon Squeezy 고객 포털 URL 반환"""
    if not user or not user.get("email"):
        raise HTTPException(status_code=400, detail="User email required")
    
    portal_url = lemonsqueezy_client.get_customer_portal_url(user["email"])
    if not portal_url:
        raise HTTPException(status_code=404, detail="No active subscription found")
        
    return {"url": portal_url}
'''
        # router 정의 부분 찾아서 맨 끝에 추가
        txt += endpoint
        print("✅ [백엔드] billing.py /portal 엔드포인트 추가 예정")

# 3. 프론트엔드 API 클라이언트 (client.ts) 추가
if API_CLIENT_PATH.exists():
    txt = API_CLIENT_PATH.read_text(encoding="utf-8")
    if "getPortalUrl" not in txt:
        # billing 관련 객체가 있는 곳에 메서드 추가 (기존 구조에 맞게 수정)
        if "billing:" in txt:
            txt = txt.replace("billing: {", "billing: {\n    getPortalUrl: () => request<{url: string}>('/billing/portal'),")
        print("✅ [프론트엔드] client.ts API 메서드 추가 예정")

# 4. 프론트엔드 화면 (settings.tsx) 수정
if SETTINGS_PATH.exists():
    txt = SETTINGS_PATH.read_text(encoding="utf-8")
    # 기존 하드코딩된 링크 로직 제거
    old_handle = '''  const handleManageSubscription = () => {
    // Lemon Squeezy 고객 포털 (구독 관리·카드 변경·영수증 다운로드)
    // TODO: 백엔드에서 signed URL을 받아 자동 로그인으로 전환 예정
    Linking.openURL("https://gyeol.lemonsqueezy.com/billing");
  };'''
    new_handle = '''  const handleManageSubscription = async () => {
    try {
      const res = await api.billing.getPortalUrl();
      if (res?.url) {
        Linking.openURL(res.url);
      } else {
        alert("구독 정보를 찾을 수 없습니다.");
      }
    } catch (e: any) {
      alert("구독 관리 페이지를 불러오지 못했습니다.");
    }
  };'''
    
    if old_handle in txt:
        txt = txt.replace(old_handle, new_handle)
        print("✅ [프론트엔드] settings.tsx handleManageSubscription 수정 예정")

# ---------- 적용 ----------
if not APPLY:
    print("\n🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    sys.exit(0)

print("\n🚀 패치를 적용합니다...")

# 파일들 저장 (기존 파일이 있는 경우에만)
if CLIENT_PATH.exists() and "def get_customer_portal_url" not in CLIENT_PATH.read_text(encoding="utf-8"):
    with open(CLIENT_PATH, "a", encoding="utf-8") as f: f.write(method)

if BILLING_PATH.exists() and "/portal" not in BILLING_PATH.read_text(encoding="utf-8"):
    with open(BILLING_PATH, "a", encoding="utf-8") as f: f.write(endpoint)

if API_CLIENT_PATH.exists() and "getPortalUrl" not in API_CLIENT_PATH.read_text(encoding="utf-8"):
    t = API_CLIENT_PATH.read_text(encoding="utf-8").replace("billing: {", "billing: {\n    getPortalUrl: () => request<{url: string}>('/billing/portal'),")
    API_CLIENT_PATH.write_text(t, encoding="utf-8")

if SETTINGS_PATH.exists():
    t = SETTINGS_PATH.read_text(encoding="utf-8").replace(old_handle, new_handle)
    SETTINGS_PATH.write_text(t, encoding="utf-8")

print("🎉 모든 패치가 완료되었습니다.")