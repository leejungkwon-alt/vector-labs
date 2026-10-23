# app/engine/relations.py
"""
땅의 기운·하늘의 기운 관계 검출.

땅의 기운:
- 육합/삼합/반합/방합 (결속·응집) — potential_element로 化 가능 오행 참고만 표시
- 육충 (충돌)
- 삼형/쌍형/자형 (마찰)
- 육해/파

하늘의 기운:
- 하늘의 기운합 (甲己 등 5쌍)
- 하늘의 기운충 (甲庚 등 4쌍)

**합화(化) 주의**: 본 모듈은 "합이 성립한다"까지만 판정한다.
실제 오행 변화(化)는 월령·통근·투출 등 추가 조건이 필요하므로,
`potential_element` 필드에 "化 가능 오행"을 참고 정보로만 담는다.
"""
from collections import Counter
from itertools import combinations


# ---- 육합 ----
LIU_HE = {
    frozenset(["子", "丑"]): "土",
    frozenset(["寅", "亥"]): "木",
    frozenset(["卯", "戌"]): "火",
    frozenset(["辰", "酉"]): "金",
    frozenset(["巳", "申"]): "水",
    frozenset(["午", "未"]): "土",
}

# ---- 삼합/반합 ----
SAN_HE = [
    (frozenset(["申", "子", "辰"]), "水"),
    (frozenset(["亥", "卯", "未"]), "木"),
    (frozenset(["寅", "午", "戌"]), "火"),
    (frozenset(["巳", "酉", "丑"]), "金"),
]
BAN_HE = {
    frozenset(["申", "子"]): "水", frozenset(["子", "辰"]): "水",
    frozenset(["亥", "卯"]): "木", frozenset(["卯", "未"]): "木",
    frozenset(["寅", "午"]): "火", frozenset(["午", "戌"]): "火",
    frozenset(["巳", "酉"]): "金", frozenset(["酉", "丑"]): "金",
}

# ---- 방합 ----
BANG_HE = [
    (frozenset(["寅", "卯", "辰"]), "木", "동방"),
    (frozenset(["巳", "午", "未"]), "火", "남방"),
    (frozenset(["申", "酉", "戌"]), "金", "서방"),
    (frozenset(["亥", "子", "丑"]), "水", "북방"),
]

# ---- 육충 ----
LIU_CHONG = {
    frozenset(["子", "午"]), frozenset(["丑", "未"]),
    frozenset(["寅", "申"]), frozenset(["卯", "酉"]),
    frozenset(["辰", "戌"]), frozenset(["巳", "亥"]),
}

# ---- 삼형/쌍형 ----
SAN_HYEONG = [
    (frozenset(["寅", "巳", "申"]), "무은지형", "배은망덕"),
    (frozenset(["丑", "戌", "未"]), "지세지형", "권력 다툼·고집"),
    (frozenset(["子", "卯"]), "무례지형", "예의 결여·성급함"),
]
# 자형: 같은 땅의 기운가 2개 이상 있을 때 성립
ZIHYEONG_BRANCHES = {"辰", "午", "酉", "亥"}

# ---- 육해 ----
LIU_HAI = {
    frozenset(["子", "未"]), frozenset(["丑", "午"]),
    frozenset(["寅", "巳"]), frozenset(["卯", "辰"]),
    frozenset(["申", "亥"]), frozenset(["酉", "戌"]),
}

# ---- 파 ----
LIU_PA = {
    frozenset(["子", "酉"]), frozenset(["丑", "辰"]),
    frozenset(["寅", "亥"]), frozenset(["卯", "午"]),
    frozenset(["巳", "申"]), frozenset(["未", "戌"]),
}

# ---- 하늘의 기운합 ----
TIAN_GAN_HE = {
    frozenset(["甲", "己"]): "土",
    frozenset(["乙", "庚"]): "金",
    frozenset(["丙", "辛"]): "水",
    frozenset(["丁", "壬"]): "木",
    frozenset(["戊", "癸"]): "火",
}

