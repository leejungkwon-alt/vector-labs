# app/services/google_play.py
"""Google Play Developer API calls used to verify in-app purchases."""
import asyncio
import json
import logging
import os

import httpx
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import service_account

log = logging.getLogger("saju.billing")

_BASE = "https://androidpublisher.googleapis.com/androidpublisher/v3/applications"
_SCOPES = ["https://www.googleapis.com/auth/androidpublisher"]
_creds = None


class GooglePlayError(Exception):
    def __init__(self, status: int, detail: str):
        super().__init__(detail)
        self.status = status
        self.detail = detail


def package_name() -> str:
    return os.environ.get("GOOGLE_PLAY_PACKAGE_NAME", "com.vectorlabs.gyeol").strip()


def _access_token() -> str:
    global _creds
    if _creds is None:
        raw = os.environ.get("GOOGLE_PLAY_SERVICE_ACCOUNT_JSON", "").strip()
        if not raw:
            raise GooglePlayError(503, "Google Play verification is not configured")
        _creds = service_account.Credentials.from_service_account_info(
            json.loads(raw), scopes=_SCOPES
        )
    if not _creds.valid:
        _creds.refresh(GoogleRequest())
    return _creds.token


async def _get(path: str) -> dict:
    token = await asyncio.to_thread(_access_token)
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(
            f"{_BASE}/{package_name()}/{path}",
            headers={"Authorization": f"Bearer {token}"},
        )
    if res.status_code != 200:
        log.warning("Google Play API %s -> %s %s", path.split("/")[0], res.status_code, res.text[:300])
        raise GooglePlayError(res.status_code, res.text[:300])
    return res.json()


async def get_product_purchase(sku: str, token: str) -> dict:
    return await _get(f"purchases/products/{sku}/tokens/{token}")


async def get_subscription(token: str) -> dict:
    return await _get(f"purchases/subscriptionsv2/tokens/{token}")