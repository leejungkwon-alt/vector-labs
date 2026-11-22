"""
티어별 섹션 게이팅 — Teaser 방식 (Step 2).

설계 원칙:
  - free 유저가 각 섹션의 "아하 모먼트"를 먼저 경험 → 전환율 향상
  - 모든 섹션은 노출하되, 티저 수준으로 잘라서
  - 잠긴 필드는 `locked_fields`에 표시 → 프론트엔드가 잠금 UI 처리

적용 위치: API 레이어 (report.py).
content_writer.py 는 손대지 않는다.

**fail-closed (2026-11)**
  규칙이 정의되지 않은 섹션은 "규칙 미정의 → 통과"가 아니라 **유료 취급**한다.
  게이트 규칙을 깜빡한 새 섹션이 무료로 새는 것을 막기 위함이다.
  - 무료로 열어야 하는 섹션은 `FREE_SECTION_RULES` 에 명시적 `keep_all: True` 규칙을 둔다.
  - 조립 가능한 모든 섹션은 규칙을 가져야 한다(`tests/test_entitlement_coverage.py`).
  - 새 섹션 팩은 `i18n_rule` 키로 섹션 id 를 신고해 커버리지 테스트에 잡히게 한다.

티어
  preview      : Step 4-A 이전 ungated. 현재는 free와 동일하게 게이팅 대상.
  free         : 모든 섹션 티저만 공개 + locked_fields 세팅
  subscription : 전체
  premium      : 전체 (AI Q&A 는 별도 크레딧)
"""

# ============================================================
# 섹션별 티저 규칙
# ============================================================
# keep_all         : True → 완전 무료 (차트, age_band)
# keep             : 이 필드들은 그대로 유지
# truncate         : 리스트 필드를 N개로 자르기 (nested "power.colors" 미지원, 명시 keep로 대체)
# paragraphs       : 문자열 필드의 첫 N문단만 유지 ("\n\n" 구분)
# item_keep_fields : items 리스트의 각 항목에서 유지할 필드 (None이면 전부)
# locked_hint      : 프론트엔드에 "잠김"으로 표시할 필드 라벨
#
# 안전 원칙: keep에 없는 필드는 teaser에 포함되지 않음.

