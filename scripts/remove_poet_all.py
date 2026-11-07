# scripts/remove_poet_all.py
"""
1) PoemFlipCard.tsx의 poet 렌더링 완전 제거
2) '작자 미상' 하드코딩 제거
3) getPoetName 함수 제거
"""
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
TSX = Path("frontend/src/components/poem/PoemFlipCard.tsx")

if not TSX.exists():
    print(f"❌ {TSX} 없음")
    sys.exit(1)

txt = TSX.read_text(encoding="utf-8")
orig = txt
changes = []

# 1) getPoetName 함수 정의 제거
pattern_func = re.compile(
    r'(?:const|function)\s+getPoetName\s*=\s*\([^)]*\)\s*=>\s*\{[^}]*\}|'
    r'function\s+getPoetName\s*\([^)]*\)\s*\{[^}]*\}',
    re.DOTALL,
)
txt, n = pattern_func.subn('', txt)
if n:
    changes.append(f"getPoetName 함수 {n}개 제거")

# 2) poet 렌더링 블록 제거 (여러 형태 대응)
patterns = [
    # {poem.poet && <Text ...>- {getPoetName(poem.poet)} -</Text>}
    r'\{poem\.poet\s*&&\s*<Text[^>]*>[^<]*\{[^}]*getPoetName[^}]*\}[^<]*</Text>\}',
    # <Text ...>- {getPoetName(poem.poet)} -</Text>
    r'<Text[^>]*>[^<]*\{[^}]*getPoetName[^}]*\}[^<]*</Text>',
    # <Text ...>작자 미상</Text>
    r'<Text[^>]*>\s*작자\s*미상\s*</Text>',
    # 그냥 작자 미상 문자열
    r'[\'\"]작자\s*미상[\'\"]',
]
for i, pat in enumerate(patterns):
    txt, n = re.subn(pat, '', txt)
    if n:
        changes.append(f"poet 렌더링 패턴 {i+1}: {n}개")

# 3) 스타일 정의 제거 (poet 스타일)
txt, n = re.subn(r'\s*poet:\s*\{[^}]*\},?', '', txt)
if n:
    changes.append(f"poet 스타일 {n}개 제거")

# 4) import에서도 getPoetName 제거 (혹시 import 목록에 있으면)
txt = re.sub(r'\bgetPoetName\s*,\s*', '', txt)

print("=" * 55)
print("PoemFlipCard.tsx 정리")
print("=" * 55)
for c in changes:
    print(f"  ✅ {c}")

if txt == orig:
    print("\nℹ️ 변경 사항 없음")
    sys.exit(0)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/remove_poet_all.py --apply")
    sys.exit(0)

TSX.write_text(txt, encoding="utf-8")
print(f"\n🎉 저장: {TSX}")
print("\n다음 두 명령을 모두 실행하세요:")
print("   .\\deploy.ps1                              ← 백엔드 재배포 (poems.json 새로 반영)")
print("   git add frontend/ && git commit -m 'fix: remove poet rendering' && git push origin main")