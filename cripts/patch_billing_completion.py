# scripts/patch_billing_completion.py
from pathlib import Path
import sys
import re

# ==========================================
# 1. 백엔드: 레몬 스퀴지 결제 API 분기 처리 (billing.py)
# ==========================================
billing_path = Path("app/api/v1/endpoints/billing.py")
if billing_path.exists():
    src = billing_path.read_text(encoding="utf-8")
    
    # checkout API가 product_id를 받도록 수정
    old_checkout = '''@router.post("/checkout")
async def create_checkout(user: dict = Depends(get_current_user)):
    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""
    from app.services.lemonsqueezy_client import create_checkout_url
    
    url = await create_checkout_url(user_id=user["id"], email=user.get("email"))
    return {"url": url}'''

    new_checkout = '''from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    product_id: str = "sub_monthly_699"

@router.post("/checkout")
async def create_checkout(body: CheckoutRequest, user: dict = Depends(get_current_user)):
    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""
    from app.services.lemonsqueezy_client import create_checkout_url
    
    # product_id에 따라 다른 Variant ID 매핑
    variant_id = "2341690" # 기본 구독 ID
    if body.product_id == "onetime":
        variant_id = "2357370" # (대표님이 레몬스퀴지에서 새로 만든 $2.99 상품 ID)
        
    url = await create_checkout_url(user_id=user["id"], email=user.get("email"), variant_id=variant_id)
    return {"url": url}'''

    if old_checkout in src:
        src = src.replace(old_checkout, new_checkout, 1)
        billing_path.write_text(src, encoding="utf-8")
        print("✅ billing.py 레몬 스퀴지 상품 분기 처리 완료")

# ==========================================
# 2. 백엔드: 텔레그램 웹훅 - 일시불 결제 처리 (telegram.py)
# ==========================================
tg_path = Path("app/api/v1/endpoints/telegram.py")
if tg_path.exists():
    src = tg_path.read_text(encoding="utf-8")
    
    # successful_payment 부분 찾기
    old_webhook = '''    if successful_payment:
        payload = successful_payment.get("invoice_payload", "")
        if payload.startswith("sub_"):'''

    new_webhook = '''    if successful_payment:
        payload = successful_payment.get("invoice_payload", "")
        
        # 1. 단품 결제 (onetime_) 처리
        if payload.startswith("onetime_"):
            user_id = payload.replace("onetime_", "")
            repo = get_repository()
            try:
                # 유저의 단품 크레딧(이용권) +1 증가
                repo.add_onetime_credit(user_id)
            except Exception as e:
                print(f"One-time credit error: {e}")
                
        # 2. 구독 결제 (sub_) 처리
        elif payload.startswith("sub_"):'''

    if old_webhook in src:
        src = src.replace(old_webhook, new_webhook, 1)
        tg_path.write_text(src, encoding="utf-8")
        print("✅ telegram.py 텔레그램 일시불 웹훅 처리 추가 완료")

# ==========================================
# 3. 프론트엔드: checkout API 호출 시 product_id 전달 (client.ts)
# ==========================================
client_path = Path("frontend/src/api/client.ts")
if client_path.exists():
    src = client_path.read_text(encoding="utf-8")
    
    old_api = 'checkout: () => request<{ url: string }>("/billing/checkout"),'
    new_api = 'checkout: (productId: string = "sub_monthly_699") => request<{ url: string }>("/billing/checkout", { method: "POST", body: JSON.stringify({ product_id: productId }) }),'

    if old_api in src:
        src = src.replace(old_api, new_api, 1)
        client_path.write_text(src, encoding="utf-8")
        print("✅ client.ts checkout API에 product_id 추가 완료")

# ==========================================
# 4. 프론트엔드: PaymentModal.tsx에서 productId 넘겨주기
# ==========================================
modal_path = Path("frontend/src/components/PaymentModal.tsx")
if modal_path.exists():
    src = modal_path.read_text(encoding="utf-8")
    
    old_call = 'const { url } = await api.checkout();'
    new_call = 'const { url } = await api.checkout(productId);'

    if old_call in src:
        src = src.replace(old_call, new_call, 1)
        modal_path.write_text(src, encoding="utf-8")
        print("✅ PaymentModal.tsx checkout 호출부 수정 완료")