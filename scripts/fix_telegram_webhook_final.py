import os
import shutil
import subprocess

print("🚀 텔레그램 웹훅 코드의 인자 오류를 수정합니다...\n")

tg_path = "app/api/v1/endpoints/telegram.py"
if os.path.exists(tg_path):
    shutil.copy2(tg_path, tg_path + ".bak")
    with open(tg_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 문제의 코드: repo.add_onetime_credit(user_id, 1) -> user_id 로 수정
    # 또한 log_purchase 도 추가하고, 에러 발생 시 500 반환하도록 수정
    old_code = '''        elif payload.startswith("onetime_"):
            user_id = payload.replace("onetime_", "")
            repo = get_repository()
            try:
                repo.add_onetime_credit(user_id, 1)
                logger.info(f"One-time credit added for user {user_id}")
            except AttributeError:
                logger.error("Repository does not have add_onetime_credit method!")
            except Exception as e:
                logger.error(f"One-time Credit DB Update Error: {e}")'''
                
    new_code = '''        elif payload.startswith("onetime_"):
            user_id = payload.replace("onetime_", "")
            repo = get_repository()
            try:
                # 💡 수정: 두 번째 인자(1) 제거! (메서드는 user_id만 받음)
                repo.add_onetime_credit(user_id)
                # 💡 구매 내역도 함께 기록
                repo.log_purchase(user_id, "stars_onetime", "telegram")
                logger.info(f"✅ [Telegram Webhook] One-time credit added for user {user_id}")
            except Exception as e:
                logger.error(f"❌ [Telegram Webhook] DB Update Error: {e}")
                # 에러 발생 시 텔레그램이 재시도하도록 500 에러 반환
                raise HTTPException(status_code=500, detail="Database update failed")'''

    content = content.replace(old_code, new_code)

    with open(tg_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ telegram.py 웹훅 로직 수정 완료 (인자 제거 및 log_purchase 추가)")
else:
    print("❌ telegram.py 파일을 찾을 수 없습니다.")

# 백엔드 배포
print("\n2. 백엔드 배포 시작...")
try:
    subprocess.run(".\\deploy.ps1", shell=True, check=True)
    print("\n🎉 배포 완료! 이제 가짜 웹훅을 다시 테스트해 보세요.")
except subprocess.CalledProcessError:
    print("\n⚠️ 배포 실패! 에러를 확인해 주세요.")