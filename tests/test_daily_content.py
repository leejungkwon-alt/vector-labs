"""일운 콘텐츠 팩 커버리지 (Step 3: list variants 지원)."""
from app.services.content.loader import load_pack


REQUIRED_TAGS = [
    "TEN_GOD_FRIEND", "TEN_GOD_ROB_WEALTH", "TEN_GOD_EATING_GOD",
    "TEN_GOD_HURTING_OFFICER", "TEN_GOD_INDIRECT_WEALTH",
    "TEN_GOD_DIRECT_WEALTH", "TEN_GOD_SEVEN_KILLINGS",
    "TEN_GOD_DIRECT_OFFICER", "TEN_GOD_INDIRECT_RESOURCE",
    "TEN_GOD_DIRECT_RESOURCE",
]

REQUIRED_FIELDS = ["name", "headline", "body", "watch_for", "lean_into"]


def _iter_variants(raw):
    if isinstance(raw, list):
        return raw
    return [raw]


def test_pack_registered_both_langs():
    for lang in ("en", "ko"):
        pack = load_pack(lang, "daily")
        assert "DAILY_THEME_CONTENT" in pack
        assert "DEFAULT_DAILY_THEME" in pack
        assert "GRADE_LABEL" in pack
        assert "DAILY_HERO_TEMPLATE" in pack


def test_all_ten_gods_covered_en():
    pack = load_pack("en", "daily")
    for tg in REQUIRED_TAGS:
        assert tg in pack["DAILY_THEME_CONTENT"], f"EN missing {tg}"
        variants = _iter_variants(pack["DAILY_THEME_CONTENT"][tg])
        assert variants, f"EN {tg} empty"
        for i, entry in enumerate(variants):
            for field in REQUIRED_FIELDS:
                assert field in entry, f"EN {tg}[{i}] missing {field}"
                assert entry[field], f"EN {tg}[{i}].{field} empty"


def test_all_ten_gods_covered_ko():
    pack = load_pack("ko", "daily")
    for tg in REQUIRED_TAGS:
        assert tg in pack["DAILY_THEME_CONTENT"], f"KO missing {tg}"
        variants = _iter_variants(pack["DAILY_THEME_CONTENT"][tg])
        assert variants, f"KO {tg} empty"
        for i, entry in enumerate(variants):
            for field in REQUIRED_FIELDS:
                assert field in entry, f"KO {tg}[{i}] missing {field}"
                assert entry[field], f"KO {tg}[{i}].{field} empty"


def test_ko_content_is_korean():
    pack = load_pack("ko", "daily")
    for tg, raw in pack["DAILY_THEME_CONTENT"].items():
        for i, entry in enumerate(_iter_variants(raw)):
            blob = entry["headline"] + " " + entry["body"]
            assert any("\uac00" <= ch <= "\ud7a3" for ch in blob), \
                f"KO {tg}[{i}] not Korean"


def test_grade_labels_complete():
    for lang in ("en", "ko"):
        pack = load_pack(lang, "daily")
        for grade in ("PEAK", "FAVORABLE", "NEUTRAL", "CAUTION", "CHALLENGING"):
            assert grade in pack["GRADE_LABEL"]