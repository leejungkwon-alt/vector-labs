# tests/test_historical.py

from datetime import datetime, timezone, timedelta
from app.engine.calculator import calculate_saju
from app.engine.time_correction import calculate_adjusted_times

KST = timezone(timedelta(hours=9))


def test_historical_korea_offset_1955():
    """
    1955년 5월 5일은 한국의 서머타임(KDT, UTC+9:30) 시행 기간에 해당합니다.
    IANA zoneinfo가 역사적 DST 규칙을 정확히 반영하는지 검증합니다.
    """
    utc_dt, adjusted = calculate_adjusted_times(
        birth_date="1955-05-05",
        birth_time="12:00:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
    )
    
    # 1955년 5월 5일 Asia/Seoul은 서머타임(UTC+9:30) 적용으로 벽시계 12:00은 UTC 02:30입니다.
    assert utc_dt == datetime(1955, 5, 5, 2, 30, tzinfo=timezone.utc)
    
    # LMT = UTC(02:30) + (126.9780 / 15)시간 = 02:30 + 8시간 27분 54.72초 = 10:57:54.72
    assert adjusted == datetime(1955, 5, 5, 10, 57, 54, 720000)


def test_historical_dst_1988_seoul():
    """
    1988년 서울 올림픽을 앞두고 시행된 서머타임(DST, UTC+10) 구간의 계산 정밀도를 검증합니다.
    """
    utc_dt, adjusted = calculate_adjusted_times(
        birth_date="1988-06-15",
        birth_time="15:00:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
    )
    
    # 1988년 6월은 DST 적용으로 UTC+10이므로 벽시계 15:00은 UTC 05:00입니다.
    assert utc_dt == datetime(1988, 6, 15, 5, 0, tzinfo=timezone.utc)
    
    # LMT = UTC(05:00) + 8시간 27분 54.72초 = 13:27:54.72
    assert adjusted == datetime(1988, 6, 15, 13, 27, 54, 720000)


def test_kasi_golden_case_saju_calculation():
    """
    알려진 표준 명식 데이터(골든 케이스)를 통해 계산된 사주 결과의 무결성을 검증합니다.
    """
    result = calculate_saju(
        birth_date="1990-05-05",
        birth_time="14:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        jasi_boundary=23,
        gender="M"
    )
    
    assert result["solar_year"] == 1990
    assert result["year_pillar"] == "庚午"
    assert result["month_pillar"] == "庚辰"
    assert result["day_pillar"] == "庚午"
    assert result["hour_pillar"] == "癸未"