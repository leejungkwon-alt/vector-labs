# tests/test_age_band_content.py
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import (
    generate_full_report,
    write_age_band_section,
    write_timeline_section,
    write_year_section,
)


def _profile_1974(target_year=2026):
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul",
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=target_year,
    )
    return build_semantic_profile(result)


def _profile_2005(target_year=2026):
    result = calculate_saju(
        birth_date="2005-08-15", birth_time="10:00:00",
        birth_location="seoul",
        correction_mode="lmt", jasi_boundary=23, gender="F",
        target_year=target_year,
    )
    return build_semantic_profile(result)


# ---- Age band section ----
def test_age_band_section_1974_peak():
    profile = _profile_1974()
    sec = write_age_band_section(profile, lang="en")
    assert sec["key"] == "PEAK"
    assert sec["age"] == 52
    assert sec["label"] == "Peak Output"
    assert sec["headline"]
    assert len(sec["advice"]) >= 3


def test_age_band_section_2005_early():
    profile = _profile_2005()
    sec = write_age_band_section(profile, lang="en")
    assert sec["key"] == "EARLY"
    assert sec["age"] == 21
    assert sec["label"] == "Early"


def test_age_band_ko():
    profile = _profile_1974()
    sec = write_age_band_section(profile, lang="ko")
    assert sec["key"] == "PEAK"
    assert sec["label"] == "전성기"            # ← 산출기에서 변경
    assert any("\uac00" <= ch <= "\ud7a3" for ch in sec["headline"])
    assert any("\uac00" <= ch <= "\ud7a3" for ch in sec["body"])


# ---- Timeline is_current ----
def test_timeline_current_marker_1974():
    profile = _profile_1974()
    tl = write_timeline_section(profile, lang="en")
    currents = [i for i in tl["items"] if i["is_current"]]
    assert len(currents) == 1
    # 반올림 규칙(6개월 이상 → +1) 도입 후 start_age 가 3 또는 4 가 될 수 있음.
    # 정확성보다 "age 52 가 정확히 한 구간에 속한다"는 규칙 일관성을 검증.
    assert 42 <= currents[0]["ages"][0] <= 44
    assert 51 <= currents[0]["ages"][1] <= 53


def test_timeline_current_marker_2005():
    profile = _profile_2005()
    tl = write_timeline_section(profile, lang="en")
    currents = [i for i in tl["items"] if i["is_current"]]
    assert len(currents) == 1


# ---- Year life_stage_context ----
def test_year_has_life_stage_context_1974():
    """year.life_stage_context는 key/label/headline만. note는 age_band 섹션에서."""
    profile = _profile_1974()
    year = write_year_section(profile, lang="en")
    assert year is not None
    ctx = year["life_stage_context"]
    assert ctx is not None
    assert ctx["key"] == "PEAK"
    assert ctx["label"] == "Peak Output"
    assert ctx["headline"]
    # note 필드는 제거됨 (중복 방지)
    assert "note" not in ctx


def test_year_life_stage_context_ko():
    profile = _profile_1974()
    year = write_year_section(profile, lang="ko")
    ctx = year["life_stage_context"]
    assert ctx["key"] == "PEAK"
    assert ctx["label"] == "전성기"            # ← 산출기에서 변경


def test_year_without_target_year_has_no_section():
    """target_year 없으면 year 섹션 자체가 없음."""
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul",
        correction_mode="lmt", jasi_boundary=23, gender="M",
        # target_year 없음
    )
    profile = build_semantic_profile(result)
    year = write_year_section(profile, lang="en")
    assert year is None


# ---- Full report ----
def test_full_report_has_age_band_meta():
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul",
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=2026,
    )
    profile = build_semantic_profile(result)
    report = generate_full_report(profile, lang="en")

    assert report["meta"]["age_band"]["key"] == "PEAK"
    assert report["meta"]["age_band"]["age"] == 52

    items = report["sections"]["timeline"]["items"]
    assert sum(1 for i in items if i["is_current"]) == 1

    year = report["sections"]["year"]
    assert year["life_stage_context"]["key"] == "PEAK"