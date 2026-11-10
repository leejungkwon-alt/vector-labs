# scripts/patch_types_labels.py
from pathlib import Path
import sys

PATH = Path("frontend/types.ts")
if not PATH.exists():
    print("❌ frontend/types.ts 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")
old = 'a: { archetype: string; element: string; intensity: string };\n      b: { archetype: string; element: string; intensity: string };'
new = 'a: { archetype: string; element: string; intensity: string; archetype_label?: string; element_label?: string; intensity_label?: string };\n      b: { archetype: string; element: string; intensity: string; archetype_label?: string; element_label?: string; intensity_label?: string };'

if new in src:
    print("⚠️ 이미 적용됨"); sys.exit(0)
if old not in src:
    print("❌ 대상 코드 찾을 수 없음"); sys.exit(1)

PATH.write_text(src.replace(old, new, 1), encoding="utf-8")
print("✅ types.ts 패치 완료")