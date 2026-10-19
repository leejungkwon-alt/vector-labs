from datetime import date, datetime, timedelta

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _pillar(idx: int) -> str:
    return f"{HEAVENLY_STEMS[idx % 10]}{EARTHLY_BRANCHES[idx % 12]}"


def get_year_pillar(solar_year: int) -> str:
    # 1984 = 甲子 (Index 0)
    idx = (solar_year - 1984) % 60
    return _pillar(idx)


def get_month_pillar(solar_year: int, month_branch_idx: int) -> str:
    year_stem_idx = (solar_year - 1984) % 10
    # 五虎遁元: 甲己년 丙寅월 시작
    starting_stem_offsets = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0, 5: 2, 6: 4, 7: 6, 8: 8, 9: 0}
    base_stem_idx = starting_stem_offsets[year_stem_idx]
    distance = (month_branch_idx - 2) % 12
    stem_idx = (base_stem_idx + distance) % 10
    return f"{HEAVENLY_STEMS[stem_idx]}{EARTHLY_BRANCHES[month_branch_idx]}"


def effective_day_date(local_dt, jasi_boundary: int = 23) -> date:
    if jasi_boundary not in (23, 0):
        raise ValueError("jasi_boundary must be 23 or 0")
    if isinstance(local_dt, datetime):
        d = local_dt.date()
        if jasi_boundary == 23 and local_dt.hour >= 23:
            d += timedelta(days=1)
        return d
    elif isinstance(local_dt, date):
        return local_dt
    else:
        raise TypeError("local_dt must be datetime or date")


def get_day_pillar(local_dt, jasi_boundary: int = 23) -> str:
    delta = (effective_day_date(local_dt, jasi_boundary) - date(2000, 1, 1)).days
    return _pillar((54 + delta) % 60)  # 2000-01-01 = 戊午


def get_hour_pillar(local_dt: datetime, jasi_boundary: int = 23) -> str:
    """
    시주 계산.

    - jasi_boundary=23 (조자시설): 23:00부터 다음날로 취급. 일주/시주 모두 다음날 일간 기준.
    - jasi_boundary=0  (야자시설): 일주는 자정에 바뀜.
      단 23:00~23:59는 '야자시'로, 일주는 당일 그대로 두되 시주는 다음날 일간 기준으로 산출한다.
    """
    if jasi_boundary not in (23, 0):
        raise ValueError("jasi_boundary must be 23 or 0")

    if jasi_boundary == 23:
        day_stem_char = get_day_pillar(local_dt, 23)[0]
    else:  # jasi_boundary == 0
        if local_dt.hour == 23:
            next_day = local_dt + timedelta(days=1)
            day_stem_char = get_day_pillar(next_day, 0)[0]
        else:
            day_stem_char = get_day_pillar(local_dt, 0)[0]

    day_stem_idx = HEAVENLY_STEMS.index(day_stem_char)
    branch_idx = ((local_dt.hour + 1) // 2) % 12
    stem_idx = ((day_stem_idx % 5) * 2 + branch_idx) % 10
    return f"{HEAVENLY_STEMS[stem_idx]}{EARTHLY_BRANCHES[branch_idx]}"