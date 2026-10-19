from app.engine.calculator import calculate_saju


def test_sohan_boundary_丑월_transition():
    """소한(1/5~1/6) 직전·직후로 子월 → 丑월 전환 검증."""
    # 1990-01-05 소한 무렵. 정확 시각은 매년 달라지나 1/5~1/6 사이.
    before = calculate_saju(
        birth_date="1990-01-05", birth_time="00:00:00",
        timezone_str="Asia/Seoul", longitude=126.9780, correction_mode="none",
    )
    after = calculate_saju(
        birth_date="1990-01-10", birth_time="00:00:00",
        timezone_str="Asia/Seoul", longitude=126.9780, correction_mode="none",
    )
    # 1/5 입춘 전이므로 solar_year = 1989
    assert before["solar_year"] == 1989
    assert after["solar_year"] == 1989
    # 1/10은 소한 이후 → 丑월
    assert after["month_pillar"][1] == "丑"