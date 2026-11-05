# app/schemas/billing.py
from typing import Literal, Optional
from pydantic import BaseModel

Plan = Literal["monthly", "compatibility"]

class CheckoutRequest(BaseModel):
    plan: Plan
    lang: Optional[str] = None

class CheckoutResponse(BaseModel):
    url: str
    sessionId: str

class PortalResponse(BaseModel):
    url: str

class BillingMe(BaseModel):
    tier: str
    is_premium: bool
    addons: list[str]
    subscription_status: Optional[str] = None
    current_period_end: Optional[str] = None