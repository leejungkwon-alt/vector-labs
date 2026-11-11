import os
import re
import shutil
import subprocess

print("🚀 [안전 모드] 웹앱은 건드리지 않고, 텔레그램 전용 공유 로직만 추가합니다...\n")

# 1. compatibility.tsx 파일 찾기
possible_paths = [
    "frontend/app/(tabs)/compatibility.tsx",
    "frontend/app/compatibility.tsx"
]
file_path = None
for p in possible_paths:
    if os.path.exists(p):
        file_path = p
        break

if file_path:
    shutil.copy2(file_path, file_path + ".bak")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1) 깨진 아이콘(□) 수정
    content = content.replace("□ 공유하기", "📤 친구에게 공유하기")

    # 2) 기존 공유 함수를 찾아서 맨 윗줄에 '텔레그램 전용 조건문'만 추가
    # 기존 코드를 지우지 않고 if문만 추가합니다.
    def inject_telegram_logic(match):
        func_header = match.group(1) # const handleShare = async () => {
        func_body = match.group(2)   # 기존 웹앱 로직 (다운로드 등)
        
        # 만약 이미 텔레그램 로직이 들어가 있다면 중복 방지
        if "tg.openTelegramLink" in func_body:
            return match.group(0)

        telegram_code = '''
    // 💡 [안전장치] 텔레그램 환경일 때만 실행되고, 웹 브라우저는 이 코드를 무시합니다.
    const tg = (window as any).Telegram?.WebApp;
    if (tg && tg.initData) {
      const inviteId = useAuthStore.getState().user?.id || "unknown";
      const deepLink = `https://t.me/my_vector_labs_bot?startapp=invite_${inviteId}`;
      const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(deepLink)}&text=${encodeURIComponent("내 궁합 결과 확인해 봐! 👇")}`;
      tg.openTelegramLink(shareUrl);
      return; // 텔레그램 공유를 실행했으므로, 아래의 웹 다운로드 로직은 실행하지 않고 종료!
    }
    
    // 👇 여기서부터는 기존 웹앱 로직이 그대로 실행됩니다. (절대 건드리지 않음)
'''
        
        return func_header + telegram_code + func_body

    # handleShare 함수 패턴 매칭 (함수 헤더와 본문 분리)
    content = re.sub(r"(const\s+handle\w*Share\w*\s*=\s*async\s*\([^)]*\)\s*=>\s*\{)([\s\S]*?\n\s*\};)", inject_telegram_logic, content)

    # useAuthStore 임포트가 없으면 추가
    if "useAuthStore" not in content:
        content = "import { useAuthStore } from '@/store/authStore';\n" + content

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ {file_path} 수정 완료 (웹앱 로직 유지, 텔레그램 분기 추가)")
else:
    print("⚠️ compatibility.tsx 파일을 찾을 수 없습니다.")

# 3. 프론트엔드 배포
print("\n2. 프론트엔드 배포를 위해 Git에 푸시합니다...")
try:
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "feat: 텔레그램 전용 공유 로직 추가 (웹앱 로직 보존)"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
except subprocess.CalledProcessError:
    print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")