# tests/test_interpret_year.py
"""연도 하드코딩 회귀 방지 (2026 하드코딩 제거)."""
from app.services.template_interpreter import generate_template_interpretation


def _saju_with_year(year):
    return {
        "day_pillar": "庚午",
        "ten_gods": {},
        "luck_info": {
            "target_year": year,
            "annual_luck": {"pillar": "庚戌", "ten_god": "TEN_GOD_FRIEND"},
        },
    }


def test_interpret_title_uses_target_year_en():
    interp = generate_template_interpretation(_saju_with_year(2030), lang="en")
    title = interp["strategic_timing"]["title"]
    assert "2030" in title
    assert "2026" not in title


def test_interpret_title_uses_target_year_ko():
    interp = generate_template_interpretation(_saju_with_year(2030), lang="ko")
    title = interp["strategic_timing"]["title"]
    assert "2030" in title
    assert "2026" not in title


def test_interpret_title_without_luck_info_uses_placeholder():
    """luck_info 없으면 — placeholder. 포맷 안 됨(중괄호 노출) 방지."""
    saju = {"day_pillar": "庚午", "ten_gods": {}}
    interp = generate_template_interpretation(saju, lang="en")
    title = interp["strategic_timing"]["title"]
    assert "2026" not in title
    assert "{" not in title
    assert "}" not in title


def test_interpret_analysis_also_reflects_target_year():
    """title과 analysis의 연도가 일치해야 함."""
    interp = generate_template_interpretation(_saju_with_year(2030), lang="en")
    title = interp["strategic_timing"]["title"]
    analysis = interp["strategic_timing"]["analysis"] or ""
    assert "2030" in title
    assert "2030" in analysis
