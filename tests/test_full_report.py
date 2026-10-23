# tests/test_full_report.py
import re
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import generate_full_report


def _report_1974():
    result = calculate_saju(
        birth_date="1974-02-24",
        birth_time="05:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        jasi_boundary=23,
        gender="M",
        target_year=2026,
    )
    profile = build_semantic_profile(result)
    return generate_full_report(profile, lang="en")


def test_full_report_top_shape():
    report = _report_1974()

    assert "meta" in report
    assert "cover" in report
    assert "summary_cards" in report
    assert "sections" in report
    assert "disclaimer" in report

    assert report["meta"]["lang"] == "en"
    assert report["meta"]["schema_version"] == "1.2"


def test_full_report_cover():
    report = _report_1974()
    cover = report["cover"]

    # cover.archetype 안에 모든 정보가 있음
    assert cover["archetype"]["key"] == "THE_RADIATOR"
    assert cover["archetype"]["name"] == "The Radiator"
    assert cover["archetype"]["color"] == "#E85D2F"
    assert cover["archetype"]["symbol"] == "☀"
    assert cover["archetype"]["tagline"] == "You warm rooms by existing in them."
    assert cover["intensity_label"] == "Self-Sourced"

    # 최상위 중복 필드는 제거됨
    assert "color" not in cover
    assert "symbol" not in cover
    assert "tagline" not in cover


def test_full_report_summary_cards():
    report = _report_1974()
    cards = report["summary_cards"]

    # 최소 4개 (year 포함 시 5개)
    assert len(cards) >= 4

    labels = [c["label"] for c in cards]
    assert "Core" in labels
    assert "Money Mode" in labels
    assert "Bonds" in labels


def test_full_report_all_sections_present():
    report = _report_1974()
    sections = report["sections"]

    for sid in ("core", "energy", "lucky_code", "money", "work", "bonds", "timeline", "year"):
        assert sid in sections, f"Missing section: {sid}"


def test_core_section_shape():
    report = _report_1974()
    core = report["sections"]["core"]

    assert core["id"] == "core"
    assert core["title"] == "Your Core"
    assert len(core["narrative"]) >= 3
    assert len(core["advice"]) >= 3


def test_energy_section_shape():
    report = _report_1974()
    energy = report["sections"]["energy"]

    assert energy["id"] == "energy"
    assert "hero" in energy
    assert len(energy["blocks"]) >= 1

    # 1974는 木 dominant, 水 deficient
    roles = {b["role"] for b in energy["blocks"]}
    signatures = {b["signature"] for b in energy["blocks"]}
    assert "dominant" in roles
    assert "GROWTH" in signatures


def test_lucky_code_section_shape():
    report = _report_1974()
    lc = report["sections"]["lucky_code"]

    assert lc["id"] == "lucky_code"
    # 1974 용신 土 → GROUND
    assert lc["power"]["signature"] == "GROUND"
    assert lc["power"]["element"] == "Earth"
    assert len(lc["power"]["colors"]) >= 1
    assert len(lc["power"]["practices"]) >= 3


def test_money_section_shape():
    report = _report_1974()
    money = report["sections"]["money"]
    # 1974 편재 → THE_OPERATOR
    assert money["mode"] == "THE_OPERATOR"
    assert money["headline"]
    assert money["body"]
    assert money["actions"] and all(money["actions"])


def test_work_section_shape():
    report = _report_1974()
    work = report["sections"]["work"]
    # 1974 편인 → THE_MYSTIC
    assert work["mode"] == "THE_MYSTIC"
    assert len(work["body"]) > 0


def test_bonds_section_shape():
    report = _report_1974()
    bonds = report["sections"]["bonds"]
    # 1974 비견 → THE_TWIN
    assert bonds["mode"] == "THE_TWIN"


