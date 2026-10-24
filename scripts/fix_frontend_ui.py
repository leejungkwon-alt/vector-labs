#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend" / "src" / "components" / "sections"

PATCHES = [
    (
        "YearSection.tsx",
        "{section.target_year}년 · {section.pillar_name || section.pillar} · {section.ten_god}",
        "{section.target_year}년{section.pillar_name ? ` · ${section.pillar_name}` : \"\"}"
    ),
    (
        "MonthlySection.tsx",
        "{item.approx_solar_month} · {item.pillar_name || item.pillar}",
        "{item.approx_solar_month}{item.pillar_name ? ` · ${item.pillar_name}` : \"\"}"
    ),
    (
        "TimelineSection.tsx",
        "{item.ages[0]}–{item.ages[1]}세 · {item.pillar_name || item.pillar}",
        "{item.ages[0]}–{item.ages[1]}세{item.pillar_name ? ` · ${item.pillar_name}` : \"\"}"
    ),
    (
        "PremiumSection.tsx",
        "{item.pillar} · {item.grade_label}",
        "{item.grade_label}"
    ),
    (
        "CoreSection.tsx",
        """          {section.pillar_name_traditional && (
            <Text style={{ fontSize: 12, color: colors.textMuted }}>
              {" "}({section.pillar_name_traditional})
            </Text>
          )}""",
        ""
    )
]

def main():
    print("=== 프론트엔드 UI 한자 노출 제거 패치 ===")
    for filename, old, new in PATCHES:
        path = FRONTEND / filename
        if not path.exists():
            print(f"❌ {filename} 없음")
            continue
        src = path.read_text(encoding="utf-8")
        if old not in src:
            print(f"⚠️  {filename}: 이미 적용됨 (또는 패턴 불일치)")
            continue
        src = src.replace(old, new)
        path.write_text(src, encoding="utf-8")
        print(f"✅ {filename} 패치 완료")

if __name__ == "__main__":
    main()
