# tests/test_hidden_stems_standard.py
"""지장간 표준 순서 (정기·중기·여기) 회귀 테스트.

배열 인덱스:
  0 = 정기(본기)
  1 = 중기
  2 = 여기
"""
from app.engine.elements import BRANCH_HIDDEN_STEMS

STANDARD_HIDDEN_STEMS = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],   # ← 丙·戊·庚 아님
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}


def test_hidden_stems_match_standard():
    failures = []
    for branch, expected in STANDARD_HIDDEN_STEMS.items():
        actual = BRANCH_HIDDEN_STEMS.get(branch)
        if actual != expected:
            failures.append(f"  {branch}: expected {expected}, got {actual}")
    assert not failures, "지장간이 표준과 다릅니다:\n" + "\n".join(failures)


def test_sa_hidden_stem_order():
    """巳: 정기 丙, 중기 庚, 여기 戊."""
    assert BRANCH_HIDDEN_STEMS["巳"] == ["丙", "庚", "戊"]