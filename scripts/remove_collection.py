# scripts/remove_collection.py
"""
'시조 모아보기' 기능 완전 제거:
1) frontend/app/collection.tsx 파일 삭제
2) home.tsx 에서 collection 으로 가는 진입점(버튼/링크) 제거
3) 5개 언어 JSON에서 poem.collection 관련 키 삭제
"""
import json
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ============ 1) collection.tsx 파일 삭제 ============
COLLECTION = Path("frontend/app/collection.tsx")
if COLLECTION.exists():
    if APPLY:
        COLLECTION.unlink()
        print(f"🗑️ 삭제 완료: {COLLECTION}")
    else:
        print(f"🧪 삭제 예정: {COLLECTION}")
else:
    print(f"ℹ️ 이미 없음: {COLLECTION}")

# ============ 2) home.tsx 진입점 제거 ============
HOME = Path("frontend/app/(tabs)/home.tsx")
if HOME.exists():
    txt = HOME.read_text(encoding="utf-8")
    orig = txt

    # (a) router.push("/collection") 또는 router.push('collection') 제거
    # 주변 문맥을 통째로 날리지 않기 위해, onPress={...} 내부의 호출만 비활성화
    txt = re.sub(
        r'(onPress\s*=\s*\{[^}]*?)router\.push\([\'"]/collection[\'"]\)([^}]*?\})',
        r'\1/* 시조 모아보기 제거됨 */\2',
        txt,
    )
    txt = re.sub(
        r'(onPress\s*=\s*\{[^}]*?)router\.push\([\'"]collection[\'"]\)([^}]*?\})',
        r'\1/* 시조 모아보기 제거됨 */\2',
        txt,
    )

    # (b) <Link href="/collection">...</Link> 통째로 제거
    txt = re.sub(
        r'<Link\s+href=[\'"]/?collection[\'"][^>]*>.*?</Link>',
        '{/* 시조 모아보기 링크 제거됨 */}',
        txt, flags=re.DOTALL,
    )

    # (c) 'collection' 텍스트가 포함된 TouchableOpacity 블록 제거 (있을 시)
    txt = re.sub(
        r'<TouchableOpacity[^>]*onPress\s*=\s*\{[^}]*collection[^}]*\}[^>]*>.*?</TouchableOpacity>',
        '{/* 시조 모아보기 버튼 제거됨 */}',
        txt, flags=re.DOTALL,
    )

    if txt != orig:
        print("✅ home.tsx: collection 진입점 제거")
        # 미리보기: 제거된 라인 주변 확인
        for line in txt.splitlines():
            if "제거됨" in line and "시조" in line:
                print(f"   → {line.strip()[:100]}")
        if APPLY:
            HOME.write_text(txt, encoding="utf-8")
    else:
        print("⚠️ home.tsx: 정규식으로 collection 진입점을 찾지 못했습니다.")
        print("   아래 명령어로 실제 코드를 확인해주세요:")
        print("   Get-Content 'frontend/app/(tabs)/home.tsx' | Select-String 'collection' -Context 3,3")

# ============ 3) JSON에서 poem.collection 키 삭제 ============
print()
for f in Path("frontend/src/locales").glob("*.json"):
    try:
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
    except Exception as e:
        print(f"❌ {f} 로드 실패: {e}")
        continue

    poem = data.get("poem")
    if not isinstance(poem, dict):
        continue

    removed = []
    # collection, viewCollection, myCollection, collectionTitle 등 poem 하위의 collection* 키 제거
    for k in list(poem.keys()):
        if "collection" in k.lower():
            removed.append(k)
            del poem[k]

    if removed:
        print(f"✅ {f.name}: 제거된 키 = {removed}")
        if APPLY:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
    else:
        print(f"ℹ️ {f.name}: collection 관련 키 없음")

print()
if not APPLY:
    print("🧪 미리보기 모드입니다. 실제로 적용하려면: python scripts/remove_collection.py --apply")
else:
    print("🎉 패치 완료. 다음:")
    print("   git add -A")
    print('   git commit -m "remove: poem collection feature"')
    print("   git push origin main")