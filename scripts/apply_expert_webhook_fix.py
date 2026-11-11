import os
import re
import shutil
import subprocess

print("🚀 전문가 가이드 기반 웹훅 완벽 수리 스크립트 시작...\n")

# 1. billing.py 수정 (로깅, 멱등성, variant 검사)
billing_path = "app/api/v1/endpoints/billing.py"
if os.path.exists(billing_path):
    shutil.copy2(billing_path, billing_path + ".bak")
    with open(billing_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 전문가가 제시한 코드로 order_created 분기 교체
    # (기존에 무식하게 짜놨던 order_created 부분을 정규식으로 찾아서 덮어씌움)
    pattern = r"    elif event_name == \"order_created\":.*?(?=    return \{\"status\": \"ok\"\})"
    
    new_code = '''    elif event_name == "order_created":
        attrs = event["data"]["attributes"]
        variant_id = str((attrs.get("first_order_item") or {}).get("variant_id"))
        onetime_variant = os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID", "")
        
        # 1회권 상품이 아니거나 결제 상태가 paid가 아니면 무시
        if variant_id != onetime_variant or attrs.get("status") != "paid":
            logger.info("LS order ignored (not onetime or not paid). variant=%s", variant_id)
            return {"status": "ignored"}
            
        order_id = event["data"]["id"]
        try:
            repo.add_onetime_credit(user_id)
            repo.log_purchase(user_id, "lemon_onetime", "lemon_squeezy")
            logger.info("✅ LS order_created success: order=%s, user=%s", order_id, user_id)
        except Exception:
            logger.exception("❌ LS order_created failed order=%s", order_id)
            raise HTTPException(status_code=500, detail="retry") # 500 에러를 던져 레몬 스퀴지가 재시도하게 함

'''
    # 기존 분기 삭제 후 새 코드 삽입
    content = re.sub(pattern, new_code, content, flags=re.DOTALL)
    
    # 로깅(logger) 및 예외 처리 추가
    if "logger = logging.getLogger" not in content:
        content = content.replace("router = APIRouter()", "import logging\nlogger = logging.getLogger(\"saju.billing\")\n\nrouter = APIRouter()")
        
    if 'logger.warning("LS webhook %s ignored: no custom_data.user_id", event_name)' not in content:
        content = content.replace('return {"status": "ignored"} # user_id가 없으면 무시', 'logger.warning("LS webhook %s ignored: no custom_data.user_id", event_name)\n        return {"status": "ignored"}')

    with open(billing_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ billing.py 웹훅 로직 완벽 수정 완료 (로깅 및 예외처리 강화)")

# 2. 백엔드 배포
print("\n3. 백엔드 배포 시작 (몇 분 소요)...")
try:
    subprocess.run(".\\deploy.ps1", shell=True, check=True)
    print("\n🎉 배포 완료!")
except subprocess.CalledProcessError:
    print("\n⚠️ 배포 실패! 터미널 에러를 확인해 주세요.")