# app/semantic/tagger.py
"""
엔진(사주 계산) → Semantic Tags.

계산 기준: 억부(抑扶) 간이판.
- 신강/신약: 지지 정기 + 천간의 가중합 (ratio 0.6/0.4 경계)
- 용신: 억부 + 조후 보정
- 학파에 따라 결과가 달라질 수 있음

calculate_saju()의 결과 dict를 받아서 언어 중립 태그를 뽑는다.
이 태그가 이후 모든 콘텐츠의 기반.
"""
from app.engine.elements import analyze_element_distribution
from app.engine.strength import assess_day_master_strength
from app.engine.yongsin import derive_useful_god
from app.engine.relations import detect_relations, summarize_relations
from app.engine.sinsal import detect_sinsal
from app.engine.gyeokguk import determine_gyeokguk
from app.engine.twelve_stages import twelve_stages_for_pillars
from app.engine.daewoon_score import score_daewoon, summarize_daewoon_timeline
from app.engine.age_band import compute_age_band           # ---- Step 9-A ----

from app.semantic.tags import (
    ARCHETYPES, ENERGY_PROFILES, ELEMENT_SIGNATURES,
    MONEY_MODES, WORK_MODES, BOND_MODES,
    SPECIAL_TRAITS, GYEOKGUK_TAGS, DAEWOON_GRADES, RELATION_TAGS,
)


def _extract_pillars(saju_result: dict) -> dict:
    """calculate_saju 결과에서 기둥을 뽑기. hour_pillar 없으면 3주만."""
    pillars = {
        "year_pillar":  saju_result["year_pillar"],
        "month_pillar": saju_result["month_pillar"],
        "day_pillar":   saju_result["day_pillar"],
    }
    hour = saju_result.get("hour_pillar")
    if isinstance(hour, str) and len(hour) == 2:
        pillars["hour_pillar"] = hour
    return pillars


def _collect_ten_god_codes(ten_gods: dict) -> set:
    """ten_gods dict에서 모든 시스템 코드를 set으로."""
    codes = set()
    if not isinstance(ten_gods, dict):
        return codes
    for p_data in ten_gods.values():
        if isinstance(p_data, dict):
            for key in ("stem", "branch"):
                code = p_data.get(key)
                if code and code != "ROLE_DAY_MASTER":
                    codes.add(code)
    return codes


def _pick_mode(codes: set, mode_map: dict, priority: list) -> str:
    """우선순위에 따라 첫 번째 매칭 코드를 mode로 반환."""
    for code in priority:
        if code in codes:
            return mode_map[code]
    return mode_map["DEFAULT"]


def _compute_age_band(saju_result: dict) -> dict | None:      # ---- Step 9-A ----
    """birth_date + target_year로 age_band 계산. 정보 부족하면 None."""
    birth_date_str = saju_result.get("birth_date")
    if not isinstance(birth_date_str, str) or len(birth_date_str) < 4:
        return None
    try:
        birth_year = int(birth_date_str[:4])
    except ValueError:
        return None

    luck = saju_result.get("luck_info")
    target_year = luck.get("target_year") if isinstance(luck, dict) else None
    return compute_age_band(birth_year, target_year)


