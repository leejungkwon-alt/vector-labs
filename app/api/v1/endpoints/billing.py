# app/api/v1/endpoints/billing.py
import hmac
import hashlib
import json
import os
from fastapi import APIRouter, Request, HTTPException, Header, Depends

from app.auth.repository import get_repository
# 👇 프로젝트의 실제 인증 의존성(Dependency) 경로로 맞춰주세요!
from app.auth.router import get_current_user 

from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    is_onetime: bool = False

router = APIRouter()

@router.post("/checkout")
async def create_checkout(payload: CheckoutRequest = CheckoutRequest(), user: dict = Depends(get_current_user)):
    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""
    from app.services.lemonsqueezy_client import create_checkout_url
    import os
    
    # 1회권인 경우 ONETIME_VARIANT_ID 사용, 아니면 기본(구독) VARIANT_ID 사용
    variant_id = os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID") if payload.is_onetime else os.environ.get("LEMONSQUEEZY_VARIANT_ID")
    
    url = await create_checkout_url(user_id=user["id"], email=user.get("email"), variant_id=variant_id)
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
        if event_name == "subscription_created":
            repo.log_purchase(user_id, "lemon_sub", "lemon_squeezy", purchase_id=f"lemon_sub_{event['data']['id']}")
        
    elif event_name in ("subscription_cancelled", "subscription_expired"):
        repo.update_subscription(
            user_id=user_id,
            subscription_id=event["data"]["id"],
            status="cancelled",
            current_period_end=None,
            is_premium=False,
        )
    elif event_name == "order_created":
        order_id = str(event["data"]["id"])
        order_attrs = event["data"].get("attributes", {})
        status = order_attrs.get("status")

        # 1. 결제 완료 상태(paid) 및 비환불 건 확인
        if status != "paid" or order_attrs.get("refunded"):
            return {
                "status": "ignored",
                "reason": f"unpaid_or_refunded (status={status}, refunded={order_attrs.get('refunded')})",
            }

        # 2. 주문 상품의 variant_id 확인
        first_item = order_attrs.get("first_order_item") or {}
        variant_id = str(first_item.get("variant_id") or "")

        onetime_variant = str(os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID", "")).strip()
        sub_variant = str(os.environ.get("LEMONSQUEEZY_VARIANT_ID", "")).strip()

        # 구독 결제의 첫 주문(order_created)인 경우 -> subscription_created에서 처리하므로 스킵
        if sub_variant and variant_id == sub_variant:
            return {"status": "ignored", "reason": "subscription_order_delegated"}

        # 1회권 variant_id가 환경변수에 설정되어 있는 경우 불일치 시 스킵
        if onetime_variant and variant_id != onetime_variant:
            return {
                "status": "ignored",
                "reason": f"variant_mismatch (got {variant_id}, expected {onetime_variant})",
            }

        # 3. 멱등적(Idempotent) 크레딧 지급 및 구매 기록
        try:
            applied = repo.add_onetime_purchase_idempotent(
                user_id=user_id, order_id=order_id, platform="lemon_squeezy"
            )
            if applied:
                print(f"[Webhook] User {user_id} 1회권 결제 완료 (Order: {order_id})")
                return {"status": "ok", "action": "credit_added", "order_id": order_id}
            else:
                print(f"[Webhook] User {user_id} 이미 처리된 주문 건 (Order: {order_id})")
                return {"status": "ok", "action": "duplicate_ignored", "order_id": order_id}
        except Exception as e:
            print(f"[Webhook] DB 업데이트 실패 (Order: {order_id}): {e}")
            raise HTTPException(status_code=500, detail="Database update failed")
            
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


@router.get("/purchases")
async def get_purchases(user: dict = Depends(get_current_user)):
    """유저의 결제(구매) 내역을 반환합니다."""
    repo = get_repository()
    purchases = repo.list_purchases(user["id"])
    return {"purchases": purchases}