FREE_SECTION_RULES = {
    # ---- 완전 무료 (후킹용) ----
    "chart": {"keep_all": True},
    "age_band": {"keep_all": True},

    # ---- Core: 첫 문단만 강조, 나머지 잠금 ----
    "core": {
        "keep": {"id", "title", "archetype", "intensity_label", "hero"},
        "truncate": {"narrative": 1, "shadows": 1, "advice": 1},
        "locked_hint": [
            "narrative", "shadows", "advice",
            "keywords", "personalized_insights",
        ],
    },

    # ---- Energy: dominant 블록 1개 ----
    "energy": {
        "keep": {"id", "title", "hero", "percentages", "raw_dominant", "raw_missing"},
        "truncate": {"blocks": 1},
        "locked_hint": ["blocks"],
    },

    # ---- Lucky Code: power 최소 필드만 ----
    "lucky_code": {
        "keep": {"id", "title", "hero", "poem"},
        "include_power_minimal": True,   # power에서 signature/element/keywords만 노출
        "poem_gate": {
            "locked_fields": {"wallpaper_image"},
        },
        "locked_hint": [
            "support", "watch_out",
            "power.colors", "power.numbers", "power.directions",
            "power.activities", "power.foods", "power.practices",
            "power.domains",
            "poem.wallpaper_image", "poem.collection",
        ],
    },

    # ---- Health: dominant 블록 1개 + practices 1개 ----
    "health": {
        "keep": {"id", "title", "hero", "disclaimer", "framework_note"},
        "truncate": {"blocks": 1, "practices": 1},
        "locked_hint": ["blocks", "practices"],
    },

    # ---- Money / Work / Bonds: body 첫 문단만 ----
    "money": {
        "keep": {"id", "title", "mode", "headline"},
        "paragraphs": {"body": 1},
        "locked_hint": ["body", "action"],
    },
    "work": {
        "keep": {"id", "title", "mode", "headline"},
        "paragraphs": {"body": 1},
        "locked_hint": ["body", "action"],
    },
    "bonds": {
        "keep": {"id", "title", "mode", "headline"},
        "paragraphs": {"body": 1},
        "locked_hint": ["body", "action"],
    },

    "love": {
        "keep": {"id", "title", "mode", "headline"},
        "locked_hint": ["body", "patterns", "compatibility", "actions", "red_flags"],
    },
    "career": {
        "keep": {"id", "title", "mode", "headline"},
        "locked_hint": ["body", "patterns", "compatibility", "actions", "red_flags"],
    },
    "wealth": {
        "keep": {"id", "title", "mode", "headline"},
        "locked_hint": ["body", "patterns", "compatibility", "actions", "red_flags"],
    },
    # ---- 하위 모듈 규칙 (팩의 `i18n_rule` 신고와 1:1) ----
    # 문구 팩이지만 "어디에 붙는지"를 명시해 두면, 교차 인사이트/타이밍을
    # 섹션으로 승격할 때 fail-closed 기본값에 걸리지 않고 의도대로 잠긴다.
    "cross_insight": {
        "keep": {"id", "title", "mode"},
        "locked_hint": ["intro", "angles", "tension_text", "closing", "disclaimer"],
    },
    # ---- Timeline: 첫 3개 인생의 큰 흐름 ----
    "timeline": {
        "keep": {"id", "title", "hero"},
        "truncate": {"items": 3},
        "locked_hint": ["items"],
    },

    # ---- Year: 헤드라인 + watch_for만 ----
    "year": {
        "keep": {
            "id", "title", "target_year", "pillar", "ten_god",
            "name", "headline", "watch_for",
            "solar_calendar_note",
        },
        "locked_hint": ["body", "lean_into", "life_stage_context"],
    },

    # ---- Monthly: 첫 2개월 + 헤드라인만 ----
    "monthly": {
        "keep": {"id", "title", "hero", "target_year"},
        "truncate": {"items": 2},
        "item_keep_fields": {
            "month_index", "pillar", "approx_solar_month",
            "grade", "grade_label", "name", "headline",
        },
        "locked_hint": ["items"],
    },

    # ---- Sinsal: 첫 1개 ----
    "sinsal": {
        "keep": {"id", "title", "hero"},
        "truncate": {"items": 1},
        "item_keep_fields": {
            "key", "name", "name_traditional", "headline",
            "position", "position_label",
        },
        "locked_hint": ["items"],
    },

    # ---- 사주×MBTI 대조: 요약/카드 무료, 상세 슬롯은 프리미엄 ----
    # 사용자가 직접 입력한 MBTI 와 사주 결의 '대조'만 다룬다(유형 추정 없음).
    # 무료: 제목·입력값·고지·결 라벨·한 줄 요약·일간 오버레이 (카드 1장 분량)
    # 잠금: slot 본문(detail_slots)
    "mbti_contrast": {
        "keep": {
            "id", "title", "mbti", "mbti_style_note", "disclaimer",
            "label", "label_title", "summary", "day_stem_overlay",
            "hour_signals_excluded", "hourly_notice",
            "link_key", "link_headline",
        },
        "locked_hint": ["detail_slots", "link_body"],
    },
}

# P0-3: extend free locked_hint with premium blocks (upsell)
_P0_3_LOCKED_EXTRA = {
    "love":   ("cross_insight", "timing"),
    "career": ("cross_insight", "timing"),
    "wealth": ("cross_insight", "timing"),
}
for _sid, _extras in _P0_3_LOCKED_EXTRA.items():
    _rule = FREE_SECTION_RULES.get(_sid)
    if not _rule:
        continue
    _hint = _rule.setdefault("locked_hint", [])
    for _f in _extras:
        if _f not in _hint:
            _hint.append(_f)

UNGATED_TIERS = {"subscription", "premium", "unlimited"}


# ============================================================
# fail-closed 기본 규칙 (규칙 미정의 섹션용)
# ============================================================
# 규칙이 없는 섹션은 **유료로 가정**한다. 본문/데이터 필드는 전부 숨기고
# 제목 등 최소 식별 정보만 남겨 프론트가 "잠김" 카드로 그릴 수 있게 한다.
FAIL_CLOSED_RULE = {
    "keep": {"id", "title"},
    "locked_hint": ["content"],
}


def is_section_rule_defined(sid: str) -> bool:
    """섹션 id 에 명시적 게이트 규칙이 있는지.

    커버리지 테스트와 fail-closed 판정에서 공용으로 사용한다.
    (애드온 기반 예외는 2026-11 정리로 제거 — 1회권은 크레딧 모델로 단일화)
    """
    rule = FREE_SECTION_RULES.get(sid)
    return rule is not None and bool(rule)


def default_free_rule(sid: str) -> dict:
    """무료 티어에서 적용할 규칙. 미정의 섹션은 fail-closed 기본 규칙."""
    return FREE_SECTION_RULES.get(sid) or FAIL_CLOSED_RULE


# ============================================================
# Summary Cards 게이팅 (Step 4-A)
# ============================================================
# 무료 티어에서는 summary_cards 중 앞의 두 개(core, energy)만 전체 노출.
# 나머지는 headline(티저)만 유지하고 body는 잠금.
FREE_SUMMARY_CARD_INDICES = {0, 1}


