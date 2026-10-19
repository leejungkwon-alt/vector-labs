# tests/test_twelve_stages.py
from app.engine.twelve_stages import twelve_stage, twelve_stages_for_pillars


PILLARS_1974 = {
    "year_pillar": "甲寅",
    "month_pillar": "丙寅",
    "day_pillar": "丙申",
    "hour_pillar": "庚寅",
}


def test_changsheng_yang_stems():
    """양간 장생 자리."""
    assert twelve_stage("甲", "亥") == "장생"
    assert twelve_stage("丙", "寅") == "장생"
    assert twelve_stage("戊", "寅") == "장생"
    assert twelve_stage("庚", "巳") == "장생"
    assert twelve_stage("壬", "申") == "장생"


def test_changsheng_yin_stems():
    """음간 장생 자리."""
    assert twelve_stage("乙", "午") == "장생"
    assert twelve_stage("丁", "酉") == "장생"
    assert twelve_stage("己", "酉") == "장생"
    assert twelve_stage("辛", "子") == "장생"
    assert twelve_stage("癸", "卯") == "장생"


def test_jewang_yang():
    """양간 제왕 자리."""
    assert twelve_stage("甲", "卯") == "제왕"
    assert twelve_stage("丙", "午") == "제왕"
    assert twelve_stage("庚", "酉") == "제왕"
    assert twelve_stage("壬", "子") == "제왕"


def test_jewang_yin():
    """음간 제왕 자리 (역행)."""
    assert twelve_stage("乙", "寅") == "제왕"
    assert twelve_stage("丁", "巳") == "제왕"
    assert twelve_stage("辛", "申") == "제왕"
    assert twelve_stage("癸", "亥") == "제왕"


def test_geonrok():
    """건록(臨官) 자리."""
    assert twelve_stage("甲", "寅") == "건록"
    assert twelve_stage("乙", "卯") == "건록"
    assert twelve_stage("丙", "巳") == "건록"
    assert twelve_stage("庚", "申") == "건록"


def test_pillars_1974():
    """1974 케이스: 丙일간, 지지 寅寅申寅."""
    stages = twelve_stages_for_pillars(PILLARS_1974)
    # 丙, 寅 → 장생
    assert stages["year_pillar"] == "장생"
    assert stages["month_pillar"] == "장생"
    # 丙, 申 → 병
    assert stages["day_pillar"] == "병"
    assert stages["hour_pillar"] == "장생"


def test_invalid_input():
    """잘못된 입력은 빈 문자열."""
    assert twelve_stage("", "子") == ""
    assert twelve_stage("甲", "") == ""
    assert twelve_stage("X", "子") == ""