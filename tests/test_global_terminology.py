# tests/test_global_terminology.py
"""글로벌 카운셀링 용어 회귀 방지."""
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import (
    generate_full_report,
    write_sinsal_section,
)
from app.services.content.loader import load_pack


def _profile_and_report(lang="ko"):
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        birth_location="seoul", correction_mode="lmt",
        jasi_boundary=23, gender="M", target_year=2026,
    )
    profile = build_semantic_profile(result)
    return profile, generate_full_report(profile, lang=lang)


# ---- KO 신살: friendly name 우선, 전통 명칭 별도 ----
def test_ko_sinsal_uses_friendly_names():
    profile, _ = _profile_and_report("ko")
    sec = write_sinsal_section(profile, lang="ko")
    for item in sec["items"]:
        # friendly 이름에 한자 없어야 함
        assert "(" not in item["name"] or "驛" not in item["name"]
        assert not any("\u4e00" <= c <= "\u9fff" for c in item["name"]), \
            f"한자 노출: {item['name']}"
        # 전통 명칭에 한자 있음
        assert item["name_traditional"], "전통 명칭 비어있음"
        assert any("\u4e00" <= c <= "\u9fff" for c in item["name_traditional"])


def test_en_sinsal_has_no_traditional_hanja():
    profile, _ = _profile_and_report("en")
    sec = write_sinsal_section(profile, lang="en")
    for item in sec["items"]:
        assert not item.get("name_traditional"), \
            "EN은 전통 명칭 없어야 함"


# ---- KO 섹션 제목: 영어 대여어 없음 ----
def test_ko_section_titles_no_tech_loanwords():
    _, report = _profile_and_report("ko")
    s = report["sections"]
    assert s["energy"]["title"] == "당신의 에너지 지도"
    assert s["lucky_code"]["title"] == "당신에게 필요한 기운"
    assert s["health"]["title"] == "몸과 마음"
    for title in (s["energy"]["title"], s["lucky_code"]["title"], s["health"]["title"]):
        assert "시그니처" not in title
        assert "코드" not in title
        assert "웰니스" not in title


# ---- 마크다운 별표 leak ----
def test_no_markdown_asterisks_in_monthly_or_year():
    for lang in ("ko", "en"):
        _, report = _profile_and_report(lang)
        sections = report["sections"]
        for sid in ("monthly", "year"):
            if sid not in sections:
                continue
            blob = str(sections[sid])
            assert "*" not in blob.replace("*\n", ""), \
                f"{lang}/{sid}에 '*' 노출"


# ---- Disclaimer: 한자 jargon 제거 ----
def test_ko_disclaimer_no_hanja_jargon():
    _, report = _profile_and_report("ko")
    d = report["disclaimer"]
    for term in ("억부", "조후", "삼합", "신강약", "격국"):
        assert term not in d, f"jargon 잔존: {term}"
    assert "유파" in d


def test_en_disclaimer_no_romanized_jargon():
    _, report = _profile_and_report("en")
    d = report["disclaimer"].lower()
    for term in ("yongsin", "gyeokguk", "sinsal"):
        assert term not in d, f"로마자 jargon 잔존: {term}"


# ---- position_role 순한국어 ----
def test_ko_position_role_is_plain_korean():
    # Phase 1 이후: 상수는 data/{lang}/labels.json 으로 이관됨
    from app.services.content.loader import load_labels
    ko = load_labels("ko")["SINSAL_POS_ROLE"]
    for role in ko.values():
        assert "궁" not in role, f"'궁' 잔존: {role}"
