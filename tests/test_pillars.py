from datetime import datetime, timezone, timedelta
from app.engine.solar_terms import determine_solar_year_and_month
from app.engine.pillars import (
    get_year_pillar,
    get_month_pillar,
    get_day_pillar,
    get_hour_pillar,
)

KST = timezone(timedelta(hours=9))


def test_solar_term_and_pillars():
    # 1990-05-05 14:30 KST → 庚午년 庚辰월 庚午일 癸未시
    birth = datetime(1990, 5, 5, 14, 30, tzinfo=KST)

    solar_year, month_branch_idx = determine_solar_year_and_month(birth)
    assert (solar_year, month_branch_idx) == (1990, 4)  # 辰월

    local = birth.replace(tzinfo=None)

    assert get_year_pillar(solar_year) == "庚午"
    assert get_month_pillar(solar_year, month_branch_idx) == "庚辰"
    assert get_day_pillar(local) == "庚午"
    assert get_hour_pillar(local, 23) == "癸未"


def test_jasi_boundary_transition():
    """23:30 출생 시 jasi_boundary에 따라 일주가 달라져야 함."""
    dt = datetime(2000, 1, 1, 23, 30)
    # 23시 경계: 다음 날(1/2) 일진
    assert get_day_pillar(dt, jasi_boundary=23) != get_day_pillar(dt, jasi_boundary=0)
    # 0시 경계: 1/1 그대로
    assert get_day_pillar(dt, jasi_boundary=0) == get_day_pillar(datetime(2000, 1, 1, 12, 0))