# ---- 하늘의 기운충 (7충 아님, 4충) ----
TIAN_GAN_CHONG = {
    frozenset(["甲", "庚"]),
    frozenset(["乙", "辛"]),
    frozenset(["丙", "壬"]),
    frozenset(["丁", "癸"]),
}


POSITIONS = ("year_pillar", "month_pillar", "day_pillar", "hour_pillar")
POSITION_LABEL = {
    "year_pillar": "년주",
    "month_pillar": "월주",
    "day_pillar": "일주",
    "hour_pillar": "시주",
}


def detect_relations(pillars: dict) -> dict:
    """
    4기둥의 땅의 기운·하늘의 기운 관계를 검출.

    반환:
      he, chong, hyeong, hai, pa: 땅의 기운 관계
      gan_he, gan_chong: 하늘의 기운 관계
    """
    branches_by_pos = {}
    stems_by_pos = {}
    for pos in POSITIONS:
        pillar = pillars.get(pos, "")
        if isinstance(pillar, str) and len(pillar) == 2:
            stems_by_pos[pos] = pillar[0]
            branches_by_pos[pos] = pillar[1]

    return {
        "he":        _detect_he(branches_by_pos),
        "chong":     _detect_pair_relation(branches_by_pos, LIU_CHONG, "육충"),
        "hyeong":    _detect_hyeong(branches_by_pos),
        "hai":       _detect_pair_relation(branches_by_pos, LIU_HAI, "육해"),
        "pa":        _detect_pair_relation(branches_by_pos, LIU_PA, "파"),
        "gan_he":    _detect_gan_he(stems_by_pos),
        "gan_chong": _detect_pair_relation(stems_by_pos, TIAN_GAN_CHONG, "하늘의 기운충"),
    }


def _detect_pair_relation(by_pos: dict, table: set, label: str) -> list:
    results = []
    positions = list(by_pos.keys())
    for p1, p2 in combinations(positions, 2):
        v1, v2 = by_pos[p1], by_pos[p2]
        if frozenset([v1, v2]) in table:
            results.append({
                "type": label,
                "positions": [p1, p2],
                "position_labels": [POSITION_LABEL[p1], POSITION_LABEL[p2]],
                "values": [v1, v2],
            })
    return results


def _detect_he(branches_by_pos: dict) -> list:
    results = []
    branch_set = set(branches_by_pos.values())
    positions = list(branches_by_pos.keys())

    # 육합
    for p1, p2 in combinations(positions, 2):
        b1, b2 = branches_by_pos[p1], branches_by_pos[p2]
        key = frozenset([b1, b2])
        if key in LIU_HE:
            results.append({
                "type": "육합",
                "positions": [p1, p2],
                "position_labels": [POSITION_LABEL[p1], POSITION_LABEL[p2]],
                "branches": [b1, b2],
                "potential_element": LIU_HE[key],
                "note": "합 성립. 化 오행은 월령 조건에 따라 달라짐.",
            })

    # 삼합 (완전)
    for combo, elem in SAN_HE:
        if combo.issubset(branch_set):
            positions_with = [p for p in positions if branches_by_pos[p] in combo]
            results.append({
                "type": "삼합",
                "positions": positions_with,
                "position_labels": [POSITION_LABEL[p] for p in positions_with],
                "branches": [branches_by_pos[p] for p in positions_with],
                "potential_element": elem,
                "note": "삼합 성립. 化 오행은 월령 조건에 따라 달라짐.",
            })

    # 반합 (삼합 완전이 없을 때만)
    full_samhap_branches = set()
    for combo, _ in SAN_HE:
        if combo.issubset(branch_set):
            full_samhap_branches |= combo

    for p1, p2 in combinations(positions, 2):
        b1, b2 = branches_by_pos[p1], branches_by_pos[p2]
        key = frozenset([b1, b2])
        if key in BAN_HE and b1 not in full_samhap_branches:
            results.append({
                "type": "반합",
                "positions": [p1, p2],
                "position_labels": [POSITION_LABEL[p1], POSITION_LABEL[p2]],
                "branches": [b1, b2],
                "potential_element": BAN_HE[key],
                "note": "반합 성립. 완전한 化는 아님.",
            })

    # 방합
    for combo, elem, direction in BANG_HE:
        if combo.issubset(branch_set):
            positions_with = [p for p in positions if branches_by_pos[p] in combo]
            results.append({
                "type": "방합",
                "positions": positions_with,
                "position_labels": [POSITION_LABEL[p] for p in positions_with],
                "branches": [branches_by_pos[p] for p in positions_with],
                "potential_element": elem,
                "direction": direction,
                "note": "방합 성립. 계절·방위 응집.",
            })

    return results


