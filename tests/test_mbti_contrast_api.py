"""골든 케이스 + API 계약 + i18n 키 테스트 (사주×MBTI 대조).

⚠️ 골든 라벨은 **현재 규칙이 낸 값을 그대로 기록**한 것이다.
   기대값에 맞추려고 규칙/가중치를 조정하지 않았다. 규칙을 의도적으로 바꾸면
   이 테스트가 깨지는 것이 정상이며, 그때는 라벨을 다시 기록한다.

⚠️ 이 기능은 MBTI **유형을 추정하지 않는다**. 사용자가 입력한 값과 사주 결을
   대조해 outward|inward|balanced 중 하나만 낸다.
"""
import json
import pathlib
import re

import pytest
from fastapi.testclient import TestClient

from app.engine.calculator import calculate_saju
from app.main import app
from app.semantic.contrast import assess_contrast
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import generate_full_report, write_mbti_contrast_section

client = TestClient(app)

DATA_DIR = pathlib.Path(__file__).parent.parent / "app" / "services" / "content" / "data"
LANGS = ["ko", "en", "ja", "zh_cn", "es"]
PACK_KEYS = [
    "i18n_rule", "DISCLAIMER", "HOURLY_NOTICE", "MBTI_STYLE_NOTE",
    "AXIS_MODULES", "LINK", "DAY_STEM_OVERLAY", "SLOTS", "TITLE",
]
LABELS = {"outward", "inward", "balanced"}
LINK_KEYS = {"match", "contrast", "balanced"}


def _flagship_profile():
    """본인 프로필(검증용 기준 케이스)."""
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        timezone_str="Asia/Seoul", longitude=126.9780,
        correction_mode="lmt", jasi_boundary=23, gender="M", target_year=2026,
    )
    return build_semantic_profile(result)


# ============================================================
# 1) 골든 케이스 — 현재 규칙이 낸 라벨을 기록
# ============================================================

def test_golden_flagship_self_profile():
    """본인 프로필: 규칙이 낸 라벨을 그대로 기록한다(조작 금지)."""
    verdict = assess_contrast(_flagship_profile())
    assert verdict["label"] == "outward"
    assert verdict["out_score"] == 10
    assert verdict["in_score"] == 2
    assert verdict["out_share"] == 0.833
    assert verdict["hour_signals_excluded"] is False


def test_golden_flagship_with_intp_is_contrast():
    """본인 프로필 + INTP: 라벨은 outward, 입력이 I(내향)라 링크는 contrast."""
    section = write_mbti_contrast_section(_flagship_profile(), "ko", mbti="INTP")
    assert section["label"] == "outward"
    assert section["link_key"] == "contrast"
    # 서사가 '틀렸다'고 판정하지 않아야 한다.
    # 전문용어 없이, '둘 다 맞을 수 있어요' 톤으로 풀어 쓴다.
    body = section["link_body"]
    for jargon in ("층위", "원국", "결", "기운"):
        assert jargon not in body, f"전문용어 노출: {jargon}"
    assert "둘 다 맞을 수 있어요" in body


def test_golden_flagship_with_entp_is_match():
    section = write_mbti_contrast_section(_flagship_profile(), "ko", mbti="ENTP")
    assert section["label"] == "outward"
    assert section["link_key"] == "match"


def test_invalid_or_missing_mbti_yields_no_section():
    assert write_mbti_contrast_section(_flagship_profile(), "ko", mbti=None) is None
    assert write_mbti_contrast_section(_flagship_profile(), "ko", mbti="") is None


# ============================================================
# 2) API 계약 — mbti 없으면 섹션 생략, 있으면 3값 라벨만
# ============================================================

BASE_PAYLOAD = {
    "birth_date": "1974-02-24",
    "birth_time": "05:30:00",
    "timezone_str": "Asia/Seoul",
    "longitude": 126.9780,
    "correction_mode": "lmt",
    "jasi_boundary": 23,
    "gender": "M",
    "target_year": 2026,
    "lang": "ko",
}


def test_api_omits_section_when_mbti_is_null():
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    assert resp.status_code == 200
    assert "mbti_contrast" not in resp.json()["report"]["sections"]


def test_api_includes_section_when_mbti_present():
    resp = client.post("/api/v1/saju/report", json={**BASE_PAYLOAD, "mbti": "intp"})
    assert resp.status_code == 200
    section = resp.json()["report"]["sections"]["mbti_contrast"]
    assert section["label"] in LABELS
    assert section["link_key"] in LINK_KEYS
    assert section["mbti"] == "INTP"          # 정규화(대문자)
    assert section["mbti_style_note"]         # 'MBTI 스타일 성향' 고지
    assert section["disclaimer"]              # '재미로 보는 대조' 고지


def test_api_free_tier_locks_detail_slots():
    resp = client.post("/api/v1/saju/report", json={**BASE_PAYLOAD, "mbti": "INTP"})
    section = resp.json()["report"]["sections"]["mbti_contrast"]
    # 요약/카드는 무료, 상세 슬롯은 잠금
    assert "summary" in section
    assert "detail_slots" not in section
    assert "detail_slots" in section["locked_fields"]


def test_api_rejects_malformed_mbti():
    resp = client.post("/api/v1/saju/report", json={**BASE_PAYLOAD, "mbti": "XXXX"})
    assert resp.status_code == 422


def test_full_report_never_emits_generated_mbti_types():
    """입력값 echo 외에 4글자 MBTI 유형을 새로 만들어 넣지 않는다."""
    report = generate_full_report(_flagship_profile(), lang="ko", mbti="INTP")
    section = report["sections"]["mbti_contrast"]
    assert section["mbti"] == "INTP"  # 입력값 그대로
    assert section["label"] in LABELS
    dumped = json.dumps(report, ensure_ascii=False).replace('"INTP"', "")
    assert not re.search(r"\b[EI][NS][TF][JP]\b", dumped), "입력값 외에 MBTI 유형 문자열이 생성됨"


# ============================================================
# 3) i18n 키 — 5개 언어 팩 구조 일치 + 3값 링크 키 완비
# ============================================================

def _pack(lang):
    return json.loads((DATA_DIR / lang / "mbti_contrast.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("lang", LANGS)
def test_pack_has_all_keys(lang):
    pack = _pack(lang)
    for key in PACK_KEYS:
        assert key in pack, f"[{lang}] 키 누락: {key}"


@pytest.mark.parametrize("lang", LANGS)
def test_pack_labels_and_links_complete(lang):
    pack = _pack(lang)
    assert set(pack["AXIS_MODULES"].keys()) == LABELS
    assert set(pack["LINK"].keys()) == LINK_KEYS
    assert set(pack["SLOTS"].keys()) == {"layer", "environment", "hidden", "complement"}
    for axis in pack["AXIS_MODULES"].values():
        assert axis["label"] and axis["body"]
    for link in pack["LINK"].values():
        assert link["headline"] and link["body"]


@pytest.mark.parametrize("lang", LANGS)
def test_pack_declares_entitlement_rule(lang):
    from app.services.entitlements import is_section_rule_defined
    assert is_section_rule_defined(_pack(lang)["i18n_rule"])


def test_pack_never_asserts_right_or_wrong():
    """문구가 '맞다/틀리다' 판정을 하지 않아야 한다."""
    for lang in LANGS:
        body = json.dumps(_pack(lang), ensure_ascii=False)
        for banned in ("틀렸", "틀립니다", "맞습니다", "정확합니다", "you are wrong"):
            assert banned not in body, f"[{lang}] 단정 문구 발견: {banned}"

