import os
import shutil
import subprocess

print("🚀 useAuthStore import 누락 문제를 해결합니다...\n")

file_path = "frontend/app/(tabs)/compatibility.tsx"
if os.path.exists(file_path):
    shutil.copy2(file_path, file_path + ".bak")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. useAuthStore import 추가
    import_stmt = "import { useAuthStore } from '@/store/authStore';\n"
    
    # 이미 import 되어 있다면 중복 추가 방지
    if "useAuthStore" not in content.split("\n\n")[0]: # 대략적인 상단 체크
        if import_stmt not in content:
            # 기존 첫 번째 import 문 위에 추가
            import re
            content = re.sub(r"(import .*?;\n)", import_stmt + r"\1", content, count=1)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ useAuthStore import 추가 완료!")
        else:
            print("ℹ️ useAuthStore import가 이미 존재합니다.")
    else:
        print("ℹ️ useAuthStore가 이미 상단에 import 되어 있습니다.")

else:
    print("❌ 파일을 찾을 수 없습니다.")

# 3. 프론트엔드 배포
print("\n2. 프론트엔드 배포를 위해 Git에 푸시합니다...")
try:
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "fix: compatibility.tsx useAuthStore import 누락 수정"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
except subprocess.CalledProcessError:
    print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")