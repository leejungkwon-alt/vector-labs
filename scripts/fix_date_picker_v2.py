# scripts/fix_date_picker_v2.py
"""
BirthDateWheelPicker.tsx 에서 t is not defined 문제 복구.
- useT import 확인/추가
- const t = useT() 함수 본문 삽입 (정규식으로 강제)
"""
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
TSX = Path("frontend/src/components/BirthDateWheelPicker.tsx")

if not TSX.exists():
    print(f"❌ {TSX} 없음")
    sys.exit(1)

txt = TSX.read_text(encoding="utf-8")
orig = txt

# ------- 1) useT import 확인 -------
has_import = ("useT" in txt) and ("from '@/i18n'" in txt or 'from "@/i18n"' in txt)
print(f"1) useT import: {'✅ 있음' if has_import else '❌ 없음'}")

if not has_import:
    old = "import { Picker } from '@react-native-picker/picker';"
    if old in txt:
        txt = txt.replace(old, old + "\nimport { useT } from '@/i18n';", 1)
        print("   → import 추가")
    else:
        print("   ❌ import 지점 못 찾음")
        sys.exit(1)

# ------- 2) const t = useT() 확인 -------
# 컴포넌트 함수 본문 안에 실제로 선언됐는지 (오탐 방지를 위해 "const t = useT()" 문자열로 체크)
has_hook = bool(re.search(r'const\s+t\s*=\s*useT\s*\(\s*\)', txt))
print(f"2) const t = useT(): {'✅ 있음' if has_hook else '❌ 없음'}")

if not has_hook:
    # 함수 정의 찾기: export default function ... ({...}: Props) { 
    pattern = re.compile(
        r'(export\s+default\s+function\s+BirthDateWheelPicker\s*\([^)]*\)\s*\{)',
        re.DOTALL,
    )
    m = pattern.search(txt)
    if not m:
        print("   ❌ 함수 정의 못 찾음")
        sys.exit(1)
    insert_pos = m.end()
    txt = txt[:insert_pos] + "\n  const t = useT();" + txt[insert_pos:]
    print(f"   → 함수 정의 직후 삽입 (offset {insert_pos})")

# ------- 3) 함수 본문 미리보기 -------
m = re.search(
    r'(export\s+default\s+function\s+BirthDateWheelPicker\s*\([^)]*\)\s*\{)([^}]{0,300})',
    txt, re.DOTALL,
)
if m:
    print("\n🩺 [삽입 후 함수 본문 앞부분]")
    for line in (m.group(1) + m.group(2)).splitlines()[:8]:
        print("   " + line)

if txt == orig:
    print("\nℹ️ 변경 없음")
    sys.exit(0)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_date_picker_v2.py --apply")
    sys.exit(0)

TSX.write_text(txt, encoding="utf-8")
print("\n🎉 저장 완료")