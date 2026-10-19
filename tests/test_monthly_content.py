# tests/test_monthly_content.py
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import (
    generate_full_report,
    write_monthly_section,
)


def _profile(target_year=2026):
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul",
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=target_year,
    )
    return build_semantic_profile(result)


def test_monthly_lucks_have_ten_god_in_calculator():
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul", gender="M", target_year=2026,
    )
    months = result["luck_info"]["monthly_lucks"]
    assert len(months) == 12
    for m in months:
        assert "ten_god" in m
        assert m["ten_god"].startswith("TEN_GOD_")


def test_profile_has_monthly_calendar():
    p = _profile()
    cal = p["monthly_calendar"]
    assert len(cal) == 12
    for item in cal:
        assert "month_index" in item
        assert "pillar" in item
        assert "ten_god" in item
        assert "score" in item
        assert "grade" in item
        assert item["grade"] in ("PEAK", "FAVORABLE", "NEUTRAL", "CAUTION", "CHALLENGING")


def test_monthly_no_target_year_returns_empty():
    p = build_semantic_profile(calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul", gender="M",
    ))
    assert p["monthly_calendar"] == []


def test_write_monthly_section_en():
    p = _profile()
    sec = write_monthly_section(p, lang="en")
    assert sec is not None
    assert sec["id"] == "monthly"
    assert "Monthly" in sec["title"] or "Calendar" in sec["title"]
    assert len(sec["items"]) == 12
    for item in sec["items"]:
        assert item["name"]
        assert item["headline"]
        assert item["body"]
        assert item["watch_for"]
        assert item["lean_into"]
        assert item["grade_label"]


def test_write_monthly_section_ko():
    p = _profile()
    sec = write_monthly_section(p, lang="ko")
    assert sec["title"] == "월별 흐름"
    for item in sec["items"]:
        assert any("\uac00" <= ch <= "\ud7a3" for ch in item["name"])
        assert any("\uac00" <= ch <= "\ud7a3" for ch in item["body"])


def test_monthly_items_sorted_by_index():
    p = _profile()
    sec = write_monthly_section(p, lang="ko")
    indices = [i["month_index"] for i in sec["items"]]
    assert indices == list(range(1, 13))


def test_monthly_hero_includes_year():
    p = _profile(target_year=2026)
    sec = write_monthly_section(p, lang="ko")
    assert "2026" in sec["hero"]


def test_full_report_includes_monthly():
    p = _profile()
    report = generate_full_report(p, lang="ko")
    assert "monthly" in report["sections"]
    monthly = report["sections"]["monthly"]
    assert len(monthly["items"]) == 12


def test_full_report_without_target_year_has_no_monthly():
    p = build_semantic_profile(calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul", gender="M",
    ))
    report = generate_full_report(p, lang="ko")
    assert "monthly" not in report["sections"]


def test_monthly_ten_god_coverage():
    p = _profile()
    sec = write_monthly_section(p, lang="en")
    ten_gods = {i["ten_god"] for i in sec["items"] if i["ten_god"]}
    assert len(ten_gods) >= 2
