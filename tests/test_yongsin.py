# tests/test_yongsin.py
from app.engine.yongsin import derive_useful_god, _role_elements


# 1974-02-24 05:30 KST: 甲寅 丙寅 丙申 庚寅
PILLARS_1974 = {
    "year_pillar": "甲寅",
    "month_pillar": "丙寅",
    "day_pillar": "丙申",
    "hour_pillar": "庚寅",
}

# 丙 일간이 水(관성)로 둘러싸인 신약 케이스
PILLARS_WEAK = {
    "year_pillar": "壬子",
    "month_pillar": "壬子",
    "day_pillar": "丙午",
    "hour_pillar": "癸亥",
}


def test_role_elements_fire_day_master():
    """일간 火 기준 역할→오행 매핑."""
    roles = _role_elements("火")
    assert roles["비겁"] == "火"
    assert roles["인성"] == "木"
    assert roles["식상"] == "土"
    assert roles["재성"] == "金"
    assert roles["관성"] == "水"


def test_role_elements_wood_day_master():
    """일간 木 기준."""
    roles = _role_elements("木")
    assert roles["비겁"] == "木"
    assert roles["인성"] == "水"
    assert roles["식상"] == "火"
    assert roles["재성"] == "土"
    assert roles["관성"] == "金"


def test_yongsin_1974_strong_uses_output():
    """신강 1974 케이스 → 식상(土) 용신, 재성(金) 희신."""
    result = derive_useful_god(PILLARS_1974)
    assert result["strength"]["verdict"] == "신강"
    assert result["yongsin"] == "土"
    assert result["yongsin_role"] == "식상"
    assert result["huisin"] == "金"
    assert result["huisin_role"] == "재성"
    assert "木" in result["gisin"]   # 인성
    assert "火" in result["gisin"]   # 비겁


def test_yongsin_weak_uses_resource():
    """신약 케이스 → 인성(木) 용신, 비겁(火) 희신."""
    result = derive_useful_god(PILLARS_WEAK)
    assert result["strength"]["verdict"] == "신약"
    assert result["yongsin"] == "木"
    assert result["yongsin_role"] == "인성"
    assert result["huisin"] == "火"
    assert result["huisin_role"] == "비겁"


def test_yongsin_gisin_are_opposite_of_favorable():
    """기신은 용신·희신과 겹치지 않아야 함."""
    for pillars in (PILLARS_1974, PILLARS_WEAK):
        result = derive_useful_god(pillars)
        favorable = {result["yongsin"], result["huisin"]}
        for g in result["gisin"]:
            assert g not in favorable


def test_yongsin_reason_nonempty():
    """reason이 문자열이며 판정 근거를 담고 있어야 함."""
    for pillars in (PILLARS_1974, PILLARS_WEAK):
        result = derive_useful_god(pillars)
        assert isinstance(result["reason"], str)
        assert len(result["reason"]) > 0
        assert result["strength"]["verdict"] in result["reason"]