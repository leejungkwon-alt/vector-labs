# scripts/fix_band_rounding.py
"""
프론트엔드 표시(Math.round)와 백엔드 인덱스 계산을 정확히 일치시킴.
- 현재: int(s100 // 20)  → 59.5가 idx 2로 떨어짐
- 수정: round(s100) // 20 → 59.5가 60으로 반올림되어 idx 3
"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
WRITER = Path("app/services/compatibility_writer.py")

if not WRITER.exists():
    print(f"❌ {WRITER} 없음")
    sys.exit(1)

txt = WRITER.read_text(encoding="utf-8")
orig = txt

# 현재 로직
old_logic = 'idx = min(n - 1, max(0, int(s // (100.0 / n))))'
new_logic = 'idx = min(n - 1, max(0, int(round(s) * n // 100)))  # 표시 반올림과 정확히 일치'

if old_logic in txt:
    txt = txt.replace(old_logic, new_logic, 1)
    print("✅ NEUTRAL 인덱스 로직 반올림 적용")
elif 'int(round(s) * n // 100)' in txt:
    print("ℹ️ 이미 반올림 로직 적용됨")
    sys.exit(0)
else:
    print("❌ 패턴 불일치. writer.py 수동 확인 필요")
    print("   [현재 NEUTRAL 블록]")
    import re
    m = re.search(r'if overall\["grade"\] == "NEUTRAL".*?overall_content = variants\[idx\]', txt, re.DOTALL)
    if m:
        print(m.group(0))
    sys.exit(1)

# 검증 계산 미리보기
print("\n🩺 검증 (n=5, 각 20점 구간):")
for raw_score in [0.04, 0.19, 0.20, 0.39, 0.40, 0.60]:
    s = (raw_score + 1) / 2 * 100
    display = round(s)  # 프론트 Math.round와 동일
    old_idx = min(4, max(0, int(s // 20)))
    new_idx = min(4, max(0, int(round(s) * 5 // 100)))
    marker = " ⭐" if old_idx != new_idx else ""
    print(f"  raw={raw_score:+.2f} → s100={s:5.1f} → display={display:3d} → old_idx={old_idx}, new_idx={new_idx}{marker}")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_band_rounding.py --apply")
    sys.exit(0)

WRITER.write_text(txt, encoding="utf-8")
print("\n🎉 패치 완료. 다음:")
print("   .\\deploy.ps1")