# app/services/billing.py
import logging
from datetime import datetime, timezone
from app.auth.repository import get_repository
from app.services.stripe_client import init_stripe, PRODUCT_ADDON

log = logging.getLogger(__name__)

def _iso_from_unix(ts: int | None) -> str | None:
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

def handle_event(event: dict) -> None:
    etype = event["type"]
    stripe = init_stripe()
    repo = get_repository()

    if etype == "checkout.session.completed":
        s = event["data"]["object"]
        user_id = (s.get("metadata") or {}).get("userId")
        if not user_id:
            return
        mode = s.get("mode")

        if mode == "payment":
            plan = (s.get("metadata") or {}).get("plan", "")
            addon = PRODUCT_ADDON.get(plan)
            if addon:
                repo.grant_addon(user_id, addon)
                repo.log_purchase(user_id, plan, "stripe")
                try:
                    # 구매 상세 정보 업데이트 (repository에 정의한 _run 사용)
                    repo._run(
                        "UPDATE purchases SET stripe_session_id = ?, "
                        "amount_cents = ?, currency = ? "
                        "WHERE id = (SELECT id FROM purchases WHERE user_id=? AND product_id=? "
                        "ORDER BY purchased_at DESC LIMIT 1)",
                        (s.get("id"), s.get("amount_total"), (s.get("currency") or "").upper(), user_id, plan),
                    )
                except Exception:
                    pass
                log.info("granted addon %s to %s", addon, user_id)

        elif mode == "subscription":
            sub_id = s.get("subscription")
            if sub_id:
                sub = stripe.Subscription.retrieve(sub_id)
                repo.update_subscription(
                    user_id=user_id,
                    subscription_id=sub.id,
                    status=sub.status,
                    current_period_end=_iso_from_unix(sub.current_period_end),
                    is_premium=sub.status in ("active", "trialing"),
                )
                log.info("subscription %s active for %s", sub.id, user_id)

    elif etype in ("customer.subscription.updated", "customer.subscription.deleted"):
        sub = event["data"]["object"]
        user_id = (sub.get("metadata") or {}).get("userId")
        if not user_id and sub.get("customer"):
            row = repo._one("SELECT id FROM users WHERE stripe_customer_id = ?", (sub.get("customer"),))
            user_id = row["id"] if row else None
        
        if user_id:
            active = sub["status"] in ("active", "trialing")
            repo.update_subscription(
                user_id=user_id,
                subscription_id=sub["id"],
                status=sub["status"],
                current_period_end=_iso_from_unix(sub.get("current_period_end")),
                is_premium=active,
            )
            log.info("subscription %s -> %s (user=%s)", sub["id"], sub["status"], user_id)

    elif etype == "invoice.payment_failed":
        log.warning("invoice.payment_failed customer=%s", event["data"]["object"].get("customer"))