# tests/test_age_band.py
from datetime import datetime
from app.engine.age_band import compute_age_band


def test_early():
    r = compute_age_band(2005, 2026)   # age 21
    assert r["key"] == "EARLY"
    assert r["age"] == 21


def test_mid_boundaries():
    assert compute_age_band(2001, 2026)["key"] == "MID"    # age 25
    assert compute_age_band(1987, 2026)["key"] == "MID"    # age 39


def test_peak_boundaries():
    assert compute_age_band(1986, 2026)["key"] == "PEAK"   # age 40
    assert compute_age_band(1972, 2026)["key"] == "PEAK"   # age 54


def test_senior_boundaries():
    assert compute_age_band(1971, 2026)["key"] == "SENIOR" # age 55
    assert compute_age_band(1957, 2026)["key"] == "SENIOR" # age 69


def test_elder():
    assert compute_age_band(1956, 2026)["key"] == "ELDER"  # age 70


def test_1974_2026():
    r = compute_age_band(1974, 2026)
    assert r["key"] == "PEAK"
    assert r["age"] == 52
    assert r["min"] == 40
    assert r["max"] == 54


def test_default_target_year_uses_current():
    """target_year 미지정 시 올해 기준."""
    current_year = datetime.now().year
    r = compute_age_band(2000)
    assert r["target_year"] == current_year
    assert r["age"] == current_year - 2000