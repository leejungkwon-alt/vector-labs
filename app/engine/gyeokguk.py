# app/engine/gyeokguk.py
"""
격국 (格局) 판정.

- 건록격(建祿格): 월지가 일간의 록(祿)일 때만.
- 양인격(陽刃格): 월지가 일간의 양인(刃)일 때만 (양간 한정).
- 그 외: 월지 지장간이 천간(년/월/시)에 투출한 것으로 격을 잡음.
  - 비견이 록 위치가 아닌 곳에서 투출하면 격으로 부적합 → skip
  - 투출이 없으면 월지 정기(본기)로 격

이전 버전은 "비견=건록격, 양간의 겁재=양인격"으로 단순 매핑해서
월지가 실제 록/양인 위치가 아니어도 잘못된 격이 나왔다.
"""
from app.engine.elements import (
    BRANCH_HIDDEN_STEMS,
    get_ten_god,
)


# ---- 록(祿) 표: 일간이 건록하는 지지 ----
GEONROK_BRANCH = {
    "甲": "寅", "乙": "卯",
    "丙": "巳", "丁": "午",
    "戊": "巳", "己": "午",   # 火土同宮
    "庚": "申", "辛": "酉",
    "壬": "亥", "癸": "子",
}

# ---- 양인(刃) 표: 양간만 정설 ----
YANGIN_BRANCH = {
    "甲": "卯", "丙": "午", "戊": "午",
    "庚": "酉", "壬": "子",
}

# 십성 → 격국 이름 (비견·겁재는 별도 처리)
_GYEOK_MAP = {
    "정관": "정관격",
    "편관": "편관격",
    "정재": "정재격",
    "편재": "편재격",
    "식신": "식신격",
    "상관": "상관격",
    "정인": "정인격",
    "편인": "편인격",
}


def determine_gyeokguk(pillars: dict) -> dict:
    """
    월지 기준으로 격국 판정.

    우선순위:
      1) 월지가 일간의 록(祿) 위치  → 건록격 (투출 무관)
      2) 월지가 일간의 양인(刃) 위치 → 양인격 (양간 한정)
      3) 월지 지장간이 천간에 투출    → 그 십성으로 격
         (비견/겁재는 록·양인 아닌 위치에서는 격으로 안 씀 → skip)
      4) 아무것도 없으면 월지 정기로 격
    """
    day_stem = pillars["day_pillar"][0]
    month_branch = pillars["month_pillar"][1]

    hidden = BRANCH_HIDDEN_STEMS.get(month_branch, [])
    if not hidden:
        return {
            "name": "미정",
            "basis_stem": "",
            "transparent": False,
            "ten_god": "",
        }

    # ---- 1) 록 위치 우선 ----
    if GEONROK_BRANCH.get(day_stem) == month_branch:
        return {
            "name": "건록격",
            "basis_stem": hidden[0],
            "transparent": True,
            "ten_god": "비견",
        }

    # ---- 2) 양인 위치 우선 ----
    if YANGIN_BRANCH.get(day_stem) == month_branch:
        return {
            "name": "양인격",
            "basis_stem": hidden[0],
            "transparent": True,
            "ten_god": "겁재",
        }

    # ---- 3) 투출 우선 (비견/겁재는 skip) ----
    upper_stems = [
        pillars["year_pillar"][0],
        pillars["month_pillar"][0],
    ]
    hour_pillar = pillars.get("hour_pillar")
    if isinstance(hour_pillar, str) and len(hour_pillar) == 2:
        upper_stems.append(hour_pillar[0])

    gyeok_stem = None
    transparent = False
    for h in hidden:
        if h not in upper_stems:
            continue
        tg = get_ten_god(day_stem, h)
        if tg in ("비견", "겁재"):
            continue        # 록·양인 아닌 위치의 비견/겁재는 격으로 부적합
        gyeok_stem = h
        transparent = True
        break

    # ---- 4) 정기 fallback ----
    if gyeok_stem is None:
        gyeok_stem = hidden[0]
        transparent = False

    ten_god = get_ten_god(day_stem, gyeok_stem)

    if ten_god in ("비견", "겁재"):
        # 록·양인 위치가 아니면서 정기까지 비견/겁재 → 월겁격
        name = "월겁격"
    else:
        name = _GYEOK_MAP.get(ten_god, "기타")

    return {
        "name": name,
        "basis_stem": gyeok_stem,
        "transparent": transparent,
        "ten_god": ten_god,
    }