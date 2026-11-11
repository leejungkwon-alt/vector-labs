import os
import re
import subprocess

print("🚀 텔레그램 미니앱 다크모드 및 뒤로가기 버튼 연동을 시작합니다...\n")

# 1. 텔레그램 UX 훅(Hook) 생성
os.makedirs("frontend/src/hooks", exist_ok=True)
hook_path = "frontend/src/hooks/useTelegramUX.ts"
hook_code = """import { useEffect } from 'react';
import { Platform } from 'react-native';
import { useRouter, usePathname } from 'expo-router';

export function useTelegramUX() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (Platform.OS !== 'web') return;
    const tg = (window as any).Telegram?.WebApp;
    if (!tg) return;

    // 1. 테마(다크모드) 동기화
    tg.ready();
    const bgColor = tg.themeParams?.bg_color || (tg.colorScheme === 'dark' ? '#1c1c1e' : '#ffffff');
    document.body.style.backgroundColor = bgColor;

    // 2. 뒤로가기 버튼 연동
    const handleBack = () => {
      if (router.canGoBack()) {
        router.back();
      }
    };

    const isRoot = ['/home', '/', '/daily', '/settings', '/compatibility'].includes(pathname);
    if (isRoot) {
      tg.BackButton.hide();
    } else {
      tg.BackButton.show();
      tg.BackButton.onClick(handleBack);
    }

    return () => {
      tg.BackButton.offClick(handleBack);
    };
  }, [router, pathname]);
}
"""
with open(hook_path, "w", encoding="utf-8") as f:
    f.write(hook_code)
print("✅ useTelegramUX 훅 생성 완료")

# 2. _layout.tsx에 훅 적용
layout_path = "frontend/app/_layout.tsx"
if os.path.exists(layout_path):
    with open(layout_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "useTelegramUX" not in content:
        # import 추가
        if "import { Stack" in content:
            content = content.replace("import { Stack", "import { useTelegramUX } from '@/hooks/useTelegramUX';\nimport { Stack")
        else:
            content = "import { useTelegramUX } from '@/hooks/useTelegramUX';\n" + content

        # 함수 본문 최상단에 훅 호출 삽입 (RootLayout, Layout 등)
        content = re.sub(r"(export default function \w+\([^)]*\)\s*\{)", r"\1\n  useTelegramUX();", content, count=1)
        
        with open(layout_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ _layout.tsx에 다크모드/뒤로가기 연동 완료")
    else:
        print("ℹ️ _layout.tsx에 이미 훅이 적용되어 있습니다.")
else:
    print("❌ _layout.tsx 파일을 찾을 수 없습니다.")

# 3. 프론트엔드 배포
print("\n2. 프론트엔드 배포를 위해 Git에 푸시합니다...")
try:
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "feat: 텔레그램 다크모드 및 뒤로가기 버튼 연동"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("🎉 프론트엔드 푸시 완료! (Vercel 자동 배포)")
except subprocess.CalledProcessError:
    print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")
