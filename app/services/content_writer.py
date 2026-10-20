# app/services/content_writer.py
"""
Semantic Tags → 자연어 콘텐츠.

엔진(semantic profile)은 언어 중립.
콘텐츠는 이 writer가 언어별 팩에서 꺼내 조립.
"""
from app.services.content.loader import load_pack
from app.services.personalizer import generate_personalized_notes
from app.compliance.crisis_resources import get_crisis_resources
from app.services.visual_generator import get_daily_wallpaper_url
from app.services.variation import pick_variant, make_seed



def _select_variant_content(
    entry,
    *,
    user_id,
    birth_date,
    scope,
    discriminator,
):
    """dict면 그대로, list면 seed 기반으로 1개 선택 (Step 3 Phase C)."""
    if isinstance(entry, dict):
        return entry
    if isinstance(entry, list) and entry:
        seed = make_seed(
            user_id=user_id,
            birth_date=birth_date,
            scope=scope,
            discriminator=discriminator,
        )
        return pick_variant(entry, seed_parts=seed)
    return {}


# ============================================================
# CORE
# ============================================================
def write_core_section(profile: dict, lang: str = "en") -> dict:
    pack = load_pack(lang, "core")
    archetypes = pack.get("ARCHETYPE_CONTENT", {})
    default_intensity = pack.get("DEFAULT_INTENSITY", {})

    arch_key = profile["archetype"]["key"]
    intensity_key = profile["archetype"]["intensity"]

    arch = archetypes.get(arch_key)
    if not arch:
        raise KeyError(f"Archetype content not found: {arch_key}")

    intensities = arch.get("intensities") or {}
    content = intensities.get(intensity_key, default_intensity)

    return {
        "id": "core",
        "title": _title(lang, "core"),
        "archetype": {
            "key": arch_key,
            "name": arch["name"],
            "tagline": arch["tagline"],
            "symbol": arch["symbol"],
            "color": arch["color"],
            "element": arch["element"],
        },
        "intensity_label": _intensity_label(lang, intensity_key),
        "hero": content["hero"],
        "narrative": content.get("narrative", []),
        "shadows": content.get("shadows", []),
        "advice": content.get("advice", []),
        "keywords": content.get("keywords", []),
        "personalized_insights": generate_personalized_notes(profile, lang),
    }


# ============================================================
# ENERGY
# ============================================================
def write_energy_section(profile: dict, lang: str = "en") -> dict:
    pack = load_pack(lang, "energy")
    content_map = pack.get("ELEMENT_CONTENT", {})
    display = pack.get("ELEMENT_DISPLAY", {})
    keywords = pack.get("ELEMENT_KEYWORDS", {})

    sig = profile["energy_signature"]
    dominant = sig.get("dominant", [])
    deficient = sig.get("deficient", [])
    missing = sig.get("missing", [])

    blocks = []
    for key in dominant:
        c = content_map.get(key, {})
        blocks.append({
            "role": "dominant",
            "signature": key,
            "name": display.get(key, key),
            "keywords": keywords.get(key, []),
            "body": c.get("on_dominant", ""),
        })
    for key in deficient:
        c = content_map.get(key, {})
        blocks.append({
            "role": "deficient",
            "signature": key,
            "name": display.get(key, key),
            "keywords": keywords.get(key, []),
            "body": c.get("on_deficient", ""),
        })
    for key in missing:
        c = content_map.get(key, {})
        blocks.append({
            "role": "missing",
            "signature": key,
            "name": display.get(key, key),
            "keywords": keywords.get(key, []),
            "body": c.get("on_missing", ""),
        })

    return {
        "id": "energy",
        "title": _title(lang, "energy"),
        "hero": _energy_hero(lang, dominant, missing, deficient),
        "percentages": sig.get("percentages", {}),
        "raw_dominant": sig.get("raw_dominant", []),
        "raw_missing": sig.get("raw_missing", []),
        "blocks": blocks,
    }


