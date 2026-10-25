# app/semantic/tags.py
"""
Semantic Layer의 태그 상수 정의.

여기 정의된 코드가 엔진(정통 명리)과 콘텐츠(자연어) 사이의 계약.
콘텐츠 파일은 반드시 이 코드를 키로 사용해야 함.
"""

# ---- 일간 → Archetype ----
# 10하늘의 기운 → 서양 컨셉 아키타입
ARCHETYPES = {
    "甲": "THE_PIONEER",     # Yang Wood
    "乙": "THE_ADAPTER",     # Yin Wood
    "丙": "THE_RADIATOR",    # Yang Fire
    "丁": "THE_KEEPER",      # Yin Fire
    "戊": "THE_ANCHOR",      # Yang Earth
    "己": "THE_CULTIVATOR",  # Yin Earth
    "庚": "THE_BLADE",       # Yang Metal
    "辛": "THE_GEM",         # Yin Metal
    "壬": "THE_DEEP",        # Yang Water
    "癸": "THE_SPRING",      # Yin Water
}

# ---- 신강/신약 → Energy Profile ----
ENERGY_PROFILES = {
    "신강": "SELF_SOURCED",
    "중화": "BALANCED_CORE",
    "신약": "ENVIRONMENT_TUNED",
}

# ---- 오행 → Energy Signature ----
ELEMENT_SIGNATURES = {
    "木": "GROWTH",
    "火": "SPARK",
    "土": "GROUND",
    "金": "EDGE",
    "水": "FLOW",
}

# ---- 십성(코드) → 역할 ----
# 엔진이 뱉는 TEN_GOD_* 코드를 그대로 키로 사용
MONEY_MODES = {
    "TEN_GOD_DIRECT_WEALTH":   "THE_STEWARD",
    "TEN_GOD_INDIRECT_WEALTH": "THE_OPERATOR",
    "DEFAULT":                 "THE_FLOW",
}

WORK_MODES = {
    "TEN_GOD_EATING_GOD":      "THE_CREATOR",
    "TEN_GOD_HURTING_OFFICER": "THE_CHALLENGER",
    "TEN_GOD_DIRECT_OFFICER":  "THE_OFFICER",
    "TEN_GOD_SEVEN_KILLINGS":  "THE_SURVIVOR",
    "TEN_GOD_INDIRECT_RESOURCE": "THE_MYSTIC",
    "TEN_GOD_DIRECT_RESOURCE":   "THE_MENTOR",
    "DEFAULT": "THE_GENERALIST",
}

BOND_MODES = {
    "TEN_GOD_FRIEND":         "THE_TWIN",
    "TEN_GOD_ROB_WEALTH":     "THE_RIVAL",
    "TEN_GOD_DIRECT_OFFICER": "THE_ALLY",
    "DEFAULT":                "THE_EMPATH",
}

# ---- 신살 → 특성 태그 ----
SPECIAL_TRAITS = {
    "도화":     "MAGNETIC_DRAW",
    "역마":     "RESTLESS_FEET",
    "화개":     "SOLITARY_DEPTH",
    "천을귀인": "ALLY_MAGNET",
    "문창귀인": "SCHOLAR_MIND",
    "양인":     "SHARP_EDGE",
    "괴강":     "COMMANDER",
}

# ---- 격국 → 정체성 태그 ----
GYEOKGUK_TAGS = {
    "정관격": "STABILIZER",
    "편관격": "WARRIOR",
    "정재격": "CUSTODIAN",
    "편재격": "DEALMAKER",
    "식신격": "EXPRESSER",
    "상관격": "DISRUPTOR",
    "정인격": "MENTOR",
    "편인격": "INTUITIVE",
    "양인격": "EDGE_WALKER",
    "월겁격": "COOPERATOR",
    "건록격": "SELF_MADE",
    "기타":   "UNCLASSIFIED",
}

# ---- 관계 유형 (관계 태그) ----
RELATION_TAGS = {
    # 땅의 기운
    "육합":   "UNION",
    "삼합":   "TRIAD_UNION",
    "반합":   "HALF_UNION",
    "방합":   "DIRECTIONAL_UNION",
    "육충":   "CLASH",
    "삼형":   "TRIANGLE_TENSION",
    "쌍형":   "PAIR_TENSION",
    "자형":   "SELF_TENSION",
    "육해":   "FRICTION",
    "파":     "RUPTURE",
    # 하늘의 기운
    "하늘의 기운합": "STEM_UNION",
    "하늘의 기운충": "STEM_CLASH",
}