import os
import re
import shutil
import subprocess

print("🚀 텔레그램/웹 환경에 맞춰 로그인 제공자 UI를 수정합니다...\n")

path = "frontend/app/(tabs)/settings.tsx"
if os.path.exists(path):
    shutil.copy2(path, path + ".bak")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # getLoginProvider 함수 전체를 찾아서 텔레그램 환경 분기 추가
    old_func_pattern = r"const getLoginProvider = \(\) => \{[\s\S]*?\};"
    
    new_func = '''const getLoginProvider = () => {
    if (!user) return t("settings.loginNotSet");
    if (user.is_anonymous) return t("settings.loginAnonymous");
    
    // 💡 텔레그램 환경에서는 무조건 텔레그램으로 표시
    if (isTgEnv) {
      return "Telegram 연동됨";
    }
    
    // 웹 환경에서는 기존 소셜 로그인 정보 표시
    const provider = user.social_provider
      ? user.social_provider.charAt(0).toUpperCase() + user.social_provider.slice(1)
      : "Social";
    return t("settings.loginSocial", { provider });
  };'''

    content = re.sub(old_func_pattern, new_func, content, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ settings.tsx 수정 완료 (isTgEnv 분기 추가)")

    # 프론트엔드 배포 (Git Push)
    print("\n2. 프론트엔드 배포를 위해 Git에 푸시합니다...")
    try:
        subprocess.run("git add .", shell=True, check=True)
        subprocess.run('git commit -m "fix: 텔레그램 환경에서 로그인 제공자 텍스트 분기 처리"', shell=True, check=True)
        subprocess.run("git push origin main", shell=True, check=True)
        print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
    except subprocess.CalledProcessError:
        print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")
else:
    print("❌ settings.tsx 파일을 찾을 수 없습니다.")