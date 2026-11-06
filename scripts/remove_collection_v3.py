# scripts/remove_collection_v3.py
"""
강력 제거: router.push('/collection'), <Link>, 그리고 빈 버튼 블록까지.
"""
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
TARGETS = [p for p in Path("frontend").rglob("*.tsx")
           if not any(x in str(p) for x in ["node_modules", "dist", "_expo"])]

def remove_empty_touchable(txt):
    """viewCollection 참조가 있거나 /collection으로 가는 TouchableOpacity 블록 통째 제거"""
    # 정규식으로 <TouchableOpacity ...> ... (viewCollection OR /collection) ... </TouchableOpacity>
    pattern = re.compile(
        r'<TouchableOpacity\b[^>]*(?:'
        r'router\.(?:push|replace)\([\'"]/?collection[\'"]'
        r'|viewCollection'
        r')[^>]*>.*?</TouchableOpacity>',
        re.DOTALL,
    )
    return pattern.subn('{/* 시조 모아보기 제거됨 */}', txt)

def remove_router_push(txt):
    """router.push('/collection') → 주석으로"""
    new_txt, n = re.subn(
        r'router\.(?:push|replace)\(\s*[\'"]/?collection[\'"]\s*\)',
        '/* 시조 모아보기 제거됨 */',
        txt,
    )
    return new_txt, n

def remove_link(txt):
    """<Link href="...collection...">...</Link> 통째 제거"""
    new_txt, n = re.subn(
        r'<Link\b[^>]*href=[\'"][^\'"]*collection[^\'"]*[\'"][^>]*>.*?</Link>',
        '{/* 시조 모아보기 링크 제거됨 */}',
        txt, flags=re.DOTALL,
    )
    return new_txt, n

total_files = 0
for p in TARGETS:
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        continue
    if "collection" not in txt.lower():
        continue

    orig = txt
    actions = []

    txt, n1 = remove_empty_touchable(txt)
    if n1: actions.append(f"TouchableOpacity 블록 제거 {n1}건")

    txt, n2 = remove_router_push(txt)
    if n2: actions.append(f"router.push('/collection') 제거 {n2}건")

    txt, n3 = remove_link(txt)
    if n3: actions.append(f"Link 블록 제거 {n3}건")

    if txt != orig:
        total_files += 1
        print(f"📂 {p.relative_to(Path('.'))}")
        for a in actions:
            print(f"   ✅ {a}")
        if APPLY:
            p.write_text(txt, encoding="utf-8")

if total_files == 0:
    print("❌ 자동 매칭 실패. 아래 명령어로 실제 코드 확인 필요:")
    print('   Get-ChildItem -Path "frontend" -Recurse -Filter "*.tsx" | Select-String "collection" -Context 5,5')
elif not APPLY:
    print(f"\n🧪 미리보기. 총 {total_files}개 파일 변경 예정.")
    print("   적용: python scripts/remove_collection_v3.py --apply")
else:
    print(f"\n🎉 완료. 다음:")
    print("   git add frontend/")
    print('   git commit -m "remove: collection link and button"')
    print("   git push origin main")