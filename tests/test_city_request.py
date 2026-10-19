# tests/test_city_request.py
import pytest
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import generate_full_report


def test_seoul_preset_matches_explicit():
    """birth_location='seoul' == longitude/timezone_str 직접 지정."""
    a = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul",
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=2026,
    )
    b = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        longitude=126.9780, timezone_str="Asia/Seoul",
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=2026,
    )
    assert a["day_pillar"] == b["day_pillar"]
    assert a["hour_pillar"] == b["hour_pillar"]
    assert a["solar_adjusted_time"] == b["solar_adjusted_time"]


def test_new_york_different_hour_pillar():
    """뉴욕 출생은 LMT가 달라 시주도 달라져야 함."""
    seoul = calculate_saju(
        birth_date="1990-05-05", birth_time="14:30:00",
        birth_location="seoul", correction_mode="lmt",
        jasi_boundary=23, gender="M",
    )
    ny = calculate_saju(
        birth_date="1990-05-05", birth_time="14:30:00",
        birth_location="new_york", correction_mode="lmt",
        jasi_boundary=23, gender="M",
    )
    assert seoul["solar_adjusted_time"] != ny["solar_adjusted_time"]
    assert ny["region"] == "NORTH_AMERICA"


def test_unknown_city_raises():
    with pytest.raises(ValueError, match="Unknown city key"):
        calculate_saju(
            birth_date="1990-05-05", birth_time="14:30:00",
            birth_location="atlantis",
        )


def test_profile_carries_region_and_age_band():
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul",
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=2026,
    )
    profile = build_semantic_profile(result)
    assert profile["region"] == "KOREA"
    assert profile["age_band"]["key"] == "PEAK"
    assert profile["age_band"]["age"] == 52
    assert profile["age_band"]["target_year"] == 2026


def test_profile_without_city_has_null_region():
    """birth_location 없으면 region=None, age_band는 계산됨."""
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        longitude=126.9780, timezone_str="Asia/Seoul",
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=2026,
    )
    profile = build_semantic_profile(result)
    assert profile["region"] is None
    assert profile["age_band"]["key"] == "PEAK"


def test_full_report_meta_includes_region_and_age_band():
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul",
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=2026,
    )
    profile = build_semantic_profile(result)
    report = generate_full_report(profile, lang="ko")
    meta = report["meta"]
    assert meta["region"] == "KOREA"
    assert meta["age_band"]["key"] == "PEAK"
    assert meta["age_band"]["age"] == 52