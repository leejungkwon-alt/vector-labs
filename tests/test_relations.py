# tests/test_relations.py
from app.engine.relations import detect_relations, summarize_relations


# 1974-02-24 05:30: 甲寅 丙寅 丙申 庚寅
# 천간: 甲丙丙庚 → 甲庚 천간충 (년-시)
# 지지: 寅寅申寅 → 寅申 육충 × 3쌍
PILLARS_1974 = {
    "year_pillar": "甲寅",
    "month_pillar": "丙寅",
    "day_pillar": "丙申",
    "hour_pillar": "庚寅",
}

# 1990-05-05 14:30: 庚午 庚辰 庚午 癸未
# 지지: 午辰午未 → 午未 육합(년-시, 일-시) + 午午 자형(년-일)
PILLARS_1990 = {
    "year_pillar": "庚午",
    "month_pillar": "庚辰",
    "day_pillar": "庚午",
    "hour_pillar": "癸未",
}

# 삼합 검출용: 申子辰
PILLARS_SAMHAP = {
    "year_pillar": "甲申",
    "month_pillar": "丙子",
    "day_pillar": "戊辰",
    "hour_pillar": "庚寅",
}

# 천간합 검출용: 甲己
PILLARS_GAN_HE = {
    "year_pillar": "甲子",
    "month_pillar": "己巳",
    "day_pillar": "丙寅",
    "hour_pillar": "庚午",
}


# ---- 지지 ----
def test_chong_1974():
    r = detect_relations(PILLARS_1974)
    chongs = r["chong"]
    assert len(chongs) >= 1
    for c in chongs:
        assert set(c["values"]) == {"寅", "申"}
        assert c["type"] == "육충"


def test_he_1990():
    r = detect_relations(PILLARS_1990)
    he_pairs = [set(h["branches"]) for h in r["he"] if h["type"] == "육합"]
    assert {"午", "未"} in he_pairs


def test_samhap_water_potential_element():
    r = detect_relations(PILLARS_SAMHAP)
    samhaps = [h for h in r["he"] if h["type"] == "삼합"]
    assert len(samhaps) == 1
    assert set(samhaps[0]["branches"]) == {"申", "子", "辰"}
    assert samhaps[0]["potential_element"] == "水"
    assert "note" in samhaps[0]      # 합화 조건 안내


def test_zihyeong_1990_午午():
    """1990: 午가 년지·일지에 있음 → 자형."""
    r = detect_relations(PILLARS_1990)
    zihyeongs = [h for h in r["hyeong"] if h["type"] == "자형"]
    assert len(zihyeongs) == 1
    assert zihyeongs[0]["branches"] == ["午", "午"]
    assert "午" in zihyeongs[0]["branches"]


def test_hyeong_detection():
    """寅巳申 삼형."""
    pillars = {
        "year_pillar": "甲寅",
        "month_pillar": "丁巳",
        "day_pillar": "戊申",
        "hour_pillar": "庚午",
    }
    r = detect_relations(pillars)
    assert any(h["name"] == "무은지형" for h in r["hyeong"])


# ---- 천간 ----
def test_gan_chong_1974():
    """甲庚 천간충."""
    r = detect_relations(PILLARS_1974)
    chongs = r["gan_chong"]
    assert len(chongs) == 1
    assert set(chongs[0]["values"]) == {"甲", "庚"}
    assert set(chongs[0]["positions"]) == {"year_pillar", "hour_pillar"}


def test_gan_he_甲己():
    r = detect_relations(PILLARS_GAN_HE)
    hes = r["gan_he"]
    assert len(hes) == 1
    assert set(hes[0]["stems"]) == {"甲", "己"}
    assert hes[0]["potential_element"] == "土"
    assert "note" in hes[0]


def test_no_gan_he_when_absent():
    """1974: 甲庚은 충이지 합이 아님."""
    r = detect_relations(PILLARS_1974)
    assert r["gan_he"] == []


# ---- 위치 라벨 ----
def test_relations_returns_position_labels():
    r = detect_relations(PILLARS_1974)
    for c in r["chong"]:
        assert "position_labels" in c
        assert all(lbl in ("년주", "월주", "일주", "시주") for lbl in c["position_labels"])


# ---- summarize ----
def test_summarize_flags_1974():
    r = detect_relations(PILLARS_1974)
    s = summarize_relations(r)
    assert s["has_chong"] is True
    assert s["day_chong"] is True
    assert s["has_gan_chong"] is True
    assert s["gan_chong_count"] == 1


def test_summarize_flags_1990():
    r = detect_relations(PILLARS_1990)
    s = summarize_relations(r)
    assert s["has_he"] is True
    assert s["day_he"] is True
    assert s["has_hyeong"] is True         # 자형
    assert s["has_gan_he"] is False


def test_summarize_gan_he():
    r = detect_relations(PILLARS_GAN_HE)
    s = summarize_relations(r)
    assert s["has_gan_he"] is True
    assert s["gan_he_count"] == 1