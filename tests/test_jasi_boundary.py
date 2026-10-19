# tests/test_jasi_boundary.py
from datetime import datetime
from app.engine.pillars import get_day_pillar, get_hour_pillar


def test_jasi_23_boundary_uses_next_day_for_both_pillars():
    """조자시설: 2000-01-01 23:30은 다음날(1/2) 일주·시주."""
    dt = datetime(2000, 1, 1, 23, 30)
    # 2000-01-02 일주 己未
    assert get_day_pillar(dt, jasi_boundary=23) == "己未"
    # 五鼠遁: 甲己일 子시는 甲子
    assert get_hour_pillar(dt, jasi_boundary=23) == "甲子"


def test_jasi_0_boundary_keeps_day_but_uses_next_day_stem_for_hour():
    """야자시설: 23:30의 일주는 당일 그대로, 시주만 다음날 일간 기준."""
    dt = datetime(2000, 1, 1, 23, 30)
    # 일주: 당일(1/1) 戊午 그대로
    assert get_day_pillar(dt, jasi_boundary=0) == "戊午"
    # 시주: 다음날(1/2) 일간 己 기준 → 甲子
    assert get_hour_pillar(dt, jasi_boundary=0) == "甲子"


def test_jasi_0_boundary_23h_not_duplicating_00h():
    """0 경계에서 23:30과 00:30의 시주가 달라야 함 (야자시 중복 방지)."""
    dt_23 = datetime(2000, 1, 1, 23, 30)
    dt_00 = datetime(2000, 1, 1, 0, 30)
    # 23:30 → 다음날(己) 기준 甲子, 00:30 → 당일(戊) 기준 壬子
    assert get_hour_pillar(dt_23, jasi_boundary=0) != get_hour_pillar(dt_00, jasi_boundary=0)