import os
import re
import shutil
import subprocess

print("🚀 텔레그램 환경 전용 공유 로직을 추가합니다 (웹 로직 보존)...\n")

file_path = "frontend/app/(tabs)/compatibility.tsx"
if os.path.exists(file_path):
    shutil.copy2(file_path, file_path + ".bak")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 현재 handleShare 함수 시작 부분을 찾아 텔레그램 분기 삽입
    # (기존 원본 코드 유지하면서 맨 앞에 텔레그램 처리만 추가)
    old_start = '''const handleShare = async () => {
    try {
      if (!shareRef.current) return;'''
      
    new_start = '''const handleShare = async () => {
    // 💡 텔레그램 환경에서는 웹뷰 다운로드가 안 되므로 안내창 표시
    const tg = (window as any).Telegram?.WebApp;
    if (tg && tg.initData) {
      tg.showAlert("이미지로 저장하시려면 화면을 캡처해 주세요!\\n(아래 '나도 내 궁합 확인하러 가기' 링크를 친구에게 공유할 수도 있습니다.)");
      return;
    }

    try {
      if (!shareRef.current) return;'''

    if old_start in content:
        content = content.replace(old_start, new_start)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 텔레그램 전용 안내 로직 추가 완료!")
    else:
        print("⚠️ handleShare 시작 부분을 찾지 못했습니다. 수동 확인 필요.")

    print("\n✨ 프론트엔드 배포를 위해 Git에 푸시합니다...")
    try:
        subprocess.run("git add .", shell=True, check=True)
        subprocess.run('git commit -m "fix: 텔레그램 환경에서 공유 시 안내창 표시"', shell=True, check=True)
        subprocess.run("git push origin main", shell=True, check=True)
        print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
    except subprocess.CalledProcessError:
        print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")
else:
    print("❌ 파일을 찾을 수 없습니다.")
