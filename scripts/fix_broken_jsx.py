# scripts/fix_broken_jsx.py
from pathlib import Path
import sys

PATH = Path("frontend/src/components/BirthDateWheelPicker.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

if "  return (\n    <>\n      {Platform.OS === 'web' ? (" in src:
    print("⚠️ 이미 문법이 수정되어 있습니다.")
    sys.exit(0)

if "  return (\n    {Platform.OS === 'web' ? (" not in src:
    print("❌ 깨진 패턴을 찾지 못했습니다. 수동 확인이 필요합니다.")
    sys.exit(1)

# 1. return ( 바로 뒤에 Fragment(<> ) 열기
src = src.replace(
    "  return (\n    {Platform.OS === 'web' ? (",
    "  return (\n    <>\n      {Platform.OS === 'web' ? (",
    1
)

# 2. return 문이 끝나는 지점에 Fragment(</>) 닫기
src = src.replace(
    "    )}\n  );\n}",
    "    )}\n    </>\n  );\n}",
    1
)

PATH.write_text(src, encoding="utf-8")
print("✅ JSX 문법 오류 복구 완료 (Fragment로 감쌈)")