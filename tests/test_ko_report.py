# tests/test_ko_report.py
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import generate_full_report


def _ko_report_1974():
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
    return generate_full_report(profile, lang="ko")


def test_ko_meta():
    report = _ko_report_1974()
    assert report["meta"]["lang"] == "ko"
    assert report["meta"]["schema_version"] == "1.2"


def test_ko_cover():
    report = _ko_report_1974()
    cover = report["cover"]
    assert cover["archetype"]["key"] == "THE_RADIATOR"
    assert cover["archetype"]["name"] == "바위 위의 태양"  # 丙申
    assert cover["intensity_label"] == "자기충전형"


def test_ko_core():
    report = _ko_report_1974()
    core = report["sections"]["core"]

    assert core["title"] == "당신의 본질"
    assert core["archetype"]["name"] == "바위 위의 태양"  # 丙申
    assert len(core["narrative"]) >= 3
    assert len(core["advice"]) >= 3

    combined = " ".join(core["narrative"])
    assert any("\uac00" <= ch <= "\ud7a3" for ch in combined), "한글 없음"
    assert core["hero"] != "" and not core["hero"].startswith("You")


def test_ko_summary_labels():
    report = _ko_report_1974()
    labels = [c["label"] for c in report["summary_cards"]]
    assert "본질" in labels
    assert "재물 모드" in labels
    assert "인연" in labels


def test_ko_section_titles():
    report = _ko_report_1974()
    s = report["sections"]
    assert s["core"]["title"] == "당신의 본질"
    assert s["money"]["title"] == "재물과 돈"
    assert s["work"]["title"] == "일과 재능"
    assert s["bonds"]["title"] == "인연과 관계"
    assert s["timeline"]["title"] == "인생의 궤적"
    assert s["year"]["title"] == "올해의 흐름"


def test_ko_disclaimer():
    report = _ko_report_1974()
    assert "안내" in report["disclaimer"]


def test_ko_year_name():
    """연운 name/headline/body의 구조 검증 (특정 문구 의존 X)."""
    report = _ko_report_1974()
    year = report["sections"]["year"]

    assert year["title"] == "올해의 흐름"
    assert year["target_year"] == 2026

    assert isinstance(year["name"], str) and year["name"].strip()
    assert any("\uac00" <= ch <= "\ud7a3" for ch in year["name"]), \
        f"연운 name이 한국어가 아님: {year['name']!r}"
    assert any("\uac00" <= ch <= "\ud7a3" for ch in year["body"]), \
        f"연운 body가 한국어가 아님: {year['body']!r}"


def test_ko_1990_blade_has_content():
    """1990 케이스(庚 일간) → THE_BLADE 한국어 콘텐츠 있음."""
    result = calculate_saju(
        birth_date="1990-05-05",
        birth_time="14:30:00",
        timezone_str="Asia/Seoul",
        longitude=126.9780,
        correction_mode="lmt",
        jasi_boundary=23,
        gender="M",
    )
    profile = build_semantic_profile(result)
    report = generate_full_report(profile, lang="ko")
    core = report["sections"]["core"]

    assert core["archetype"]["key"] == "THE_BLADE"
    assert core["archetype"]["name"] == "제련로의 검"  # 1990 = 庚午
    assert core["hero"] != "아직 채워지지 않은 흐름입니다."
    assert len(core["narrative"]) >= 3


def test_en_report_still_works():
    """영어 리포트 회귀 방지."""
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
    report = generate_full_report(profile, lang="en")

    assert report["cover"]["archetype"]["name"] == "Sun Above Stone"  # 1974 = 丙申
    assert report["cover"]["intensity_label"] == "Self-Sourced"
    assert "Note:" in report["disclaimer"]


# ============================================================
# Step 6-3: 한국어 sections 콘텐츠 검증
# ============================================================
def test_ko_money_content_is_korean():
    report = _ko_report_1974()
    money = report["sections"]["money"]

    assert money["title"] == "재물과 돈"
    assert money["mode"] == "THE_OPERATOR"
    assert any("\uac00" <= ch <= "\ud7a3" for ch in money["headline"])


def test_ko_work_content_is_korean():
    report = _ko_report_1974()
    work = report["sections"]["work"]
    assert work["title"] == "일과 재능"
    assert any("\uac00" <= ch <= "\ud7a3" for ch in work["body"])


def test_ko_bonds_content_is_korean():
    report = _ko_report_1974()
    bonds = report["sections"]["bonds"]
    assert bonds["title"] == "인연과 관계"
    assert any("\uac00" <= ch <= "\ud7a3" for ch in " ".join(bonds["actions"]))


