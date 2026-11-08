# scripts/fix_dup_api_import.py
"""profileStore.ts 중복 import 제거"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
STORE = Path("frontend/src/store/profileStore.ts")

if not STORE.exists():
    print(f"❌ {STORE} 없음")
    sys.exit(1)

txt = STORE.read_text(encoding="utf-8")
orig = txt

# 중복 라인 제거
DUP = 'import { api } from "@/api/client";\n'
if DUP in txt:
    txt = txt.replace(DUP, "", 1)
    print("✅ 중복 import 제거: @/api/client")
elif 'import { api } from "@/api/client";' in txt:
    # 줄바꿈 없이 있어도 처리
    txt = txt.replace('import { api } from "@/api/client";', "", 1)
    print("✅ 중복 import 제거 (줄바꿈 없음)")

if txt == orig:
    print("ℹ️ 변경 없음")
    sys.exit(0)

# 확인
if txt.count('import { api }') > 1:
    print(f"⚠️ 여전히 api import {txt.count('import { api }')}개 — 수동 확인 필요")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_dup_api_import.py --apply")
    sys.exit(0)

STORE.write_text(txt, encoding="utf-8")
print(f"\n🎉 저장: {STORE}")
print("\n다음:")
print('   git add "frontend/src/store/profileStore.ts"')
print('   git commit -m "fix(profile): remove duplicate api import"')
print("   git push origin main")