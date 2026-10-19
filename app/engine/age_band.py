# app/engine/age_band.py
"""
Age band — 생애 단계.

글로벌 보편성을 위해 IMF/세대 코호트가 아닌 **연령대**만 사용.

- EARLY  (0-24): 탐색·실험기
- MID    (25-39): 가속·누적기
- PEAK   (40-54): 산출·정점기
- SENIOR (55-69): 수확·전수기
- ELDER  (70+): 유산·존재기
"""
from datetime import datetime


BAND_RANGES = [
    ("EARLY",   0,  24),
    ("MID",    25,  39),
    ("PEAK",   40,  54),
    ("SENIOR", 55,  69),
    ("ELDER",  70, 999),
]


def compute_age_band(birth_year: int, target_year: int | None = None) -> dict:
    """
    생년 → age band 정보.

    Args:
        birth_year: 달력 출생 연도
        target_year: 기준 연도 (None이면 올해)

    Returns:
        {"key": "PEAK", "age": 52, "target_year": 2026, "min": 40, "max": 54}
    """
    ref = target_year or datetime.now().year
    age = ref - birth_year

    for key, lo, hi in BAND_RANGES:
        if lo <= age <= hi:
            return {
                "key": key,
                "age": age,
                "target_year": ref,
                "min": lo,
                "max": hi if hi < 999 else None,
            }

    return {"key": "EARLY", "age": age, "target_year": ref, "min": 0, "max": 24}