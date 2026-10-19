# app/engine/sinsal.py
"""
신살(神煞) 검출.

전통적으로 100종 이상 있으나, 해석 임팩트가 큰 것만 선별:
  - 삼합 기반: 도화(桃花), 역마(驛馬), 화개(華蓋)
  - 일간 기반: 천을귀인(天乙貴人), 문창귀인(文昌貴人), 양인(羊刃)
  - 일주 기반: 괴강(魁罡)

삼합 기준은 년지와 일지를 모두 사용하는 학파가 있으나,
본 모듈은 **년지(年支) 기준**으로 통일한다 (가장 고전적).
"""
from app.engine.elements import BRANCH_HIDDEN_STEMS


POSITIONS = ("year_pillar", "month_pillar", "day_pillar", "hour_pillar")
POSITION_LABEL = {
    "year_pillar": "년주",
    "month_pillar": "월주",
    "day_pillar": "일주",
    "hour_pillar": "시주",
}


# ---- 삼합국 분류 (년지 기준) ----
# 寅午戌 / 申子辰 / 巳酉丑 / 亥卯未
SAMHAP_GROUPS = {
    "寅午戌": "火",
    "申子辰": "水",
    "巳酉丑": "金",
    "亥卯未": "木",
}


def _samhap_group(branch: str) -> str:
    """지지가 속한 삼합국 문자열 반환. 없으면 빈 문자열."""
    if not branch:                     # ← 빈 문자열 / None 방어
        return ""
    for group in SAMHAP_GROUPS:
        if branch in group:
            return group
    return ""


# ---- 삼합국별 신살 대상 지지 ----
DOHWA = {"寅午戌": "卯", "申子辰": "酉", "巳酉丑": "午", "亥卯未": "子"}
YEOKMA = {"寅午戌": "申", "申子辰": "寅", "巳酉丑": "亥", "亥卯未": "巳"}
HWAGAE = {"寅午戌": "戌", "申子辰": "辰", "巳酉丑": "丑", "亥卯未": "未"}

# ---- 일간 기준 귀인 ----
CHEONEUL = {
    "甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
    "乙": ["子", "申"], "己": ["子", "申"],
    "丙": ["亥", "酉"], "丁": ["亥", "酉"],
    "壬": ["巳", "卯"], "癸": ["巳", "卯"],
    "辛": ["午", "寅"],
}

MUNCHANG = {
    "甲": "巳", "乙": "午", "丙": "申", "丁": "酉",
    "戊": "申", "己": "酉", "庚": "亥", "辛": "子",
    "壬": "寅", "癸": "卯",
}

# ---- 양인(羊刃) — 양간만 ----
YANGIN = {
    "甲": "卯", "丙": "午", "戊": "午", "庚": "酉", "壬": "子",
}

# ---- 괴강(魁罡) — 일주(일간+일지)가 특정 조합 ----
GOEGANG_PILLARS = {"庚辰", "庚戌", "壬辰", "戊戌"}


def detect_sinsal(pillars: dict) -> dict:
    """
    4기둥에서 신살을 검출.

    반환: {
      "도화":     [{"position": "year_pillar", ...}, ...],
      "역마":     [...],
      "화개":     [...],
      "천을귀인": [...],
      "문창귀인": [...],
      "양인":     [...],
      "괴강":     [...],
    }
    각 신살이 없으면 빈 리스트.
    """
    branches_by_pos = {}
    for pos in POSITIONS:
        pillar = pillars.get(pos, "")
        if isinstance(pillar, str) and len(pillar) == 2:
            branches_by_pos[pos] = (pillar[0], pillar[1])  # (stem, branch)

    if not branches_by_pos:
        return {
            "도화": [], "역마": [], "화개": [],
            "천을귀인": [], "문창귀인": [], "양인": [], "괴강": [],
        }

    day_stem = branches_by_pos.get("day_pillar", ("", ""))[0]
    year_branch = branches_by_pos.get("year_pillar", ("", ""))[1]
    day_branch = branches_by_pos.get("day_pillar", ("", ""))[1]

    result = {
        "도화": [],
        "역마": [],
        "화개": [],
        "천을귀인": [],
        "문창귀인": [],
        "양인": [],
        "괴강": [],
    }

    # ---- 삼합 기반 (년지 기준) ----
    group = _samhap_group(year_branch)
    if group:
        target_dohwa = DOHWA[group]
        target_yeokma = YEOKMA[group]
        target_hwagae = HWAGAE[group]

        for pos, (_, b) in branches_by_pos.items():
            if b == target_dohwa:
                result["도화"].append(_entry("도화", pos, b))
            if b == target_yeokma:
                result["역마"].append(_entry("역마", pos, b))
            if b == target_hwagae:
                result["화개"].append(_entry("화개", pos, b))

    # ---- 일간 기준 ----
    if day_stem in CHEONEUL:
        for pos, (_, b) in branches_by_pos.items():
            if b in CHEONEUL[day_stem]:
                result["천을귀인"].append(_entry("천을귀인", pos, b))

    if day_stem in MUNCHANG:
        target = MUNCHANG[day_stem]
        for pos, (_, b) in branches_by_pos.items():
            if b == target:
                result["문창귀인"].append(_entry("문창귀인", pos, b))

    if day_stem in YANGIN:
        target = YANGIN[day_stem]
        for pos, (_, b) in branches_by_pos.items():
            if b == target:
                result["양인"].append(_entry("양인", pos, b))

    # ---- 괴강 (일주 조합) ----
    day_pillar_str = f"{day_stem}{day_branch}"
    if day_pillar_str in GOEGANG_PILLARS:
        result["괴강"].append(_entry("괴강", "day_pillar", day_branch))

    return result


def _entry(name: str, pos: str, branch: str) -> dict:
    return {
        "name": name,
        "position": pos,
        "position_label": POSITION_LABEL.get(pos, pos),
        "branch": branch,
    }


def summarize_sinsal(sinsal: dict) -> dict:
    """콘텐츠에서 쓰기 좋은 요약."""
    return {
        "has_dohwa": len(sinsal["도화"]) > 0,
        "has_yeokma": len(sinsal["역마"]) > 0,
        "has_hwagae": len(sinsal["화개"]) > 0,
        "has_cheoneul": len(sinsal["천을귀인"]) > 0,
        "has_munchang": len(sinsal["문창귀인"]) > 0,
        "has_yangin": len(sinsal["양인"]) > 0,
        "has_goegang": len(sinsal["괴강"]) > 0,
        "count": sum(len(v) for v in sinsal.values()),
    }