def _detect_hyeong(branches_by_pos: dict) -> list:
    results = []
    branch_set = set(branches_by_pos.values())
    positions = list(branches_by_pos.keys())

    # 삼형 / 쌍형
    for combo, name, meaning in SAN_HYEONG:
        if combo.issubset(branch_set):
            positions_with = [p for p in positions if branches_by_pos[p] in combo]
            results.append({
                "type": "삼형" if len(combo) == 3 else "쌍형",
                "name": name,
                "meaning": meaning,
                "positions": positions_with,
                "position_labels": [POSITION_LABEL[p] for p in positions_with],
                "branches": [branches_by_pos[p] for p in positions_with],
            })

    # 자형: 같은 땅의 기운가 2개 이상
    counts = Counter(branches_by_pos.values())
    for branch, cnt in counts.items():
        if branch in ZIHYEONG_BRANCHES and cnt >= 2:
            positions_with = [p for p in positions if branches_by_pos[p] == branch]
            results.append({
                "type": "자형",
                "name": "자형",
                "meaning": "자기 파괴·내적 갈등",
                "positions": positions_with,
                "position_labels": [POSITION_LABEL[p] for p in positions_with],
                "branches": [branch] * cnt,
            })

    return results


def _detect_gan_he(stems_by_pos: dict) -> list:
    results = []
    positions = list(stems_by_pos.keys())
    for p1, p2 in combinations(positions, 2):
        s1, s2 = stems_by_pos[p1], stems_by_pos[p2]
        key = frozenset([s1, s2])
        if key in TIAN_GAN_HE:
            results.append({
                "type": "하늘의 기운합",
                "positions": [p1, p2],
                "position_labels": [POSITION_LABEL[p1], POSITION_LABEL[p2]],
                "stems": [s1, s2],
                "potential_element": TIAN_GAN_HE[key],
                "note": "하늘의 기운합 성립. 化 오행은 월령 조건에 따라 달라짐.",
            })
    return results


def summarize_relations(relations: dict) -> dict:
    """관계 검출 결과를 요약."""
    return {
        "has_chong":      len(relations["chong"]) > 0,
        "has_hyeong":     len(relations["hyeong"]) > 0,
        "has_he":         len(relations["he"]) > 0,
        "has_hai":        len(relations["hai"]) > 0,
        "has_gan_he":     len(relations["gan_he"]) > 0,
        "has_gan_chong":  len(relations["gan_chong"]) > 0,
        "chong_count":    len(relations["chong"]),
        "hyeong_count":   len(relations["hyeong"]),
        "he_count":       len(relations["he"]),
        "gan_he_count":   len(relations["gan_he"]),
        "gan_chong_count": len(relations["gan_chong"]),
        "day_chong":      any("day_pillar" in c["positions"] for c in relations["chong"]),
        "day_he":         any("day_pillar" in h["positions"] for h in relations["he"]),
        "day_gan_he":     any("day_pillar" in h["positions"] for h in relations["gan_he"]),
    }