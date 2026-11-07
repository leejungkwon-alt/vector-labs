# scripts/remove_poet_field.py
"""
data/poems.json에서 poet 필드 제거.
- 프론트엔드는 poem.poet && 조건이라 필드 없으면 자동 미표시
- "작자 미상", "- OOO -" 등 모든 작자 표시 사라짐
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
POEMS = Path("data/poems.json")

if not POEMS.exists():
    print(f"❌ {POEMS} 없음")
    sys.exit(1)

with open(POEMS, "r", encoding="utf-8") as f:
    data = json.load(f)

poems = data.get("poems", [])
print(f"📖 총 {len(poems)}개 시조\n")

removed = 0
samples = []
for p in poems:
    pid = p.get("id", "?")
    if "poet" in p:
        old = p.pop("poet")
        removed += 1
        if len(samples) < 5:
            samples.append((pid, old))

print(f"🔄 poet 필드 제거: {removed}건")
if samples:
    print("\n샘플:")
    for pid, old in samples:
        print(f"  [{pid}] 삭제됨: {old}")

if not APPLY:
    print(f"\n🧪 미리보기. 적용: python scripts/remove_poet_field.py --apply")
    sys.exit(0)

with open(POEMS, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n🎉 저장 완료: {POEMS}")
print("   다음: .\\deploy.ps1")