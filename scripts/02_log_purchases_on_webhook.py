import os
import re
import shutil

print("🚀 결제 웹훅에 '구매 내역 기록' 로직을 추가합니다...\n")

# =====================================================================
# 1. 텔레그램 웹훅 (telegram.py) 수정
# =====================================================================
telegram_path = "app/api/v1/endpoints/telegram.py"
if os.path.exists(telegram_path):
    shutil.copy2(telegram_path, telegram_path + ".bak")
    with open(telegram_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 구독 결제 시 log_purchase 추가
    if "repo.log_purchase" not in content:
        # 1) sub_ 결제
        content = content.replace(
            'repo.update_user_tier(user_id, "premium")',
            'repo.update_user_tier(user_id, "premium")\n                repo.log_purchase(user_id, "stars_sub", "telegram")'
        )
        # 2) onetime_ 결제
        content = content.replace(
            'repo.add_onetime_credit(user_id)',
            'repo.add_onetime_credit(user_id)\n                repo.log_purchase(user_id, "stars_onetime", "telegram")'
        )
        
        with open(telegram_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ telegram.py 웹훅 내역 기록 추가 완료")
    else:
        print("ℹ️ telegram.py에 이미 내역 기록 로직이 있습니다.")

# =====================================================================
# 2. 레몬 스퀴지 웹훅 (billing.py) 수정
# =====================================================================
billing_path = "app/api/v1/endpoints/billing.py"
if os.path.exists(billing_path):
    shutil.copy2(billing_path, billing_path + ".bak")
    with open(billing_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "repo.log_purchase" not in content:
        # 구독 생성/업데이트 시 log_purchase 추가
        old_code = '''        repo.update_subscription(
            user_id=user_id,
            subscription_id=event["data"]["id"],
            status=status,
            current_period_end=renews_at,
            is_premium=is_premium,
        )'''
        
        new_code = '''        repo.update_subscription(
            user_id=user_id,
            subscription_id=event["data"]["id"],
            status=status,
            current_period_end=renews_at,
            is_premium=is_premium,
        )
        if event_name == "subscription_created":
            repo.log_purchase(user_id, "lemon_sub", "lemon_squeezy")'''

        if old_code in content:
            content = content.replace(old_code, new_code)
            with open(billing_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ billing.py 웹훅 내역 기록 추가 완료")
        else:
            print("⚠️ billing.py의 update_subscription 패턴을 찾지 못했습니다.")
    else:
         print("ℹ️ billing.py에 이미 내역 기록 로직이 있습니다.")

print("\n✨ 수정 완료! 백엔드 배포(.\\deploy.ps1)를 실행해 주세요.")