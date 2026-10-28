# tests/test_age_validation.py
"""미래 생년월일은 '만 14세 미만'이 아닌 별개 에러로 거부되어야 함."""
from datetime import date, timedelta

import pytest

from app.compliance.age import validate_age, MIN_AGE


def test_future_birth_date_rejected_with_future_message():
    future = (date.today() + timedelta(days=30)).isoformat()
    with pytest.raises(ValueError, match="future"):
        validate_age(future)


def test_far_future_birth_date_rejected_with_future_message():
    """+10년 같은 극단 미래도 '14세 미만'이 아닌 미래 에러."""
    future = date.today().replace(year=date.today().year + 10).isoformat()
    with pytest.raises(ValueError, match="future"):
        validate_age(future)


def test_under_14_still_rejected():
    """정상 케이스: 10세는 여전히 '14세 미만' 에러."""
    baby = (date.today() - timedelta(days=365 * 10)).isoformat()
    with pytest.raises(ValueError, match="at least"):
        validate_age(baby)


def test_exactly_14_years_old_passes():
    """경계: 만 14세 생일 당일은 통과."""
    fourteen_years_ago = date.today().replace(year=date.today().year - 14)
    validate_age(fourteen_years_ago.isoformat())  # 예외 없이 통과


def test_normal_adult_passes():
    validate_age("1990-05-05")  # 예외 없음


def test_future_message_does_not_mention_age():
    """미래 날짜 에러 메시지에 '14' 또는 'at least'가 섞이지 않아야 함."""
    future = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValueError) as exc_info:
        validate_age(future)
    msg = str(exc_info.value)
    assert "14" not in msg
    assert "at least" not in msg
