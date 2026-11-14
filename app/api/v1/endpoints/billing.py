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

import logging
logger = logging.getLogger("saju.billing")

router = APIRouter()

@router.post("/checkout")
async def create_checkout(payload: CheckoutRequest = CheckoutRequest(), user: dict = Depends(get_current_user)):
    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""
    if user.get("is_anonymous"):
        raise HTTPException(status_code=401, detail="Login required for checkout.")
    from app.services.lemonsqueezy_client import create_checkout_url
    import os
    
    # 1회권인 경우 ONETIME_VARIANT_ID 사용, 아니면 기본(구독) VARIANT_ID 사용
    variant_id = (os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID") or "").strip() if payload.is_onetime else (os.environ.get("LEMONSQUEEZY_VARIANT_ID") or "").strip()
    
    url = await create_checkout_url(user_id=user["id"], email=user.get("email"), variant_id=variant_id)
    return {"url": url}


@router.post("/webhook")
async def lemonsqueezy_webhook(
    request: Request,
    x_signature: str = Header(..., alias="X-Signature"),
):
    """Lemon Squeezy 결제 완료/취소 웹훅 수신"""
    secret_str = os.environ.get("LEMONSQUEEZY_WEBHOOK_SECRET", "").strip()
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
        logger.warning("LS webhook %s ignored: no custom_data.user_id", event_name)
        return {"status": "ignored"}

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
        attrs = event["data"]["attributes"]
        variant_id = str((attrs.get("first_order_item") or {}).get("variant_id"))
        onetime_variant = os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID", "").strip()
        
        # 1회권 상품이 아니거나 결제 상태가 paid가 아니면 무시
        if variant_id != onetime_variant or attrs.get("status") != "paid":
            logger.info("LS order ignored (not onetime or not paid). variant=%s", variant_id)
            return {"status": "ignored"}
            
        order_id = event["data"]["id"]
        try:
            # 💡 멱등성 메서드 적용 (중복 적립 방지)
            granted = repo.add_onetime_purchase_idempotent(user_id, order_id)
            logger.info("✅ LS order_created order=%s user=%s granted=%s", order_id, user_id, granted)
        except Exception:
            logger.exception("❌ LS order_created failed order=%s", order_id)
            raise HTTPException(status_code=500, detail="retry") # 500 에러를 던져 레몬 스퀴지가 재시도하게 함

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
    # 텔레그램 Stars 구독: 앱에서 관리할 수 없고 텔레그램 안에서 해지/관리한다.
    if str(sub_id).startswith("stars_"):
        return {"url": None, "provider": "telegram"}
    # Google Play로 구독한 계정: 구독 ID가 "google_..."이라 Lemon Squeezy 포털로는 열 수 없다.
    # Play 스토어의 구독 관리 페이지로 보낸다.
    if str(sub_id).startswith("google_"):
        package = (os.environ.get("GOOGLE_PLAY_PACKAGE_NAME") or "com.vectorlabs.gyeol").strip()
        return {
            "url": f"https://play.google.com/store/account/subscriptions?sku=gyeol_premium_monthly&package={package}"
        }
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
    if user.get("is_anonymous"):
        raise HTTPException(status_code=401, detail="Login required for checkout.")
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
        "subscription_period": 2592000,  # 30일마다 자동 갱신되는 구독 (텔레그램은 현재 30일만 지원)
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
    if user.get("is_anonymous"):
        raise HTTPException(status_code=401, detail="Login required for checkout.")
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

# ------------------------- Google Play purchase verification -------------------------
import hashlib
from datetime import datetime, timezone
from app.services import google_play

SKU_SUBS = "gyeol_premium_monthly"
SKU_ONETIME = "gyeol_onetime_credit"
_VALID_SUB_STATES = {"SUBSCRIPTION_STATE_ACTIVE", "SUBSCRIPTION_STATE_IN_GRACE_PERIOD"}


class GoogleVerifyRequest(BaseModel):
    sku: str
    purchaseToken: str
    productId: str | None = None


def _parse_time(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _check_binding(user_id: str, obfuscated: str | None) -> None:
    # If the app set obfuscatedAccountId on purchase, only that account may claim it.
    if obfuscated and obfuscated != user_id:
        raise HTTPException(status_code=403, detail="Purchase belongs to another account.")
    if not obfuscated:
        logger.warning("Google purchase has no obfuscated account id (user=%s)", user_id)


@router.post("/google/verify")
async def verify_google_purchase(
    payload: GoogleVerifyRequest, user: dict = Depends(get_current_user)
):
    """Verify an Android Google Play purchase and grant the entitlement."""
    if user.get("is_anonymous"):
        raise HTTPException(status_code=401, detail="Login required.")
    sku = payload.sku.strip()
    token = payload.purchaseToken.strip()
    if sku not in (SKU_SUBS, SKU_ONETIME) or not token:
        raise HTTPException(status_code=400, detail="Invalid product or token.")

    repo = get_repository()
    token_id = hashlib.sha256(token.encode()).hexdigest()[:32]

    try:
        if sku == SKU_SUBS:
            data = await google_play.get_subscription(token)
            line = next((i for i in data.get("lineItems", []) if i.get("productId") == sku), None)
            if not line:
                raise HTTPException(status_code=400, detail="Product mismatch.")
            _check_binding(
                user["id"],
                (data.get("externalAccountIdentifiers") or {}).get("obfuscatedExternalAccountId"),
            )
            state = data.get("subscriptionState")
            expiry = _parse_time(line.get("expiryTime"))
            still_valid = bool(expiry and expiry > datetime.now(timezone.utc))
            is_premium = state in _VALID_SUB_STATES or (
                state == "SUBSCRIPTION_STATE_CANCELED" and still_valid
            )
            if not is_premium:
                raise HTTPException(status_code=400, detail=f"Subscription not active ({state}).")

            repo.update_subscription(
                user_id=user["id"],
                subscription_id=f"google_{token_id}",
                status="active" if state != "SUBSCRIPTION_STATE_CANCELED" else "cancelled",
                current_period_end=expiry.isoformat() if expiry else None,
                is_premium=True,
            )
            try:
                repo.log_purchase(user["id"], SKU_SUBS, "google_play", purchase_id=f"google_sub_{token_id}")
            except Exception:
                logger.info("google sub purchase log skipped user=%s", user["id"])
            return {"status": "ok", "kind": "subscription", "is_premium": True}

        # one-time credit
        data = await google_play.get_product_purchase(sku, token)
        _check_binding(user["id"], data.get("obfuscatedExternalAccountId"))
        if data.get("purchaseState") == 2:
            raise HTTPException(status_code=409, detail="Payment is pending.")
        if data.get("purchaseState") != 0:
            raise HTTPException(status_code=400, detail="Purchase is not completed.")
        order_id = data.get("orderId") or token_id
        granted = repo.add_onetime_purchase_idempotent(
            user["id"], f"google_{order_id}", platform="google_play", product_id=SKU_ONETIME
        )
        logger.info("Google onetime order=%s user=%s granted=%s", order_id, user["id"], granted)
        return {"status": "ok", "kind": "onetime", "granted": bool(granted)}

    except google_play.GooglePlayError as e:
        if e.status in (400, 404, 410):
            raise HTTPException(status_code=400, detail="Purchase could not be verified.")
        logger.error("Google Play API error status=%s", e.status)
        raise HTTPException(status_code=502, detail="Purchase verification is temporarily unavailable.")
