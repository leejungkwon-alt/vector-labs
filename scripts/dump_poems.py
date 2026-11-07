# scripts/dump_poems.py
"""poems.json 위치를 찾아 전체 내용을 덤프"""
from pathlib import Path

found = []
for p in Path("app").rglob("*.json"):
    if "poem" in p.name.lower() or "poem" in str(p.parent).lower():
        found.append(p)

if not found:
    print("❌ poems.json을 찾지 못했습니다. 다음 명령으로 광범위 검색:")
    print("   Get-ChildItem -Path 'app' -Recurse -Filter '*.json' | Select-String '월건|기릅니다'")
    exit()

for f in found:
    print(f"\n{'='*60}")
    print(f"📂 {f}  ({f.stat().st_size} bytes)")
    print('='*60)
    txt = f.read_text(encoding="utf-8")
    print(txt[:3000])  # 앞 3000자만
    if len(txt) > 3000:
        print(f"\n... (총 {len(txt)}자, 나머지 생략)")

# poems.json이 아닌 다른 파일에서 "월건" 검색
print("\n" + "="*60)
print("🔎 모든 JSON에서 '월건' 또는 '기릅니다' 검색")
print("="*60)
for p in Path("app").rglob("*.json"):
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        continue
    if "월건" in txt or "기릅니다" in txt:
        print(f"\n📂 {p}")
        for i, line in enumerate(txt.splitlines(), 1):
            if "월건" in line or "기릅니다" in line:
                print(f"   L{i}: {line.strip()[:150]}")
                