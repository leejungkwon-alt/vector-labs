#!/usr/bin/env python3
"""
Phase 3-9 후속: 癸未 keywords[1] 순한자 → 카나 포함 형태로 교정.
- "節制" → "節制の知恵" (の 포함, 스타일 통일 + KANA_RE 통과)
- 저장 전 JSON 유효성 사전검증
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "core_pillars"

def main() -> int:
    fpath = JA / "癸未.json"
    if not fpath.exists():
        print(f"❌ 파일 없음: {fpath}")
        return 1

    data = json.loads(fpath.read_text(encoding="utf-8"))
    kws = data.get("keywords", [])
    if len(kws) > 1 and kws[1] == "節制":
        kws[1] = "節制の知恵"
        data["keywords"] = kws
    else:
        print(f"⏭  변경 없음 (현재: {kws})")
        return 0

    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)  # 사전검증
    fpath.write_text(payload, encoding="utf-8")
    print(f"✅ 癸未 keywords → {kws}")

    # 재검증
    reloaded = json.loads(fpath.read_text(encoding="utf-8"))
    print(f"   verify: keywords = {reloaded['keywords']}")
    return 0

if __name__ == "__main__":
    sys.exit(main())