def _energy_hero(lang: str, dominant: list, missing: list, deficient: list) -> str:
    try:
        pack = load_pack(lang, "sections")
        templates = pack.get("ENERGY_HERO_TEMPLATES", {})
    except KeyError:
        templates = {}

    try:
        energy_pack = load_pack(lang, "energy")
        display = energy_pack.get("ELEMENT_DISPLAY", {})
    except KeyError:
        display = {}

    def name(sig: str) -> str:
        return display.get(sig, sig)

    balance_fallback = {"ko": "균형", "en": "balance"}.get(lang, "balance")

    dom = ", ".join(name(s) for s in dominant) or balance_fallback
    miss = ", ".join(name(s) for s in missing)
    defi = ", ".join(name(s) for s in deficient)

    if missing and "missing" in templates:
        return templates["missing"].format(dominant=dom, missing=miss)
    if deficient and "deficient" in templates:
        return templates["deficient"].format(dominant=dom, deficient=defi)
    return templates.get("default", "You run on {dominant}.").format(dominant=dom)


# ============================================================
# LUCKY CODE
# ============================================================
def write_lucky_code_section(profile: dict, lang: str = "en") -> dict:
    pack = load_pack(lang, "lucky_code")
    content_map = pack.get("LUCKY_CODE_CONTENT", {})
    domain_map = pack.get("LUCKY_CODE_DOMAINS", {})

    try:
        sections_pack = load_pack(lang, "sections")
        hero_tpl = sections_pack.get(
            "LUCKY_CODE_HERO_TEMPLATE",
            "Your power element is {element} — lean into it.",
        )
    except KeyError:
        hero_tpl = "Your power element is {element} — lean into it."

    try:
        energy_pack = load_pack(lang, "energy")
        element_display = energy_pack.get("ELEMENT_DISPLAY", {})
    except KeyError:
        element_display = {}

    lc = profile["lucky_code"]
    power_sig = lc["power"]
    support_sig = lc["support"]

    power = content_map.get(power_sig, {})
    support = content_map.get(support_sig, {})

    power_element = power.get("element", power_sig)
    power_domains = domain_map.get(power_sig, {})

    watch_out = [
        {"signature": s, "name": element_display.get(s, s)}
        for s in lc.get("watch_out", [])
    ]

    return {
        "id": "lucky_code",
        "title": _title(lang, "lucky_code"),
        "hero": hero_tpl.format(element=power_element),
        "power": {
            "signature": power_sig,
            "element": power_element,
            "keywords": power.get("keywords", []),
            "colors": power.get("colors", []),
            "numbers": power.get("numbers", []),
            "directions": power.get("directions", []),
            "activities": power.get("activities", []),
            "foods": power.get("foods", []),
            "practices": power.get("practices", []),
            "domains": power_domains,
        },
        "support": {
            "signature": support_sig,
            "element": support.get("element", support_sig),
            "keywords": support.get("keywords", []),
            "colors": support.get("colors", []),
            "numbers": support.get("numbers", []),
            "directions": support.get("directions", []),
        },
        "watch_out": watch_out,
    }


