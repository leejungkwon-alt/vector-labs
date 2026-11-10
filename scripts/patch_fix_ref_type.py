# scripts/patch_fix_ref_type.py
from pathlib import Path
import sys

PATH = Path("frontend/app/(tabs)/compatibility.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

old = "const shareRef = useRef<View>(null);"
new = "const shareRef = useRef<any>(null);"

if new in src:
    print("⚠️ 이미 적용됨"); sys.exit(0)
if old not in src:
    print("❌ 대상 코드 못 찾음. 수동 확인 필요."); sys.exit(1)

PATH.write_text(src.replace(old, new, 1), encoding="utf-8")
print("✅ useRef 타입 수정 완료 (useRef<any>)")