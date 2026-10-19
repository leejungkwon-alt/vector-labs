# tests/test_dst_fold.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from app.engine.time_correction import calculate_adjusted_times


# ---- 헬퍼: 해당 날짜에서 실제로 모호한 시각을 찾는다 (tzdata 무관) ----
def _find_ambiguous_time(date_str: str, tz_name: str = "Asia/Seoul") -> str:
    tz = ZoneInfo(tz_name)
    base = datetime.fromisoformat(date_str + "T00:00:00")
    for h in range(24):
        for m in (0, 15, 30, 45):
            clock = base + timedelta(hours=h, minutes=m)
            o0 = clock.replace(tzinfo=tz, fold=0).utcoffset()
            o1 = clock.replace(tzinfo=tz, fold=1).utcoffset()
            if o0 != o1:
                return f"{h:02d}:{m:02d}:00"
    pytest.skip(f"{date_str}에 모호한 시각이 없음 (tzdata 버전 이슈)")


def _find_gap_time(date_str: str, tz_name: str = "Asia/Seoul") -> str:
    tz = ZoneInfo(tz_name)
    base = datetime.fromisoformat(date_str + "T00:00:00")
    for h in range(24):
        for m in (0, 15, 30, 45):
            clock = base + timedelta(hours=h, minutes=m)
            aware0 = clock.replace(tzinfo=tz, fold=0)
            rt = aware0.astimezone(ZoneInfo("UTC")).astimezone(tz).replace(tzinfo=None)
            if rt != clock:
                return f"{h:02d}:{m:02d}:00"
    pytest.skip(f"{date_str}에 gap 시각이 없음 (tzdata 버전 이슈)")


def test_dst_gap_rejected():
    t = _find_gap_time("1988-05-08")
    with pytest.raises(ValueError, match="존재하지 않는"):
        calculate_adjusted_times(
            birth_date="1988-05-08",
            birth_time=t,
            timezone_str="Asia/Seoul",
            longitude=126.9780,
            correction_mode="lmt",
        )


def test_dst_ambiguous_without_fold_rejected():
    t = _find_ambiguous_time("1988-10-09")
    with pytest.raises(ValueError, match="모호한"):
        calculate_adjusted_times(
            birth_date="1988-10-09",
            birth_time=t,
            timezone_str="Asia/Seoul",
            longitude=126.9780,
            correction_mode="lmt",
        )


def test_dst_ambiguous_fold_0_and_1():
    t = _find_ambiguous_time("1988-10-09")
    utc0, _ = calculate_adjusted_times(
        birth_date="1988-10-09",
        birth_time=t,
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="none",
        dst_fold=0,
    )
    utc1, _ = calculate_adjusted_times(
        birth_date="1988-10-09",
        birth_time=t,
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="none",
        dst_fold=1,
    )
    assert utc0 != utc1
    assert (utc1 - utc0).total_seconds() == 3600


def test_dst_fold_invalid_value_rejected():
    t = _find_ambiguous_time("1988-10-09")
    with pytest.raises(ValueError, match="dst_fold"):
        calculate_adjusted_times(
            birth_date="1988-10-09",
            birth_time=t,
            timezone_str="Asia/Seoul",
            longitude=126.9780,
            correction_mode="lmt",
            dst_fold=2,
        )


def test_dst_fold_ignored_when_not_ambiguous():
    """모호하지 않은 시각에는 dst_fold가 무시됨."""
    utc_a, _ = calculate_adjusted_times(
        birth_date="1990-05-05",
        birth_time="14:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        dst_fold=0,
    )
    utc_b, _ = calculate_adjusted_times(
        birth_date="1990-05-05",
        birth_time="14:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        dst_fold=1,
    )
    assert utc_a == utc_b