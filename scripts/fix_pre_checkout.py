# scripts/fix_pre_checkout.py
from pathlib import Path
import sys
import re

PATH = Path("app/api/v1/endpoints/telegram.py")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

if "pre_checkout_query" in src:
    print("⚠️ 이미 pre_checkout_query 처리가 존재합니다.")
    sys.exit(0)

# 기존 webhook 함수 찾기
pattern = r'(@router\.post\("/webhook"\)[\s\S]*?def telegram_payment_webhook\(request: Request\):[\s\S]*?)(return \{"ok": True\})'
match = re.search(pattern, src)

if not match:
    print("❌ webhook 함수를 찾지 못했습니다. 수동 확인 필요.")
    sys.exit(1)

# pre_checkout_query 처리 로직 삽입
new_logic = '''    update = await request.json()
    
    # 1. 결제 사전 확인 (pre_checkout_query) 처리 - 10초 내 응답 필수
    pre_checkout = update.get("pre_checkout_query")
    if pre_checkout:
        import os, httpx
        bot_token = os.getenv("SAJU_TELEGRAM_BOT_TOKEN")
        query_id = pre_checkout["id"]
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{bot_token}/answerPreCheckoutQuery",
                json={"pre_checkout_query_id": query_id, "ok": True}
            )
        return {"ok": True}

    # 2. 결제 완료 (successful_payment) 처리
    msg = update.get("message", {})
    successful_payment = msg.get("successful_payment")
    # ... (기존 코드 유지)'''

# 기존 로직 앞부분을 새로운 로직으로 교체
old_start = '''    update = await request.json()
    msg = update.get("message", {})
    successful_payment = msg.get("successful_payment")'''

if old_start in src:
    src = src.replace(old_start, new_logic, 1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ pre_checkout_query 처리 로직 추가 완료")
else:
    print("❌ 기존 update 로직을 찾지 못했습니다. 수동 확인 필요.")