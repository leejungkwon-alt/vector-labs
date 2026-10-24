"""일주(60) + intensity(3) 콘텐츠 레이어 테스트."""
import pathlib

from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import write_core_section
from app.services.content.loader import load_pack

DATA_ROOT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "app" / "services" / "content" / "data"
)


def _profile(birth_date, birth_time, gender="M"):
    return build_semantic_profile(calculate_saju(
        birth_date=birth_date, birth_time=birth_time,
        birth_location="seoul", correction_mode="lmt",
        jasi_boundary=23, gender=gender,
    ))


def test_1974_day_pillar_is_bingshen():
    p = _profile("1974-02-24", "05:30:00")
    assert p["pillars"]["day_pillar"] == "丙申"


def test_1990_day_pillar_is_gengwu():
    p = _profile("1990-05-05", "14:30:00")
    assert p["pillars"]["day_pillar"] == "庚午"


def test_bingshen_uses_pillar_content():
    p = _profile("1974-02-24", "05:30:00")
    sec = write_core_section(p, lang="ko")
    assert sec["pillar"] == "丙申"
    assert sec["content_source"] == "pillar"
    assert "바위 위" in sec["hero"] or "태양" in sec["hero"]


def test_gengwu_uses_pillar_content_en():
    p = _profile("1990-05-05", "14:30:00")
    sec = write_core_section(p, lang="en")
    assert sec["pillar"] == "庚午"
    assert sec["content_source"] == "pillar"
    assert "forge" in sec["hero"].lower()


def test_same_stem_different_pillar_differ():
    """丙申과 庚午는 다른 hero/narrative (스텁이 아닌 파일럿이므로)."""
    p74 = write_core_section(_profile("1974-02-24", "05:30:00"), lang="ko")
    p90 = write_core_section(_profile("1990-05-05", "14:30:00"), lang="ko")
    assert p74["pillar"] != p90["pillar"]
    assert p74["hero"] != p90["hero"]
    assert p74["narrative"] != p90["narrative"]


def test_missing_pillar_file_falls_back(monkeypatch):
    """일주 파일이 없으면 10×3 fallback으로 넘어가야 함."""
    import app.services.content_writer as cw
    original = cw.load_pack

    def patched(lang, section):
        if section.startswith("core_pillars/"):
            raise KeyError("simulated missing")
        return original(lang, section)

    monkeypatch.setattr(cw, "load_pack", patched)
    sec = write_core_section(_profile("1974-02-24", "05:30:00"), lang="ko")
    assert sec["content_source"] == "intensity_fallback"
    assert sec["intensity_label"] == "자기충전형"
    assert len(sec["narrative"]) >= 3


def test_intensity_voice_is_prepended():
    p = _profile("1974-02-24", "05:30:00")
    sec = write_core_section(p, lang="ko")
    overlay = load_pack("ko", "core")["INTENSITY_OVERLAY"]["SELF_SOURCED"]
    assert sec["narrative"][0] == overlay["voice"]


def test_intensity_advice_addon_included():
    p = _profile("1974-02-24", "05:30:00")
    sec = write_core_section(p, lang="ko")
    overlay = load_pack("ko", "core")["INTENSITY_OVERLAY"]["SELF_SOURCED"]
    for extra in overlay["advice_addon"]:
        assert extra in sec["advice"]


def test_cover_tagline_unchanged():
    """일주 파일럿이 tagline을 override하지 않아야 함 (기존 cover 테스트 보호)."""
    from app.services.content_writer import _build_cover
    cover = _build_cover(_profile("1974-02-24", "05:30:00"), "en")
    assert cover["archetype"]["tagline"] == "You warm rooms by existing in them."
    assert cover["archetype"]["name"] == "Sun Above Stone"  # 1974 = 丙申


def test_intensity_overlay_complete_in_both_langs():
    """3개 intensity overlay가 두 언어에 모두 존재."""
    for lang in ("ko", "en"):
        pack = load_pack(lang, "core")
        overlay = pack.get("INTENSITY_OVERLAY", {})
        for key in ("SELF_SOURCED", "BALANCED_CORE", "ENVIRONMENT_TUNED"):
            assert key in overlay, f"{lang} missing overlay: {key}"
            assert overlay[key].get("voice"), f"{lang}/{key} voice empty"
            assert overlay[key].get("advice_addon"), f"{lang}/{key} advice_addon empty"
