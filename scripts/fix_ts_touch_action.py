# scripts/fix_ts_touch_action.py
from pathlib import Path
import sys

PATH = Path("frontend/src/components/BirthDateWheelPicker.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 문제가 된 style 객체에 as any 추가
old_style = "<View style={{ position: 'fixed' as any, top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999, touchAction: 'manipulation' }}>"
new_style = "<View style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999, touchAction: 'manipulation' } as any}>"

if old_style in src:
    src = src.replace(old_style, new_style, 1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ touchAction 타입 에러 수정 완료 (style 객체 전체에 as any 적용)")
else:
    print("⚠️ 대상 코드를 찾지 못했습니다. 이미 수정되었거나 형태가 다를 수 있습니다.")