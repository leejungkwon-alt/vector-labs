# tests/test_daewoon_score.py
from app.engine.daewoon_score import score_daewoon, summarize_daewoon_timeline


# 1974 케이스: 일간 丙, 용신 土, 희신 金, 기신 [木, 火]
YONGSIN_1974 = {
    "yongsin": "土",
    "huisin": "金",
    "gisin": ["木", "火"],
}

DAEWOON_PILLARS_1974 = [
    {"daewoon_index": 1, "start_age": 3, "end_age": 12, "pillar": "丁卯"},
    {"daewoon_index": 2, "start_age": 13, "end_age": 22, "pillar": "戊辰"},
    {"daewoon_index": 3, "start_age": 23, "end_age": 32, "pillar": "己巳"},
    {"daewoon_index": 4, "start_age": 33, "end_age": 42, "pillar": "庚午"},
    {"daewoon_index": 5, "start_age": 43, "end_age": 52, "pillar": "辛未"},
    {"daewoon_index": 6, "start_age": 53, "end_age": 62, "pillar": "壬申"},
    {"daewoon_index": 7, "start_age": 63, "end_age": 72, "pillar": "癸酉"},
    {"daewoon_index": 8, "start_age": 73, "end_age": 82, "pillar": "甲戌"},
    {"daewoon_index": 9, "start_age": 83, "end_age": 92, "pillar": "乙亥"},
    {"daewoon_index": 10, "start_age": 93, "end_age": 102, "pillar": "丙子"},
]


def test_score_daewoon_1974_length():
    scored = score_daewoon(DAEWOON_PILLARS_1974, YONGSIN_1974)
    assert len(scored) == 10


def test_score_daewoon_1974_values():
    """1974 각 대운의 예상 점수."""
    scored = score_daewoon(DAEWOON_PILLARS_1974, YONGSIN_1974)
    by_index = {x["daewoon_index"]: x for x in scored}

    # 丁卯: 火(-1) + 木(-2) = -3 → 흉
    assert by_index[1]["score"] == -3.0
    assert by_index[1]["grade"]["ko"] == "흉"

    # 戊辰: 土(+1) + 土(+2) = +3 → 대길
    assert by_index[2]["score"] == 3.0
    assert by_index[2]["grade"]["ko"] == "대길"

    # 己巳: 土(+1) + 火(-2) = -1 → 주의
    assert by_index[3]["score"] == -1.0
    assert by_index[3]["grade"]["ko"] == "주의"

    # 庚午: 金(+0.5) + 火(-2) = -1.5 → 주의
    assert by_index[4]["score"] == -1.5
    assert by_index[4]["grade"]["ko"] == "주의"

    # 辛未: 金(+0.5) + 土(+2) = +2.5 → 대길
    assert by_index[5]["score"] == 2.5
    assert by_index[5]["grade"]["ko"] == "대길"

    # 壬申: 水(0) + 金(+1) = +1 → 길
    assert by_index[6]["score"] == 1.0
    assert by_index[6]["grade"]["ko"] == "길"


def test_score_elements_present():
    """각 항목에 stem_elem / branch_elem 이 채워져야 함."""
    scored = score_daewoon(DAEWOON_PILLARS_1974, YONGSIN_1974)
    for x in scored:
        assert x["stem_elem"] in ("木", "火", "土", "金", "水")
        assert x["branch_elem"] in ("木", "火", "土", "金", "水")


def test_summarize_timeline():
    scored = score_daewoon(DAEWOON_PILLARS_1974, YONGSIN_1974)
    summ = summarize_daewoon_timeline(scored)
    assert summ["best"]["daewoon_index"] == 2      # 戊辰 +3.0
    assert summ["worst"]["daewoon_index"] == 1     # 丁卯 -3.0
    assert isinstance(summ["average_score"], float)
    assert summ["positive_count"] > 0
    assert summ["negative_count"] > 0


def test_score_empty():
    """빈 입력 안전."""
    scored = score_daewoon([], YONGSIN_1974)
    assert scored == []
    summ = summarize_daewoon_timeline([])
    assert summ["best"] is None
    assert summ["worst"] is None