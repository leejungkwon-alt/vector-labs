from datetime import datetime, timezone
from app.engine.time_correction import calculate_adjusted_times


def test_lmt_exact_seoul():
    """서울 1990-05-05 14:30 KST의 LMT 및 UTC 값 검증."""
    utc_dt, adjusted = calculate_adjusted_times(
        birth_date="1990-05-05",
        birth_time="14:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
    )
    # KST(UTC+9) → UTC 05:30
    assert utc_dt == datetime(1990, 5, 5, 5, 30, tzinfo=timezone.utc)
    # LMT = UTC + 126.9780/15h = 05:30 + 8h27m54.72s = 13:57:54.72
    assert adjusted == datetime(1990, 5, 5, 13, 57, 54, 720000)


def test_calculate_adjusted_times_none():
    """correction_mode='none'이면 보정 없이 벽시계 그대로."""
    utc_dt, adjusted = calculate_adjusted_times(
        birth_date="1990-05-05",
        birth_time="14:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="none",
    )
    assert adjusted == datetime(1990, 5, 5, 14, 30, 0)
    assert utc_dt == datetime(1990, 5, 5, 5, 30, tzinfo=timezone.utc)


def test_lmt_negative_longitude():
    """서부 경도(뉴욕 -74)에서는 LMT가 벽시계보다 느려야 함."""
    utc_dt, adjusted = calculate_adjusted_times(
        birth_date="2000-07-04",
        birth_time="12:00:00",
        timezone_str="America/New_York",
        longitude=-74.0060,
        correction_mode="lmt",
    )
    # 2000-07-04 EDT (UTC-4) → UTC 16:00
    assert utc_dt == datetime(2000, 7, 4, 16, 0, tzinfo=timezone.utc)
    # LMT = 16:00 + (-74.0060/15)h = 16:00 - 4h56m1.44s = 11:03:58.56
    assert adjusted == datetime(2000, 7, 4, 11, 3, 58, 560000)


def test_dst_lmt_seoul_1988():
    """서울 서머타임 기간(1988-05-08) LMT 검증."""
    utc_dt, adjusted = calculate_adjusted_times(
        birth_date="1988-05-08",
        birth_time="12:00:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
    )
    # 1988-05-08 KST는 DST 시행 중 (UTC+10) → UTC 02:00
    assert utc_dt == datetime(1988, 5, 8, 2, 0, tzinfo=timezone.utc)
    # LMT = 02:00 + 8h27m54.72s = 10:27:54.72
    assert adjusted == datetime(1988, 5, 8, 10, 27, 54, 720000)