def test_ko_timeline_blurb_is_korean():
    report = _ko_report_1974()
    timeline = report["sections"]["timeline"]
    assert len(timeline["items"]) == 10
    assert any("\uac00" <= ch <= "\ud7a3" for ch in timeline["items"][0]["blurb"])
    assert "세 무렵" in timeline["hero"] or "가장 강한 시기" in timeline["hero"]

    
def test_ko_energy_is_korean():
    report = _ko_report_1974()
    energy = report["sections"]["energy"]
    assert energy["title"] == "당신의 에너지 지도"
    assert "기운" in energy["hero"] or "성장" in energy["hero"] or "흐름" in energy["hero"]
    for block in energy["blocks"]:
        assert any("\uac00" <= ch <= "\ud7a3" for ch in block["body"]), f"블록 한글 없음: {block['signature']}"


def test_ko_lucky_code_is_korean():
    report = _ko_report_1974()
    lc = report["sections"]["lucky_code"]
    assert lc["title"] == "당신에게 필요한 기운"
    # 1974 용신 土 → GROUND
    assert lc["power"]["signature"] == "GROUND"
    assert "대지" in lc["power"]["element"] or "토" in lc["power"]["element"]
    assert any("\uac00" <= ch <= "\ud7a3" for ch in lc["power"]["practices"][0])


def test_ko_year_is_korean():
    """연운 섹션 전체가 한국어인지 (구조 기반 검증)."""
    report = _ko_report_1974()
    year = report["sections"]["year"]

    assert year["title"] == "올해의 흐름"

    for field in ("name", "headline", "body", "watch_for", "lean_into"):
        value = year.get(field, "")
        assert isinstance(value, str) and value.strip(), \
            f"연운 {field}가 비어있음"
        assert any("\uac00" <= ch <= "\ud7a3" for ch in value), \
            f"연운 {field}가 한국어가 아님: {value!r}"

def test_ko_report_has_no_english_in_content_sections():
    """핵심 콘텐츠 섹션은 완전히 한국어여야 함."""
    report = _ko_report_1974()
    s = report["sections"]

    for sid in ("core", "energy", "lucky_code", "money", "work", "bonds", "year"):
        blob = str(s[sid])
        # 한글이 반드시 포함됨
        assert any("\uac00" <= ch <= "\ud7a3" for ch in blob), f"{sid}: 한글 없음"

def test_ko_energy_summary_card_uses_display_name():
    """KO summary_cards의 에너지 헤드라인이 한국어 표시명."""
    report = _ko_report_1974()
    cards = {c["label"]: c for c in report["summary_cards"]}
    energy_card = cards["에너지"]

    assert energy_card["headline"] == "성장"
    assert "GROWTH" not in energy_card["headline"]

def test_ko_summary_card_headlines_are_korean():
    """Summary 카드 헤드라인에 raw 영어 코드가 없어야 함."""
    report = _ko_report_1974()
    for card in report["summary_cards"]:
        h = card["headline"]
        # 영문 대문자 단어 포함 여부 검사
        # 한글(영어) 병기 정책이므로 raw 코드(THE_)만 아니면 통과
        assert "THE_" not in h, f"헤드라인에 raw 영어 코드 노출: {h!r}"
        assert any("\uac00" <= ch <= "\ud7a3" for ch in h), f"한글이 없음: {h!r}"


def test_ko_money_bonds_headlines_are_korean():
    report = _ko_report_1974()
    cards = {c["label"]: c for c in report["summary_cards"]}
    assert cards["재물 모드"]["headline"].startswith("운영자")
    assert cards["인연"]["headline"].startswith("동반자")


def test_ko_lucky_code_hero_is_korean():
    report = _ko_report_1974()
    lc = report["sections"]["lucky_code"]
    # 문구가 바뀌어도 유연하게 대응하도록 수정
    assert "필요한" in lc["hero"]
    assert "기운" in lc["hero"] or "에너지" in lc["hero"]
    assert "Your power element" not in lc["hero"]


def test_ko_lucky_code_watch_out_display_names():
    """watch_out이 raw signature가 아닌 표시명 객체."""
    report = _ko_report_1974()
    lc = report["sections"]["lucky_code"]
    # 1974 기신: [木, 火] → [성장, 불꽃]
    names = [w["name"] for w in lc["watch_out"]]
    sigs = [w["signature"] for w in lc["watch_out"]]
    assert "성장" in names
    assert "불꽃" in names
    assert "GROWTH" in sigs
    assert "SPARK" in sigs    