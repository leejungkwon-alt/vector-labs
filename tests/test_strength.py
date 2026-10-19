# tests/test_strength.py
from app.engine.elements import analyze_element_distribution
from app.engine.strength import assess_day_master_strength


# 1974-02-24 05:30 KST (庚寅시) — 甲寅 丙寅 丙申 庚寅
PILLARS_1974 = {
    "year_pillar": "甲寅",
    "month_pillar": "丙寅",
    "day_pillar": "丙申",
    "hour_pillar": "庚寅",
}


def test_element_distribution_1974():
    """목(木) 과다, 甲·寅이 압도적. 화(火)는 丙 2개."""
    dist = analyze_element_distribution(PILLARS_1974)
    counts = dist["counts"]

    # 木: 년간 甲(1.0) + 월지寅 정기 甲(1.0) + 일지X + 시지寅 정기 甲(1.0)
    #    + 년지寅 정기 甲(1.0) + 지장간 중기들(丙戊)
    # 대략 4~5점 예상
    assert counts["木"] >= 4.0
    assert "木" in dist["dominant"]
    assert dist["counts"]["水"] < 1.0  # 물 기운 거의 없음


def test_day_master_strength_1974_strong():
    """丙 일간에 甲(인성)·丙(비견)·寅(인성) 다수 → 신강."""
    s = assess_day_master_strength(PILLARS_1974)
    assert s["verdict"] == "신강"
    assert s["support_ratio"] >= 0.6


def test_day_master_strength_weak_case():
    """일간이 극을 많이 받는 케이스 검증."""
    # 丙 일간이 水(관성)로 둘러싸인 케이스
    pillars = {
        "year_pillar": "壬子",   # 水
        "month_pillar": "壬子",   # 水
        "day_pillar": "丙午",    # 丙 일간
        "hour_pillar": "癸亥",   # 水
    }
    s = assess_day_master_strength(pillars)
    # 水(관성)가 압도적이므로 신약 방향
    assert s["verdict"] in ("신약", "중화")
    assert s["oppose_score"] > s["support_score"]


def test_element_distribution_empty_safe():
    """비어있는 pillars dict도 크래시 없이 처리."""
    dist = analyze_element_distribution({})
    assert dist["total"] == 0.0
    assert dist["missing"] == ["木", "火", "土", "金", "水"]