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
    """Lemon Squeezy 고객 포털(Signed URL) 반환"""
    from app.services.lemonsqueezy_client import get_customer_portal_url
    
    # 유저 객체에 이메일이 있는지 안전하게 확인
    email = user.get("email")
    
    if not email:
        # 이메일이 없으면 400 대신 명확한 에러 메시지 반환
        print(f"DEBUG: User {user.get('id')} has no email in DB.")
        raise HTTPException(
            status_code=400, 
            detail="User has no email address. Please link a social account (Google) first."
        )
    
    portal_url = await get_customer_portal_url(email)
    if not portal_url:
        raise HTTPException(status_code=404, detail="No active subscription found for this email.")
        
    return {"url": portal_url}

