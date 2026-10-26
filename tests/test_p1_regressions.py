"""P1 회귀: daewoon gender 화이트리스트 + loader 중복 정의."""
import pytest
from datetime import datetime, timezone

from app.engine.daewoon import calculate_daewoon
from app.services.content.loader import list_available


_KST = timezone.utc


# ── gender 화이트리스트 ──
def _calc(gender):
    return calculate_daewoon(
        utc_instant=datetime(1990, 5, 5, 5, 30, tzinfo=_KST),
        gender=gender,
        year_stem="庚",
        solar_year=1990,
        month_branch_idx=4,
    )


@pytest.mark.parametrize("g", ["M", "m", "남", "MALE", " male ", "남성X"])
def test_male_tokens_forward(g):
    # '남성X'는 화이트리스트 밖 → ValueError 여야 함
    if g.strip().upper() not in ("M", "남", "MALE"):
        with pytest.raises(ValueError):
            _calc(g)
    else:
        assert _calc(g)["is_forward"] is True


@pytest.mark.parametrize("g", ["F", "f", "여", "FEMALE", " female "])
def test_female_tokens_backward(g):
    assert _calc(g)["is_forward"] is False


@pytest.mark.parametrize("g", ["", "X", "other", None, "  "])
def test_invalid_gender_raises(g):
    with pytest.raises(ValueError, match="gender must be one of"):
        _calc(g)


# ── list_available ──
def test_list_available_returns_json_based_lists():
    """JSON 디렉터리 기반 함수가 살아있어야 함 (en JSON 파일들 인식)."""
    sections = list_available("en")
    # JSON 팩에 존재하는 섹션
    for expected in ("core", "compatibility", "daily", "sections"):
        assert expected in sections, f"{expected} not in {sections}"


def test_list_available_unknown_lang_empty():
    """미지원 언어는 빈 리스트 (크래시 없음)."""
    assert list_available("xx") == []


def test_list_available_ja_or_zh_if_present():
    """ja/zh_cn JSON 이 있으면 자동 인식, 없으면 빈 리스트."""
    import pathlib
    data_root = pathlib.Path("app/services/content/data")
    for lang in ("ja", "zh_cn", "zh_tw"):
        if (data_root / lang).exists() and any((data_root / lang).glob("*.json")):
            assert list_available(lang), f"{lang} JSON 있는데 빈 리스트"