# ============================================================
# HEALTH
# ============================================================
def write_health_section(profile: dict, lang: str = "en") -> dict:
    try:
        pack = load_pack(lang, "health")
        content_map = pack.get("HEALTH_CONTENT", {})
        display = pack.get("HEALTH_DISPLAY", {})
        organs_map = pack.get("ELEMENT_ORGANS", {})
    except KeyError:
        pack = {}
        content_map, display, organs_map = {}, {}, {}

    sig = profile["energy_signature"]
    dominant = sig.get("dominant", [])
    deficient = sig.get("deficient", [])
    missing = sig.get("missing", [])

    blocks = []
    for key in dominant:
        c = content_map.get(key, {})
        o = organs_map.get(key, {})
        blocks.append({
            "role": "dominant",
            "signature": key,
            "name": display.get(key, key),
            "organs": {
                "zang": o.get("zang", ""),
                "fu": o.get("fu", ""),
                "openings": o.get("openings", []),
                "emotion": o.get("emotion", ""),
            },
            "body": c.get("over_pattern", ""),
        })
    for key in (deficient + missing):
        c = content_map.get(key, {})
        o = organs_map.get(key, {})
        blocks.append({
            "role": "deficient" if key in deficient else "missing",
            "signature": key,
            "name": display.get(key, key),
            "organs": {
                "zang": o.get("zang", ""),
                "fu": o.get("fu", ""),
                "openings": o.get("openings", []),
                "emotion": o.get("emotion", ""),
            },
            "body": c.get("under_pattern", ""),
        })

    practices = []
    for key in dominant:
        c = content_map.get(key, {})
        for p in c.get("practices", []):
            if p not in practices:
                practices.append(p)
    for key in (deficient + missing):
        c = content_map.get(key, {})
        for p in c.get("practices", []):
            if p not in practices:
                practices.append(p)

    return {
        "id": "health",
        "title": _title(lang, "health"),
        "hero": _health_hero(lang, dominant, deficient, missing),
        "blocks": blocks,
        "practices": practices,
        "disclaimer": pack.get("HEALTH_DISCLAIMER", ""),
        "framework_note": pack.get("HEALTH_FRAMEWORK_NOTE", ""),
    }


def _health_hero(lang: str, dominant: list, deficient: list, missing: list) -> str:
    try:
        pack = load_pack(lang, "sections")
        templates = pack.get("HEALTH_HERO_TEMPLATES", {})
    except KeyError:
        templates = {}

    # signature → 언어별 display (성장/불꽃/대지/예리함/흐름)
    try:
        health_pack = load_pack(lang, "health")
        display = health_pack.get("HEALTH_DISPLAY", {})
    except KeyError:
        display = {}

    def name(sig: str) -> str:
        return display.get(sig, sig)

    def join(items):
        return ", ".join(name(s) for s in items)

    if missing and "missing" in templates:
        return templates["missing"].format(dominant=join(dominant), missing=join(missing))
    if deficient and "deficient" in templates:
        return templates["deficient"].format(dominant=join(dominant), deficient=join(deficient))
    return templates.get("default", "{dominant} energy shapes your body.").format(
        dominant=join(dominant) or ("균형" if lang == "ko" else "Balanced")
    )


# ============================================================
# MONEY / WORK / BONDS
# ============================================================
def _write_mode_section(profile: dict, lang: str, section_id: str,
                        mode_key: str) -> dict:
    pack = load_pack(lang, "sections")
    key_map = {
        "money": "MONEY_CONTENT",
        "work": "WORK_CONTENT",
        "bonds": "BONDS_CONTENT",
    }
    content_map = pack.get(key_map[section_id], {})
    content = content_map.get(mode_key, {})

    return {
        "id": section_id,
        "title": _title(lang, section_id),
        "mode": mode_key,
        "headline": content.get("headline", ""),
        "body": content.get("body", ""),
        "action": content.get("action", ""),
    }


def write_money_section(profile: dict, lang: str = "en") -> dict:
    return _write_mode_section(profile, lang, "money", profile["money_mode"])


def write_work_section(profile: dict, lang: str = "en") -> dict:
    return _write_mode_section(profile, lang, "work", profile["work_mode"])


def write_bonds_section(profile: dict, lang: str = "en") -> dict:
    return _write_mode_section(profile, lang, "bonds", profile["bond_mode"])