def test_year_section_shape():
    report = _report_1974()
    year = report["sections"]["year"]

    assert year["id"] == "year"
    assert year["target_year"] == 2026
    assert year["pillar"] == "丙午"
    assert year["ten_god"] == "TEN_GOD_FRIEND"

    # 구조 검증 (콘텐츠가 Gemini 등으로 교체되어도 통과)
    assert isinstance(year["name"], str) and year["name"].strip()
    assert isinstance(year["headline"], str) and year["headline"].strip()
    assert isinstance(year["body"], str) and year["body"].strip()
    assert isinstance(year["watch_for"], str) and year["watch_for"].strip()
    assert isinstance(year["lean_into"], str) and year["lean_into"].strip()

    # 3문장 이상 (Gemini 스펙)
    sentence_count = len([s for s in re.split(r"[.!?]", year["body"]) if s.strip()])
    assert sentence_count >= 3, f"body is too short: {year['body']!r}"

def test_timeline_section_shape():
    report = _report_1974()
    timeline = report["sections"]["timeline"]

    assert timeline["id"] == "timeline"
    assert len(timeline["items"]) == 10

    # 각 항목에 blurb 있어야 함
    for item in timeline["items"]:
        assert item["grade"] in ("PEAK", "FAVORABLE", "NEUTRAL", "CAUTION", "CHALLENGING")
        assert item["blurb"]

    # hero에 best/worst 나이 언급
    assert "age" in timeline["hero"]


def test_year_section_none_without_target():
    result = calculate_saju(
        birth_date="1974-02-24",
        birth_time="05:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        jasi_boundary=23,
        gender="M",
    )
    profile = build_semantic_profile(result)
    report = generate_full_report(profile, lang="en")

    # year 섹션 없어야 함
    assert "year" not in report["sections"]

    # 나머지는 다 있어야 함
    for sid in ("core", "energy", "lucky_code", "money", "work", "bonds", "timeline"):
        assert sid in report["sections"]


def test_no_ai_string_in_report():
    """리포트 어디에도 'ai', 'gemini', 'llm' 문자열이 없어야 함."""
    report = _report_1974()
    import json
    blob = json.dumps(report).lower()
    for banned in ("gemini", "openai", "gpt-", "llm"):
        assert banned not in blob

def test_energy_summary_card_uses_display_name():
    """summary_cards의 Energy 헤드라인이 raw signature가 아닌 표시명."""
    report = _report_1974()
    cards = {c["label"]: c for c in report["summary_cards"]}
    energy_card = cards["Energy"]

    # raw "GROWTH"가 아니라 "Growth"
    assert energy_card["headline"] == "Growth"
    assert "GROWTH" not in energy_card["headline"]

def test_en_lucky_code_hero_template():
    """EN lucky_code hero가 템플릿 기반."""
    report = _report_1974()
    lc = report["sections"]["lucky_code"]
    assert "Your power element is Earth" in lc["hero"]
    assert "lean into it" in lc["hero"]


def test_en_watch_out_display_names():
    """EN watch_out도 {signature, name} 구조."""
    report = _report_1974()
    lc = report["sections"]["lucky_code"]
    names = [w["name"] for w in lc["watch_out"]]
    sigs = [w["signature"] for w in lc["watch_out"]]
    assert "Growth" in names
    assert "Spark" in names
    assert "GROWTH" in sigs


def test_full_report_has_chart_sinsal_monthly_health_age_band():
    """최근 추가된 섹션이 회귀 없이 포함되어야 함."""
    report = _report_1974()
    sections = report["sections"]
    for sid in ("chart", "sinsal", "monthly", "health", "age_band"):
        assert sid in sections, f"Missing: {sid}"


def test_chart_section_has_layers_and_notes():
    """Chart: 4 layers, is_self 1개, notes는 RADIATOR 중복으로 최소 1개."""
    report = _report_1974()
    chart = report["sections"]["chart"]
    assert chart["id"] == "chart"
    assert len(chart["layers"]) == 4
    assert sum(1 for l in chart["layers"] if l["is_self"]) == 1
    assert isinstance(chart["notes"], list)
    # 1974: month/career & day/self 모두 RADIATOR → note 최소 1개
    assert len(chart["notes"]) >= 1
