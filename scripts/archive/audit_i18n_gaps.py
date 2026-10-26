#!/usr/bin/env python3
"""
i18n 데이터 팩 누락 감사.
en 기준으로 ja, zh_cn, es에 어떤 JSON 파일이 없는지 확인.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app" / "services" / "content" / "data"
LANGS = ["ja", "zh_cn", "es"]

# 비교 기준이 될 en의 파일 목록
en_dir = DATA / "en"
en_files = {p.name for p in en_dir.glob("*.json")}
# core_pillars 같은 하위 폴더도 포함
en_pillar_files = {p.name for p in (en_dir / "core_pillars").glob("*.json")}

print("=" * 60)
print("[i18n Gap Audit] en 대비 누락된 JSON 파일")
print("=" * 60)

for lang in LANGS:
    lang_dir = DATA / lang
    if not lang_dir.exists():
        print(f"\n❌ [{lang}] 디렉토리 없음")
        continue

    lang_files = {p.name for p in lang_dir.glob("*.json")}
    lang_pillar_dir = lang_dir / "core_pillars"
    lang_pillar_files = {p.name for p in lang_pillar_dir.glob("*.json")} if lang_pillar_dir.exists() else set()

    missing = sorted(en_files - lang_files)
    missing_pillars = sorted(en_pillar_files - lang_pillar_files)

    print(f"\n[{lang}]")
    if not missing and not missing_pillars:
        print("  ✅ 모든 파일 존재")
    else:
        if missing:
            print(f"  ❌ 누락된 최상위 JSON ({len(missing)}개):")
            for f in missing:
                print(f"     - {f}")
        if missing_pillars:
            print(f"  ❌ 누락된 core_pillars ({len(missing_pillars)}개):")
            for f in missing_pillars[:5]:
                print(f"     - core_pillars/{f}")
            if len(missing_pillars) > 5:
                print(f"     ... 외 {len(missing_pillars)-5}개")

print("\n" + "=" * 60)