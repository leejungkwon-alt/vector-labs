"""사주 × MBTI **대조** 판정 단위 테스트.

이 판정은 측정이 아니라 해석 장치다(contrast.py docstring).
여기서는 (1) 경계값, (2) 시각 미상 시 시주 의존 신호 제외 를 고정한다.
"""
import pytest

from app.engine.calculator import calculate_saju
from app.semantic.contrast import (
    BALANCED_HIGH,
    BALANCED_LOW,
    MIN_SIGNAL_MASS,
    SIGNAL_WEIGHTS,
    assess_contrast,
    label_for,
)
from app.semantic.tagger import build_semantic_profile


def _profile(birth_date="1974-02-24", birth_time="05:30:00", **kwargs):
    result = calculate_saju(birth_date=birth_date, birth_time=birth_time, gender="M", **kwargs)
    return build_semantic_profile(result)


def _profile_no_time(birth_date="1974-02-24"):
    result = calculate_saju(birth_date=birth_date, birth_time_mode="day_only", gender="M")
    return build_semantic_profile(result)


# ============================================================
# 1) 경계값 — label_for 는 순수 함수
# ============================================================

@pytest.mark.parametrize(
    "out_score,in_score,expected",
    [
        # 절대량 가드: OUT+IN < 4 는 무조건 balanced (신호 1개로 극단 라벨 금지)
        (3, 0, "balanced"),
        (0, 3, "balanced"),
        (0, 0, "balanced"),
        (2, 1, "balanced"),
        # 가드 통과(합 4) 이후는 out_share 로 판정
        (4, 0, "outward"),    # share 1.00
        (0, 4, "inward"),     # share 0.00
        (3, 1, "outward"),    # share 0.75 > 0.65
        (1, 3, "inward"),     # share 0.25 < 0.35
        (2, 2, "balanced"),   # share 0.50
    ],
)
def test_label_for_boundaries(out_score, in_score, expected):
    assert label_for(out_score, in_score) == expected


def test_label_thresholds_are_t1():
    """T1: out_share 0.35~0.65 는 balanced, 바깥은 극단."""
    assert (BALANCED_LOW, BALANCED_HIGH) == (0.35, 0.65)
    # 0.65 경계: 13/20 = 0.65 → balanced (초과만 outward)
    assert label_for(65, 35) == "balanced"
    assert label_for(66, 34) == "outward"
    # 0.35 경계: 35/100 = 0.35 → balanced, 미만만 inward
    assert label_for(35, 65) == "balanced"
    assert label_for(34, 66) == "inward"


def test_min_signal_mass_guard():
    assert MIN_SIGNAL_MASS == 4
    # 합이 4 미만이면 share 가 아무리 극단이어도 balanced
    assert label_for(3, 0) == "balanced"
    assert label_for(0, 3) == "balanced"


def test_label_output_is_only_three_values():
    """출력 계약: outward | inward | balanced 3값뿐."""
    for out_score in range(0, 22):
        for in_score in range(0, 16):
            assert label_for(out_score, in_score) in ("outward", "inward", "balanced")


# ============================================================
# 2) 시각 미상 — 시주 의존 신호는 '감쇠'가 아니라 '제외'
# ============================================================

HOUR_DEPENDENT = {sid for sid, (_, hour_dep) in SIGNAL_WEIGHTS.items() if hour_dep}


@pytest.mark.parametrize("via_kwargs", [True, False])
def test_hour_dependent_signals_are_excluded_when_time_unknown(via_kwargs):
    profile = _profile_no_time()
    assert profile["hour_pillar_confidence"] in ("unknown", "assumed")

    verdict = assess_contrast(profile)
    kept_ids = {s["id"] for s in verdict["signals"]}

    # 시주 의존 신호는 하나도 점수에 남지 않아야 한다
    assert kept_ids & HOUR_DEPENDENT == set()
    assert verdict["hour_signals_excluded"] is True
    assert set(verdict["excluded_signals"]) <= HOUR_DEPENDENT


def test_noon_confidence_counts_as_unknown():
    """noon 가정(assumed)도 시각 미상으로 본다 — 시주가 가정값이기 때문."""
    result = calculate_saju(birth_date="1974-02-24", birth_time_mode="noon", gender="M")
    profile = build_semantic_profile(result)
    assert profile["hour_pillar_confidence"] == "assumed"

    verdict = assess_contrast(profile)
    assert verdict["hour_signals_excluded"] is True
    assert {s["id"] for s in verdict["signals"]} & HOUR_DEPENDENT == set()


def test_exact_time_does_not_flag_exclusion():
    verdict = assess_contrast(_profile())
    assert verdict["hour_signals_excluded"] is False


def test_exclusion_is_removal_not_decay():
    """같은 사람의 exact/unknown 결과에서 시주 의존 신호는 '가중치 감소'가 아니라 부재."""
    p_exact = assess_contrast(_profile())
    p_unknown = assess_contrast(_profile_no_time())

    exact_ids = {s["id"] for s in p_exact["signals"]}
    unknown_ids = {s["id"] for s in p_unknown["signals"]}

    gone = exact_ids - unknown_ids
    # exact 에서 사라진 신호는 모두 시주 의존 신호여야 한다
    assert gone <= HOUR_DEPENDENT
    # 잔류 신호의 가중치는 그대로(감쇠 없음)
    weights_unknown = {s["id"]: s["weight"] for s in p_unknown["signals"]}
    for sid, weight in weights_unknown.items():
        assert weight == SIGNAL_WEIGHTS[sid][0]


# ============================================================
# 3) 결정 확정 사항 — 중립/제거 신호는 점수에 없다
# ============================================================

def test_s11_pyeonjae_is_removed():
    from app.semantic.contrast import REMOVED_SIGNALS
    assert any("S11" in key for key in REMOVED_SIGNALS)
    assert not any(sid.startswith("S11") for sid in SIGNAL_WEIGHTS)


def test_s5_s10_s17_are_neutral():
    from app.semantic.contrast import NEUTRAL_SIGNALS
    for prefix in ("S5", "S10", "S17"):
        assert any(key.startswith(prefix) for key in NEUTRAL_SIGNALS)
        assert not any(sid.startswith(prefix) for sid in SIGNAL_WEIGHTS)


def test_inward_signals_n1_to_n7_are_promoted():
    """N1~N7 승격 확인 — inward 신호가 실제로 존재해야 한다."""
    inward = {sid for sid in SIGNAL_WEIGHTS if sid.startswith("N")}
    for n in range(1, 8):
        assert any(sid.startswith(f"N{n}_") for sid in inward), f"N{n} 누락"
