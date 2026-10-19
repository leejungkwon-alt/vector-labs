# app/services/template_interpreter.py

from app.services.template_data import TEMPLATE_DATABASE

# 천간/지지 한자를 한글 독음으로 변환하는 매핑 딕셔너리
HANJA_TO_HANGUL = {
    "甲": "갑", "乙": "을", "丙": "병", "丁": "정", "戊": "무",
    "己": "기", "庚": "경", "辛": "신", "壬": "임", "癸": "계",
    "子": "자", "丑": "축", "寅": "인", "卯": "묘", "辰": "진", "巳": "사",
    "午": "오", "未": "미", "申": "신", "酉": "유", "戌": "술", "亥": "해",
}

_VALID_STEMS = set("甲乙丙丁戊己庚辛壬癸")
_VALID_BRANCHES = set("子丑寅卯辰巳午未申酉戌亥")


def format_pillar(pillar: str, lang: str) -> str:
    """언어 설정에 따라 간지 표기를 '한자 (한글)' 형태로 변환합니다 (한국어 기준)."""
    if not pillar:
        return ""
    if lang == "ko":
        hangul = "".join(HANJA_TO_HANGUL.get(char, char) for char in pillar)
        return f"{pillar} ({hangul})"
    return pillar


def _validate_saju_data(saju_data: dict) -> str:
    """최소한의 입력 검증. 검증된 day_pillar(2글자)를 반환."""
    if not isinstance(saju_data, dict):
        raise ValueError("saju_data must be an object.")

    day_pillar = saju_data.get("day_pillar")
    if not isinstance(day_pillar, str) or len(day_pillar) != 2:
        raise ValueError("saju_data.day_pillar must be a 2-character pillar string.")
    if day_pillar[0] not in _VALID_STEMS or day_pillar[1] not in _VALID_BRANCHES:
        raise ValueError(f"saju_data.day_pillar has invalid characters: {day_pillar!r}")

    ten_gods = saju_data.get("ten_gods")
    if ten_gods is not None and not isinstance(ten_gods, dict):
        raise ValueError("saju_data.ten_gods must be an object if provided.")

    return day_pillar


