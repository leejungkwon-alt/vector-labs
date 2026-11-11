import os
import re
import shutil
import subprocess

print("🚀 텔레그램 스타 결제 웹훅 로직을 강제로 수리합니다...\n")

tg_path = "app/api/v1/endpoints/telegram.py"
if os.path.exists(tg_path):
    shutil.copy2(tg_path, tg_path + ".bak")
    with open(tg_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 onetime_ 처리 로직을 찾아서 확실하게 DB에 반영하도록 교체
    # (기존 코드가 try-except로 에러를 숨기고 있거나 메서드 이름이 틀렸을 수 있음)
    
    # 1. repo.add_onetime_credit 부분이 제대로 되어 있는지 확인
    if "repo.add_onetime_credit(user_id)" not in content and "repo.add_onetime_credit(user_id, 1)" not in content:
        # 기존 로직 대체
        old_code = '''        elif payload.startswith("onetime_"):
            user_id = payload.replace("onetime_", "")
            repo = get_repository()
            try:
                repo.add_onetime_credits(user_id, 1)
                logger.info(f"One-time credit added for user {user_id}")
            except AttributeError:
                logger.error("Repository does not have add_onetime_credits method!")
            except Exception as e:
                logger.error(f"One-time Credit DB Update Error: {e}")'''
                
        new_code = '''        elif payload.startswith("onetime_"):
            user_id = payload.replace("onetime_", "")
            repo = get_repository()
            try:
                # 확실하게 크레딧 적립
                repo.add_onetime_credit(user_id)
                repo.log_purchase(user_id, "stars_onetime", "telegram")
                logger.info(f"✅ [Telegram Webhook] One-time credit added for user {user_id}")
            except Exception as e:
                logger.error(f"❌ [Telegram Webhook] DB Update Error: {e}")
                # 에러가 나면 텔레그램이 재시도하도록 500 에러를 던짐
                raise HTTPException(status_code=500, detail="Database update failed")'''

        if old_code in content:
            content = content.replace(old_code, new_code)
            with open(tg_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ telegram.py 웹훅 코드 수리 완료 (에러 발생 시 500 반환)")
        else:
            print("⚠️ telegram.py에서 onetime_ 분기 패턴을 찾지 못했습니다. 파일을 직접 확인해주세요.")
    else:
        print("ℹ️ telegram.py에 add_onetime_credit 로직이 이미 존재합니다.")

# 백엔드 배포
print("\n2. 백엔드 배포 시작 (몇 분 소요)...")
try:
    subprocess.run(".\\deploy.ps1", shell=True, check=True)
    print("\n🎉 배포 완료! 이제 다시 가짜 웹훅을 쏘거나 실제 결제를 테스트하세요.")
except subprocess.CalledProcessError:
    print("\n⚠️ 배포 실패! 에러를 확인해 주세요.")