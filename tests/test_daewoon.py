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