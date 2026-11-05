#!/usr/bin/env python3
"""
scripts/smoke_p0_1.py — P0-1 timing 블록 스모크 테스트.

사용:
    python scripts/smoke_p0_1.py
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


MOCK = {
    "archetype": {"key": "THE_PIONEER", "intensity": "BALANCED_CORE", "stem": "甲"},
    "energy_signature": {
        "dominant": ["GROWTH"], "deficient": [], "missing": [],
        "percentages": {"木": 40.0, "火": 15.0, "土": 15.0, "金": 15.0, "水": 15.0},
    },
    "money_mode": "THE_STEWARD",
    "work_mode": "THE_CREATOR",
    "bond_mode": "THE_TWIN",
    "daewoon_timeline": [
        {"index": 1, "ages": [30, 39], "pillar": "壬戌", "score": 1.5, "grade": "FAVORABLE"},
    ],
    "year_theme": {
        "target_year": 2026, "pillar": "丙午", "ten_god": "TEN_GOD_DIRECT_OFFICER",
    },
    "monthly_calendar": [
        {"month_index": 1,  "pillar": "庚寅", "branch": "寅",
         "approx_solar_month": "2026-02", "ten_god": "TEN_GOD_EATING_GOD",
         "score": 1.2,  "grade": "FAVORABLE"},
        {"month_index": 5,  "pillar": "甲午", "branch": "午",
         "approx_solar_month": "2026-06", "ten_god": "TEN_GOD_HURTING_OFFICER",
         "score": -1.5, "grade": "CAUTION"},
        {"month_index": 10, "pillar": "己酉", "branch": "酉",
         "approx_solar_month": "2026-11", "ten_god": "TEN_GOD_DIRECT_WEALTH",
         "score": 1.4,  "grade": "FAVORABLE"},
        {"month_index": 11, "pillar": "庚戌", "branch": "戌",
         "approx_solar_month": "2026-12", "ten_god": "TEN_GOD_SEVEN_KILLINGS",
         "score": -1.2, "grade": "CAUTION"},
    ],
    "age_band": {"key": "PEAK", "age": 35, "target_year": 2026},
    "birth_time_mode": "exact",
    "hour_pillar_confidence": "exact",
}


def main():
    from app.services.content_writer import write_premium_section

    print("=" * 60)
    print("[smoke_p0_1] full-year mode (today=None)")
    print("=" * 60)
    for section in ("love", "career", "wealth"):
        r = write_premium_section(MOCK, "ko", section)  # today=None
        assert r is not None, f"{section} returned None"
        assert "timing" in r, f"{section} timing missing"
        t = r["timing"]
        assert t["daewoon"]["pillar"] == "壬戌"
        assert t["year"]["ten_god_label"] == "질서의 에너지"
        assert t["opportunity_month"] is not None
        assert t["caution_month"] is not None
        print(f"\n--- {section} ---")
        print(json.dumps(t, ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("[smoke_p0_1] filtered mode (today=2026-10-21)")
    print("=" * 60)
    r = write_premium_section(MOCK, "ko", "love", today=date(2026, 10, 21))
    t = r["timing"]
    assert t["opportunity_month"]["approx_solar_month"] == "2026-11"
    assert t["caution_month"]["approx_solar_month"] == "2026-12"
    print(f"  opportunity = {t['opportunity_month']['approx_solar_month']}")
    print(f"  caution     = {t['caution_month']['approx_solar_month']}")
    print("  (2026-02, 2026-06 은 과거라 자동 제외됨)")

    print("\n[smoke_p0_1] OK — timing 블록 정상")


if __name__ == "__main__":
    main()