# app/engine/luck.py

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