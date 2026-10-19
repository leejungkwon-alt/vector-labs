"""궁합 콘텐츠 팩 커버리지 테스트 (Step 3 structure-aware)."""
from app.services.content.loader import load_pack


REQUIRED_TAGS = {
    "ELEMENT_CONTENT": ["COMPLEMENTARY", "BALANCED", "MODERATE", "TENSION", "DEFAULT"],
    "DAY_MASTER_CONTENT": [
        "STEM_UNION", "STEM_CLASH", "BRANCH_UNION", "BRANCH_CLASH",
        "TEN_GOD_FRIEND", "TEN_GOD_WEALTH", "TEN_GOD_OFFICER",
        "TEN_GOD_OUTPUT", "TEN_GOD_RESOURCE", "MIXED",
    ],
    "TEN_GODS_CONTENT": ["COMPLEMENTARY", "MIRROR", "TENSION", "NEUTRAL", "DEFAULT"],
    "SINSAL_CONTENT": [
        "SHARED_ATTRACTION", "SHARED_DEPTH", "SHARED_WANDER",
        "SHARED_LEADERSHIP", "SHARED_RESONANCE", "OPPOSITE_PULL",
        "SINGLE_ANCHOR", "NEITHER", "DEFAULT",
    ],
    "OVERALL_CONTENT": ["PEAK", "FAVORABLE", "NEUTRAL", "CAUTION", "CHALLENGING"],
}


def _iter_section_entries(sec: dict):
    """flat / nested(romance|business) 구조 모두 지원."""
    if not isinstance(sec, dict):
        return
    if "romance" in sec or "business" in sec:
        for rel_key in ("romance", "business"):
            sub = sec.get(rel_key, {})
            if not isinstance(sub, dict):
                continue
            for tag, entry in sub.items():
                if isinstance(entry, dict):
                    yield f"{rel_key}/{tag}", entry
    else:
        for tag, entry in sec.items():
            if isinstance(entry, dict):
                yield tag, entry


def _get_tag_content(sec: dict, tag: str):
    if tag in sec:
        return sec[tag]
    for rel_key in ("romance", "business"):
        sub = sec.get(rel_key, {})
        if tag in sub:
            return sub[tag]
    return None


def test_pack_registered_both_langs():
    for lang in ("en", "ko"):
        pack = load_pack(lang, "compatibility")
        assert "ELEMENT_CONTENT" in pack
        assert "DISCLAIMER" in pack


def test_all_tags_present_en():
    pack = load_pack("en", "compatibility")
    for section, tags in REQUIRED_TAGS.items():
        for tag in tags:
            content = _get_tag_content(pack[section], tag)
            assert content is not None, f"EN missing {section}/{tag}"
            assert content.get("headline"), f"EN {section}/{tag} headline empty"
            assert content.get("body"), f"EN {section}/{tag} body empty"


def test_all_tags_present_ko():
    pack = load_pack("ko", "compatibility")
    for section, tags in REQUIRED_TAGS.items():
        for tag in tags:
            content = _get_tag_content(pack[section], tag)
            assert content is not None, f"KO missing {section}/{tag}"


def test_ko_content_is_korean():
    pack = load_pack("ko", "compatibility")
    for section in REQUIRED_TAGS:
        for label, entry in _iter_section_entries(pack[section]):
            blob = entry.get("headline", "") + " " + entry.get("body", "")
            assert any("\uac00" <= ch <= "\ud7a3" for ch in blob), \
                f"KO {section}/{label} not Korean"


def test_disclaimers_present():
    for lang in ("en", "ko"):
        pack = load_pack(lang, "compatibility")
        d = pack.get("DISCLAIMER", "")
        assert len(d) > 40
        assert "verdict" in d.lower() or "판결" in d or "예측" in d