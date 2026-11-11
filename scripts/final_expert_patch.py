import os
import re
import shutil
import subprocess

print("🚀 전문가 가이드 기반 웹훅 멱등성 최적화 패치 시작...\n")

billing_path = "app/api/v1/endpoints/billing.py"
if os.path.exists(billing_path):
    shutil.copy2(billing_path, billing_path + ".bak")
    with open(billing_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 분기 로직을 멱등성 메서드로 교체
    old_code = '''        order_id = event["data"]["id"]
        try:
            repo.add_onetime_credit(user_id)
            repo.log_purchase(user_id, "lemon_onetime", "lemon_squeezy")
            logger.info("✅ LS order_created success: order=%s, user=%s", order_id, user_id)'''
            
    new_code = '''        order_id = event["data"]["id"]
        try:
            # 💡 멱등성 메서드 적용 (중복 적립 방지)
            granted = repo.add_onetime_purchase_idempotent(user_id, order_id)
            logger.info("✅ LS order_created order=%s user=%s granted=%s", order_id, user_id, granted)'''

    content = content.replace(old_code, new_code)
    
    with open(billing_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ billing.py 멱등성 로직 적용 완료")

# 백엔드 배포
print("\n4. 백엔드 배포 시작 (시크릿 교체 및 코드 반영)...")
try:
    subprocess.run(".\\deploy.ps1", shell=True, check=True)
    print("\n🎉 모든 조치가 완료되었습니다!")
except subprocess.CalledProcessError:
    print("\n⚠️ 배포 실패! 에러를 확인해 주세요.")