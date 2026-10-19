# tests/test_counseling_tone.py
"""카운셀링 톤 회귀 방지: disclaimer 학파 의존성, 월운 등급 컨텍스트, 신살 role/note."""
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import (
    generate_full_report,
    write_sinsal_section,
)


def _profile_and_report(lang="ko"):
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul",
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=2026,
    )
    profile = build_semantic_profile(result)
    return profile, generate_full_report(profile, lang=lang)


# ---- Disclaimer ----
def test_disclaimer_ko_mentions_school_dependency():
    _, report = _profile_and_report(lang="ko")
    d = report["disclaimer"]
    assert "유파" in d or "학파" in d
    # 기술 용어 대신 의미로 풀어 설명해야 함
    assert "부족한" in d or "균형" in d
    assert "의료" in d and "금융" in d


def test_disclaimer_en_mentions_school_dependency():
    _, report = _profile_and_report(lang="en")
    d = report["disclaimer"]
    assert "school-dependent" in d
    assert "lineage" in d or "lineages" in d
    assert "not medical" in d


# ---- Monthly grade_context ----
def test_monthly_items_have_grade_context_ko():
    _, report = _profile_and_report(lang="ko")
    for item in report["sections"]["monthly"]["items"]:
        assert "grade_context" in item
        assert item["grade_context"]
        assert any(k in item["grade_context"] for k in ("지지", "기반", "흐름"))


def test_monthly_items_have_grade_context_en():
    _, report = _profile_and_report(lang="en")
    for item in report["sections"]["monthly"]["items"]:
        assert item["grade_context"]
        assert any(k in item["grade_context"].lower() for k in ("root", "energy"))


# ---- Sinsal position_role / position_note ----
def test_sinsal_has_position_role_and_note_ko():
    profile, _ = _profile_and_report(lang="ko")
    sec = write_sinsal_section(profile, lang="ko")
    assert sec is not None
    for item in sec["items"]:
        assert item.get("position_role"), f"position_role 비어있음: {item['name']}"
        assert item.get("position_note"), f"position_note 비어있음: {item['name']}"


def test_sinsal_has_position_role_and_note_en():
    profile, _ = _profile_and_report(lang="en")
    sec = write_sinsal_section(profile, lang="en")
    for item in sec["items"]:
        assert item["position_role"]
        assert item["position_note"]
