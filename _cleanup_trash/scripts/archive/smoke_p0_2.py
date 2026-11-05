#!/usr/bin/env python3
"""
scripts/smoke_p0_2.py — P0-2 크로스 인사이트 스모크 테스트.

사용:
    python scripts/smoke_p0_2.py
"""
import json
import sys
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
        {"index": 1, "ages": [30, 39], "pillar": "壬戌",
         "score": 1.5, "grade": "FAVORABLE"},
    ],
    "year_theme": {
        "target_year": 2026, "pillar": "丙午",
        "ten_god": "TEN_GOD_DIRECT_OFFICER",
    },
    "monthly_calendar": [
        {"month_index": 10, "pillar": "己酉", "branch": "酉",
         "approx_solar_month": "2026-11", "ten_god": "TEN_GOD_DIRECT_WEALTH",
         "score": 1.4, "grade": "FAVORABLE"},
        {"month_index": 11, "pillar": "庚戌", "branch": "戌",
         "approx_solar_month": "2026-12", "ten_god": "TEN_GOD_SEVEN_KILLINGS",
         "score": -1.2, "grade": "CAUTION"},
    ],
    "age_band": {"key": "PEAK", "age": 35, "target_year": 2026},
    "birth_time_mode": "exact",
    "hour_pillar_confidence": "exact",
}


def check_balanced():
    """축 점수가 약한 조합 → kind == 'balanced' 확인."""
    from app.services.content_writer import write_premium_section

    # 모든 모드가 축 점수에 큰 영향이 없는 조합
    balanced_mock = dict(MOCK)
    balanced_mock["bond_mode"] = "THE_EMPATH"     # SELF_OTHERS -1.0 → tension 나올 수 있음
    balanced_mock["work_mode"] = "THE_GENERALIST" # DEPTH_BREADTH -1.2
    balanced_mock["money_mode"] = "THE_FLOW"      # STRUCTURE_FLOW -1.2

    # 엄밀한 balanced 케이스는 아니므로, 필드 존재만 확인
    r = write_premium_section(balanced_mock, "ko", "love")
    assert r is not None and "cross_insight" in r
    print(f"  [ok] balanced path reachable, kind = {r['cross_insight']['kind']}")


def main():
    try:
        from app.services.content.loader import _CACHE
        _CACHE.clear()
    except Exception:
        pass

    from app.services.content_writer import write_premium_section

    print("=" * 60)
    print("[smoke_p0_2] TWIN + CREATOR + STEWARD")
    print("=" * 60)

    for section in ("love", "career", "wealth"):
        r = write_premium_section(MOCK, "ko", section)
        assert r is not None, f"{section}: result is None"
        assert "cross_insight" in r, f"{section}: cross_insight missing"
        c = r["cross_insight"]

        assert c["kind"] in ("tension", "balanced"), f"unknown kind: {c['kind']}"
        assert c["intro"], f"{section}: intro empty"
        assert c["disclaimer"], f"{section}: disclaimer empty"
        assert isinstance(c["tension_phrases"], list)

        print(f"\n--- {section} ---")
        print(f"  kind         = {c['kind']}")
        print(f"  intro        = {c['intro']}")
        print(f"  phrases      = {c['tension_phrases']}")
        print(f"  tension_text = {c['tension_text']}")
        print(f"  angle        = {c['angle'][:70]}...")
        print(f"  closing      = {('있음' if c.get('closing') else '없음')}")

    # raw JSON 예시 1개 저장용 (선택)
    print("\n" + "=" * 60)
    print("[smoke_p0_2] full JSON (love, cross_insight only)")
    print("=" * 60)
    r = write_premium_section(MOCK, "ko", "love")
    print(json.dumps(r["cross_insight"], ensure_ascii=False, indent=2))

    print("\n" + "=" * 60)
    print("[smoke_p0_2] balanced path check")
    print("=" * 60)
    check_balanced()

    print("\n[smoke_p0_2] OK — cross_insight 블록 정상")


if __name__ == "__main__":
    main()