# app/api/v1/endpoints/billing.py
import logging
import os
from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import get_current_user
from app.auth.repository import get_repository
from app.schemas.billing import BillingMe, CheckoutRequest, CheckoutResponse, PortalResponse
from app.services.billing import handle_event
from app.services.stripe_client import init_stripe, mode_for_plan, price_id_for_plan

log = logging.getLogger(__name__)
router = APIRouter()

def _app_url() -> str:
    url = os.environ.get("APP_URL", "").strip().rstrip("/")
    if not url:
        raise RuntimeError("APP_URL is not configured")
    return url

def _webhook_secret() -> str:
    s = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
    if not s:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is not configured")
    return s

@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout(body: CheckoutRequest, current_user: dict = Depends(get_current_user)):
    try:
        stripe = init_stripe()
        repo = get_repository()
        user_id = current_user["id"]

        customer_id = repo.get_stripe_customer_id(user_id)
        if not customer_id:
            customer = stripe.Customer.create(
                email=current_user.get("email") or None,
                metadata={"userId": user_id},
            )
            customer_id = customer.id
            repo.set_stripe_customer_id(user_id, customer_id)

        session = stripe.checkout.Session.create(
            mode=mode_for_plan(body.plan),
            customer=customer_id,
            line_items=[{"price": price_id_for_plan(body.plan), "quantity": 1}],
            success_url=f"{_app_url()}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&plan={body.plan}",
            cancel_url=f"{_app_url()}/payment/cancel",
            allow_promotion_codes=True,
            metadata={"userId": user_id, "plan": body.plan},
        )
        return CheckoutResponse(url=session.url, sessionId=session.id)
    except Exception as e:
        log.exception("create_checkout failed")
        raise HTTPException(status_code=500, detail="Checkout creation failed")

@router.post("/portal", response_model=PortalResponse)
def create_portal(current_user: dict = Depends(get_current_user)):
    try:
        repo = get_repository()
        customer_id = repo.get_stripe_customer_id(current_user["id"])
        if not customer_id:
            raise HTTPException(status_code=400, detail="No Stripe customer")
        
        stripe = init_stripe()
        portal = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{_app_url()}/settings",
        )
        return PortalResponse(url=portal.url)
    except HTTPException:
        raise
    except Exception as e:
        log.exception("create_portal failed")
        raise HTTPException(status_code=500, detail="Portal creation failed")

@router.get("/me", response_model=BillingMe)
def get_billing_me(current_user: dict = Depends(get_current_user)):
    repo = get_repository()
    row = repo.get_user(current_user["id"])
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return BillingMe(
        tier=row["tier"],
        is_premium=row["tier"] in ("premium", "subscription", "unlimited"),
        addons=repo.list_addons(current_user["id"]),
        subscription_status=row.get("subscription_status"),
        current_period_end=row.get("current_period_end"),
    )

@router.post("/webhook")
async def stripe_webhook(request: Request):
    try:
        stripe = init_stripe()
        payload = await request.body()
        sig = request.headers.get("stripe-signature", "")
        event = stripe.Webhook.construct_event(payload, sig, _webhook_secret())
    except Exception as e:
        log.warning("webhook signature failed: %s", e)
        raise HTTPException(status_code=400, detail="Invalid signature")

    repo = get_repository()
    if not repo.record_stripe_event(event["id"], event["type"]):
        return {"received": True, "duplicate": True}

    try:
        handle_event(dict(event))
    except Exception:
        log.exception("handle_event failed for %s", event["id"])
        repo._run("DELETE FROM stripe_events WHERE id = ?", (event["id"],)) # 재시도 허용
        raise HTTPException(status_code=500, detail="Webhook handler failed")

    return {"received": True}