def _gate_summary_cards(cards, tier):
    if not isinstance(cards, list):
        return cards
    if tier in UNGATED_TIERS:
        return cards
    gated = []
    for i, card in enumerate(cards):
        if not isinstance(card, dict):
            gated.append(card)
            continue
        if i in FREE_SUMMARY_CARD_INDICES:
            gated.append(card)
        else:
            gated.append({
                "label": card.get("label", ""),
                "headline": card.get("headline", ""),  # 티저: headline 유지
                "body": "",                              # 본문 잠금
                "locked": True,
            })
    return gated




# ============================================================
# Public API
# ============================================================

def apply_entitlement_gate(report: dict, tier: str, addons: list[str] = None) -> dict:
    """
    report 를 제자리에서 게이팅하고 반환.

    - preview/subscription/premium: 그대로. meta.tier 만 갱신.
    - free (그 외 tier 포함): 각 섹션을 티저로 잘라내고 locked_fields 세팅.
    """
    addons = addons or []
    meta = report.setdefault("meta", {})
    meta["tier"] = tier

    if tier in UNGATED_TIERS:
        meta["locked_sections"] = []
        return report

    # Step 4-A: summary_cards 게이팅
    if "summary_cards" in report:
        report["summary_cards"] = _gate_summary_cards(report["summary_cards"], tier)

    sections = report.get("sections", {})
    gated_sections = {}
    locked_section_ids = []

    for sid, section in sections.items():
        # (제거) 과거 `deep_report` 애드온 분기 — 지급 경로가 없어 도달 불가였고,
        # 1회권은 크레딧(report.py 의 tier 승격)으로 단일화되었다.
        # 다른 애드온(예: compatibility)은 이 함수와 무관한 경로에서 판정한다.

        # fail-closed: 규칙이 없으면 통과시키지 않고 FAIL_CLOSED_RULE 로 잠근다.
        rule = default_free_rule(sid)
        unknown_section = sid not in FREE_SECTION_RULES

        if rule.get("keep_all"):
            gated_sections[sid] = section
            continue

        teaser, locked_fields = _apply_teaser_rule(section, rule)
        if unknown_section and "content" not in locked_fields:
            locked_fields = list(locked_fields) + ["content"]
        if locked_fields:
            teaser["locked_fields"] = locked_fields
            locked_section_ids.append(sid)
        gated_sections[sid] = teaser

    report["sections"] = gated_sections
    meta["locked_sections"] = locked_section_ids
    return report


# ============================================================
# 내부: teaser 적용
# ============================================================

def _apply_teaser_rule(section: dict, rule: dict) -> tuple:
    teaser = {}
    locked = list(rule.get("locked_hint", []))

    # 1) keep 필드 유지
    for k in rule.get("keep", ()):
        if k in section:
            teaser[k] = section[k]

    # 2) lucky_code 전용: power 최소 필드만
    if rule.get("include_power_minimal") and "power" in section:
        p = section["power"] or {}
        teaser["power"] = {
            "signature": p.get("signature", ""),
            "element": p.get("element", ""),
            "keywords": p.get("keywords", []),
        }

    # 3) truncate: 리스트 필드 자르기
    for field, count in rule.get("truncate", {}).items():
        if field in section and isinstance(section[field], list):
            full = section[field]
            teaser[field] = full[:count]
            if len(full) > count and field not in locked:
                locked.append(field)

    # 4) paragraphs: 문자열 필드의 첫 N문단만 유지
    for field, count in rule.get("paragraphs", {}).items():
        if field in section and isinstance(section[field], str):
            body = section[field]
            paras = [p.strip() for p in body.split("\n\n") if p.strip()]
            teaser[field] = "\n\n".join(paras[:count])
            if len(paras) > count and field not in locked:
                locked.append(field)

    # 5) item_keep_fields: items 각 항목에서 유지할 필드만
    item_keep = rule.get("item_keep_fields")
    if item_keep and "items" in teaser and isinstance(teaser["items"], list):
        item_keep = set(item_keep)
        teaser["items"] = [
            {k: v for k, v in it.items() if k in item_keep}
            for it in teaser["items"]
        ]


    # 6) poem 게이팅 (free: wallpaper/collection 잠금)
    if "poem_gate" in rule and isinstance(teaser.get("poem"), dict):
        locked_poem = rule["poem_gate"]["locked_fields"]
        teaser["poem"] = {
            k: (None if k in locked_poem else v)
            for k, v in teaser["poem"].items()
        }
        teaser["poem"]["locked_fields"] = sorted(locked_poem)

    return teaser, locked
