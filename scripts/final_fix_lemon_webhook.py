import os
import shutil
import subprocess

print("🚀 레몬 스퀴지 1회권 웹 결제 및 내역 버그를 완벽하게 수정합니다...\n")

# 1. 백엔드: billing.py 수정 (order_created 이벤트 처리 추가)
billing_path = "app/api/v1/endpoints/billing.py"
if os.path.exists(billing_path):
    shutil.copy2(billing_path, billing_path + ".bak")
    with open(billing_path, "r", encoding="utf-8") as f:
        content = f.read()

    # order_created 처리 로직 추가 (기존 subscription 처리문 아래에 삽입)
    old_code = '''    elif event_name in ("subscription_cancelled", "subscription_expired"):
        repo.update_subscription(
            user_id=user_id,
            subscription_id=event["data"]["id"],
            status="cancelled",
            current_period_end=None,
            is_premium=False,
        )'''
    
    new_code = '''    elif event_name in ("subscription_cancelled", "subscription_expired"):
        repo.update_subscription(
            user_id=user_id,
            subscription_id=event["data"]["id"],
            status="cancelled",
            current_period_end=None,
            is_premium=False,
        )
    elif event_name == "order_created":
        # 💡 1회성 결제(단품) 웹훅 처리
        order = event["data"]["attributes"]
        variant_id = str(order.get("first_order_item", {}).get("variant_id"))
        onetime_variant = os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID")
        
        if onetime_variant and variant_id == str(onetime_variant):
            repo.add_onetime_credit(user_id)
            repo.log_purchase(user_id, "lemon_onetime", "lemon_squeezy")
        else:
            # 구독 상품 결제인 경우
            repo.update_user_tier(user_id, "premium")
            repo.log_purchase(user_id, "lemon_sub", "lemon_squeezy")'''

    if "order_created" not in content:
        content = content.replace(old_code, new_code)
        with open(billing_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 백엔드: order_created 웹훅 처리 로직 추가 완료")
    else:
        print("ℹ️ 백엔드: order_created 로직이 이미 존재합니다.")

# 2. 프론트엔드: settings.tsx 수정 (lemon_onetime UI 매핑 추가)
settings_path = "frontend/app/(tabs)/settings.tsx"
if os.path.exists(settings_path):
    shutil.copy2(settings_path, settings_path + ".bak")
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 기존 UI 매핑 코드에 lemon_onetime 추가
    old_ui = 'item.product_id === "lemon_sub" ? "프리미엄 구독 (웹 결제)" :'
    new_ui = 'item.product_id === "lemon_sub" ? "프리미엄 구독 (웹 결제)" :\n                 item.product_id === "lemon_onetime" ? "1회 이용권 (웹 결제)" :'
    
    if old_ui in content and "lemon_onetime" not in content:
        content = content.replace(old_ui, new_ui)
        with open(settings_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 프론트엔드: 구매 내역 UI에 'lemon_onetime' 매핑 추가 완료")

print("\n✨ 코드 수정 완료! 터미널에 아래 명령어를 입력하여 배포를 진행하세요.")
print("1. .\\deploy.ps1")
print("2. git add . && git commit -m 'fix: 레몬 스퀴지 1회권 웹훅 최종 수정' && git push origin main")