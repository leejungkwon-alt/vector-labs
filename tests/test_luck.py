from app.engine.luck import calculate_monthly_lucks, calculate_annual_luck

def test_calculate_annual_luck():
    annual = calculate_annual_luck(2026)
    assert annual["year"] == 2026
    assert isinstance(annual["pillar"], str)
    assert len(annual["pillar"]) == 2

def test_calculate_monthly_lucks_boundary():
    """월운 연도 경계값 검증 (자월=당해년도 12월, 축월=다음해 1월)"""
    target_year = 2026
    monthly_lucks = calculate_monthly_lucks(target_year)
    
    assert len(monthly_lucks) == 12
    
    # 11번째 달: 子월 (인덱스 10) -> 2026-12여야 함
    zi_month = monthly_lucks[10]
    assert zi_month["branch"] == "子"
    assert zi_month["approx_solar_month"] == "2026-12"
    
    # 12번째 달: 丑월 (인덱스 11) -> 2027-01여야 함 (다음 해)
    chul_month = monthly_lucks[11]
    assert chul_month["branch"] == "丑"
    assert chul_month["approx_solar_month"] == "2027-01"


# ==== current_solar_year (입춘 기준 절기년) ====

from datetime import datetime, timedelta, timezone
from app.engine.luck import current_solar_year

_KST = timezone(timedelta(hours=9))


def test_current_solar_year_before_lichun():
    """1월 15일은 아직 전년도 절기년 (입춘 전)."""
    now = datetime(2026, 1, 15, 12, 0, tzinfo=_KST)
    assert current_solar_year("Asia/Seoul", now=now) == 2025


def test_current_solar_year_after_lichun():
    """3월 15일은 해당 연도 절기년."""
    now = datetime(2026, 3, 15, 12, 0, tzinfo=_KST)
    assert current_solar_year("Asia/Seoul", now=now) == 2026


def test_current_solar_year_jan_1():
    """1월 1일은 확실히 전년도."""
    now = datetime(2026, 1, 1, 0, 0, tzinfo=_KST)
    assert current_solar_year("Asia/Seoul", now=now) == 2025


def test_current_solar_year_dec_31():
    """12월 31일은 해당 연도 절기년."""
    now = datetime(2026, 12, 31, 23, 59, tzinfo=_KST)
    assert current_solar_year("Asia/Seoul", now=now) == 2026


def test_current_solar_year_invalid_tz_falls_back():
    """잘못된 tz는 Asia/Seoul로 폴백 (예외 없이)."""
    now = datetime(2026, 1, 15, 12, 0, tzinfo=_KST)
    assert current_solar_year("Invalid/Zone", now=now) == 2025
