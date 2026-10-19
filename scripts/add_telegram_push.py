from pathlib import Path
import subprocess

BASE = Path.cwd()
API_DIR = BASE / "app" / "api" / "v1" / "endpoints"
API_DIR.mkdir(parents=True, exist_ok=True)

# 1. 텔레그램 푸시 API 파일 생성
TELEGRAM_PY = """import os
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
            message = f"🌅 Good morning!\\n오늘 당신을 채워줄 에너지가 도착했어요.\\n[3D 배경화면 다운로드하기](https://vector-labs-three.vercel.app)"
            
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
"""
API_DIR.joinpath("telegram.py").write_text(TELEGRAM_PY, encoding="utf-8")
print("✅ app/api/v1/endpoints/telegram.py 생성 완료")

# 2. main.py에 라우터 등록
MAIN_PY = BASE / "app" / "main.py"
text = MAIN_PY.read_text(encoding="utf-8")
if "from app.api.v1.endpoints import saju, report, compatibility, daily" in text:
    text = text.replace(
        "from app.api.v1.endpoints import saju, report, compatibility, daily",
        "from app.api.v1.endpoints import saju, report, compatibility, daily, telegram"
    )
    text = text.replace(
        'app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])',
        'app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])\\napp.include_router(telegram.router, prefix="/api/v1/telegram", tags=["Telegram"])'
    )
    MAIN_PY.write_text(text, encoding="utf-8")
    print("✅ main.py에 텔레그램 라우터 등록 완료")

# 3. 프론트엔드(App.jsx)에 텔레그램 ID 전송 로직 추가
APP_JSX = BASE / "tma" / "src" / "App.jsx"
jsx_text = APP_JSX.read_text(encoding="utf-8")

# API fetch 부분 수정 (텔레그램 ID를 백엔드로 전송)
old_fetch = """    const fetchReport = async () => {
      try {
        const res = await fetch('/api/v1/saju/report', {"""
new_fetch = """    const fetchReport = async () => {
      try {
        const tg = window.Telegram?.WebApp;
        const tgId = tg?.initDataUnsafe?.user?.id?.toString();
        
        // 1. 텔레그램 ID 백엔드에 등록
        if (tgId) {
          await fetch('/api/v1/telegram/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              telegram_id: tgId,
              birth_date: "1974-02-24",
              birth_time: "05:30:00"
            })
          });
        }

        // 2. 리포트 데이터 요청
        const res = await fetch('/api/v1/saju/report', {"""
if old_fetch in jsx_text:
    jsx_text = jsx_text.replace(old_fetch, new_fetch)
    APP_JSX.write_text(jsx_text, encoding="utf-8")
    print("✅ App.jsx에 텔레그램 ID 등록 로직 추가 완료")

# 4. 깃허브 푸시
print("\\n[4] 깃허브 푸시")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "commit", "-m", "feat: add telegram push notification API & frontend registration"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)
print("\\n✅ 깃허브 업로드 완료! Vercel과 Cloud Run이 자동으로 재배포됩니다.")