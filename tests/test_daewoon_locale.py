# tests/test_daewoon_locale.py
"""daewoon 로케일 회귀: lang 파라미터 및 폴백 체인 검증."""
from datetime import datetime, timezone

import pytest

from app.engine.daewoon import calculate_daewoon

BASE_ARGS = dict(
    utc_instant=datetime(1990, 5, 5, 5, 30, tzinfo=timezone.utc),
    gender="M",
    year_stem="庚",
    solar_year=1990,
    month_branch_idx=0,
)


def test_daewoon_default_is_ko():
    """lang 인자 생략 시 기존과 동일 (ko) — 하위 호환."""
    r_default = calculate_daewoon(**BASE_ARGS)
    r_ko = calculate_daewoon(**BASE_ARGS, lang="ko")
    assert r_default == r_ko


@pytest.mark.parametrize("lang", ["en", "ja", "zh_cn", "es"])
def test_daewoon_lang_returns_result(lang):
    """5개 언어 각각 load_pack 성공 (KeyError 없이)."""
    r = calculate_daewoon(**BASE_ARGS, lang=lang)
    assert isinstance(r, dict)


def test_daewoon_unknown_lang_falls_back():
    """알 수 없는 lang → 폴백 체인 (예외 없음)."""
    r = calculate_daewoon(**BASE_ARGS, lang="xx_unknown")
    assert isinstance(r, dict)


def test_daewoon_none_lang_falls_back():
    """lang=None 도 폴백 (예외 없음)."""
    r = calculate_daewoon(**BASE_ARGS, lang=None)
    assert isinstance(r, dict)
