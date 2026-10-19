# tests/test_gyeokguk.py
"""
격국 판정 테스트.

기존 골든 케이스 + 이전 버전의 건록/양인 오판 회귀 방지.
"""
from app.engine.gyeokguk import determine_gyeokguk


# ---- 기존 골든 케이스 ----
PILLARS_1974 = {
    "year_pillar": "甲寅",
    "month_pillar": "丙寅",
    "day_pillar": "丙申",
    "hour_pillar": "庚寅",
}

PILLARS_1990 = {
    "year_pillar": "庚午",
    "month_pillar": "庚辰",
    "day_pillar": "庚午",
    "hour_pillar": "癸未",
}


def test_gyeokguk_1974_편인격():
    """1974: 丙일간, 월지 寅. 寅의 정기 甲이 천간에 투출 → 편인격."""
    r = determine_gyeokguk(PILLARS_1974)
    assert r["basis_stem"] == "甲"
    assert r["transparent"] is True
    assert r["ten_god"] == "편인"
    assert r["name"] == "편인격"


def test_gyeokguk_1990_상관격():
    """1990: 庚일간, 월지 辰. 정기 戊는 투출 안 됨, 여기 癸만 투출 → 상관격."""
    r = determine_gyeokguk(PILLARS_1990)
    assert r["basis_stem"] == "癸"
    assert r["transparent"] is True
    assert r["ten_god"] == "상관"
    assert r["name"] == "상관격"


# ============================================================
# 회귀 방지 — 이전 버전의 건록/양인 오판 케이스
# ============================================================
def test_건록격_오판_방지_甲일간_亥월_甲투출():
    """
    이전 버그: 甲일간, 월지 亥에서 甲이 투출하면 '건록격'이 나옴.
    실제 甲의 록은 寅월. 亥월은 록이 아님.
    → 편인격(정기 壬)이 되어야 함.
    """
    pillars = {
        "year_pillar": "戊子",   # 戊 (편인 아님, 관계 무관)
        "month_pillar": "甲亥",   # 亥월, 월간에 甲이 있음 (중기 투출)
        "day_pillar": "甲寅",    # 甲일간
        "hour_pillar": "庚午",
    }
    r = determine_gyeokguk(pillars)

    assert r["name"] != "건록격", "亥월은 甲의 록이 아님"
    # 정기 壬으로 fallback → 편인격
    assert r["name"] == "편인격"
    assert r["basis_stem"] == "壬"
    assert r["ten_god"] == "편인"


def test_양인격_오판_방지_甲일간_辰월_乙투출():
    """
    이전 버그: 甲일간, 월지 辰에서 乙이 투출하면 '양인격'이 나옴.
    실제 甲의 양인은 卯월. 辰월은 양인 위치가 아님.
    → 편재격(정기 戊) 또는 월겁격.
    """
    pillars = {
        "year_pillar": "戊子",
        "month_pillar": "乙辰",   # 辰월, 월간 乙
        "day_pillar": "甲寅",    # 甲일간
        "hour_pillar": "庚午",
    }
    r = determine_gyeokguk(pillars)

    assert r["name"] != "양인격", "辰월은 甲의 양인 위치가 아님"
    # 겁재가 그대로 격_stem이 되면 월겁격, 아니면 정기로 편재격
    assert r["name"] in ("월겁격", "편재격")


# ============================================================
# 건록격 / 양인격 정상 케이스
# ============================================================
def test_건록격_정상_甲일간_寅월():
    """甲일간 寅월 → 건록격."""
    pillars = {
        "year_pillar": "丙子",
        "month_pillar": "丙寅",   # 寅월
        "day_pillar": "甲午",
        "hour_pillar": "庚午",
    }
    r = determine_gyeokguk(pillars)
    assert r["name"] == "건록격"
    assert r["ten_god"] == "비견"
    assert r["basis_stem"] == "甲"


def test_양인격_정상_甲일간_卯월():
    """甲일간 卯월 → 양인격."""
    pillars = {
        "year_pillar": "丙子",
        "month_pillar": "丁卯",   # 卯월
        "day_pillar": "甲午",
        "hour_pillar": "庚午",
    }
    r = determine_gyeokguk(pillars)
    assert r["name"] == "양인격"
    assert r["ten_god"] == "겁재"
    assert r["basis_stem"] == "乙"


def test_양인격_정상_庚일간_酉월():
    """庚일간 酉월 → 양인격."""
    pillars = {
        "year_pillar": "甲子",
        "month_pillar": "乙酉",   # 酉월
        "day_pillar": "庚午",
        "hour_pillar": "丙子",
    }
    r = determine_gyeokguk(pillars)
    assert r["name"] == "양인격"
    assert r["basis_stem"] == "辛"


def test_음간_겁재_월겁격():
    """
    乙일간 寅월, 천간에 甲丙戊가 전혀 없음.
    → 정기 甲(겁재) fallback → 월겁격.
    (만약 丙이 투출하면 상관격이 정답 — 투출 우선.)
    """
    pillars = {
        "year_pillar": "庚子",
        "month_pillar": "庚寅",   # 寅월, 월간도 庚
        "day_pillar": "乙丑",
        "hour_pillar": "庚辰",
    }
    r = determine_gyeokguk(pillars)
    assert r["name"] != "양인격"       # 乙의 양인은 없음
    assert r["name"] == "월겁격"
    assert r["basis_stem"] == "甲"
    assert r["transparent"] is False


def test_투출_없으면_정기로_격():
    """투출 없으면 정기 십성으로 격."""
    pillars = {
        "year_pillar": "甲子",
        "month_pillar": "丙卯",   # 卯월, 정기 乙
        "day_pillar": "庚午",     # 庚일간
        "hour_pillar": "庚辰",
    }
    r = determine_gyeokguk(pillars)
    # 庚일간, 乙 = 정재
    assert r["basis_stem"] == "乙"
    assert r["transparent"] is False
    assert r["name"] == "정재격"

def test_음간_본기_겁재_투출없고_중기_상관_투출():
    """
    乙일간 寅월, 본기 甲은 투출 안 됨, 중기 丙이 투출.
    → 투출 우선 → 상관격.
    """
    pillars = {
        "year_pillar": "丙子",
        "month_pillar": "戊寅",
        "day_pillar": "乙丑",
        "hour_pillar": "庚辰",
    }
    r = determine_gyeokguk(pillars)
    assert r["name"] == "상관격"
    assert r["basis_stem"] == "丙"
    assert r["transparent"] is True    