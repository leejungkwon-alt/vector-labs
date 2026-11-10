# scripts/patch_telegram_visibility_fix.py
from pathlib import Path
import sys

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 컴포넌트 상단에 텔레그램 감지 상태(useState/useEffect) 추가
# 기존 import 확인
if 'import { useState, useEffect }' not in src:
    src = src.replace('import { useState }', 'import { useState, useEffect }', 1)
elif 'import { useEffect' not in src:
    src = src.replace('import { useState }', 'import { useState, useEffect }', 1)

# 기존 핸들러 근처에 상태 추가
old_state = 'const [isTgLoading, setIsTgLoading] = useState(false);'
new_state = '''const [isTgLoading, setIsTgLoading] = useState(false);
  const [isTgEnv, setIsTgEnv] = useState(false);

  // 화면이 그려진 후 텔레그램 SDK가 로드되었는지 확인
  useEffect(() => {
    if (typeof window !== "undefined" && (window as any).Telegram?.WebApp) {
      setIsTgEnv(true);
    }
  }, []);'''

if 'const [isTgEnv, setIsTgEnv]' not in src:
    src = src.replace(old_state, new_state, 1)

# 2. 기존 UI 조건문을 isTgEnv 상태로 교체 (조건이 더 확실해짐)
old_condition = '{typeof window !== "undefined" && !!(window as any).Telegram?.WebApp?.initData && ('
new_condition = '{isTgEnv && ('

if old_condition in src:
    src = src.replace(old_condition, new_condition, 1)
else:
    print("⚠️ UI 조건문을 찾지 못했습니다. 수동 확인 필요.")

PATH.write_text(src, encoding="utf-8")
print("✅ settings.tsx 텔레그램 감지 로직(useEffect) 수정 완료")