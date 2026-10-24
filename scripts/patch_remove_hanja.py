#!/usr/bin/env python3
"""
scripts/patch_remove_hanja.py
프론트엔드 화면에서 노출되는 모든 한자(원본 기둥, 전통 명칭)를 제거합니다.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend" / "src" / "components" / "sections"

PATCHES = [
    # 1. YearSection: 한자 pillar 및 영어 ten_god 제거
    (
        "YearSection.tsx",
        "{section.target_year}년 · {section.pillar_name || section.pillar} · {section.ten_god}",
        "{section.target_year}년{section.pillar_name ? ` · ${section.pillar_name}` : \"\"}"
    ),
    # 2. MonthlySection: 한자 pillar 제거
    (
        "MonthlySection.tsx",
        "{item.approx_solar_month} · {item.pillar_name || item.pillar}",
        "{item.approx_solar_month}{item.pillar_name ? ` · ${item.pillar_name}` : \"\"}"
    ),
    # 3. TimelineSection: 한자 pillar 제거
    (
        "TimelineSection.tsx",
        "{item.ages[0]}–{item.ages[1]}세 · {item.pillar_name || item.pillar}",
        "{item.ages[0]}–{item.ages[1]}세{item.pillar_name ? ` · ${item.pillar_name}` : \"\"}"
    ),
    # 4. PremiumSection: 타이밍 블록 내 한자 pillar 제거
    (
        "PremiumSection.tsx",
        "{item.pillar} · {item.grade_label}",
        "{item.grade_label}"
    ),
    # 5. SinsalSection: 전통 명칭(한자) 제거
    (
        "SinsalSection.tsx",
        """            {item.name_traditional && (
              <Text style={{ fontSize: 13, color: colors.textMuted }}>
                {" "}({item.name_traditional})
              </Text>
            )}""",
        ""
    )
]

def main():
    print("=== 프론트엔드 한자 노출 제거 패치 ===")
    for filename, old, new in PATCHES:
        path = FRONTEND / filename
        if not path.exists():
            print(f"❌ {filename} 파일 없음")
            continue
        src = path.read_text(encoding="utf-8")
        if old not in src:
            print(f"⚠️  {filename}: 패턴 없음 (이미 적용되었거나 코드가 다름)")
            continue
        src = src.replace(old, new)
        path.write_text(src, encoding="utf-8")
        print(f"✅ {filename} 패치 완료")

if __name__ == "__main__":
    main()