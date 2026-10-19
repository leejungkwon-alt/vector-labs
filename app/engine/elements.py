# app/engine/elements.py

# NOTE: BRANCH_MAIN_STEM은 '체(體)'가 아닌 '용(用)' 기준의 본기(本氣)를 사용한다.
#       子=癸, 午=丁, 巳=丙, 亥=壬. 체 기준 만세력을 채택하려면 이 표를 교체할 것.

STEM_ATTRIBUTES = {
    "甲": (0, True),  "乙": (0, False),
    "丙": (1, True),  "丁": (1, False),
    "戊": (2, True),  "己": (2, False),
    "庚": (3, True),  "辛": (3, False),
    "壬": (4, True),  "癸": (4, False),
}

# 지지의 본기(Main Hidden Stem) 매핑
BRANCH_MAIN_STEM = {
    "子": "癸", "丑": "己", "寅": "甲", "卯": "乙",
    "辰": "戊", "巳": "丙", "午": "丁", "未": "己",
    "申": "庚", "酉": "辛", "戌": "戊", "亥": "壬",
}

# 글로벌 확장을 위한 십성 시스템 코드 정의
TEN_GOD_CODES = {
    "비견": "TEN_GOD_FRIEND",
    "겁재": "TEN_GOD_ROB_WEALTH",
    "식신": "TEN_GOD_EATING_GOD",
    "상관": "TEN_GOD_HURTING_OFFICER",
    "편재": "TEN_GOD_INDIRECT_WEALTH",
    "정재": "TEN_GOD_DIRECT_WEALTH",
    "편관": "TEN_GOD_SEVEN_KILLINGS",
    "정관": "TEN_GOD_DIRECT_OFFICER",
    "편인": "TEN_GOD_INDIRECT_RESOURCE",
    "정인": "TEN_GOD_DIRECT_RESOURCE",
}


def get_ten_god(day_stem: str, target_stem: str) -> str:
    """일간(day_stem)을 기준으로 대상 천간(target_stem)의 십성을 판정합니다."""
    if day_stem not in STEM_ATTRIBUTES or target_stem not in STEM_ATTRIBUTES:
        return ""

    dm_elem, dm_yang = STEM_ATTRIBUTES[day_stem]
    tg_elem, tg_yang = STEM_ATTRIBUTES[target_stem]

    same_polarity = (dm_yang == tg_yang)

    if dm_elem == tg_elem:
        return "비견" if same_polarity else "겁재"
    elif (dm_elem + 1) % 5 == tg_elem:
        return "식신" if same_polarity else "상관"
    elif (dm_elem + 2) % 5 == tg_elem:
        return "편재" if same_polarity else "정재"
    elif (dm_elem + 3) % 5 == tg_elem:
        return "편관" if same_polarity else "정관"
    elif (dm_elem + 4) % 5 == tg_elem:
        return "편인" if same_polarity else "정인"
    return ""


def get_pillar_ten_gods(day_stem: str, pillar: str) -> dict:
    """주(Pillar, 예: '庚午')에 대해 천간과 지지의 십성 시스템 코드를 반환합니다."""
    if len(pillar) != 2:
        return {"stem": "", "branch": ""}

    stem_char = pillar[0]
    branch_char = pillar[1]

    stem_korean = get_ten_god(day_stem, stem_char)
    branch_main_stem = BRANCH_MAIN_STEM.get(branch_char, "")
    branch_korean = get_ten_god(day_stem, branch_main_stem) if branch_main_stem else ""

    return {
        "stem": TEN_GOD_CODES.get(stem_korean, stem_korean),
        "branch": TEN_GOD_CODES.get(branch_korean, branch_korean),
    }


# ============================================================
# 오행 분포 분석 (Phase 1 확장)
# ============================================================

# 오행 인덱스 (기존 STEM_ATTRIBUTES와 동일): 0=木, 1=火, 2=土, 3=金, 4=水
ELEMENT_NAMES = ["木", "火", "土", "金", "水"]

STEM_TO_ELEMENT = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 지장간: [정기, 중기, 여기] 순서 (인덱스 0 = 정기)
# 학파에 따라 중기/여기 유무가 다를 수 있음.
BRANCH_HIDDEN_STEMS = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

# 지장간 가중치: 정기 1.0, 중기 0.3, 여기 0.2
_HIDDEN_WEIGHTS = [1.0, 0.3, 0.2]


def analyze_element_distribution(pillars: dict) -> dict:
    """
    4기둥(천간 4 + 지지 4) 오행 분포 분석.

    pillars: {"year_pillar": "甲寅", "month_pillar": "丙寅",
              "day_pillar": "丙申", "hour_pillar": "庚寅"}

    반환:
      counts:       {"木": 4.5, "火": 2.0, ...}
      percentages:  {"木": 45.0, ...}
      dominant:     과다 오행 리스트 (평균의 1.5배 이상)
      deficient:    부족 오행 리스트 (평균의 0.3배 이하, 0 초과)
      missing:      결핍 오행 리스트 (0)
      total:        가중치 합계
    """
    counts = {name: 0.0 for name in ELEMENT_NAMES}

    for pos in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        pillar = pillars.get(pos, "")
        if not isinstance(pillar, str) or len(pillar) != 2:
            continue

        stem_char, branch_char = pillar[0], pillar[1]

        # 천간 가중치 1.0
        if stem_char in STEM_TO_ELEMENT:
            counts[STEM_TO_ELEMENT[stem_char]] += 1.0

        # 지지: 지장간에 가중치 부여
        hidden = BRANCH_HIDDEN_STEMS.get(branch_char, [])
        for i, h in enumerate(hidden):
            if h in STEM_TO_ELEMENT and i < len(_HIDDEN_WEIGHTS):
                counts[STEM_TO_ELEMENT[h]] += _HIDDEN_WEIGHTS[i]

    raw_total = sum(counts.values())              # 표시용 실제 합계
    divisor = raw_total if raw_total > 0 else 1.0 # 0 나눗셈 방지용

    percentages = {k: round(v / divisor * 100, 1) for k, v in counts.items()}

    mean = raw_total / 5 if raw_total > 0 else 0.0
    if mean > 0:
        dominant = [k for k, v in counts.items() if v >= mean * 1.5]
        deficient = [k for k, v in counts.items() if 0 < v <= mean * 0.3]
    else:
        dominant = []
        deficient = []
    missing = [k for k, v in counts.items() if v == 0]

    return {
        "counts": {k: round(v, 2) for k, v in counts.items()},
        "percentages": percentages,
        "dominant": dominant,
        "deficient": deficient,
        "missing": missing,
        "total": round(raw_total, 2),
    }


# 오행 상생·상극 관계 (인덱스 기반)
def element_generates(a_idx: int, b_idx: int) -> bool:
    """a가 b를 生하는가 (木→火→土→金→水→木)"""
    return (a_idx + 1) % 5 == b_idx


def element_controls(a_idx: int, b_idx: int) -> bool:
    """a가 b를 剋하는가 (木→土→水→火→金→木)"""
    return (a_idx + 2) % 5 == b_idx