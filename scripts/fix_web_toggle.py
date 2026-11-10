from pathlib import Path
import sys

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists(): sys.exit(1)
src = PATH.read_text(encoding="utf-8")

# 기존 useEffect 조건문을 initData 길이 체크로 변경
old_effect = '''  useEffect(() => {
    if (typeof window !== "undefined" && (window as any).Telegram?.WebApp) {
      setIsTgEnv(true);
    }
  }, []);'''

new_effect = '''  useEffect(() => {
    if (typeof window !== "undefined") {
      // 텔레그램 SDK는 웹에서도 객체를 만들기 때문에, initData가 실제로 있는지 확인해야 함
      const tg = (window as any).Telegram?.WebApp;
      setIsTgEnv(!!tg?.initData && tg.initData.length > 0);
    }
  }, []);'''

if old_effect in src:
    src = src.replace(old_effect, new_effect, 1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ 웹 노출 방지 패치 완료")
else:
    print("⚠️ 패턴을 찾지 못했습니다. 수동 확인 필요.")