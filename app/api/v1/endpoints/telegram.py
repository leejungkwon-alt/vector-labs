"""
텔레그램 미니앱 일일 푸시.

보안 모델
- /register, /unregister : Telegram WebApp `initData` 의 HMAC-SHA256 서명을 봇 토큰으로
  검증해 telegram_id 를 확정한다. (클라이언트가 보낸 telegram_id 는 신뢰하지 않음)
  /register 는 추가로 Bearer 로그인 + 저장된 생년 프로필(만 14세 이상)이 필요하다.
- /push-daily : 크론 전용. SAJU_CRON_SECRET(16자 이상) 이 설정되어 있어야만 활성화되고
  상수 시간 비교(hmac.compare_digest)로 검증한다. 기본값 없음.
- 구독자는 DB(리포지토리)에 저장되므로 인스턴스 재시작에 영향받지 않고,
  계정 삭제 시 CASCADE 로 함께 삭제된다.
"""
import hashlib
import hmac
import json
import logging
import os
import time
from urllib.parse import parse_qsl

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.auth.repository import get_repository
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.visual_generator import get_daily_wallpaper_url

logger = logging.getLogger(__name__)
router = APIRouter()

INIT_DATA_MAX_AGE_SECONDS = 24 * 3600
_MIN_CRON_SECRET_LEN = 16


class TelegramInitData(BaseModel):
    init_data: str = Field(
        min_length=1,
        description="Telegram.WebApp.initData 원문 (서버가 서명을 검증합니다)",
    )


def verify_init_data(
    init_data: str,
    bot_token: str,
    max_age: int = INIT_DATA_MAX_AGE_SECONDS,
    now: float | None = None,
) -> dict:
    """
    Telegram WebApp initData 검증 후 user dict 반환. 실패 시 ValueError.
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise ValueError("initData has no hash.")

    check_string = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received_hash):
        raise ValueError("initData signature mismatch.")

    try:
        auth_date = int(pairs.get("auth_date", "0"))
    except ValueError:
        raise ValueError("initData auth_date is invalid.")
    if (now if now is not None else time.time()) - auth_date > max_age:
        raise ValueError("initData has expired.")

    try:
        user = json.loads(pairs.get("user", ""))
        int(user["id"])
    except (ValueError, KeyError, TypeError):
        raise ValueError("initData has no valid user.")
    return user


def _bot_token() -> str:
    token = os.getenv("SAJU_TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise HTTPException(status_code=503, detail="Telegram integration is not configured.")
    return token


def _verified_telegram_id(payload: TelegramInitData) -> str:
    try:
        user = verify_init_data(payload.init_data, _bot_token())
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return str(user["id"])


@router.post("/register")
def register_user(
    payload: TelegramInitData,
    user: dict = Depends(get_current_user),
):
    tg_id = _verified_telegram_id(payload)
    repo = get_repository()

    profile = repo.get_profile(user["id"])
    if not profile or not profile.get("birth_date"):
        raise HTTPException(
            status_code=409,
            detail="Save your birth profile first (PUT /api/v1/auth/me/profile).",
        )
    try:  # 만 14세 미만 차단 (calculate_saju 와 동일 정책)
        from app.compliance.age import validate_age

        validate_age(profile["birth_date"])
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    repo.upsert_telegram_subscriber(tg_id, user["id"])
    return {"status": "ok", "message": "Subscribed to daily push."}


@router.post("/unregister")
def unregister_user(payload: TelegramInitData):
    tg_id = _verified_telegram_id(payload)
    removed = get_repository().delete_telegram_subscriber(tg_id)
    return {"status": "ok", "removed": removed}


def _check_cron_auth(authorization: str | None) -> None:
    secret = os.getenv("SAJU_CRON_SECRET", "")
    if len(secret) < _MIN_CRON_SECRET_LEN:
        # 기본값 없음: 미설정/약한 시크릿이면 엔드포인트 자체를 비활성화
        raise HTTPException(status_code=503, detail="Cron endpoint is not configured.")
    expected = f"Bearer {secret}"
    if not authorization or not hmac.compare_digest(
        authorization.encode(), expected.encode()
    ):
        raise HTTPException(status_code=401, detail="Invalid cron secret")


def _wallpaper_for(profile_row: dict) -> str:
    saju = calculate_saju(
        birth_date=profile_row["birth_date"],
        birth_time=profile_row.get("birth_time"),
        birth_time_mode="exact" if profile_row.get("birth_time") else "day_only",
        timezone_str=profile_row.get("timezone_str") or "Asia/Seoul",
        longitude=profile_row.get("longitude") or 126.9780,
        correction_mode=profile_row.get("correction_mode") or "lmt",
        jasi_boundary=profile_row.get("jasi_boundary") or 23,
        gender=profile_row.get("gender") or "M",
        birth_location=profile_row.get("birth_location"),
    )
    return get_daily_wallpaper_url(build_semantic_profile(saju))


@router.post("/push-daily")
def push_daily_wallpapers(authorization: str | None = Header(default=None)):
    _check_cron_auth(authorization)
    bot_token = _bot_token()
    webapp_url = os.getenv("SAJU_WEBAPP_URL", "https://vector-labs-three.vercel.app")

    repo = get_repository()
    sent = failed = removed = skipped = 0
    # 봇 토큰이 URL 에 들어가므로 httpx 요청 로그(INFO)를 남기지 않는다.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    with httpx.Client(timeout=10.0) as client:
        for sub in repo.list_telegram_subscribers():
            profile_row = repo.get_profile(sub["user_id"])
            if not profile_row or not profile_row.get("birth_date"):
                skipped += 1
                continue
            try:
                image_url = _wallpaper_for(profile_row)
            except Exception:  # 연령 미달/잘못된 프로필 등
                logger.warning("wallpaper skipped for user=%s", sub["user_id"])
                skipped += 1
                continue

            try:
                res = client.post(
                    f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                    json={
                        "chat_id": sub["telegram_id"],
                        "photo": image_url,
                        "caption": (
                            "🌅 Good morning!\n오늘 당신을 채워줄 에너지가 도착했어요.\n"
                            f"[3D 배경화면 다운로드하기]({webapp_url})"
                        ),
                        "parse_mode": "Markdown",
                    },
                )
            except httpx.HTTPError:
                failed += 1
                continue

            if res.status_code == 200:
                sent += 1
            elif res.status_code in (400, 403):
                # 봇 차단/채팅 없음 → 구독 해제 (불필요한 재시도·스팸 방지)
                if res.status_code == 403:
                    repo.delete_telegram_subscriber(sub["telegram_id"])
                    removed += 1
                else:
                    failed += 1
            else:
                failed += 1
            time.sleep(0.05)  # Telegram 전송 한도(초당 ~30건) 보호

    return {"status": "ok", "sent": sent, "failed": failed, "removed": removed, "skipped": skipped}
