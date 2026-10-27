#!/usr/bin/env python3
"""ja/ 콘텐츠 팩의 미번역(영어 잔존) 비율 스캔."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja"

# 가나(히라가나 + 가타카나) — 일본어 번역 마커
KANA_RE = re.compile(r'[\u3040-\u30FF]')
LATIN_RE = re.compile(r'[A-Za-z]')

SKIP_KEYS = {"pillar", "name_traditional", "signature", "key", "tag", "code"}

def is_english_like(text: str) -> bool:
    if not isinstance(text, str) or len(text) < 20:
        return False
    if " " not in text:
        return False          # 태그/코드 류 스킵
    if text.isupper() and "_" in text:
        return False          # MAGNETIC_DRAW 같은 코드
    if KANA_RE.search(text):
        return False          # 가나 있으면 번역됨
    if not LATIN_RE.search(text):
        return False
    return True

def scan_file(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": str(e), "untranslated": 0, "total": 0, "sample": []}

    stats = {"untranslated": 0, "total": 0, "sample": []}

    def walk(obj, key_path=""):
        if isinstance(obj, str):
            stats["total"] += 1
            if is_english_like(obj):
                stats["untranslated"] += 1
                if len(stats["sample"]) < 3:
                    stats["sample"].append((key_path, obj[:70]))
        elif isinstance(obj, dict):
            for k, v in obj.items():
                if k in SKIP_KEYS:
                    continue
                walk(v, f"{key_path}.{k}" if key_path else k)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{key_path}[{i}]")

    walk(data)
    return stats

def main() -> int:
    if not JA.exists():
        print(f"Not found: {JA}")
        return 1

    top_results, pillar_results = [], []

    for f in sorted(JA.glob("*.json")):
        r = scan_file(f)
        if r.get("error"):
            print(f"  ERR {f.name}: {r['error']}")
            continue
        pct = (r["untranslated"] / r["total"] * 100) if r["total"] else 0.0
        top_results.append((f.name, r["untranslated"], r["total"], pct, r["sample"]))

    pdir = JA / "core_pillars"
    if pdir.exists():
        for f in sorted(pdir.glob("*.json")):
            r = scan_file(f)
            if not r.get("error"):
                pillar_results.append((f.name, r["untranslated"], r["total"]))

    print("=" * 70)
    print("ja/ Top-level (untranstaled 우선)")
    print("=" * 70)
    for name, un, tot, pct, sample in sorted(top_results, key=lambda x: -x[1]):
        status = "OK" if un == 0 else "WARN" if pct < 20 else "GAP "
        print(f"  [{status}] {name:30} {un:3}/{tot:3} ({pct:5.1f}%)")
        for kp, s in sample[:2]:
            print(f"         {kp}: {s}")

    print()
    print("=" * 70)
    print(f"ja/core_pillars/ ({len(pillar_results)} files)")
    print("=" * 70)
    done = [r for r in pillar_results if r[1] == 0]
    gap = [r for r in pillar_results if r[1] > 0]
    print(f"  번역 완료: {len(done)}")
    print(f"  번역 필요: {len(gap)}")
    if gap:
        print("\n  번역 필요 파일 (상위 15):")
        for name, un, tot in gap[:15]:
            print(f"    - {name}: {un}/{tot}")

    return 0

if __name__ == "__main__":
    sys.exit(main())