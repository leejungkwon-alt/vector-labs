# scripts/remove_hardcoded_age_icon.py
"""
compatibility.tsx 에서 하드코딩된 큰 이모지(🔞) 제거.
(텍스트 제목에 이미 🚫 아이콘이 포함되어 있으므로 중복 제거)
"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
TSX = Path("frontend/app/(tabs)/compatibility.tsx")

if not TSX.exists():
    print(f"❌ {TSX} 없음")
    sys.exit(1)

txt = TSX.read_text(encoding="utf-8")
orig = txt

# 하드코딩된 이모지 라인 제거
old_line = '<Text style={{ fontSize: 40, marginBottom: 12 }}>🔞</Text>'
if old_line in txt:
    txt = txt.replace(old_line, '', 1)
    print("✅ 하드코딩된 🔞 아이콘 제거 완료")
else:
    print("ℹ️ 🔞 아이콘을 찾지 못했습니다 (이미 제거되었거나 코드가 다름)")

# 혹시 남아있을 수 있는 다른 형태의 하드코딩 제거
import re
pattern = r'<Text[^>]*>\s*🔞\s*</Text>'
txt, n = re.subn(pattern, '', txt)
if n > 0:
    print(f"✅ 추가 정규식으로 {n}건 제거 완료")

if txt == orig:
    print("ℹ️ 변경 사항 없음")
    sys.exit(0)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/remove_hardcoded_age_icon.py --apply")
    sys.exit(0)

TSX.write_text(txt, encoding="utf-8")
print("\n🎉 저장 완료. 다음:")
print("   git add frontend/app/(tabs)/compatibility.tsx")
print('   git commit -m "fix(compat): remove hardcoded 18+ icon"')
print("   git push origin main")