def generate_template_interpretation(saju_data: dict, lang: str = "en") -> dict:
    """계산된 사주 데이터를 바탕으로 템플릿 기반 해석 리포트를 조립합니다."""
    lang_pack = TEMPLATE_DATABASE.get(lang, TEMPLATE_DATABASE["en"])

    raw_day_pillar = _validate_saju_data(saju_data)
    day_pillar = format_pillar(raw_day_pillar, lang)

    ten_gods = saju_data.get("ten_gods") or {}
    luck_info = saju_data.get("luck_info")

    # 1. 일주 및 기질 성향 추출
    day_stem = raw_day_pillar[0]
    traits_dict = lang_pack.get("day_master_traits", {})
    default_trait = {
        "summary": "You possess a balanced inner rhythm.",
        "strengths": ["Balanced energy", "Adaptability"],
        "blind_spot": "Maintain consistency.",
    } if lang == "en" else {
        "summary": "조화롭고 균형 잡힌 내면의 리듬을 지니고 있습니다.",
        "strengths": ["균형 잡힌 에너지", "유연한 적응력"],
        "blind_spot": "꾸준한 템포 유지가 중요합니다.",
    }

    trait_data = traits_dict.get(day_stem, default_trait)

    # 십성 코드 수집
    found_codes = set()
    if isinstance(ten_gods, dict):
        for p_data in ten_gods.values():
            if isinstance(p_data, dict):
                for key in ("stem", "branch"):
                    code = p_data.get(key)
                    if code:
                        found_codes.add(code)

    # 2. 머니 플로우 조언 매핑
    wealth_advice_dict = lang_pack["wealth_section"]["advice"]
    wealth_code = "DEFAULT"
    for code in ("TEN_GOD_DIRECT_WEALTH", "TEN_GOD_INDIRECT_WEALTH"):
        if code in found_codes:
            wealth_code = code
            break
    wealth_text = wealth_advice_dict.get(wealth_code, wealth_advice_dict["DEFAULT"])

    # 3. 커리어 성향 조언 매핑
    career_advice_dict = lang_pack["career_section"]["advice"]
    career_code = "DEFAULT"
    for code in ("TEN_GOD_EATING_GOD", "TEN_GOD_HURTING_OFFICER", "TEN_GOD_DIRECT_OFFICER"):
        if code in found_codes:
            career_code = code
            break
    career_text = career_advice_dict.get(career_code, career_advice_dict["DEFAULT"])

    # 4. 대인관계 소통 방식 조언 매핑
    relation_advice_dict = lang_pack["relationship_section"]["advice"]
    relation_code = "DEFAULT"
    for code in ("TEN_GOD_FRIEND", "TEN_GOD_DIRECT_OFFICER"):
        if code in found_codes:
            relation_code = code
            break
    relation_text = relation_advice_dict.get(relation_code, relation_advice_dict["DEFAULT"])

    # 5. 웰니스 멘탈 케어 조언 매핑
    wellness_advice_dict = lang_pack["wellness_section"]["advice"]
    wellness_code = "DEFAULT"
    for code in ("TEN_GOD_SEVEN_KILLINGS", "TEN_GOD_INDIRECT_RESOURCE"):
        if code in found_codes:
            wellness_code = code
            break
    wellness_text = wellness_advice_dict.get(wellness_code, wellness_advice_dict["DEFAULT"])

    # 6. 세운 및 성장 타이밍 조언 매핑
    luck_analysis_text = None
    target_year_for_title = None
    if isinstance(luck_info, dict):
        target_year = luck_info.get("target_year")   # ← 하드코딩 폴백 제거
        target_year_for_title = target_year
        annual_data = luck_info.get("annual_luck") or {}
        raw_annual_pillar = annual_data.get("pillar", "")
        annual_pillar = format_pillar(raw_annual_pillar, lang)
        annual_ten_god = (
            annual_data.get("annual_ten_god")
            or annual_data.get("ten_god", "")
        )

        if target_year is not None and raw_annual_pillar:
            base_annual_text = lang_pack["annual_luck_note"].format(
                target_year=target_year,
                annual_pillar=annual_pillar,
            )

            advice_dict = lang_pack.get("annual_luck_advice", {})
            default_advice = (
                "Focus on mindful growth and steady well-being." if lang == "en"
                else "마음의 성장과 꾸준한 웰니스 관리에 집중해 보세요."
            )
            advice_text = advice_dict.get(annual_ten_god, default_advice)
            luck_analysis_text = f"{base_annual_text} {advice_text}"

    # 최종 구조화된 리포트
    report_sections = {
        "title": lang_pack["title"],
        "intro": lang_pack["intro"],
        "core_blueprint": {
            "title": lang_pack["day_master_intro"].format(day_pillar=day_pillar),
            "details": trait_data,
        },
        "wealth_flow": {
            "title": lang_pack["wealth_section"]["title"],
            "description": lang_pack["wealth_section"]["description"],
            "advice": wealth_text,
        },
        "career_architecture": {
            "title": lang_pack["career_section"]["title"],
            "description": lang_pack["career_section"]["description"],
            "advice": career_text,
        },
        "relationship_dynamics": {
            "title": lang_pack["relationship_section"]["title"],
            "description": lang_pack["relationship_section"]["description"],
            "advice": relation_text,
        },
        "wellness_care": {
            "title": lang_pack["wellness_section"]["title"],
            "description": lang_pack["wellness_section"]["description"],
            "advice": wellness_text,
        },
        "strategic_timing": {
            "title": lang_pack["annual_luck_title"].format(
                target_year=(
                    target_year_for_title
                    if target_year_for_title is not None
                    else "—"
                )
            ),
            "analysis": luck_analysis_text,
        },
        "disclaimer": lang_pack["disclaimer"],
    }

    return report_sections