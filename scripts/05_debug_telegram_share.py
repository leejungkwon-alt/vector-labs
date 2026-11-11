import os
import re
import shutil
import subprocess

print("🚀 [안전 모드] 텔레그램 공유 로직을 강제 디버깅 모드로 교체합니다...\n")

file_path = "frontend/app/(tabs)/compatibility.tsx"
if os.path.exists(file_path):
    shutil.copy2(file_path, file_path + ".bak")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 정규식을 사용해 기존 텔레그램 분기 부분만 정확히 찾아서 교체
    # (웹 로직인 try { ... } 앞부분까지만 교체합니다)
    pattern = r"(const\s+handleShare\s*=\s*async\s*\(\)\s*=>\s*\{)([\s\S]*?)(//\s*👇\s*여기서부터는 기존 웹앱 로직이 그대로 실행됩니다\.)"
    
    new_tma_logic = r'''\1
    const tg = (window as any).Telegram?.WebApp;
    if (tg) {
      try {
        if (typeof tg.openTelegramLink === "function") {
          const inviteId = useAuthStore.getState().user?.id || "unknown";
          const deepLink = `https://t.me/my_vector_labs_bot?startapp=invite_${inviteId}`;
          const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(deepLink)}&text=${encodeURIComponent("내 궁합 결과 확인해 봐! 👇")}`;
          
          // 텔레그램 공유창 호출
          tg.openTelegramLink(shareUrl);
        } else {
          tg.showAlert("이 텔레그램 버전은 공유 기능을 지원하지 않습니다. 업데이트 해주세요.");
        }
      } catch (e: any) {
        // 에러가 나면 텔레그램 화면에 팝업으로 보여줌
        tg.showAlert("공유 에러 발생: " + (e.message || String(e)));
      }
      return;
    }

    \3'''

    new_content, count = re.subn(pattern, new_tma_logic, content)

    if count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ compatibility.tsx 수정 완료 (에러 확인용 Alert 추가)")
    else:
        print("⚠️ handleShare 함수 패턴을 찾지 못했습니다. 수동 확인이 필요합니다.")
else:
    print("❌ 파일을 찾을 수 없습니다.")

# 3. 프론트엔드 배포
print("\n2. 프론트엔드 배포를 위해 Git에 푸시합니다...")
try:
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "fix: 텔레그램 공유 에러 디버깅 로직 추가"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
except subprocess.CalledProcessError:
    print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")