# ============================================================
# YEAR
# ============================================================
def write_year_section(profile: dict, lang: str = "en", user_id: str | None = None) -> dict | None:
    year_theme = profile.get("year_theme")
    if not year_theme:
        return None

    pack = load_pack(lang, "year")
    theme_map = pack.get("YEAR_THEME_CONTENT", {})
    default_theme = pack.get("DEFAULT_YEAR_THEME", {})

    ten_god = year_theme.get("ten_god", "")
    raw = theme_map.get(ten_god, default_theme)
    theme = _select_variant_content(
        raw,
        user_id=user_id,
        birth_date=profile.get("birth_date"),
        scope="year",
        discriminator=str(year_theme.get("target_year")),
    )

    # ---- 생애 단계 컨텍스트 ----
    age_band = profile.get("age_band")
    life_stage_context = None
    if age_band:
        try:
            ab_pack = load_pack(lang, "age_band")
            ab_map = ab_pack.get("AGE_BAND_CONTENT", {})
        except KeyError:
            ab_map = {}
        band = ab_map.get(age_band["key"], {})
        if band:
            life_stage_context = {
                "key": age_band["key"],
                "label": band.get("label", ""),
                "headline": band.get("headline", ""),
                # 본문(note)은 생략 — age_band 섹션에서 전체 확인
            }

    return {
        "id": "year",
        "title": _title(lang, "year"),
        "target_year": year_theme.get("target_year"),
        "pillar": year_theme.get("pillar"),
        "ten_god": ten_god,
        "name": theme["name"],
        "headline": theme["headline"],
        "body": theme["body"],
        "watch_for": theme.get("watch_for", ""),
        "lean_into": theme.get("lean_into", ""),
        "life_stage_context": life_stage_context,
    }


# ============================================================
# MONTHLY (Step 10)
# ============================================================
def write_monthly_section(profile: dict, lang: str = "en", user_id: str | None = None) -> dict | None:
    monthly = profile.get("monthly_calendar", [])
    if not monthly:
        return None

    try:
        pack = load_pack(lang, "monthly")
        content_map = pack.get("MONTHLY_THEME_CONTENT", {})
        default_theme = pack.get("DEFAULT_MONTHLY_THEME", {})
        hero_tpl = pack.get("MONTHLY_HERO_TEMPLATE", "{year} months")
        grade_label = pack.get("GRADE_LABEL", {})
        grade_context_map = pack.get("MONTHLY_GRADE_CONTEXT", {})
    except KeyError:
        content_map, default_theme = {}, {}
        hero_tpl = "{year} months"
        grade_label = {}
        grade_context_map = {}

    year_theme = profile.get("year_theme") or {}
    target_year = year_theme.get("target_year") or ""

    items = []
    for m in monthly:
        tg = m.get("ten_god", "")
        raw = content_map.get(tg, default_theme)
        content = _select_variant_content(
            raw,
            user_id=user_id,
            birth_date=profile.get("birth_date"),
            scope="monthly",
            discriminator=f"{target_year}-{m['month_index']}",
        )
        items.append({
            "month_index": m["month_index"],
            "pillar": m["pillar"],
            "branch": m["branch"],
            "approx_solar_month": m["approx_solar_month"],
            "ten_god": tg,
            "score": m["score"],
            "grade": m["grade"],
            "grade_label": grade_label.get(m["grade"], m["grade"]),
            "grade_context": grade_context_map.get(m["grade"], ""),
            "name": content.get("name", ""),
            "headline": content.get("headline", ""),
            "body": content.get("body", ""),
            "watch_for": content.get("watch_for", ""),
            "lean_into": content.get("lean_into", ""),
        })

    return {
        "id": "monthly",
        "title": _title(lang, "monthly"),
        "hero": hero_tpl.format(year=target_year),
        "target_year": target_year,
        "items": items,
    }


# ============================================================
# CHART (C+ Global)
# ============================================================
_LAYER_META = {
    "en": {
        "year_pillar":  {"label": "Childhood", "role": "Your roots — how you started and family influence"},
        "month_pillar": {"label": "Career",    "role": "Your social life — how you work and interact"},
        "day_pillar":   {"label": "Core Self", "role": "Your true identity — who you are at your core"},
        "hour_pillar":  {"label": "Future",    "role": "Your inner world — your dreams and later years"},
    },
    "ko": {
        "year_pillar":  {"label": "어린 시절 (년주)", "role": "가족과 유년기의 영향 — 당신의 시작점"},
        "month_pillar": {"label": "사회 생활 (월주)", "role": "직장과 사회에서의 모습 — 당신의 활동 무대"},
        "day_pillar":   {"label": "나의 본질 (일주)", "role": "가장 핵심이 되는 나 — 진짜 내 모습"},
        "hour_pillar":  {"label": "미래와 내면 (시주)", "role": "나이 들수록 드러나는 꿈과 내면의 세계"},
    },
}


