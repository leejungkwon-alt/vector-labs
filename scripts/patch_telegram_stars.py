# scripts/patch_telegram_stars.py
from pathlib import Path
import sys
import re

def append_code(file_path, code_to_append):
    path = Path(file_path)
    if not path.exists():
        print(f"❌ {file_path} 파일을 찾을 수 없습니다.")
        return
    src = path.read_text(encoding="utf-8")
    if code_to_append.strip() in src:
        print(f"⚠️ {file_path}에 이미 코드가 존재합니다.")
        return
    src += "\n\n" + code_to_append.strip() + "\n"
    path.write_text(src, encoding="utf-8")
    print(f"✅ {file_path} 패치 완료")

# ==========================================
# 1. 백엔드: 인보이스 발급 API 추가 (billing.py)
# ==========================================
billing_endpoint = '''
import httpx

@router.post("/stars/invoice")
async def create_stars_invoice(user: dict = Depends(get_current_user)):
    """Telegram Stars 결제를 위한 인보이스 링크 생성"""
    import os
    bot_token = os.getenv("SAJU_TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise HTTPException(status_code=503, detail="Bot token not configured")

    # 가격: 250 Stars (필요시 조정 가능)
    prices = [{"label": "Gyeol Premium", "amount": 250}]

    payload = {
        "title": "Gyeol Premium Subscription",
        "description": "Unlock all deep reports and daily insights.",
        "payload": f"sub_{user['id']}",
        "currency": "XTR", # Telegram Stars 화폐 코드
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
append_code("app/api/v1/endpoints/billing.py", billing_endpoint)

# ==========================================
# 2. 백엔드: 결제 완료 웹훅 추가 (telegram.py)
# ==========================================
telegram_webhook = '''
from fastapi import Request

@router.post("/webhook")
async def telegram_payment_webhook(request: Request):
    """텔레그램 결제 완료(successful_payment) 웹훅 수신"""
    update = await request.json()
    msg = update.get("message", {})
    successful_payment = msg.get("successful_payment")
    
    if successful_payment:
        payload = successful_payment.get("invoice_payload", "")
        if payload.startswith("sub_"):
            user_id = payload.replace("sub_", "")
            repo = get_repository()
            # DB 유저 등급을 프리미엄으로 업데이트
            try:
                repo.update_user_tier(user_id, "premium") 
            except AttributeError:
                # 기존 레몬 스퀴지용 메서드가 있다면 그것을 사용
                try:
                    repo.update_subscription(
                        user_id=user_id,
                        subscription_id=f"stars_{successful_payment.get('telegram_payment_charge_id')}",
                        status="active",
                        renews_at=None
                    )
                except Exception as e:
                    print(f"DB Update Error: {e}")
                    
    return {"ok": True}
'''
append_code("app/api/v1/endpoints/telegram.py", telegram_webhook)

# ==========================================
# 3. 프론트엔드: API 클라이언트 추가 (client.ts)
# ==========================================
client_path = Path("frontend/src/api/client.ts")
if client_path.exists():
    src = client_path.read_text(encoding="utf-8")
    if "createStarsInvoice" not in src:
        src = src.replace(
            'checkout: () => request<{ url: string }>("/billing/checkout"),',
            'checkout: () => request<{ url: string }>("/billing/checkout"),\n  createStarsInvoice: () => request<{ invoice_link: string }>("/billing/stars/invoice", { method: "POST" }),'
        )
        client_path.write_text(src, encoding="utf-8")
        print("✅ frontend/src/api/client.ts 패치 완료")

# ==========================================
# 4. 프론트엔드: 결제 모달 로직 수정 (PaymentModal.tsx)
# ==========================================
modal_path = Path("frontend/src/components/PaymentModal.tsx")
if modal_path.exists():
    src = modal_path.read_text(encoding="utf-8")
    
    old_handle_pay = '''  const handlePay = async (productId: string) => {
    setLoading(productId);
    try {
      // 1. 백엔드에서 Lemon Squeezy 결제창 URL 받아오기
      const { url } = await api.checkout();
      
      // 2. 플랫폼(웹/앱)에 따라 결제창 열기
      if (Platform.OS === "web") {
        window.location.href = url; // 웹: 현재 창에서 결제창으로 이동
      } else {
        await Linking.openURL(url); // 앱: 외부 브라우저로 결제창 열기
        onClose(); // 앱의 경우 결제창을 띄운 후 모달은 닫아줌
      }
      
    } catch (e: any) {
      Alert.alert("Checkout Failed", e.message || "Please try again.");
    } finally {
      setLoading(null);
    }
  };'''

    new_handle_pay = '''  const handlePay = async (productId: string) => {
    setLoading(productId);
    try {
      const tg = (window as any).Telegram?.WebApp;
      const isTelegram = !!tg?.initData;

      if (isTelegram) {
        // --- 텔레그램 스타 결제 ---
        const { invoice_link } = await api.createStarsInvoice();
        tg.openInvoice(invoice_link, (status: string) => {
          if (status === "paid") {
            Alert.alert("결제 완료", "프리미엄이 활성화되었습니다! 앱을 새로고침합니다.");
            window.location.reload();
          } else if (status === "cancelled") {
            // 사용자가 결제 취소
          } else if (status === "failed") {
            Alert.alert("결제 실패", "결제를 다시 시도해주세요.");
          }
        });
        return;
      }

      // --- 기존 Lemon Squeezy 결제 (일반 웹) ---
      const { url } = await api.checkout();
      if (Platform.OS === "web") {
        window.location.href = url;
      } else {
        await Linking.openURL(url);
        onClose();
      }
    } catch (e: any) {
      Alert.alert("Checkout Failed", e.message || "Please try again.");
    } finally {
      setLoading(null);
    }
  };'''

    if "createStarsInvoice" not in src:
        src = src.replace(old_handle_pay, new_handle_pay)
        modal_path.write_text(src, encoding="utf-8")
        print("✅ frontend/src/components/PaymentModal.tsx 패치 완료")
    else:
        print("⚠️ PaymentModal.tsx에 이미 결제 분기 로직이 존재합니다.")

print("\n🎉 텔레그램 스타 결제 연동 패치가 모두 완료되었습니다!")