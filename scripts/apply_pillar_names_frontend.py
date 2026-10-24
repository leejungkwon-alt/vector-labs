#!/usr/bin/env python3
"""
프론트엔드 pillar_name 필드 적용 스크립트.

- types.ts → CoreSection / YearSection / MonthlyItem / TimelineItem 에 pillar_name 필드 추가
- Year/Monthly/Timeline/Core Section → pillar_name 우선 표시, 없으면 pillar fallback

멱등(idempotent). 파일 수정 전 .bak.<ts> 자동 백업.

사용:
    python scripts/apply_pillar_names_frontend.py --dry-run   # 미리보기
    python scripts/apply_pillar_names_frontend.py
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _backup(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + f".bak.{_ts()}")
    shutil.copy2(path, bak)
    return bak


# ─────────────────────────────────────────────────────
# (rel_path, old_string, new_string) — 순서 중요: types.ts 먼저
# ─────────────────────────────────────────────────────
PATCHES: list[tuple[str, str, str]] = [

    # ---- types.ts : CoreSection ----
    (
        "frontend/types.ts",
        (
            "  keywords: string[];\n"
            "  personalized_insights: string[];\n"
            "}"
        ),
        (
            "  keywords: string[];\n"
            "  personalized_insights: string[];\n"
            "  pillar?: string | null;\n"
            "  pillar_name?: string;\n"
            "  pillar_name_traditional?: string;\n"
            "}"
        ),
    ),

    # ---- types.ts : YearSection ----
    (
        "frontend/types.ts",
        (
            'export interface YearSection extends ReportSectionBase {\n'
            '  id: "year";\n'
            "  target_year: number;\n"
            "  pillar: string;\n"
            "  ten_god: string;"
        ),
        (
            'export interface YearSection extends ReportSectionBase {\n'
            '  id: "year";\n'
            "  target_year: number;\n"
            "  pillar: string;\n"
            "  pillar_name?: string;\n"
            "  pillar_name_traditional?: string;\n"
            "  ten_god: string;"
        ),
    ),

    # ---- types.ts : MonthlyItem ----
    (
        "frontend/types.ts",
        (
            "export interface MonthlyItem {\n"
            "  month_index: number;\n"
            "  pillar: string;\n"
            "  branch: string;"
        ),
        (
            "export interface MonthlyItem {\n"
            "  month_index: number;\n"
            "  pillar: string;\n"
            "  pillar_name?: string;\n"
            "  pillar_name_traditional?: string;\n"
            "  branch: string;"
        ),
    ),

    # ---- types.ts : TimelineItem ----
    (
        "frontend/types.ts",
        (
            "export interface TimelineItem {\n"
            "  index: number;\n"
            "  ages: [number, number];\n"
            "  pillar: string;\n"
            "  score: number;"
        ),
        (
            "export interface TimelineItem {\n"
            "  index: number;\n"
            "  ages: [number, number];\n"
            "  pillar: string;\n"
            "  pillar_name?: string;\n"
            "  pillar_name_traditional?: string;\n"
            "  score: number;"
        ),
    ),

    # ---- YearSection.tsx ----
    (
        "frontend/src/components/sections/YearSection.tsx",
        "{section.target_year}년 · {section.pillar} · {section.ten_god}",
        "{section.target_year}년 · {section.pillar_name || section.pillar} · {section.ten_god}",
    ),

    # ---- MonthlySection.tsx ----
    (
        "frontend/src/components/sections/MonthlySection.tsx",
        "{item.approx_solar_month} · {item.pillar}",
        "{item.approx_solar_month} · {item.pillar_name || item.pillar}",
    ),

    # ---- TimelineSection.tsx ----
    (
        "frontend/src/components/sections/TimelineSection.tsx",
        "{item.ages[0]}–{item.ages[1]}세 · {item.pillar}",
        "{item.ages[0]}–{item.ages[1]}세 · {item.pillar_name || item.pillar}",
    ),

    # ---- CoreSection.tsx : hero 위에 pillar_name 표시 ----
    (
        "frontend/src/components/sections/CoreSection.tsx",
        "      <Text style={ss.coreHero}>{section.hero}</Text>",
        (
            "      {section.pillar_name && (\n"
            "        <Text style={[ss.metaText, { marginBottom: 8 }]}>\n"
            "          {section.pillar_name}\n"
            "          {section.pillar_name_traditional && (\n"
            "            <Text style={{ fontSize: 12, color: colors.textMuted }}>\n"
            '              {" "}({section.pillar_name_traditional})\n'
            "            </Text>\n"
            "          )}\n"
            "        </Text>\n"
            "      )}\n"
            "      <Text style={ss.coreHero}>{section.hero}</Text>"
        ),
    ),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="프론트엔드 pillar_name 필드 적용")
    ap.add_argument("--dry-run", action="store_true", help="미리보기만, 파일 수정 없음")
    args = ap.parse_args()

    applied = already = missing = 0
    print("=== 프론트엔드 pillar_name 패치 ===")
    for rel, old, new in PATCHES:
        path = ROOT / rel
        if not path.exists():
            print(f"  ❌ {rel} 없음")
            missing += 1
            continue

        src = path.read_text(encoding="utf-8")

        if new in src:
            print(f"  ⏭️  {path.name}: 이미 적용됨")
            already += 1
            continue

        if old not in src:
            print(f"  ⚠️  {path.name}: 대상 패턴 없음 (수동 확인 필요)")
            missing += 1
            continue

        if args.dry_run:
            print(f"  [dry] {path.name}: 적용 예정")
            applied += 1
            continue

        _backup(path)
        path.write_text(src.replace(old, new, 1), encoding="utf-8")
        print(f"  ✅ {path.name}: 적용")

        # 같은 파일 여러 패치 시 최신 상태로 다시 읽도록
        applied += 1

    print(f"\n결과: 적용 {applied} / 이미됨 {already} / 실패 {missing}")

    if applied and not args.dry_run:
        print("\n다음 검증:")
        print("  cd frontend")
        print("  npx tsc --noEmit")
        print("  npx expo start   # 또는 기존 개발 서버 재시작")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())