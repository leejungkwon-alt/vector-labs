# tests/test_content_writer.py
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import write_core_section


def _profile_1974():
    result = calculate_saju(
        birth_date="1974-02-24",
        birth_time="05:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        jasi_boundary=23,
        gender="M",
        target_year=2026,
    )
    return build_semantic_profile(result)


def test_core_section_basic_shape():
    """필수 필드가 다 있는지."""
    profile = _profile_1974()
    section = write_core_section(profile, lang="en")

    for key in ("title", "archetype", "hero", "narrative",
                "shadows", "advice", "keywords", "intensity_label"):
        assert key in section, f"Missing key: {key}"

    assert section["title"] == "Your Core"
    assert isinstance(section["narrative"], list)
    assert isinstance(section["advice"], list)


def test_core_section_radiator_self_sourced():
    """1974 프로필 → RADIATOR / SELF_SOURCED."""
    profile = _profile_1974()
    section = write_core_section(profile, lang="en")

    assert section["archetype"]["key"] == "THE_RADIATOR"
    assert section["archetype"]["name"] == "Sun Above Stone"  # 1974 = 丙申
    assert section["intensity_label"] == "Self-Sourced"
    assert len(section["hero"]) > 0
    assert len(section["narrative"]) >= 3
    assert len(section["advice"]) >= 3


def test_core_section_fallback_unknown_intensity():
    """실제 아키타입 + 존재하지 않는 강도 → DEFAULT_INTENSITY 폴백."""
    fake_profile = {
        "archetype": {
            "key": "THE_RADIATOR",
            "stem": "丙",
            "intensity": "ZZZ_UNKNOWN",
            "strength_raw": "신강",
        }
    }
    section = write_core_section(fake_profile, lang="en")
    assert section["archetype"]["name"] == "The Radiator"
    assert section["hero"] == "You are still becoming."
    assert section["intensity_label"] == "ZZZ_UNKNOWN"
    assert section["narrative"] == [
        "This chart is being read in a way we don't have words for yet."
    ]


def test_core_section_unknown_archetype_raises():
    import pytest
    fake_profile = {"archetype": {"key": "THE_UNKNOWN", "stem": "X", "intensity": "SELF_SOURCED"}}
    with pytest.raises(KeyError):
        write_core_section(fake_profile, lang="en")


def test_loader_lists_available():
    from app.services.content.loader import list_available
    sections = list_available("en")
    assert "core" in sections


def test_loader_invalid_lang_raises():
    import pytest
    from app.services.content.loader import load_pack
    with pytest.raises(KeyError):
        load_pack("xx", "core")