from app.semantic.tags import (
    ARCHETYPES as _ARCHETYPES_SRC,
    ELEMENT_SIGNATURES as _ELEM_SIG_SRC,
)
from app.engine.elements import STEM_TO_ELEMENT as _STEM_ELEM_SRC

# 유일 진실 소스(tags.py / elements.py)에서 파생
_STEM_TO_ARCH_KEY = dict(_ARCHETYPES_SRC)
_STEM_TO_ELEM_SIG = {
    stem: _ELEM_SIG_SRC[elem]
    for stem, elem in _STEM_ELEM_SRC.items()
}

def write_chart_section(profile: dict, lang: str = "en") -> dict:
    pillars = profile.get("pillars", {})
    layer_meta = _LAYER_META.get(lang, _LAYER_META["en"])

    core_pack = load_pack(lang, "core")
    arch_content = core_pack.get("ARCHETYPE_CONTENT", {})
    try:
        energy_pack = load_pack(lang, "energy")
        elem_display = energy_pack.get("ELEMENT_DISPLAY", {})
    except KeyError:
        elem_display = {}

    sections_pack = load_pack(lang, "sections")
    pos_templates = sections_pack.get("CHART_POSITION_TEMPLATES", {})
    note_tpl = sections_pack.get("CHART_NOTE_TEMPLATE", "")

    layers = []
    for pos in ("year_pillar", "month_pillar", "day_pillar", "hour_pillar"):
        pillar = pillars.get(pos, "")
        if not isinstance(pillar, str) or len(pillar) != 2:
            continue
        stem = pillar[0]
        arch_key = _STEM_TO_ARCH_KEY.get(stem, "UNKNOWN")
        elem_sig = _STEM_TO_ELEM_SIG.get(stem, "")
        arch_meta = arch_content.get(arch_key, {})
        meta = layer_meta.get(pos, {})
        arch_name = arch_meta.get("name", arch_key)
        narrative = pos_templates.get(pos, "{archetype}").format(archetype=arch_name)

        layers.append({
            "position": pos,
            "label": meta.get("label", pos),
            "role": meta.get("role", ""),
            "archetype": arch_name,
            "archetype_key": arch_key,
            "element": elem_display.get(elem_sig, elem_sig),
            "element_signature": elem_sig,
            "narrative": narrative,
            "is_self": pos == "day_pillar",
        })

    from collections import Counter
    counts = Counter(l["archetype_key"] for l in layers)
    notes = []
    for key, cnt in counts.items():
        if cnt < 2:
            continue
        same = [l for l in layers if l["archetype_key"] == key]
        arch_name = same[0]["archetype"]
        for i in range(len(same)):
            for j in range(i + 1, len(same)):
                notes.append(
                    note_tpl.format(
                        a=same[i]["label"],
                        b=same[j]["label"],
                        archetype=arch_name,
                    )
                )

    hero = (
        "Your blueprint, expressed as four faces."
        if lang == "en"
        else "당신의 청사진, 네 가지 얼굴."
    )

    return {
        "id": "chart",
        "title": _title(lang, "chart"),
        "hero": hero,
        "layers": layers,
        "notes": notes,
    }



# ============================================================
# SINSAL (C+ Global)
# ============================================================
_SINSAL_POS_LABEL = {
    "en": {"year_pillar": "Origins", "month_pillar": "Career",
           "day_pillar": "Self", "hour_pillar": "Legacy"},
    "ko": {"year_pillar": "뿌리", "month_pillar": "커리어",
           "day_pillar": "본질", "hour_pillar": "유산"},
}

