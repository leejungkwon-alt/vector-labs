#!/usr/bin/env python3
"""
fix_stale_archetype_tests.py

`fix_archetype_names.py`로 archetype.name이 일주별 이름(Sun Above Stone 등)으로
바뀐 뒤, stale 상태가 된 테스트 8개를 갱신합니다.

안전장치: 파일 저장 전 .bak.<ts> 백업, 패턴 미발견 시 skip.
"""
from __future__ import annotations
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _backup(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + f".bak.{datetime.now():%Y%m%d_%H%M%S}")
    shutil.copy2(path, bak)
    return bak


# (파일, old_exact, new_exact, 설명)
PATCHES = [
    # 1) test_content_writer.py
    (
        "tests/test_content_writer.py",
        'assert section["archetype"]["name"] == "The Radiator"',
        'assert section["archetype"]["name"] == "Sun Above Stone"  # 1974 = 丙申',
        "test_content_writer: 丙申 → Sun Above Stone",
    ),
    # 2) test_core_pillar_content.py
    (
        "tests/test_core_pillar_content.py",
        'assert cover["archetype"]["name"] == "The Radiator"',
        'assert cover["archetype"]["name"] == "Sun Above Stone"  # 1974 = 丙申',
        "test_core_pillar_content: 丙申 → Sun Above Stone",
    ),
    # 3) test_full_report.py
    (
        "tests/test_full_report.py",
        'assert cover["archetype"]["name"] == "The Radiator"',
        'assert cover["archetype"]["name"] == "Sun Above Stone"  # 1974 = 丙申',
        "test_full_report: 丙申 → Sun Above Stone",
    ),
    # 4) test_ko_report.py — cover
    (
        "tests/test_ko_report.py",
        'assert cover["archetype"]["name"] == "태양"',
        'assert cover["archetype"]["name"] == "바위 위의 태양"  # 丙申',
        "test_ko_report(cover): 丙申 → 바위 위의 태양",
    ),
    # 5) test_ko_report.py — core
    (
        "tests/test_ko_report.py",
        'assert core["archetype"]["name"] == "태양"',
        'assert core["archetype"]["name"] == "바위 위의 태양"  # 丙申',
        "test_ko_report(core): 丙申 → 바위 위의 태양",
    ),
    # 6) test_ko_report.py — 1990 THE_BLADE
    (
        "tests/test_ko_report.py",
        'assert core["archetype"]["name"] == "칼날"',
        'assert core["archetype"]["name"] == "제련로의 검"  # 1990 = 庚午',
        "test_ko_report(1990 blade): 庚午 → 제련로의 검",
    ),
    # 7) test_ko_report.py — en still works
    (
        "tests/test_ko_report.py",
        'assert report["cover"]["archetype"]["name"] == "The Radiator"',
        'assert report["cover"]["archetype"]["name"] == "Sun Above Stone"  # 1974 = 丙申',
        "test_ko_report(en): 丙申 → Sun Above Stone",
    ),
    # 8) test_report_api.py
    (
        "tests/test_report_api.py",
        'assert cover["archetype"]["name"] == "The Radiator"',
        'assert cover["archetype"]["name"] == "Sun Above Stone"  # 1974 = 丙申',
        "test_report_api: 丙申 → Sun Above Stone",
    ),
]


def main() -> int:
    print("=== stale archetype-name 테스트 갱신 ===\n")
    ok = skipped = missing = 0

    for rel, old, new, label in PATCHES:
        p = ROOT / rel
        if not p.exists():
            print(f"  ❌ 파일 없음: {rel}")
            missing += 1
            continue

        src = p.read_text(encoding="utf-8")

        # 이미 반영된 경우: new 문자열로 이미 존재 → skip
        if new in src:
            print(f"  ⏭️  이미 적용됨: {label}")
            skipped += 1
            continue

        if old not in src:
            print(f"  ⚠️  패턴 없음(수동 확인): {label}\n     {old!r}")
            missing += 1
            continue

        bak = _backup(p)
        p.write_text(src.replace(old, new, 1), encoding="utf-8")
        print(f"  ✅ {label}\n     백업: {bak.name}")
        ok += 1

    print(f"\n결과: 갱신 {ok} / 이미 적용 {skipped} / 실패 {missing}")
    if missing == 0:
        print("\n다음 단계: pytest -q")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())