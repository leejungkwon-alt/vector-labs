# scripts/find_daily_api.py
from pathlib import Path

keywords = ["saju/daily", "getDaily", "api.daily", "/daily", "daily"]
hits = {}

print("🔎 프론트엔드에서 'daily' 관련 코드를 전수 조사합니다...\n")

for p in Path("frontend").rglob("*"):
    if p.is_file() and p.suffix in [".ts", ".tsx", ".js", ".jsx"]:
        try:
            txt = p.read_text(encoding="utf-8")
        except Exception:
            continue
        
        for i, line in enumerate(txt.splitlines(), 1):
            for kw in keywords:
                if kw in line:
                    if p not in hits:
                        hits[p] = []
                    hits[p].append((i, kw, line.strip()))
                    break # 한 줄에 하나만 기록

if not hits:
    print("❌ 프론트엔드에서 'daily' 관련 코드를 찾지 못했습니다.")
    print("   api 클라이언트 코드(frontend/src/api/client.ts)를 직접 열어서 확인해야 할 수도 있습니다.")
else:
    for p, lines in hits.items():
        print(f"📂 {p}")
        for i, kw, line in lines:
            print(f"   L{i}: [{kw}] {line[:120]}")
        print()