_SINSAL_POS_ROLE = {
    "en": {
        "year_pillar": "ancestry / early environment",
        "month_pillar": "career / public life",
        "day_pillar": "self / partnership",
        "hour_pillar": "inner world / legacy",
    },
    "ko": {
        "year_pillar": "가문과 어린 시절",
        "month_pillar": "직업과 사회 활동",
        "day_pillar": "자신과 친밀한 관계",
        "hour_pillar": "내면과 말년",
    },
}

_SINSAL_THEME_KEYWORD = {
    "MAGNETIC_DRAW": {"en": "magnetism and attraction", "ko": "매력과 인연"},
    "RESTLESS_FEET": {"en": "movement and exploration", "ko": "이동과 탐험"},
    "SOLITARY_DEPTH": {"en": "reflection and creativity", "ko": "성찰과 창조"},
    "ALLY_MAGNET": {"en": "help and support", "ko": "도움과 귀인"},
    "SCHOLAR_MIND": {"en": "study and learning", "ko": "학습과 지식"},
    "SHARP_EDGE": {"en": "drive and competition", "ko": "추진과 경쟁"},
    "COMMANDER": {"en": "leadership and decisiveness", "ko": "결단과 카리스마"},
}

_SINSAL_NOTE_TPL = {
    "en": "This trait sits in your {role} — so {theme} shows up most in that area.",
    "ko": "{role}에 자리해, 그 영역에서 {theme}의 기운이 두드러집니다.",
}

def write_sinsal_section(profile: dict, lang: str = "en") -> dict | None:
    raw = profile.get("special_traits_raw") or {}
    if not raw:
        return None
    try:
        pack = load_pack(lang, "sinsal")
        content_map = pack.get("SINSAL_CONTENT", {})
    except KeyError:
        return None

    code_map = {
        "도화": "MAGNETIC_DRAW", "역마": "RESTLESS_FEET", "화개": "SOLITARY_DEPTH",
        "천을귀인": "ALLY_MAGNET", "문창귀인": "SCHOLAR_MIND",
        "양인": "SHARP_EDGE", "괴강": "COMMANDER",
    }
    pos_labels = _SINSAL_POS_LABEL.get(lang, _SINSAL_POS_LABEL["en"])
    pos_roles = _SINSAL_POS_ROLE.get(lang, _SINSAL_POS_ROLE["en"])
    note_tpl = _SINSAL_NOTE_TPL.get(lang, _SINSAL_NOTE_TPL["en"])

    items = []
    for ko_name, entries in raw.items():
        code = code_map.get(ko_name)
        if not code: continue
        content = content_map.get(code)
        if not content: continue
        theme_kw = _SINSAL_THEME_KEYWORD.get(code, {}).get(lang, "")
        for entry in entries:
            pos = entry.get("position")
            role = pos_roles.get(pos, "")
            items.append({
                "key": code,
                "name": content.get("name", ""),
                "name_traditional": content.get("name_traditional", ""),
                "headline": content["headline"], "body": content["body"],
                "advice": content["advice"],
                "position": pos,
                "position_label": pos_labels.get(pos, pos),
                "position_role": role,
                "position_note": (
                    note_tpl.format(role=role, theme=theme_kw)
                    if role and theme_kw else ""
                ),
            })
    if not items: return None
    if lang == "en":
        word = "trait" if len(items) == 1 else "traits"
        hero = f"You carry {len(items)} special {word}."
    else:
        hero = f"당신에게는 {len(items)}개의 특별한 기질이 있습니다."
    return {
        "id": "sinsal",
        "title": _title(lang, "sinsal"),
        "hero": hero,
        "items": items,
    }


# ============================================================
# AGE BAND (신규 — Step 9-B)
# ============================================================
def write_age_band_section(profile: dict, lang: str = "en") -> dict | None:
    age_band = profile.get("age_band")
    if not age_band:
        return None

    try:
        pack = load_pack(lang, "age_band")
        content_map = pack.get("AGE_BAND_CONTENT", {})
    except KeyError:
        content_map = {}

    band = content_map.get(age_band["key"], {})
    if not band:
        return None

    return {
        "id": "age_band",
        "key": age_band["key"],
        "age": age_band["age"],
        "target_year": age_band["target_year"],
        "label": band.get("label", ""),
        "headline": band.get("headline", ""),
        "body": band.get("body", ""),
        "advice": band.get("advice", []),
    }


