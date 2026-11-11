import os
import re
import shutil
import subprocess

print("🚀 줄바꿈 문자 제거 및 웹훅 멱등성 최적화 패치 시작...\n")

# 1. lemonsqueezy_client.py 수정 (_env 헬퍼 추가 및 strip 적용)
client_path = "app/services/lemonsqueezy_client.py"
if os.path.exists(client_path):
    shutil.copy2(client_path, client_path + ".bak")
    with open(client_path, "r", encoding="utf-8") as f:
        content = f.read()

    # _env 헬퍼 함수 추가
    if "def _env(" not in content:
        content = content.replace("LS_API =", "def _env(name: str, default: str = \"\") -> str:\n    return os.environ.get(name, default).strip()\n\nLS_API =")

    # 환경변수 읽는 부분 교체
    content = content.replace('os.environ[\'LEMONSQUEEZY_API_KEY\']', '_env("LEMONSQUEEZY_API_KEY")')
    content = content.replace('os.environ["LEMONSQUEEZY_API_KEY"]', '_env("LEMONSQUEEZY_API_KEY")')
    content = content.replace('os.environ["LEMONSQUEEZY_STORE_ID"]', '_env("LEMONSQUEEZY_STORE_ID")')
    content = content.replace('os.environ["LEMONSQUEEZY_VARIANT_ID"]', '_env("LEMONSQUEEZY_VARIANT_ID")')

    with open(client_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ lemonsqueezy_client.py: 환경변수 공백 제거(.strip) 적용 완료")

# 2. billing.py 수정 (strip 적용 및 멱등성 메서드 적용)
billing_path = "app/api/v1/endpoints/billing.py"
if os.path.exists(billing_path):
    shutil.copy2(billing_path, billing_path + ".bak")
    with open(billing_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 웹훅 시크릿 및 variant ID 공백 제거
    content = content.replace('os.environ.get("LEMONSQUEEZY_WEBHOOK_SECRET", "")', 'os.environ.get("LEMONSQUEEZY_WEBHOOK_SECRET", "").strip()')
    content = content.replace('os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID")', '(os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID") or "").strip()')

    # 멱등성 메서드 적용
    old_idempotency = '''        try:
            repo.add_onetime_credit(user_id)
            repo.log_purchase(user_id, "lemon_onetime", "lemon_squeezy")
            logger.info("✅ LS order_created success: order=%s, user=%s", order_id, user_id)'''
    new_idempotency = '''        try:
            granted = repo.add_onetime_purchase_idempotent(user_id, order_id)
            logger.info("✅ LS order_created order=%s user=%s granted=%s", order_id, user_id, granted)'''
    
    content = content.replace(old_idempotency, new_idempotency)

    with open(billing_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ billing.py: 공백 제거 및 멱등성(add_onetime_purchase_idempotent) 적용 완료")

print("\n✨ 코드 수정 완료! 이제 백엔드를 배포하세요: .\\deploy.ps1")