import os
import re
import shutil
import subprocess

print("🚀 웹앱 복구 및 텔레그램 공유 조건문을 수정합니다...\n")

file_path = "frontend/app/(tabs)/compatibility.tsx"
if os.path.exists(file_path):
    shutil.copy2(file_path, file_path + ".bak")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 웹앱이 텔레그램 코드를 실행하지 않도록 조건문 강화
    # 기존: if (tg) { ... }
    # 변경: if (tg && tg.platform !== "unknown") { ... }
    content = content.replace("if (tg) {", 'if (tg && tg.platform !== "unknown") {')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ compatibility.tsx 수정 완료 (웹앱은 텔레그램 코드를 무시하도록 수정)")
else:
    print("❌ 파일을 찾을 수 없습니다.")

# 2. 프론트엔드 배포
print("\n2. 프론트엔드 배포를 위해 Git에 푸시합니다...")
try:
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "fix: 웹앱에서 텔레그램 공유 코드가 실행되지 않도록 조건문 강화"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
except subprocess.CalledProcessError:
    print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")