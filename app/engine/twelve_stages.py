# app/engine/twelve_stages.py
"""
12운성 (十二運星).

일간이 특정 지지에서 어떤 생애 주기 상태에 있는가.

장생 → 목욕 → 관대 → 건록 → 제왕 → 쇠 → 병 → 사 → 묘 → 절 → 태 → 양

- 양간은 순행, 음간은 역행
- 戊·己는 火土同宮: 戊=丙과 동일, 己=丁과 동일
"""
from app.engine.pillars import EARTHLY_BRANCHES


TWELVE_STAGES = [
    "장생", "목욕", "관대", "건록", "제왕", "쇠",
    "병", "사", "묘", "절", "태", "양",
]

# 각 일간이 장생하는 지지
CHANGSHENG_START = {
    "甲": "亥", "乙": "午",
    "丙": "寅", "丁": "酉",
    "戊": "寅", "己": "酉",
    "庚": "巳", "辛": "子",
    "壬": "申", "癸": "卯",
}

_YANG_STEMS = {"甲", "丙", "戊", "庚", "壬"}


def twelve_stage(day_stem: str, branch: str) -> str:
    """
    일간이 지지에서 어떤 12운성 단계인지 반환.
    잘못된 입력이면 빈 문자열.
    """
    if day_stem not in CHANGSHENG_START or branch not in EARTHLY_BRANCHES:
        return ""

    start = CHANGSHENG_START[day_stem]
    start_idx = EARTHLY_BRANCHES.index(start)
    target_idx = EARTHLY_BRANCHES.index(branch)

    if day_stem in _YANG_STEMS:
        offset = (target_idx - start_idx) % 12
    else:
        offset = (start_idx - target_idx) % 12

    return TWELVE_STAGES[offset]


def twelve_stages_for_pillars(pillars: dict) -> dict:
    """
    4기둥 각 지지의 12운성을 반환.

    반환:
      {"year_pillar": "장생", "month_pillar": "...", ...}
    """
    day_stem = pillars["day_pillar"][0]
    result = {}
    for pos in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        pillar = pillars.get(pos, "")
        if isinstance(pillar, str) and len(pillar) == 2:
            result[pos] = twelve_stage(day_stem, pillar[1])
    return result


# 12운성의 성격 요약 (콘텐츠 활용용, 한국어)
STAGE_MEANINGS_KO = {
    "장생": "새로 시작하는 생명력. 순수하고 성장 지향적.",
    "목욕": "변화와 유혹. 감정 기복, 예술성.",
    "관대": "사회 진출. 자립과 성숙.",
    "건록": "자수성가. 자기 힘으로 서는 단계.",
    "제왕": "최전성기. 강한 추진력과 리더십.",
    "쇠": "전성기 이후. 안정과 내실.",
    "병": "쇠약. 섬세함, 예민함.",
    "사": "정지. 내면 성찰, 영적 깊이.",
    "묘": "저장. 축적, 숨은 재능.",
    "절": "단절과 재생. 극적인 전환점.",
    "태": "잉태. 새로운 가능성, 잠재력.",
    "양": "양육. 성장 준비, 보호받는 시기.",
}