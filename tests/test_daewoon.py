# tests/test_daewoon.py

from datetime import datetime, timezone, timedelta
from app.engine.daewoon import calculate_daewoon

KST = timezone(timedelta(hours=9))

def test_calculate_daewoon_forward_and_backward():
    """대운 순행/역행 및 대운수 산출 로직 검증 (골든 케이스 고정)"""
    # 1990-05-05 14:30 KST (庚午년 庚辰월, 庚은 양금)
    # 양년생 남성 -> 순행
    utc_instant = datetime(1990, 5, 5, 5, 30, tzinfo=timezone.utc)
    
    result_male = calculate_daewoon(
        utc_instant=utc_instant,
        gender="M",
        year_stem="庚",
        solar_year=1990,
        month_branch_idx=4  # 辰월
    )
    
    assert result_male["is_forward"] is True
    assert isinstance(result_male["daewoon_number"], float)
    assert len(result_male["daewoon_pillars"]) == 10
    assert result_male["daewoon_pillars"][0]["start_age"] >= 1
    # 첫 번째 대운 간지 검증 (골든 케이스)
    assert result_male["daewoon_pillars"][0]["pillar"] == "辛巳"

    # 양년생 여성 -> 역행
    result_female = calculate_daewoon(
        utc_instant=utc_instant,
        gender="F",
        year_stem="庚",
        solar_year=1990,
        month_branch_idx=4
    )
    
    assert result_female["is_forward"] is False
    assert len(result_female["daewoon_pillars"]) == 10
    # 첫 번째 대운 간지 검증 (골든 케이스)
    assert result_female["daewoon_pillars"][0]["pillar"] == "己卯"

def test_daewoon_age_basis_international():
    """대운 응답에 age_basis='international' (만 나이) 명시."""
    from datetime import datetime, timezone
    result = calculate_daewoon(
        utc_instant=datetime(1990, 5, 5, 5, 30, tzinfo=timezone.utc),
        gender="M", year_stem="庚", solar_year=1990, month_branch_idx=4,
    )
    assert result["age_basis"] == "international"


# ==== 대운 나이 반올림 (6개월 기준) ====

def test_daewoon_rounding_up_6_months():
    """2년 11개월 → 3년 0개월 (start_age = 3)."""
    from app.engine.daewoon import _years_months_from_days
    # raw_years = 8.75 / 3 = 2.9167
    y, m, raw = _years_months_from_days(8.75)
    assert (y, m) == (3, 0)


def test_daewoon_rounding_boundary_exactly_6_months():
    """2년 6개월 → 3년 0개월 (경계값)."""
    from app.engine.daewoon import _years_months_from_days
    # raw_years = 7.5 / 3 = 2.5
    y, m, raw = _years_months_from_days(7.5)
    assert (y, m) == (3, 0)


def test_daewoon_rounding_below_6_months():
    """2년 5개월 → 유지."""
    from app.engine.daewoon import _years_months_from_days
    # raw_years = 7.25 / 3 = 2.4167
    y, m, raw = _years_months_from_days(7.25)
    assert (y, m) == (2, 5)


def test_daewoon_rounding_tiny_delta():
    """0.4년 이하는 start_age=1 보정 (CORRECTION_TPL 대상)."""
    from app.engine.daewoon import _years_months_from_days
    # raw_years = 1.2 / 3 = 0.4 → months=round(4.8)=5
    y, m, raw = _years_months_from_days(1.2)
    assert (y, m) == (0, 5)
