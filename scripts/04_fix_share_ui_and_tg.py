import os
import re
import shutil
import subprocess

print("🚀 [안전 모드] 깨진 아이콘 교체 및 텔레그램 공유 로직을 수정합니다...\n")

file_path = "frontend/app/(tabs)/compatibility.tsx"
if os.path.exists(file_path):
    shutil.copy2(file_path, file_path + ".bak")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 텔레그램 조건 완화 (initData가 없어도 텔레그램 환경이면 무조건 실행)
    content = content.replace("if (tg && tg.initData) {", "if (tg) {")

    # 2. 깨진 Ionicons(□)를 이모지(📤)로 교체하여 빈 박스 제거
    # 기존: <Ionicons name="share-outline" size={20} color="#FFF" style={{ marginRight: 8 }} />
    old_icon_pattern = r"<Ionicons\s+name=\"share-outline\"\s+size=\{20\}\s+color=\"#FFF\"\s+style=\{\{\s*marginRight:\s*8\s*\}\}\s*/>"
    new_icon = '<Text style={{ fontSize: 20, color: "#FFF", marginRight: 8 }}>📤</Text>'
    
    content = re.sub(old_icon_pattern, new_icon, content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ compatibility.tsx 수정 완료 (빈 박스 제거 및 텔레그램 공유 조건 완화)")
else:
    print("❌ 파일을 찾을 수 없습니다.")

# 3. 프론트엔드 배포
print("\n2. 프론트엔드 배포를 위해 Git에 푸시합니다...")
try:
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "fix: 공유 버튼 깨진 아이콘 수정 및 텔레그램 공유 로직 안정화"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
except subprocess.CalledProcessError:
    print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")