def build_semantic_profile(saju_result: dict) -> dict:
    """
    calculate_saju()의 결과 → Semantic Tags.

    반환 구조 (주요 필드):
    {
      "archetype": { "key": "THE_RADIATOR", "intensity": "SELF_SOURCED", ... },
      "energy_signature": { "dominant": [...], "deficient": [...], "missing": [...] },
      "lucky_code": { "power": "GROUND", "support": "EDGE", "watch_out": [...] },
      "money_mode", "work_mode", "bond_mode": "THE_OPERATOR" / ...,
      "structure": { "gyeokguk": ..., "twelve_stages": {...}, "relations": {...} },
      "special_traits": [...],
      "year_theme": {...} 또는 None,
      "daewoon_timeline": [...],
      "daewoon_summary": {...},
      "region": "KOREA" 또는 None,                 # ---- Step 9-A ----
      "age_band": { "key": "PEAK", "age": 52, ... } 또는 None,  # ---- Step 9-A ----
    }
    """
    pillars = _extract_pillars(saju_result)
    day_stem = pillars["day_pillar"][0]

    # 1. 일간 + 신강/신약
    strength = assess_day_master_strength(pillars)
    archetype_key = ARCHETYPES.get(day_stem, "UNKNOWN")
    intensity = ENERGY_PROFILES.get(strength["verdict"], "BALANCED_CORE")

    # 2. 오행 분포
    dist = analyze_element_distribution(pillars)
    dominant_sigs = [ELEMENT_SIGNATURES[e] for e in dist["dominant"]]
    deficient_sigs = [ELEMENT_SIGNATURES[e] for e in dist["deficient"]]
    missing_sigs = [ELEMENT_SIGNATURES[e] for e in dist["missing"]]

    # 3. 용신/희신/기신
    yongsin = derive_useful_god(pillars)

    # 4. 십성 → mode
    codes = _collect_ten_god_codes(saju_result.get("ten_gods", {}))

    money_mode = _pick_mode(
        codes, MONEY_MODES,
        ["TEN_GOD_DIRECT_WEALTH", "TEN_GOD_INDIRECT_WEALTH"],
    )
    work_mode = _pick_mode(
        codes, WORK_MODES,
        ["TEN_GOD_EATING_GOD", "TEN_GOD_HURTING_OFFICER",
         "TEN_GOD_DIRECT_OFFICER", "TEN_GOD_SEVEN_KILLINGS",
         "TEN_GOD_INDIRECT_RESOURCE", "TEN_GOD_DIRECT_RESOURCE"],
    )
    bond_mode = _pick_mode(
        codes, BOND_MODES,
        ["TEN_GOD_FRIEND", "TEN_GOD_ROB_WEALTH", "TEN_GOD_DIRECT_OFFICER"],
    )

    # 5. 격국
    gyeok = determine_gyeokguk(pillars)
    gyeokguk_tag = GYEOKGUK_TAGS.get(gyeok["name"], "UNCLASSIFIED")

    # 6. 12운성
    stages = twelve_stages_for_pillars(pillars)

    # 7. 관계
    rels = detect_relations(pillars)
    rel_summary = summarize_relations(rels)
    relation_tags = []
    for kind in ("he", "chong", "hyeong", "hai", "pa", "gan_he", "gan_chong"):
        for item in rels.get(kind, []):
            tag = RELATION_TAGS.get(item["type"])
            if tag and tag not in relation_tags:
                relation_tags.append(tag)

    # 8. 신살
    sinsal = detect_sinsal(pillars)
    special_traits = []
    for ko_name, entries in sinsal.items():
        if entries:
            tag = SPECIAL_TRAITS.get(ko_name)
            if tag:
                special_traits.append(tag)

    # 9. 대운 점수화
    daewoon_info = saju_result.get("daewoon_info") or {}
    raw_daewoon = daewoon_info.get("daewoon_pillars", [])
    scored_daewoon = score_daewoon(raw_daewoon, yongsin)
    timeline = [
        {
            "index": d["daewoon_index"],
            "ages": [d["start_age"], d["end_age"]],
            "pillar": d["pillar"],
            "score": d["score"],
            "grade": DAEWOON_GRADES.get(d["grade"]["ko"], "NEUTRAL"),
        }
        for d in scored_daewoon
    ]
    daewoon_summary = summarize_daewoon_timeline(scored_daewoon)

    # 10. 세운
    luck_info = saju_result.get("luck_info")
    year_theme = None
    if isinstance(luck_info, dict):
        annual = luck_info.get("annual_luck", {})
        year_theme = {
            "target_year": luck_info.get("target_year"),
            "pillar": annual.get("pillar"),
            "ten_god": annual.get("ten_god"),
        }

    # ---- Step 10: monthly calendar ----
    monthly_calendar = []
    if isinstance(luck_info, dict):
        monthly_raw = luck_info.get("monthly_lucks", [])
        if monthly_raw:
            scored_months = score_daewoon(monthly_raw, yongsin)
            for s in scored_months:
                monthly_calendar.append({
                    "month_index": s["month_index"],
                    "pillar": s["pillar"],
                    "branch": s["branch"],
                    "approx_solar_month": s["approx_solar_month"],
                    "ten_god": s.get("ten_god", ""),
                    "score": s["score"],
                    "grade": DAEWOON_GRADES.get(s["grade"]["ko"], "NEUTRAL"),
                })

    # ---- Step 9-A: region + age_band ----
    region = saju_result.get("region")
    age_band = _compute_age_band(saju_result)

    # ---- 최종 조립 ----
    return {
        "archetype": {
            "key": archetype_key,
            "stem": day_stem,
            "intensity": intensity,
            "strength_raw": strength["verdict"],
        },
        "energy_signature": {
            "dominant": dominant_sigs,
            "deficient": deficient_sigs,
            "missing": missing_sigs,
            "percentages": dist["percentages"],
            "raw_dominant": dist["dominant"],
            "raw_missing": dist["missing"],
        },
        "lucky_code": {
            "power": ELEMENT_SIGNATURES.get(yongsin["yongsin"], ""),
            "power_element": yongsin["yongsin"],
            "support": ELEMENT_SIGNATURES.get(yongsin["huisin"], ""),
            "support_element": yongsin["huisin"],
            "watch_out": [ELEMENT_SIGNATURES.get(e, "") for e in yongsin["gisin"]],
            "watch_out_elements": yongsin["gisin"],
        },
        "money_mode": money_mode,
        "work_mode": work_mode,
        "bond_mode": bond_mode,
        "structure": {
            "gyeokguk": gyeokguk_tag,
            "gyeokguk_raw": gyeok["name"],
            "twelve_stages": stages,
            "relations": {
                "tags": relation_tags,
                "summary": rel_summary,
            },
        },
        "special_traits": special_traits,
        "special_traits_raw": {k: v for k, v in sinsal.items() if v},
        "year_theme": year_theme,
        "daewoon_timeline": timeline,
        "daewoon_summary": daewoon_summary,
        "region": region,                  # ---- Step 9-A ----
        "age_band": age_band,              # ---- Step 9-A ----
        "monthly_calendar": monthly_calendar,  # ---- Step 10 ----
        "pillars": pillars,                # ---- C+ ----
        "birth_time_mode": saju_result.get("birth_time_mode", "exact"),
        "hour_pillar_confidence": saju_result.get("hour_pillar_confidence", "exact"),
    }