# ============================================================
# TIMELINE
# ============================================================
def write_timeline_section(profile: dict, lang: str = "en") -> dict:
    timeline = profile.get("daewoon_timeline", [])

    try:
        pack = load_pack(lang, "sections")
        blurbs = pack.get("TIMELINE_GRADE_BLURB", {})
    except KeyError:
        blurbs = {}

    age_band = profile.get("age_band") or {}
    current_age = age_band.get("age")

    items = []
    for d in timeline:
        start, end = d["ages"]
        is_current = (
            current_age is not None and start <= current_age <= end
        )
        items.append({
            "index": d["index"],
            "ages": [start, end],
            "pillar": d["pillar"],
            "score": d["score"],
            "grade": d["grade"],
            "blurb": blurbs.get(d["grade"], ""),
            "is_current": is_current,
        })

    summary = profile.get("daewoon_summary", {})
    best = summary.get("best")
    worst = summary.get("worst")

    return {
        "id": "timeline",
        "title": _title(lang, "timeline"),
        "hero": _timeline_hero(lang, best, worst),
        "items": items,
    }


def _timeline_hero(lang: str, best: dict | None, worst: dict | None) -> str:
    try:
        pack = load_pack(lang, "sections")
        template = pack.get("TIMELINE_HERO", "")
    except KeyError:
        template = ""

    if not best or not worst or not template:
        return "Your decades, mapped."

    return template.format(
        best_age=best["start_age"],
        best_pillar=best["pillar"],
        worst_age=worst["start_age"],
    )



# ============================================================
# PREMIUM SECTIONS (Love / Career / Wealth)
# ============================================================
def write_premium_section(profile: dict, lang: str, section_name: str) -> dict | None:
    try:
        pack = load_pack(lang, section_name)
    except KeyError:
        return None
        
    arch = profile["archetype"]["key"]
    content_map = pack.get("CONTENT", {})
    content = content_map.get(arch, {"headline": "Premium feature", "body": "Analyze your chart deeply."})
    
    return {
        "id": section_name,
        "title": pack.get("SECTION_TITLE", section_name.title()),
        "mode": arch,
        "headline": content.get("headline", ""),
        "body": content.get("body", ""),
        "action": "꾸준한 기록과 실행이 필요합니다." if lang == "ko" else "Consistent action is required.",
    }

def write_love_section(profile: dict, lang: str = "ko") -> dict:
    return write_premium_section(profile, lang, "love")

def write_career_section(profile: dict, lang: str = "ko") -> dict:
    return write_premium_section(profile, lang, "career")

def write_wealth_section(profile: dict, lang: str = "ko") -> dict:
    return write_premium_section(profile, lang, "wealth")

# ============================================================
# COVER & SUMMARY
# ============================================================
def _build_cover(profile: dict, lang: str) -> dict:
    core = write_core_section(profile, lang)
    return {
        "archetype": core["archetype"],
        "intensity_label": core["intensity_label"],
    }


