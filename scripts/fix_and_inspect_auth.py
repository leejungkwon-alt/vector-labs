import glob
import os
import re
import shutil

print("🚀 1. 웹훅 메서드 이름 불일치 수정을 시작합니다...\n")

# 1. telegram.py 웹훅 메서드 이름 수정 (credits -> credit)
telegram_path = "app/api/v1/endpoints/telegram.py"
if os.path.exists(telegram_path):
    shutil.copy2(telegram_path, telegram_path + ".bak")
    with open(telegram_path, "r", encoding="utf-8") as f:
        tg_content = f.read()
    
    if "add_onetime_credits" in tg_content:
        tg_content = tg_content.replace("add_onetime_credits", "add_onetime_credit")
        with open(telegram_path, "w", encoding="utf-8") as f:
            f.write(tg_content)
        print("✅ telegram.py 웹훅 메서드 이름 수정 완료 (add_onetime_credit)")
    else:
        print("ℹ️ telegram.py에 add_onetime_credits가 없습니다 (이미 수정됨).")

# 2. repository.py 중복 메서드 제거 (혹시 모를 중복 방지)
repo_path = "app/auth/repository.py"
if os.path.exists(repo_path):
    with open(repo_path, "r", encoding="utf-8") as f:
        repo_content = f.read()
    
    # 제가 이전에 넣은 복수형 메서드(add_onetime_credits)가 있다면 삭제
    if "def add_onetime_credits" in repo_content:
        # 정규식으로 복수형 메서드 통째로 삭제
        repo_content = re.sub(r"def add_onetime_credits.*?(?=def |$)", "", repo_content, flags=re.DOTALL)
        with open(repo_path, "w", encoding="utf-8") as f:
            f.write(repo_content)
        print("✅ repository.py의 중복 메서드(add_onetime_credits) 삭제 완료")


print("\n🚀 2. /me 엔드포인트와 인증 로직(get_current_user) 코드를 추출합니다...\n")
print("="*60)

# 3. auth.py, dependencies.py 등 관련 파일 찾아서 출력
files_to_check = glob.glob("app/api/v1/endpoints/*.py") + glob.glob("app/auth/*.py")

for filepath in files_to_check:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
        if "def get_current_user" in content:
            print(f"===== [get_current_user 발견] {filepath} =====")
            match = re.search(r"(def get_current_user\(.*?\n(?:.*\n)*?)(?=\ndef |\n@|$)", content)
            if match:
                print(match.group(1).strip())
            print("-" * 60)
            
        if '@router.get("/me")' in content or "@router.get('/me')" in content:
            print(f"===== [/me 엔드포인트 발견] {filepath} =====")
            match = re.search(r"(@router\.get\([\'\"].*/me[\'\"].*?\n(?:.*\n)*?)(?=\ndef |\n@|$)", content)
            if match:
                print(match.group(1).strip())
            print("-" * 60)

print("\n✨ 수정이 완료되었습니다. 위에 출력된 /me 엔드포인트와 get_current_user 코드를 복사해서 저에게 보여주세요!")