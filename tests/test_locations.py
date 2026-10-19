# tests/test_locations.py
import pytest
from app.engine.locations import CITY_PRESETS, resolve_location, list_cities


def test_known_cities_resolve():
    lon, tz, region = resolve_location("seoul")
    assert abs(lon - 126.9780) < 0.001
    assert tz == "Asia/Seoul"
    assert region == "KOREA"

    lon, tz, region = resolve_location("new_york")
    assert abs(lon - (-74.0060)) < 0.001
    assert tz == "America/New_York"
    assert region == "NORTH_AMERICA"


def test_case_insensitive_and_whitespace():
    lon_a, tz_a, _ = resolve_location("Seoul")
    lon_b, tz_b, _ = resolve_location("  SEOUL  ")
    assert lon_a == lon_b
    assert tz_a == tz_b


def test_unknown_city_raises_with_hint():
    with pytest.raises(ValueError, match="Unknown city key"):
        resolve_location("atlantis")
    with pytest.raises(ValueError, match="longitude"):
        resolve_location("atlantis")


def test_region_filter():
    korea = list_cities(region="KOREA")
    assert all(c["region"] == "KOREA" for c in korea)
    assert any(c["key"] == "seoul" for c in korea)
    assert any(c["key"] == "busan" for c in korea)

    us = list_cities(region="NORTH_AMERICA")
    assert any(c["key"] == "new_york" for c in us)
    assert any(c["key"] == "toronto" for c in us)


def test_total_city_count():
    assert len(CITY_PRESETS) >= 50


def test_seoul_vs_busan_longitude_difference():
    lon_s, _, _ = resolve_location("seoul")
    lon_b, _, _ = resolve_location("busan")
    diff_degrees = abs(lon_b - lon_s)
    assert diff_degrees > 2.0       # 약 2.1도 차이