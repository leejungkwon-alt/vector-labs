# tests/test_edge_cases.py

import pytest
from datetime import datetime, timezone, timedelta
from app.engine.calculator import calculate_saju
from app.schemas.saju import SajuRequest

KST = timezone(timedelta(hours=9))


def test_solar_term_boundary_transition():
    """1990년 입춘 정확한 시각(11:13:58 KST) 직전/직후로 solar_year/월지 경계 검증."""
    # 1990년 입춘 직전: 11:13:00 KST (입춘 전 -> 1989년)
    dt_before = datetime(1990, 2, 4, 11, 13, 0, tzinfo=KST)
    # 1990년 입춘 직후: 11:15:00 KST (입춘 후 -> 1990년)
    dt_after = datetime(1990, 2, 4, 11, 15, 0, tzinfo=KST)

    result_before = calculate_saju(
        birth_date=dt_before.strftime("%Y-%m-%d"),
        birth_time=dt_before.strftime("%H:%M:%S"),
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="none",
    )
    result_after = calculate_saju(
        birth_date=dt_after.strftime("%Y-%m-%d"),
        birth_time=dt_after.strftime("%H:%M:%S"),
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="none",
    )

    # 입춘 전: 전년도(1989) 기운 유지
    assert result_before["solar_year"] == 1989
    # 입춘 후: 새해(1990) 진입, 월지는 寅
    assert result_after["solar_year"] == 1990
    assert result_after["month_pillar"][1] == "寅"

    assert "birth_instant_utc" in result_before
    assert "birth_instant_utc" in result_after
    assert result_before["birth_instant_utc"] != result_after["birth_instant_utc"]


def test_pydantic_validation_error_handling():
    # 잘못된 날짜 형식 (1990-02-31은 존재하지 않음)
    with pytest.raises(ValueError):
        SajuRequest(birth_date="1990-02-31", birth_time="14:30:00")

    # 범위를 벗어난 경도
    with pytest.raises(ValueError):
        SajuRequest(
            birth_date="1990-05-05", birth_time="14:30:00", longitude=200.0
        )

    # 잘못된 자시 경계값
    with pytest.raises(ValueError):
        SajuRequest(
            birth_date="1990-05-05", birth_time="14:30:00", jasi_boundary=12
        )

    # 미구현 eot 모드 → 스키마에서 거부
    with pytest.raises(ValueError):
        SajuRequest(
            birth_date="1990-05-05", birth_time="14:30:00", correction_mode="eot"
        )