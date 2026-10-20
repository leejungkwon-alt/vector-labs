"""
티어별 섹션 게이팅 — Teaser 방식 (Step 2).

설계 원칙:
  - free 유저가 각 섹션의 "아하 모먼트"를 먼저 경험 → 전환율 향상
  - 모든 섹션은 노출하되, 티저 수준으로 잘라서
  - 잠긴 필드는 `locked_fields`에 표시 → 프론트엔드가 잠금 UI 처리

적용 위치: API 레이어 (report.py).
content_writer.py 는 손대지 않는다.

티어
  preview      : 게이팅 없음 (CLI, 하위호환, 인증 없음)
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
        "keep": {"id", "title", "hero"},
        "include_power_minimal": True,   # power에서 signature/element/keywords만 노출
        "locked_hint": [
            "support", "watch_out",
            "power.colors", "power.numbers", "power.directions",
            "power.activities", "power.foods", "power.practices",
            "power.domains",
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
    # ---- Timeline: 첫 3개 대운 ----
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
}

UNGATED_TIERS = {"subscription", "premium", "unlimited"}

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

def apply_entitlement_gate(report: dict, tier: str) -> dict:
    """
    report 를 제자리에서 게이팅하고 반환.

    - preview/subscription/premium: 그대로. meta.tier 만 갱신.
    - free (그 외 tier 포함): 각 섹션을 티저로 잘라내고 locked_fields 세팅.
    """
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
        rule = FREE_SECTION_RULES.get(sid)

        if rule is None:
            # 규칙 미정의 → 안전하게 통과 (원본 유지)
            gated_sections[sid] = section
            continue

        if rule.get("keep_all"):
            gated_sections[sid] = section
            continue

        teaser, locked_fields = _apply_teaser_rule(section, rule)
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

    return teaser, locked
