# scripts/patch_onetime_purchase.py
from pathlib import Path
import sys
import re

# ==========================================
# 1. 백엔드: 일시불 인보이스 발급 API 추가 (billing.py)
# ==========================================
billing_path = Path("app/api/v1/endpoints/billing.py")
if billing_path.exists():
    src = billing_path.read_text(encoding="utf-8")
    
    if "stars/invoice/onetime" not in src:
        onetime_api = '''

@router.post("/stars/invoice/onetime")
async def create_stars_invoice_onetime(user: dict = Depends(get_current_user)):
    """Telegram Stars 일시불(단품) 결제 인보이스 링크 생성"""
    import os
    import httpx
    from fastapi import HTTPException
    
    bot_token = os.getenv("SAJU_TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise HTTPException(status_code=503, detail="Bot token not configured")

    # 일시불 가격: 150 Stars
    prices = [{"label": "Gyeol Deep Report (1-time)", "amount": 150}]

    payload = {
        "title": "Gyeol Deep Report",
        "description": "Unlock one deep report.",
        "payload": f"onetime_{user['id']}",
        "currency": "XTR",
        "prices": prices,
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{bot_token}/createInvoiceLink",
            json=payload,
        )
        data = resp.json()
        if not data.get("ok"):
            raise HTTPException(status_code=500, detail=data.get("description"))

    return {"invoice_link": data["result"]}
'''
        # 파일 끝에 API 추가
        billing_path.write_text(src + onetime_api, encoding="utf-8")
        print("✅ billing.py에 일시불 인보이스 API 추가 완료")

# ==========================================
# 2. 프론트엔드: API 클라이언트 함수 추가 (client.ts)
# ==========================================
client_path = Path("frontend/src/api/client.ts")
if client_path.exists():
    src = client_path.read_text(encoding="utf-8")
    if "createStarsInvoiceOnetime" not in src:
        # 기존 createStarsInvoice 아래에 추가
        src = src.replace(
            'createStarsInvoice: () => request<{ invoice_link: string }>("/billing/stars/invoice", { method: "POST" }),',
            'createStarsInvoice: () => request<{ invoice_link: string }>("/billing/stars/invoice", { method: "POST" }),\n  createStarsInvoiceOnetime: () => request<{ invoice_link: string }>("/billing/stars/invoice/onetime", { method: "POST" }),'
        )
        client_path.write_text(src, encoding="utf-8")
        print("✅ client.ts에 일시불 API 함수 추가 완료")

# ==========================================
# 3. 프론트엔드: 결제 모달 UI 및 로직 수정 (PaymentModal.tsx)
# ==========================================
modal_path = Path("frontend/src/components/PaymentModal.tsx")
if modal_path.exists():
    src = modal_path.read_text(encoding="utf-8")

    # 3-1. handlePay에서 productId에 따라 다른 인보이스 API 호출
    old_stars_api = 'const { invoice_link } = await api.createStarsInvoice();'
    new_stars_api = '''const { invoice_link } = productId === "onetime" 
            ? await api.createStarsInvoiceOnetime() 
            : await api.createStarsInvoice();'''
    
    if old_stars_api in src:
        src = src.replace(old_stars_api, new_stars_api, 1)

    # 3-2. 프리미엄 구독 박스 아래에 일시불 결제 박스 추가
    old_box_end = '''          <Text style={styles.terms}>{isTelegramEnv ? "Secure checkout powered by Telegram Stars." : "Secure checkout powered by Lemon Squeezy."}</Text>'''

    new_box_end = '''          {/* 💳 일시불 단품 결제 (One-time) */}
          <TouchableOpacity 
            style={[styles.planBox, { borderColor: colors.border, backgroundColor: colors.surface, marginTop: 12 }]} 
            onPress={() => handlePay("onetime")} 
            disabled={!!loading}
          >
            <View style={{ flex: 1 }}>
              <Text style={styles.planName}>Deep Report (1-time)</Text>
              <Text style={styles.planDetail}>Unlock one deep report. No subscription.</Text>
              <Text style={styles.planPrice}>{isTelegramEnv ? "150 Stars" : "$2.99 (One-time)"}</Text>
            </View>
            {loading === "onetime" ? (
              <ActivityIndicator color={colors.textMuted} />
            ) : (
              <Ionicons name="chevron-forward" size={24} color={colors.textMuted} />
            )}
          </TouchableOpacity>

          <Text style={styles.terms}>{isTelegramEnv ? "Secure checkout powered by Telegram Stars." : "Secure checkout powered by Lemon Squeezy."}</Text>'''

    if old_box_end in src:
        src = src.replace(old_box_end, new_box_end, 1)
        print("✅ PaymentModal.tsx에 일시불 결제 UI 추가 완료")
    else:
        print("❌ terms 텍스트를 찾지 못했습니다. 수동 확인 필요.")

    modal_path.write_text(src, encoding="utf-8")