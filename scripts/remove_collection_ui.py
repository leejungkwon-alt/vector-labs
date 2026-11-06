# scripts/remove_collection_ui.py
"""
'poem.viewCollection' 버튼을 렌더링하는 UI 블록을 완전히 제거.
home.tsx 및 관련 섹션 컴포넌트를 전수 조사하여 타겟팅.
"""
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
FRONTEND = Path("frontend")

# 검색 대상 확장자
extensions = ["*.tsx"]

target_files = []
for ext in extensions:
    target_files.extend(FRONTEND.rglob(ext))

found_count = 0
patched_files = []

# 제거할 패턴 1: <TouchableOpacity ...> ... {t("poem.viewCollection")} ... </TouchableOpacity>
# 제거할 패턴 2: <Link ...> ... viewCollection ... </Link>
# 제거할 패턴 3: {t("poem.viewCollection")} 를 포함하는 Text 블록

# 안전한 정규식 (비탐욕적 매칭)
patterns = [
    # TouchableOpacity 블록
    re.compile(
        r'<TouchableOpacity[^>]*>\s*(?:<[^>]+>\s*)*\{[^\}]*viewCollection[^\}]*\}[^<]*</[^>]+>\s*(?:<[^>]+>\s*)*</TouchableOpacity>',
        re.DOTALL
    ),
    # Link 블록
    re.compile(
        r'<Link[^>]*>.*?viewCollection.*?</Link>',
        re.DOTALL
    ),
    # 혹시 버튼 텍스트만 있는 경우 (Text 만)
    re.compile(
        r'<Text[^>]*>\s*\{[^\}]*viewCollection[^\}]*\}\s*(?:\(\d+\))?\s*</Text>',
        re.DOTALL
    )
]

for p in target_files:
    if any(x in str(p) for x in ["node_modules", "dist", "_expo"]):
        continue
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        continue

    if "viewCollection" not in txt:
        continue

    orig = txt
    print(f"📂 발견: {p} (파일 내에 viewCollection 존재)")

    for i, pattern in enumerate(patterns):
        # 매칭되는 블록 찾기
        matches = pattern.findall(txt)
        if matches:
            print(f"   - 패턴 {i+1} 매칭됨 ({len(matches)}건)")
            # 주석 처리로 안전하게 제거
            def replacer(m):
                return f"{{/* 시조 모아보기 버튼 제거됨 */}}"
            txt = pattern.sub(replacer, txt)

    if txt != orig:
        found_count += 1
        patched_files.append(p)
        if APPLY:
            p.write_text(txt, encoding="utf-8")
            print(f"   ✅ 패치 완료: {p}")
        else:
            print(f"   🧪 미리보기: {p} (적용 예정)")

print()
if found_count == 0:
    print("❌ viewCollection 버튼 블록을 찾지 못했습니다.")
    print("   home.tsx 또는 관련 컴포넌트를 직접 확인해야 합니다.")
    print("   다음 명령어로 주변 코드를 확인해보세요:")
    print("   Get-ChildItem -Path 'frontend' -Recurse -Filter '*.tsx' | Select-String 'viewCollection' -Context 5, 5")
elif not APPLY:
    print(f"🧪 미리보기 완료. 총 {found_count}개 파일 변경 예정.")
    print("   적용: python scripts/remove_collection_ui.py --apply")
else:
    print(f"🎉 패치 완료. 총 {found_count}개 파일 수정됨.")
    print("   다음: git add frontend/ && git commit -m 'remove: collection button UI' && git push origin main")