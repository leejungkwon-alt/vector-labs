# tests/test_sinsal.py
from app.engine.sinsal import detect_sinsal, summarize_sinsal, _samhap_group


# 1974-02-24 05:30 KST: 甲寅 丙寅 丙申 庚寅
# 년지 寅 → 삼합 寅午戌(火)
#   도화(卯): 없음
#   역마(申): 일지 申 ✅
#   화개(戌): 없음
# 일간 丙 → 천을귀인: 亥, 酉 (없음)
#        → 문창귀인: 申 (일지에 있음 ✅)
#        → 양인: 午 (없음)
# 일주 丙申 → 괴강 아님
PILLARS_1974 = {
    "year_pillar": "甲寅",
    "month_pillar": "丙寅",
    "day_pillar": "丙申",
    "hour_pillar": "庚寅",
}

# 1990-05-05 14:30: 庚午 庚辰 庚午 癸未
# 년지 午 → 삼합 寅午戌(火)
#   도화(卯): 없음
#   역마(申): 없음
#   화개(戌): 없음
# 일간 庚 → 천을귀인: 丑, 未 → 시지 未 ✅
#        → 문창귀인: 亥 (없음)
#        → 양인: 酉 (없음)
PILLARS_1990 = {
    "year_pillar": "庚午",
    "month_pillar": "庚辰",
    "day_pillar": "庚午",
    "hour_pillar": "癸未",
}

# 도화 검출용: 년지 申 → 삼합 申子辰(水), 도화=酉
PILLARS_DOHWA = {
    "year_pillar": "甲申",
    "month_pillar": "乙酉",   # 도화!
    "day_pillar": "戊午",
    "hour_pillar": "庚申",
}

# 괴강 검출용: 일주 庚辰
PILLARS_GOEGANG = {
    "year_pillar": "甲子",
    "month_pillar": "丙寅",
    "day_pillar": "庚辰",   # 괴강!
    "hour_pillar": "庚午",
}


def test_samhap_group():
    assert _samhap_group("寅") == "寅午戌"
    assert _samhap_group("申") == "申子辰"
    assert _samhap_group("酉") == "巳酉丑"
    assert _samhap_group("亥") == "亥卯未"
    assert _samhap_group("") == ""


def test_yeokma_1974():
    """1974: 년지 寅 → 역마 申 → 일지에 있음."""
    s = detect_sinsal(PILLARS_1974)
    yeokmas = s["역마"]
    assert len(yeokmas) == 1
    assert yeokmas[0]["position"] == "day_pillar"
    assert yeokmas[0]["branch"] == "申"


def test_munchang_1974():
    """1974: 일간 丙 → 문창귀인 申 → 일지에 있음."""
    s = detect_sinsal(PILLARS_1974)
    munchangs = s["문창귀인"]
    assert len(munchangs) == 1
    assert munchangs[0]["branch"] == "申"


def test_cheoneul_1990():
    """1990: 일간 庚 → 천을귀인 丑,未 → 시지 未."""
    s = detect_sinsal(PILLARS_1990)
    cheoneuls = s["천을귀인"]
    assert len(cheoneuls) == 1
    assert cheoneuls[0]["position"] == "hour_pillar"
    assert cheoneuls[0]["branch"] == "未"


def test_dohwa_detection():
    """년지 申 → 도화 酉 → 월지에 있음."""
    s = detect_sinsal(PILLARS_DOHWA)
    dohwas = s["도화"]
    assert len(dohwas) == 1
    assert dohwas[0]["position"] == "month_pillar"
    assert dohwas[0]["branch"] == "酉"


def test_goegang_detection():
    """일주 庚辰 → 괴강."""
    s = detect_sinsal(PILLARS_GOEGANG)
    assert len(s["괴강"]) == 1
    assert s["괴강"][0]["position"] == "day_pillar"


def test_yangin_detection():
    """일간 丙 → 양인 午. 1990 케이스는 午가 년지/일지에 있음."""
    # 일간 甲 양인=卯 케이스
    pillars = {
        "year_pillar": "甲子",
        "month_pillar": "丁卯",   # 양인
        "day_pillar": "甲寅",
        "hour_pillar": "丙寅",
    }
    s = detect_sinsal(pillars)
    yangins = s["양인"]
    assert len(yangins) == 1
    assert yangins[0]["branch"] == "卯"


def test_summarize():
    """요약 플래그 및 카운트 검증."""
    s = detect_sinsal(PILLARS_1974)
    summ = summarize_sinsal(s)
    assert summ["has_yeokma"] is True
    assert summ["has_munchang"] is True
    assert summ["has_cheoneul"] is False
    assert summ["has_dohwa"] is False
    assert summ["count"] >= 2


def test_empty_safe():
    """비어있는 입력도 크래시 없이 빈 결과."""
    s = detect_sinsal({})
    assert s["도화"] == []
    assert s["역마"] == []
    assert s["괴강"] == []