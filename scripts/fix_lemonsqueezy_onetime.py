import os
import re
import shutil

print("🚀 레몬 스퀴지 1회권 결제 분기 처리를 시작합니다...\n")

# =====================================================================
# 1. 백엔드: lemonsqueezy_client.py 수정 (variant_id 파라미터 추가)
# =====================================================================
client_path = "app/services/lemonsqueezy_client.py"
if os.path.exists(client_path):
    shutil.copy2(client_path, client_path + ".bak")
    with open(client_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 함수 시그니처 변경
    content = content.replace(
        "async def create_checkout_url(user_id: str, email: str | None = None) -> str:",
        "async def create_checkout_url(user_id: str, email: str | None = None, variant_id: str | None = None) -> str:"
    )
    
    # variant_id 분기 처리
    old_variant = '"variant": {"data": {"type": "variants", "id": os.environ["LEMONSQUEEZY_VARIANT_ID"]}},'
    new_variant = '"variant": {"data": {"type": "variants", "id": variant_id or os.environ["LEMONSQUEEZY_VARIANT_ID"]}},'
    
    if old_variant in content:
        content = content.replace(old_variant, new_variant)
        with open(client_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ lemonsqueezy_client.py 수정 완료 (variant_id 분기 추가)")
    else:
        print("⚠️ lemonsqueezy_client.py의 variant 패턴을 찾지 못했습니다.")

# =====================================================================
# 2. 백엔드: billing.py 수정 (is_onetime 파라미터 받기)
# =====================================================================
billing_path = "app/api/v1/endpoints/billing.py"
if os.path.exists(billing_path):
    shutil.copy2(billing_path, billing_path + ".bak")
    with open(billing_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1) Pydantic 모델 임포트 및 추가
    if "class CheckoutRequest" not in content:
        content = content.replace(
            "router = APIRouter()",
            "from pydantic import BaseModel\n\nclass CheckoutRequest(BaseModel):\n    is_onetime: bool = False\n\nrouter = APIRouter()"
        )
        
    # 2) create_checkout 함수 수정
    old_endpoint = '''@router.post("/checkout")
async def create_checkout(user: dict = Depends(get_current_user)):
    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""
    from app.services.lemonsqueezy_client import create_checkout_url
    
    url = await create_checkout_url(user_id=user["id"], email=user.get("email"))
    return {"url": url}'''

    new_endpoint = '''@router.post("/checkout")
async def create_checkout(payload: CheckoutRequest = CheckoutRequest(), user: dict = Depends(get_current_user)):
    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""
    from app.services.lemonsqueezy_client import create_checkout_url
    import os
    
    # 1회권인 경우 ONETIME_VARIANT_ID 사용, 아니면 기본(구독) VARIANT_ID 사용
    variant_id = os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID") if payload.is_onetime else os.environ.get("LEMONSQUEEZY_VARIANT_ID")
    
    url = await create_checkout_url(user_id=user["id"], email=user.get("email"), variant_id=variant_id)
    return {"url": url}'''

    if old_endpoint in content:
        content = content.replace(old_endpoint, new_endpoint)
        with open(billing_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ billing.py 수정 완료 (/checkout 엔드포인트 분기 처리)")
    else:
        print("⚠️ billing.py의 create_checkout 패턴을 찾지 못했습니다.")

# =====================================================================
# 3. 프론트엔드: api/client.ts 수정 (is_onetime 전달)
# =====================================================================
frontend_client_path = "frontend/src/api/client.ts"
if os.path.exists(frontend_client_path):
    shutil.copy2(frontend_client_path, frontend_client_path + ".bak")
    with open(frontend_client_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 createCheckout 함수를 찾아서 is_onetime 파라미터 추가
    pattern = r"createCheckout:\s*\(\)\s*=>\s*[^\n]+,"
    new_code = '''createCheckout: (is_onetime = false) => request<{ url: string }>('/billing/checkout', { method: 'POST', body: JSON.stringify({ is_onetime }) }),'''
    
    new_content, count = re.subn(pattern, new_code, content)
    if count > 0:
        with open(frontend_client_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ client.ts 수정 완료 (createCheckout에 is_onetime 파라미터 추가)")
    else:
        print("⚠️ client.ts에서 createCheckout 패턴을 찾지 못했습니다. 수동 확인 필요.")
else:
    print("❌ 파일을 찾을 수 없습니다: frontend/src/api/client.ts")

print("\n✨ 수정이 완료되었습니다!")
print("⚠️ 주의: Cloud Run 환경변수에 'LEMONSQUEEZY_ONETIME_VARIANT_ID' (1회권 상품 ID)를 꼭 추가해 주세요!")