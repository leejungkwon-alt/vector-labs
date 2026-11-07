# scripts/dump_poems_v2.py
"""_POEM_JSON_PATH 변수를 자동 추출해서 실제 파일을 덤프"""
import json
import re
from pathlib import Path

# 1. _POEM_JSON_PATH 값 찾기
CW = Path("app/services/content_writer.py")
txt = CW.read_text(encoding="utf-8")

m = re.search(r"_POEM_JSON_PATH\s*=\s*(.+)", txt)
if not m:
    print("❌ _POEM_JSON_PATH 정의를 못 찾았습니다.")
    print("   Get-Content 'app/services/content_writer.py' | Select-String '_POEM_JSON_PATH'")
    exit()

definition = m.group(1).strip()
print(f"✅ _POEM_JSON_PATH 정의: {definition}")

# 2. 실제 경로 추론 (여러 후보 시도)
candidates = [
    Path("app/services/content/data/poems.json"),
    Path("app/services/data/poems.json"),
    Path("app/content/data/poems.json"),
    Path("app/data/poems.json"),
    Path("app/services/content_writer.py").parent / "poems.json",
]

# 추가: 모든 JSON 중에서 '당신의' 또는 '월건'이 있는 것
all_json = list(Path("app").rglob("*.json"))

print("\n" + "="*60)
print("🔎 '당신의' / '월건' / '기릅니다' 검색 (모든 JSON)")
print("="*60)

found_files = set()
for p in all_json:
    try:
        content = p.read_text(encoding="utf-8")
    except Exception:
        continue
    if any(kw in content for kw in ["당신의 수", "당신의 목", "당신의 화", "당신의 토", "당신의 금",
                                     "월건", "기릅니다"]):
        found_files.add(p)
        print(f"\n📂 {p}")
        hits = 0
        for i, line in enumerate(content.splitlines(), 1):
            if any(kw in line for kw in ["당신의 수", "당신의 목", "당신의 화", "당신의 토", "당신의 금",
                                         "월건", "기릅니다"]):
                print(f"   L{i}: {line.strip()[:200]}")
                hits += 1
                if hits >= 5:
                    break

if not found_files:
    print("❌ 어떤 JSON에도 해당 문구가 없습니다.")
    print("   파이썬 코드에서 직접 조합하는지 확인 필요:")
    print("   Get-ChildItem -Path 'app' -Recurse -Filter '*.py' | Select-String '당신의 수|당신의 목' -Context 2,2")

# 3. 파일 크기 30KB 이하면 전체 덤프
print("\n" + "="*60)
print("📄 파일 구조 상세 (30KB 이하만)")
print("="*60)
for p in found_files:
    size = p.stat().st_size
    print(f"\n📂 {p} ({size} bytes)")
    if size < 30000:
        try:
            data = json.load(p.open(encoding="utf-8"))
            if isinstance(data, dict):
                print(f"   Top keys: {list(data.keys())[:20]}")
                if "poems" in data and isinstance(data["poems"], list):
                    print(f"   poems: {len(data['poems'])}개 항목")
                    for i, item in enumerate(data["poems"][:2]):
                        print(f"   [{i}] keys: {list(item.keys()) if isinstance(item, dict) else '?'}")
        except Exception as e:
            print(f"   ⚠️ {e}")