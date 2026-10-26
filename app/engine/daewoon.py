# app/engine/daewoon.py
from datetime import datetime, timezone
from app.engine.solar_terms import get_adjacent_terms
from app.engine.pillars import HEAVENLY_STEMS, EARTHLY_BRANCHES, get_month_pillar
from app.services.content.loader import load_pack

YANG_STEMS = {"甲", "丙", "戊", "庚", "壬"}


def _normalize_utc(utc_instant: datetime) -> datetime:
    if utc_instant.tzinfo is None:
        raise ValueError("utc_instant must be timezone-aware (UTC).")
    return utc_instant.astimezone(timezone.utc)


def _years_months_from_days(delta_days: float) -> tuple[int, int, float]:
    """
    3일=1년, 1일=4개월 규칙. 개월 6개월 이상은 다음 해로 반올림하여
    표시 값(daewoon_display)과 start_age_first 가 일치하도록 통일한다
    (전통 만세력 관례).
    """
    raw_years = delta_days / 3.0
    years_int = int(raw_years)
    months_int = int(round((raw_years - years_int) * 12))
    if months_int == 12:
        years_int += 1
        months_int = 0
    # 6개월 이상은 다음 해로 반올림 (표시·start_age 일치)
    if months_int >= 6:
        years_int += 1
        months_int = 0
    return years_int, months_int, raw_years


def calculate_daewoon(utc_instant, gender, year_stem, solar_year, month_branch_idx):
    utc_instant = _normalize_utc(utc_instant)

    # 화이트리스트: 스키마를 우회하는 호출(스크립트, telegram, 시각화)에서
    # 빈 문자열이나 알 수 없는 값이 조용히 여성(역행)으로 처리되는 것을 방지한다.
    g = (gender or "").strip().upper()
    _MALE_TOKENS = ("M", "남", "男性", "MALE")
    _FEMALE_TOKENS = ("F", "여", "女性", "FEMALE")
    if g in _MALE_TOKENS:
        is_male = True
    elif g in _FEMALE_TOKENS:
        is_male = False
    else:
        raise ValueError(
            f"gender must be one of {_MALE_TOKENS + _FEMALE_TOKENS} "
            f"(got {gender!r})."
        )

    prev_term, next_term = get_adjacent_terms(utc_instant)

    is_year_yang = year_stem in YANG_STEMS
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

    # 표시 문자열: 언어 중립 데이터(data/{lang}/daewoon.json). 기본 "ko".
    try:
        _daewoon_pack = load_pack("ko", "daewoon")
    except KeyError:
        _daewoon_pack = {
            "DISPLAY_TPL": "{years}y {months}m",
            "CORRECTION_TPL": " (corrected to start age {start_age})",
        }
    display = _daewoon_pack["DISPLAY_TPL"].format(
        years=years_int, months=months_int,
    )
    corrected = (years_int == 0)
    if corrected:
        display += _daewoon_pack["CORRECTION_TPL"].format(
            start_age=start_age_first,
        )

    return {
        "is_forward": is_forward,
        "age_basis": "international",
        "daewoon_number": raw_years,
        "daewoon_years": years_int,
        "daewoon_months": months_int,
        "daewoon_display": display,
        "start_age_first_daewoon": start_age_first,
        "daewoon_was_corrected": corrected,
        "daewoon_pillars": daewoon_list,
    }