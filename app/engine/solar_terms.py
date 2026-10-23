# app/engine/solar_terms.py
from datetime import datetime, timezone
from functools import lru_cache

import astronomy

# (태양 황경, 월지 인덱스: 子=0 … 亥=11) — 입춘부터 소한까지 12절(節)
JEOLGI = [
    (315.0, 2), (345.0, 3), (15.0, 4), (45.0, 5), (75.0, 6), (105.0, 7),
    (135.0, 8), (165.0, 9), (195.0, 10), (225.0, 11), (255.0, 0), (285.0, 1),
]


def _to_utc(t: "astronomy.Time") -> datetime:
    return t.Utc().replace(tzinfo=timezone.utc)


@lru_cache(maxsize=256)
def get_solar_year_terms(solar_year: int):
    """입춘(solar_year)부터 다음 해 소한까지 12절의 UTC 시각: [(datetime, branch_idx), ...]"""
    t = astronomy.Time.Make(solar_year, 1, 1, 0, 0, 0)
    terms = []
    for deg, branch in JEOLGI:
        t = astronomy.SearchSunLongitude(deg, t, 60.0)
        if t is None:
            raise RuntimeError(
                f"SearchSunLongitude failed for {deg}° ({solar_year})"
            )
        terms.append((_to_utc(t), branch))
    return terms


def determine_solar_year_and_month(utc_dt: datetime):
    """실제 UTC 순간(instant)을 받아 (입춘 기준 연도, 월지 인덱스) 반환."""
    if utc_dt.tzinfo is None:
        raise ValueError("utc_dt must be timezone-aware (real UTC instant)")
    utc_dt = utc_dt.astimezone(timezone.utc)

    year = utc_dt.year
    solar_year = year if utc_dt >= get_solar_year_terms(year)[0][0] else year - 1

    branch = None
    for t_dt, b in get_solar_year_terms(solar_year):
        if utc_dt >= t_dt:
            branch = b
    return solar_year, branch


def get_adjacent_terms(utc_dt: datetime):
    """임의의 UTC 시각을 기준으로 직전·직후 절기를 반환. 인생의 큰 흐름수 계산에 사용."""
    if utc_dt.tzinfo is None:
        raise ValueError("utc_dt must be timezone-aware (UTC).")
    utc_dt = utc_dt.astimezone(timezone.utc)

    target_year = utc_dt.year

    # 전년도·당해년도·내년도의 모든 절기 시각을 수집해 시간순 정렬
    all_terms = []
    for y in (target_year - 1, target_year, target_year + 1):
        for t_dt, branch in get_solar_year_terms(y):
            all_terms.append((t_dt, branch))

    all_terms.sort(key=lambda x: x[0])

    prev_term = all_terms[0]
    next_term = all_terms[-1]

    for i in range(len(all_terms) - 1):
        if all_terms[i][0] <= utc_dt < all_terms[i + 1][0]:
            prev_term = all_terms[i]
            next_term = all_terms[i + 1]
            break

    return prev_term, next_term