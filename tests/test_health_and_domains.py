# tests/test_health_and_domains.py
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import generate_full_report


def _report(birth_date, birth_time, lang="en", target_year=None):
    kwargs = dict(
        birth_date=birth_date,
        birth_time=birth_time,
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        jasi_boundary=23,
        gender="M",
    )
    if target_year:
        kwargs["target_year"] = target_year
    result = calculate_saju(**kwargs)
    profile = build_semantic_profile(result)
    return generate_full_report(profile, lang=lang)


# ---- Health ----
def test_health_section_en_present():
    report = _report("1974-02-24", "05:30:00", lang="en")
    assert "health" in report["sections"]
    health = report["sections"]["health"]
    assert health["id"] == "health"
    assert health["title"] == "Body & Wellness"
    assert len(health["blocks"]) >= 1
    assert len(health["practices"]) >= 3


def test_health_section_ko_present():
    report = _report("1974-02-24", "05:30:00", lang="ko")
    health = report["sections"]["health"]
    assert health["title"] == "몸과 마음"
    assert any("\uac00" <= ch <= "\ud7a3" for ch in health["hero"])


def test_health_dominant_and_deficient():
    """1974: 木 dominant, 水 deficient."""
    report = _report("1974-02-24", "05:30:00", lang="en")
    health = report["sections"]["health"]
    roles = {b["role"] for b in health["blocks"]}
    sigs = {b["signature"] for b in health["blocks"]}
    assert "dominant" in roles
    assert "GROWTH" in sigs
    assert "FLOW" in sigs


# ---- Lucky Code Domains ----
def test_lucky_code_domains_en():
    report = _report("1974-02-24", "05:30:00", lang="en")
    power = report["sections"]["lucky_code"]["power"]
    assert "domains" in power
    domains = power["domains"]
    # 1974 용신 土 → GROUND
    assert power["signature"] == "GROUND"
    for key in ("career", "wealth", "relationships", "learning", "everyday", "avoid"):
        assert key in domains


def test_lucky_code_domains_ko():
    report = _report("1974-02-24", "05:30:00", lang="ko")
    power = report["sections"]["lucky_code"]["power"]
    domains = power["domains"]
    assert "career" in domains
    assert any("\uac00" <= ch <= "\ud7a3" for ch in domains["career"])
    assert any("\uac00" <= ch <= "\ud7a3" for ch in domains["everyday"])
    assert isinstance(domains["avoid"], list)


def test_lucky_code_domains_differ_by_element():
    """용신 오행이 다르면 domains 내용도 달라야 함."""
    r_1974 = _report("1974-02-24", "05:30:00", lang="en")
    r_1990 = _report("1990-05-05", "14:30:00", lang="en")

    d_1974 = r_1974["sections"]["lucky_code"]["power"]["domains"]
    d_1990 = r_1990["sections"]["lucky_code"]["power"]["domains"]

    assert d_1974["career"] != d_1990["career"]
    assert d_1974["wealth"] != d_1990["wealth"]