# app/engine/luck.py

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.engine.pillars import get_year_pillar, get_month_pillar, EARTHLY_BRANCHES


def calculate_annual_luck(target_year: int) -> dict:
    pillar = get_year_pillar(target_year)
    return {
        "year": target_year,
        "pillar": pillar,
        "stem": pillar[0],
        "branch": pillar[1],
    }


def calculate_monthly_lucks(target_year: int) -> list:
    branches = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
    monthly_results = []

    for i, branch in enumerate(branches):
        branch_idx = EARTHLY_BRANCHES.index(branch)
        # pillars.py의 get_month_pillar를 호출하여 월두법 로직 단일화
        pillar = get_month_pillar(target_year, branch_idx)

        # 양력 기준 대략적 월 (寅월 ≈ 2월)
        approx_solar_month = (i + 2) if i < 11 else 1
        calc_year = target_year if i < 11 else target_year + 1

        monthly_results.append({
            "month_index": i + 1,
            "branch": branch,
            "pillar": pillar,
            "approx_solar_month": f"{calc_year}-{approx_solar_month:02d}",
        })

    return monthly_results


def current_solar_year(
    tz_str: str = "Asia/Seoul",
    now: datetime | None = None,
) -> int:
    """
    주어진 시각(기본: 지금) 기준 절기년(입춘 기준)을 반환.

    - 2026-01-15 KST → 2025 (乙巳)
    - 2026-03-15 KST → 2026 (丙午)

    Args:
        tz_str: 유저 로컬 타임존. 잘못된 값은 Asia/Seoul로 폴백.
        now: 테스트/재현용 기준 시각. None이면 지금.
    """
    from app.engine.solar_terms import determine_solar_year_and_month

    try:
        tz = ZoneInfo(tz_str)
    except (ZoneInfoNotFoundError, ValueError):
        tz = ZoneInfo("Asia/Seoul")

    ref = now if now is not None else datetime.now(tz)
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=tz)
    utc = ref.astimezone(timezone.utc)
    solar_year, _ = determine_solar_year_and_month(utc)
    return solar_year
