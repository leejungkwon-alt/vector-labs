# app/api/v1/endpoints/billing.py
import hmac
import hashlib
import json
import os
from fastapi import APIRouter, Request, HTTPException, Header, Depends

from app.auth.repository import get_repository
# 👇 프로젝트의 실제 인증 의존성(Dependency) 경로로 맞춰주세요!
from app.auth.router import get_current_user 

router = APIRouter()

@router.post("/checkout")
async def create_checkout(user: dict = Depends(get_current_user)):
    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""
    from app.services.lemonsqueezy_client import create_checkout_url
    
    url = await create_checkout_url(user_id=user["id"], email=user.get("email"))
    return {"url": url}


@router.post("/webhook")
async def lemonsqueezy_webhook(
    request: Request,
    x_signature: str = Header(..., alias="X-Signature"),
):
    """Lemon Squeezy 결제 완료/취소 웹훅 수신"""
    secret_str = os.environ.get("LEMONSQUEEZY_WEBHOOK_SECRET", "")
    if not secret_str:
        raise HTTPException(status_code=503, detail="Webhook not configured")
    secret = secret_str.encode()
    raw_body = await request.body()
    
    # 1. 서명 검증 (보안)
    expected = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 2. 이벤트 데이터 파싱
    event = json.loads(raw_body)
    event_name = event["meta"]["event_name"]
    custom = event["meta"].get("custom_data", {}) or {}
    user_id = custom.get("user_id")

    if not user_id:
        return {"status": "ignored"} # user_id가 없으면 무시

    repo = get_repository()
    
    # 3. 구독 이벤트에 따른 DB 상태 변경
    if event_name in ("subscription_created", "subscription_updated"):
        sub = event["data"]["attributes"]
        status = sub.get("status") # active, past_due, cancelled 등
        renews_at = sub.get("renews_at") # 다음 결제일
        is_premium = status in ("active", "on_trial")
        
        repo.update_subscription(
            user_id=user_id,
            subscription_id=event["data"]["id"],
            status=status,
            current_period_end=renews_at,
            is_premium=is_premium,
        )
        
    elif event_name in ("subscription_cancelled", "subscription_expired"):
        repo.update_subscription(
            user_id=user_id,
            subscription_id=event["data"]["id"],
            status="cancelled",
            current_period_end=None,
            is_premium=False,
        )

    return {"status": "ok"}


@router.get("/portal")
async def get_customer_portal(user: dict = Depends(get_current_user)):
    """Lemon Squeezy 고객 포털(Signed URL) 반환 (구독 ID 기반)"""
    from app.services.lemonsqueezy_client import get_customer_portal_url

    sub_id = user.get("stripe_subscription_id")
    if not sub_id:
        raise HTTPException(
            status_code=404,
            detail="No subscription linked to this account. Please subscribe to Premium first.",
        )
    url = await get_customer_portal_url(str(sub_id))
    if not url:
        raise HTTPException(
            status_code=502,
            detail="Could not load the billing portal. Please try again later.",
        )
    return {"url": url}


import httpx

@router.post("/stars/invoice")
async def create_stars_invoice(user: dict = Depends(get_current_user)):
    """Telegram Stars 결제를 위한 인보이스 링크 생성"""
    import os
    bot_token = os.getenv("SAJU_TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise HTTPException(status_code=503, detail="Bot token not configured")

    # 가격: 250 Stars (필요시 조정 가능)
    prices = [{"label": "Gyeol Premium", "amount": 400}]

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
