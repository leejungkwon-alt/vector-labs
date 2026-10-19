import os
import httpx
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class TelegramRegister(BaseModel):
    telegram_id: str
    birth_date: str
    birth_time: Optional[str] = None
    birth_location: Optional[str] = "seoul"

# 가상의 DB (실제 운영 시 SQLite/PostgreSQL 연동 필요)
FAKE_DB = {}

@router.post("/register")
def register_user(payload: TelegramRegister):
    FAKE_DB[payload.telegram_id] = payload.dict()
    return {"status": "ok", "message": "User registered"}

@router.post("/push-daily")
def push_daily_wallpapers(authorization: str = Header(default=None)):
    # 보안: 크론탭에서 보낼 비밀번호 검증
    cron_secret = os.getenv("SAJU_CRON_SECRET", "my-cron-secret")
    if not authorization or authorization != f"Bearer {cron_secret}":
        raise HTTPException(status_code=401, detail="Invalid cron secret")

    bot_token = os.getenv("SAJU_TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return {"error": "Telegram token not set"}

    sent_count = 0
    with httpx.Client() as client:
        for tg_id, profile in FAKE_DB.items():
            # (간단한 예시) 유저에게 메시지 + 이미지 발송
            image_url = "https://vector-labs-three.vercel.app/wallpapers/bg_wood_generalist.jpg"
            message = f"🌅 Good morning!\n오늘 당신을 채워줄 에너지가 도착했어요.\n[3D 배경화면 다운로드하기](https://vector-labs-three.vercel.app)"
            
            res = client.post(
                f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                json={
                    "chat_id": tg_id,
                    "photo": image_url,
                    "caption": message,
                    "parse_mode": "Markdown"
                }
            )
            if res.status_code == 200:
                sent_count += 1

    return {"status": "ok", "sent": sent_count}
