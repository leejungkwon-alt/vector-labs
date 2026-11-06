# app/services/lemonsqueezy_client.py
import os
import httpx
import logging

log = logging.getLogger("saju.billing")
LS_API = "https://api.lemonsqueezy.com/v1"

async def create_checkout_url(user_id: str, email: str | None = None) -> str:
    """프론트엔드에서 결제 버튼을 눌렀을 때 이동할 Lemon Squeezy 결제창 URL을 생성합니다."""
    headers = {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {os.environ['LEMONSQUEEZY_API_KEY']}",
    }
    
    payload = {
        "data": {
            "type": "checkouts",
            "attributes": {
                "checkout_data": {
                    "email": email,
                    "custom": {"user_id": user_id}, # 웹훅 수신 시 유저 식별용
                },
                "product_options": {
                    "redirect_url": f"{os.environ.get('APP_URL', 'https://gyeol-blond.vercel.app')}/billing/success",
                },
            },
            "relationships": {
                "store": {"data": {"type": "stores", "id": os.environ["LEMONSQUEEZY_STORE_ID"]}},
                "variant": {"data": {"type": "variants", "id": os.environ["LEMONSQUEEZY_VARIANT_ID"]}},
            },
        }
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{LS_API}/checkouts", headers=headers, json=payload)
        
    if resp.status_code >= 400:
        log.error("LemonSqueezy API Error %s: %s", resp.status_code, resp.text)
        resp.raise_for_status()
        
    return resp.json()["data"]["attributes"]["url"]