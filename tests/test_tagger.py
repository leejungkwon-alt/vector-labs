# tests/test_tagger.py
from datetime import datetime, timezone, timedelta
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile


KST = timezone(timedelta(hours=9))


def _calc_1974():
    return calculate_saju(
        birth_date="1974-02-24",
        birth_time="05:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        jasi_boundary=23,
        gender="M",
        target_year=2026,
    )


def test_archetype_1974():
    """丙 일간 → THE_RADIATOR, 신강 → SELF_SOURCED."""
    result = _calc_1974()
    profile = build_semantic_profile(result)

    assert profile["archetype"]["key"] == "THE_RADIATOR"
    assert profile["archetype"]["stem"] == "丙"
    assert profile["archetype"]["intensity"] == "SELF_SOURCED"
    assert profile["archetype"]["strength_raw"] == "신강"


def test_energy_signature_1974():
    """목 과다, 물 부족(deficient). 완전 결핍은 아님 (申 지장간 壬)."""
    result = _calc_1974()
    profile = build_semantic_profile(result)

    sig = profile["energy_signature"]
    assert "GROWTH" in sig["dominant"]          # 木 과다
    assert "FLOW" in sig["deficient"]            # 水 부족 (0.3)
    assert "FLOW" not in sig["missing"]          # 완전 결핍은 아님
    assert "木" in sig["percentages"]
    assert sig["percentages"]["水"] > 0          # 0은 아님


def test_lucky_code_1974():
    """용신 土 → GROUND, 희신 金 → EDGE, 기신 [木, 火] → [GROWTH, SPARK]."""
    result = _calc_1974()
    profile = build_semantic_profile(result)

    lc = profile["lucky_code"]
    assert lc["power"] == "GROUND"
    assert lc["power_element"] == "土"
    assert lc["support"] == "EDGE"
    assert lc["support_element"] == "金"
    assert "GROWTH" in lc["watch_out"]
    assert "SPARK" in lc["watch_out"]


def test_money_work_bond_modes_1974():
    """1974: 편재(INDIRECT_WEALTH) + 편인(INDIRECT_RESOURCE) + 비견(FRIEND)."""
    result = _calc_1974()
    profile = build_semantic_profile(result)

    assert profile["money_mode"] == "THE_OPERATOR"       # 편재
    assert profile["work_mode"] == "THE_MYSTIC"          # 편인
    assert profile["bond_mode"] == "THE_TWIN"            # 비견


def test_gyeokguk_1974():
    """편인격 → INTUITIVE."""
    result = _calc_1974()
    profile = build_semantic_profile(result)

    assert profile["structure"]["gyeokguk"] == "INTUITIVE"
    assert profile["structure"]["gyeokguk_raw"] == "편인격"


def test_twelve_stages_1974():
    """丙일간: 寅 → 장생."""
    result = _calc_1974()
    profile = build_semantic_profile(result)
    stages = profile["structure"]["twelve_stages"]

    assert stages["year_pillar"] == "장생"
    assert stages["month_pillar"] == "장생"
    assert stages["day_pillar"] == "병"
    assert stages["hour_pillar"] == "장생"


def test_relations_1974():
    """寅申 육충 태그 포함."""
    result = _calc_1974()
    profile = build_semantic_profile(result)

    tags = profile["structure"]["relations"]["tags"]
    assert "CLASH" in tags


def test_special_traits_1974():
    """역마 + 문창귀인."""
    result = _calc_1974()
    profile = build_semantic_profile(result)

    traits = profile["special_traits"]
    assert "RESTLESS_FEET" in traits    # 역마
    assert "SCHOLAR_MIND" in traits      # 문창귀인


def test_year_theme_1974():
    """2026 세운 丙午 → THE_RADIATOR's own energy (비견)."""
    result = _calc_1974()
    profile = build_semantic_profile(result)

    assert profile["year_theme"]["target_year"] == 2026
    assert profile["year_theme"]["pillar"] == "丙午"
    assert profile["year_theme"]["ten_god"] == "TEN_GOD_FRIEND"


def test_daewoon_timeline_1974():
    """10개 대운, 등급 매핑 확인."""
    result = _calc_1974()
    profile = build_semantic_profile(result)

    timeline = profile["daewoon_timeline"]
    assert len(timeline) == 10

    # 1번 (丁卯): CHALLENGING
    assert timeline[0]["grade"] == "CHALLENGING"
    assert timeline[0]["score"] == -3.0

    # 2번 (戊辰): PEAK
    assert timeline[1]["grade"] == "PEAK"
    assert timeline[1]["score"] == 3.0

    # 각 항목에 ages 있음
    for item in timeline:
        assert len(item["ages"]) == 2


def test_daewoon_summary_1974():
    result = _calc_1974()
    profile = build_semantic_profile(result)
    summ = profile["daewoon_summary"]

    assert summ["best"]["daewoon_index"] == 2
    assert summ["worst"]["daewoon_index"] == 1


def test_no_luck_info_ok():
    """target_year 없으면 year_theme=None."""
    result = calculate_saju(
        birth_date="1974-02-24",
        birth_time="05:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        jasi_boundary=23,
        gender="M",
        # target_year 없음
    )
    profile = build_semantic_profile(result)
    assert profile["year_theme"] is None
    assert len(profile["daewoon_timeline"]) == 10

def test_relation_tags_1974_includes_stem_clash():
    """1974 프로필: 甲庚 천간충 → STEM_CLASH 포함."""
    result = _calc_1974()
    profile = build_semantic_profile(result)
    tags = profile["structure"]["relations"]["tags"]
    assert "CLASH" in tags
    assert "STEM_CLASH" in tags


def test_relation_tags_1990_zihyeong():
    """1990 프로필: 午午 자형 → SELF_TENSION."""
    result = calculate_saju(
        birth_date="1990-05-05",
        birth_time="14:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        jasi_boundary=23,
        gender="M",
    )
    profile = build_semantic_profile(result)
    tags = profile["structure"]["relations"]["tags"]
    assert "SELF_TENSION" in tags
    assert "UNION" in tags