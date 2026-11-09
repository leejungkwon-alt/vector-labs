# scripts/patch_compatibility_tsx.py
"""
compatibility.tsx의 4번째 축(axisSinsal) 라벨을 relationshipType에 따라 분기.
- 관계별 로케일 키: axisSinsal_{romance|business|friend|family}
- 기본은 dry-run (diff 미리보기). 실제 적용은 --apply
"""
import re
import sys
import difflib
from pathlib import Path

PATH = Path("frontend/app/(tabs)/compatibility.tsx")

if not PATH.exists():
    print(f"❌ 파일 없음: {PATH}")
    sys.exit(1)

src = PATH.read_text(encoding="utf-8")

USE_STATE_PATTERN = re.compile(
    r'(const \[relationshipType, setRelationshipType\] = useState<[^>]+>\([^)]+\);)'
)
SINSAL_OLD = 't("compatibility.axisSinsal")'

# ---------- 진단 ----------
print("=" * 60)
print("[1] relationshipType useState 매칭")
m = USE_STATE_PATTERN.findall(src)
print(f"    개수: {len(m)}")
for x in m:
    print(f"    → {x[:120]}")

print(f"\n[2] '{SINSAL_OLD}' 출현 횟수: {src.count(SINSAL_OLD)}")
print(f"[3] 이미 SINSAL_AXIS_KEY 존재? {'YES' if 'SINSAL_AXIS_KEY' in src else 'NO'}")
print("=" * 60)

# ---------- 안전성 검증 ----------
if "SINSAL_AXIS_KEY" in src and "--apply" in sys.argv:
    print("⚠️ 이미 패치된 파일입니다. 중단.")
    sys.exit(1)

if len(m) != 1:
    print("❌ useState 매칭이 정확히 1개가 아닙니다. 수동 확인 필요.")
    sys.exit(1)

if src.count(SINSAL_OLD) != 1:
    print(f"❌ axisSinsal 출현이 1회가 아닙니다. 수동 확인 필요.")
    sys.exit(1)

# ---------- 패치 생성 ----------
CONST_BLOCK = """
  const SINSAL_AXIS_KEY = {
    romance: "compatibility.axisSinsal_romance",
    business: "compatibility.axisSinsal_business",
    friend: "compatibility.axisSinsal_friend",
    family: "compatibility.axisSinsal_family",
  } as const;
"""

patched = USE_STATE_PATTERN.sub(
    lambda mt: mt.group(1) + "\n" + CONST_BLOCK,
    src,
    count=1,
)
patched = patched.replace(
    SINSAL_OLD,
    "t(SINSAL_AXIS_KEY[relationshipType])",
    1,
)

# ---------- diff 미리보기 ----------
print("\n===== DIFF PREVIEW =====")
sys.stdout.writelines(
    difflib.unified_diff(
        src.splitlines(keepends=True),
        patched.splitlines(keepends=True),
        fromfile="before",
        tofile="after",
        n=3,
    )
)

if "--apply" not in sys.argv:
    print("\n💡 dry-run입니다. 실제 적용: python scripts/patch_compatibility_tsx.py --apply")
    sys.exit(0)

# ---------- 적용 ----------
backup = PATH.with_suffix(".tsx.bak")
backup.write_text(src, encoding="utf-8")
print(f"\n✅ 백업: {backup}")

PATH.write_text(patched, encoding="utf-8")
print(f"✅ 패치 완료: {PATH}")