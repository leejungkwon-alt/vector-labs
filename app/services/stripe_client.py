# app/services/stripe_client.py
import os
import stripe

_stripe_key: str | None = None

def init_stripe() -> stripe:
    """환경변수 → stripe 모듈 글로벌 세팅. 키 없으면 fail-fast."""
    global _stripe_key
    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not key:
        raise RuntimeError("STRIPE_SECRET_KEY is not configured")
    if _stripe_key != key:
        stripe.api_key = key
        stripe.api_version = "2024-06-20"
        stripe.max_network_retries = 2
        _stripe_key = key
    return stripe

PLAN_TO_PRICE_ENV = {
    "monthly": "STRIPE_PRICE_MONTHLY",
    "compatibility": "STRIPE_PRICE_COMPAT",
}

# 앱에서 오는 plan 값 → user_addons.addon 에 저장될 값
PRODUCT_ADDON = {
    "compatibility": "compatibility",
}

def price_id_for_plan(plan: str) -> str:
    env = PLAN_TO_PRICE_ENV.get(plan)
    if not env:
        raise ValueError(f"Unknown plan: {plan!r}")
    val = os.environ.get(env, "").strip()
    if not val:
        raise RuntimeError(f"{env} is not configured")
    return val

def mode_for_plan(plan: str) -> str:
    return "subscription" if plan == "monthly" else "payment"