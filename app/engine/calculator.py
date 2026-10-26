# app/engine/calculator.py

from app.engine.time_correction import calculate_adjusted_times
from app.compliance.age import validate_age
from app.engine.solar_terms import determine_solar_year_and_month
from app.engine.pillars import (
    get_year_pillar, get_month_pillar, get_day_pillar, get_hour_pillar,
)
from app.engine.daewoon import calculate_daewoon
from app.engine.elements import get_pillar_ten_gods, get_ten_god, TEN_GOD_CODES
from app.engine.luck import calculate_annual_luck, calculate_monthly_lucks


def calculate_saju(
    birth_date,
    birth_time=None,
    birth_time_mode="exact",
    timezone_str="Asia/Seoul",
    longitude=126.9780,
    correction_mode="lmt",
    jasi_boundary=23,
    gender="M",
    target_year=None,
    dst_fold=None,
    birth_location=None,
    use_current_solar_year=False,
):
    # ---- 연령 확인 ----
    validate_age(birth_date)

    # ---- birth_time_mode 처리 ----
    if birth_time_mode not in ("exact", "noon", "day_only"):
        raise ValueError(
            "birth_time_mode must be 'exact', 'noon', or 'day_only'."
        )
    if birth_time_mode == "exact":
        if not birth_time:
            raise ValueError(
                "birth_time is required when birth_time_mode='exact'."
            )
        effective_birth_time = birth_time
        hour_pillar_confidence = "exact"
    elif birth_time_mode == "noon":
        if birth_time:
            raise ValueError(
                "birth_time must be omitted when birth_time_mode='noon'."
            )
        effective_birth_time = "12:00:00"
        hour_pillar_confidence = "assumed"
    else:  # day_only
        if birth_time:
            raise ValueError(
                "birth_time must be omitted when birth_time_mode='day_only'."
            )
        effective_birth_time = "12:00:00"
        hour_pillar_confidence = "unknown"

    # ---- 도시 프리셋 우선 ----
    region = None
    if birth_location:
        from app.engine.locations import resolve_location
        longitude, timezone_str, region = resolve_location(birth_location)

    utc_instant, corrected_local = calculate_adjusted_times(
        birth_date, effective_birth_time, timezone_str, longitude, correction_mode,
        dst_fold=dst_fold,
    )

    solar_year, month_branch_idx = determine_solar_year_and_month(utc_instant)

    year_pillar = get_year_pillar(solar_year)
    month_pillar = get_month_pillar(solar_year, month_branch_idx)
    day_pillar = get_day_pillar(corrected_local, jasi_boundary)
    if birth_time_mode == "day_only":
        hour_pillar = None
    else:
        hour_pillar = get_hour_pillar(corrected_local, jasi_boundary)

    daewoon_info = calculate_daewoon(
        utc_instant=utc_instant,
        gender=gender,
        year_stem=year_pillar[0],
        solar_year=solar_year,
        month_branch_idx=month_branch_idx,
    )

    day_stem = day_pillar[0]
    ten_gods = {
        "year_pillar":  get_pillar_ten_gods(day_stem, year_pillar),
        "month_pillar": get_pillar_ten_gods(day_stem, month_pillar),
        "day_pillar": {
            "stem": "ROLE_DAY_MASTER",
            "branch": get_pillar_ten_gods(day_stem, day_pillar)["branch"],
        },
        "hour_pillar": (
            get_pillar_ten_gods(day_stem, hour_pillar)
            if hour_pillar is not None
            else None
        ),
    }

    # ---- 세운 기준 절기년 결정 (입춘 반영) ----
    if use_current_solar_year:
        from app.engine.luck import current_solar_year
        effective_solar_year = current_solar_year(timezone_str)
    elif target_year is not None:
        effective_solar_year = target_year
    else:
        effective_solar_year = None

    luck_info = None
    if effective_solar_year is not None:
        annual = calculate_annual_luck(effective_solar_year)
        monthly = calculate_monthly_lucks(effective_solar_year)

        annual_stem_korean = get_ten_god(day_stem, annual["stem"])
        annual_stem_god = TEN_GOD_CODES.get(annual_stem_korean, annual_stem_korean)

        # 각 월의 십성 계산 (일간 기준)
        for m in monthly:
            stem_char = m["pillar"][0]
            tg_kr = get_ten_god(day_stem, stem_char)
            m["ten_god"] = TEN_GOD_CODES.get(tg_kr, tg_kr)

        luck_info = {
            "target_year": effective_solar_year,
            "annual_luck": {**annual, "ten_god": annual_stem_god},
            "monthly_lucks": monthly,
        }

    return {
        "solar_year": solar_year,
        "year_pillar": year_pillar,
        "month_pillar": month_pillar,
        "day_pillar": day_pillar,
        "hour_pillar": hour_pillar,
        "hour_pillar_confidence": hour_pillar_confidence,
        "birth_time_mode": birth_time_mode,
        "solar_adjusted_time": corrected_local.isoformat(),
        "birth_instant_utc": utc_instant.isoformat(),
        "daewoon_info": daewoon_info,
        "ten_gods": ten_gods,
        "luck_info": luck_info,
        # ---- Step 9-A 신규 ----
        "birth_date": birth_date,
        "birth_location": birth_location,
        "region": region,
    }