def _build_summary_cards(profile: dict, lang: str, user_id: str | None = None) -> list:
    pack = load_pack(lang, "sections")
    labels = pack.get("SUMMARY_LABELS", {})
    mode_display = pack.get("MODE_DISPLAY", {})

    try:
        energy_pack = load_pack(lang, "energy")
        element_display = energy_pack.get("ELEMENT_DISPLAY", {})
    except KeyError:
        element_display = {}

    def elem_name(sig: str) -> str:
        return element_display.get(sig, sig)

    def mode_name(mode: str) -> str:
        return mode_display.get(mode, mode.replace("THE_", "").title())

    core = write_core_section(profile, lang)

    cards = [
        {
            "label": labels.get("core", "Core"),
            "headline": core["archetype"]["name"],
            "body": core["archetype"]["tagline"],
        },
    ]

    # Energy
    energy = write_energy_section(profile, lang)
    dom_sigs = profile["energy_signature"].get("dominant", [])
    dom_names = [elem_name(s) for s in dom_sigs]
    energy_headline = " · ".join(dom_names) if dom_names else (
        "균형" if lang == "ko" else "Balanced"
    )
    cards.append({
        "label": labels.get("energy", "Energy"),
        "headline": energy_headline,
        "body": energy["hero"],
    })

    # Money
    money = write_money_section(profile, lang)
    cards.append({
        "label": labels.get("money", "Money Mode"),
        "headline": mode_name(money["mode"]),
        "body": money["headline"],
    })

    # Bonds
    bonds = write_bonds_section(profile, lang)
    cards.append({
        "label": labels.get("bonds", "Bonds"),
        "headline": mode_name(bonds["mode"]),
        "body": bonds["headline"],
    })

    # Year
    year = write_year_section(profile, lang, user_id=user_id)
    if year:
        cards.append({
            "label": labels.get("year", "This Year"),
            "headline": year["name"],
            "body": year["headline"],
        })

    return cards


# ============================================================
# FULL REPORT
# ============================================================
def generate_full_report(profile: dict, lang: str = "en", user_id: str | None = None) -> dict:
    """모든 섹션을 조립한 완성 리포트."""
    sections = {
        "chart": write_chart_section(profile, lang),
        "core": write_core_section(profile, lang),
        "energy": write_energy_section(profile, lang),
        "lucky_code": write_lucky_code_section(profile, lang),
        "health": write_health_section(profile, lang),
        "money": write_money_section(profile, lang),
        "work": write_work_section(profile, lang),
        "bonds": write_bonds_section(profile, lang),
        "love": write_love_section(profile, lang),
        "career": write_career_section(profile, lang),
        "wealth": write_wealth_section(profile, lang),
        "timeline": write_timeline_section(profile, lang),
    }

    year = write_year_section(profile, lang, user_id=user_id)
    if year:
        sections["year"] = year

    monthly = write_monthly_section(profile, lang, user_id=user_id)
    if monthly:
        sections["monthly"] = monthly

    sinsal = write_sinsal_section(profile, lang)
    if sinsal:
        sections["sinsal"] = sinsal

    age_band = write_age_band_section(profile, lang)
    if age_band:
        sections["age_band"] = age_band

    return {
        "meta": {
            "lang": lang,
            "schema_version": "1.2",
            "tier": "preview",
            "locked_sections": [],
            "birth_time_mode": profile.get("birth_time_mode", "exact"),
            "hour_pillar_confidence": profile.get("hour_pillar_confidence", "exact"),
            "calculation_method": "weighted-sum eokbu (simplified), school-dependent",
            "region": profile.get("region"),
            "age_band": profile.get("age_band"),
            "daily_wallpaper_url": get_daily_wallpaper_url(profile),
        },
        "cover": _build_cover(profile, lang),
        "summary_cards": _build_summary_cards(profile, lang, user_id=user_id),
        "sections": sections,
        "disclaimer": _disclaimer(lang),
        "crisis_resources": get_crisis_resources(profile.get("region")),
    }


def _disclaimer(lang: str) -> str:
    try:
        pack = load_pack(lang, "sections")
        return pack.get("DISCLAIMER", "")
    except KeyError:
        return ""


# ============================================================
# HELPERS
# ============================================================
def _title(lang: str, section: str) -> str:
    pack = load_pack(lang, "sections")
    return pack.get("SECTION_TITLES", {}).get(section, section)


def _intensity_label(lang: str, intensity_key: str) -> str:
    try:
        pack = load_pack(lang, "sections")
        labels = pack.get("INTENSITY_LABELS", {})
    except KeyError:
        labels = {}
    return labels.get(intensity_key, intensity_key)