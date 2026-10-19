# app/engine/daewoon.py
from datetime import datetime, timezone
from app.engine.solar_terms import get_adjacent_terms
from app.engine.pillars import HEAVENLY_STEMS, EARTHLY_BRANCHES, get_month_pillar

YANG_STEMS = {"甲", "丙", "戊", "庚", "壬"}


def _normalize_utc(utc_instant: datetime) -> datetime:
    if utc_instant.tzinfo is None:
        raise ValueError("utc_instant must be timezone-aware (UTC).")
    return utc_instant.astimezone(timezone.utc)


def _years_months_from_days(delta_days: float) -> tuple[int, int, float]:
    """3일=1년, 1일=4개월 규칙. 절사 + 개월 반올림."""
    raw_years = delta_days / 3.0
    years_int = int(raw_years)
    months_int = int(round((raw_years - years_int) * 12))
    if months_int == 12:
        years_int += 1
        months_int = 0
    return years_int, months_int, raw_years


def calculate_daewoon(utc_instant, gender, year_stem, solar_year, month_branch_idx):
    utc_instant = _normalize_utc(utc_instant)

    prev_term, next_term = get_adjacent_terms(utc_instant)

    is_year_yang = year_stem in YANG_STEMS
    is_male = gender.upper() in ("M", "남", "男性", "MALE")
    is_forward = (is_year_yang and is_male) or (not is_year_yang and not is_male)

    if is_forward:
        delta_days = (next_term[0] - utc_instant).total_seconds() / 86400.0
    else:
        delta_days = (utc_instant - prev_term[0]).total_seconds() / 86400.0

    years_int, months_int, raw_years = _years_months_from_days(delta_days)
    start_age_first = max(1, years_int)

    month_pillar = get_month_pillar(solar_year, month_branch_idx)
    m_stem_idx = HEAVENLY_STEMS.index(month_pillar[0])
    m_branch_idx = EARTHLY_BRANCHES.index(month_pillar[1])

    step = 1 if is_forward else -1
    daewoon_list = []
    for i in range(1, 11):
        s_idx = (m_stem_idx + i * step) % 10
        b_idx = (m_branch_idx + i * step) % 12
        pillar = f"{HEAVENLY_STEMS[s_idx]}{EARTHLY_BRANCHES[b_idx]}"
        start_age = start_age_first + (i - 1) * 10
        daewoon_list.append({
            "daewoon_index": i,
            "start_age": start_age,
            "end_age": start_age + 9,
            "pillar": pillar,
        })

    # 표시 문자열: 일반 케이스는 "N년 M개월". years_int == 0일 때만 보정 안내 추가.
    display = f"{years_int}년 {months_int}개월"
    if years_int == 0:
        display += f" (시작 나이 {start_age_first}세로 보정)"

    return {
        "is_forward": is_forward,
        "age_basis": "international",
        "daewoon_number": raw_years,
        "daewoon_years": years_int,
        "daewoon_months": months_int,
        "daewoon_display": display,
        "start_age_first_daewoon": start_age_first,
        "daewoon_pillars": daewoon_list,
    }