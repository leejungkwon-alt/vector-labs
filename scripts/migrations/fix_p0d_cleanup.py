#!/usr/bin/env python3
"""scripts/migrations/fix_p0d_cleanup.py

P0-d:
  1. ko/sections.json SECTION_TITLES 복구 (P1 오버리치 롤백)
  2. es "Deep" 잔존 6건 정확 치환

실행:
  python scripts/migrations/fix_p0d_cleanup.py
  python scripts/migrations/fix_p0d_cleanup.py --apply
"""
from __future__ import annotations
import json, shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "app" / "services" / "content" / "data"
APPLY = "--apply" in sys.argv
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

# P1 오버리치 복구 대상 (sections.json)
KO_TITLES = {
    "cover":      "당신의 명식",
    "core":       "당신의 본질",
    "energy":     "당신의 에너지 지도",
    "lucky_code": "당신에게 필요한 기운",
    "chart":      "당신의 네 가지 얼굴",
}

# es 문맥 내 "Deep" → 스페인어
ES_DEEP_FIXES = [
    ("core_pillars/己亥.json", "Deep, silencioso",              "Profundo, silencioso"),
    ("core_pillars/甲子.json", "El agua Deep es buena",         "El agua profunda es buena"),
    ("core_pillars/辛亥.json", "Deep: el agua refleja",         "Profundo: el agua refleja"),
    ("lucky_code.json",        '"Deep gris"',                    '"Gris profundo"'),
    ("lucky_code.json",        "Estudio Deep sobre",             "Estudio profundo sobre"),
    ("lucky_code.json",        "Deep, tranquilo, sin prisas",    "Profundo, tranquilo, sin prisas"),
]


def backup(p: Path) -> None:
    shutil.copy2(p, p.with_name(p.name + f".{TS}.bak"))


def fix_ko_titles() -> None:
    p = DATA / "ko" / "sections.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    titles = data.get("SECTION_TITLES", {})
    changed = 0
    for k, v in KO_TITLES.items():
        if titles.get(k) != v:
            titles[k] = v
            changed += 1
    if changed == 0:
        print("  ➖ ko SECTION_TITLES: 이미 복구됨")
        return
    if APPLY:
        backup(p)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  {'✅' if APPLY else '🔍'} ko SECTION_TITLES 복구: {changed}건")


def fix_es_deep() -> None:
    total = 0
    backed = set()
    for rel, old, new in ES_DEEP_FIXES:
        p = DATA / "es" / rel
        if not p.exists():
            continue
        src = p.read_text(encoding="utf-8")
        if old not in src:
            continue
        src = src.replace(old, new)
        if APPLY:
            if rel not in backed:
                backup(p)
                backed.add(rel)
            p.write_text(src, encoding="utf-8")
        total += 1
    print(f"  {'✅' if APPLY else '🔍'} es Deep 잔존: {total}건")


def main() -> int:
    print("=" * 66)
    print(f"  fix_p0d_cleanup ({'APPLY' if APPLY else 'DRY-RUN'})")
    print("=" * 66)
    fix_ko_titles()
    fix_es_deep()
    print("=" * 66)
    if not APPLY:
        print("  dry-run 완료 → --apply 로 적용")
    else:
        print(f"  백업: *. {TS} .bak")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())