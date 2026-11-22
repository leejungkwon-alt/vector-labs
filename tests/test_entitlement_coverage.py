"""entitlement 규칙 커버리지 + fail-closed 가드.

배경
- 이전 `apply_entitlement_gate` 는 `FREE_SECTION_RULES` 에 없는 섹션을
  "규칙 미정의 → 안전하게 통과" 로 처리했다(fail-open). 즉 새 섹션을 만들고
  게이트 규칙을 깜빡하면 **유료 콘텐츠가 무료로 노출**됐다.
- 이제는 미정의 섹션을 유료 취급(fail-closed)한다.
- 따라서 "조립 가능한 모든 섹션은 규칙을 가진다" 를 테스트로 고정한다.

전제: conftest.py 가 SAJU_ENV=development 로 고정하므로 wallpaper URL 이 mock CDN 으로 대체된다.
"""
import json
import pathlib

import pytest

from app.services.content_writer import generate_full_report
from app.services.entitlements import (
    apply_entitlement_gate,
    is_section_rule_defined,
)
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

BASE_PAYLOAD = {
    "birth_date": "1974-02-24",
    "birth_time": "05:30:00",
    "timezone_str": "Asia/Seoul",
    "longitude": 126.9780,
    "correction_mode": "lmt",
    "jasi_boundary": 23,
    "gender": "M",
    "target_year": 2026,
    "lang": "en",
}


@pytest.fixture
def fresh_auth(tmp_path, monkeypatch):
    """테스트마다 새 SQLite DB (SAJU_AUTH_DB_PATH 격리)."""
    monkeypatch.setenv("SAJU_AUTH_DB_PATH", str(tmp_path / "auth.db"))
    from app.auth.repository import reset_repository
    reset_repository()
    yield
    reset_repository()


def _h(token):
    return {"Authorization": f"Bearer {token}"}


DATA_DIR = pathlib.Path(__file__).parent.parent / "app" / "services" / "content" / "data"
LANGS = ["ko", "en"]

# content_writer.generate_full_report 가 조립하는 섹션 id
BUILT_SECTIONS = [
    "chart", "core", "energy", "lucky_code", "health",
    "money", "work", "bonds", "love", "career", "wealth",
    "timeline", "year", "monthly", "sinsal", "age_band",
]


def _report(lang="en", target_year=2026):
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        timezone_str="Asia/Seoul", longitude=126.9780,
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=target_year,
    )
    profile = build_semantic_profile(result)
    return generate_full_report(profile, lang=lang)


# ============================================================
# 1) 규칙 커버리지 — 조립 섹션 전부 규칙 보유
# ============================================================

@pytest.mark.parametrize("sid", BUILT_SECTIONS)
def test_every_built_section_has_entitlement_rule(sid):
    assert is_section_rule_defined(sid), f"[{sid}] FREE_SECTION_RULES 규칙 누락"


@pytest.mark.parametrize("lang", LANGS)
def test_report_sections_all_have_rules(lang):
    """실제 조립 결과에 등장하는 섹션은 모두 규칙이 있어야 한다."""
    report = _report(lang=lang)
    missing = [sid for sid in report["sections"] if not is_section_rule_defined(sid)]
    assert missing == [], f"규칙 누락 섹션: {missing}"


# ============================================================
# 2) fail-closed — 미정의 섹션은 유료 취급(엔진이 만들어도 잠금)
# ============================================================

def test_unknown_section_is_locked_for_free():
    report = _report()
    report["sections"]["brand_new_section"] = {
        "id": "brand_new_section",
        "title": "New",
        "body": "premium body",
        "secret": ["a", "b"],
    }
    out = apply_entitlement_gate(report, "free")

    section = out["sections"]["brand_new_section"]
    # 유료 필드는 남지 않는다
    assert "body" not in section
    assert "secret" not in section
    # 잠금 표시 + locked_sections 등록
    assert section.get("locked_fields")
    assert "brand_new_section" in out["meta"]["locked_sections"]
    # 티저 최소 정보(제목)는 유지 — 프론트가 "잠김" 카드로 그릴 수 있게
    assert section["id"] == "brand_new_section"
    assert section["title"] == "New"


def test_fail_closed_does_not_leak_engine_dict_fields():
    """엔진 dict 를 미정의 섹션으로 넣어도 원본 dict 가 그대로 노출되지 않는다."""
    report = _report()
    engine_block = {"id": "engine_block", "title": "Engine", "charts": [1, 2, 3], "text": "x"}
    report["sections"]["engine_block"] = dict(engine_block)
    out = apply_entitlement_gate(report, "free")
    assert out["sections"]["engine_block"] != engine_block
    assert "charts" not in out["sections"]["engine_block"]
    assert "text" not in out["sections"]["engine_block"]


@pytest.mark.parametrize("tier", ["free", "preview", "vip_unknown"])
def test_fail_closed_applies_to_every_gated_tier(tier):
    report = _report()
    report["sections"]["brand_new_section"] = {"id": "brand_new_section", "title": "New", "body": "b"}
    out = apply_entitlement_gate(report, tier)
    assert "body" not in out["sections"]["brand_new_section"]
    assert "brand_new_section" in out["meta"]["locked_sections"]


@pytest.mark.parametrize("tier", ["subscription", "premium", "unlimited"])
def test_ungated_tiers_keep_unknown_section(tier):
    report = _report()
    report["sections"]["brand_new_section"] = {"id": "brand_new_section", "title": "New", "body": "b"}
    out = apply_entitlement_gate(report, tier)
    assert out["sections"]["brand_new_section"]["body"] == "b"
    assert out["meta"]["locked_sections"] == []


def test_addon_still_unlocks_deep_report_sections():
    """회귀 방지: deep_report 애드온 예외는 fail-closed 전환 후에도 동작해야 한다."""
    report = _report()
    out = apply_entitlement_gate(report, "free", addons=["deep_report"])
    for sid in ("love", "career", "wealth"):
        assert "body" in out["sections"][sid]
        assert sid not in out["meta"]["locked_sections"]


# ============================================================
# 3) 콘텐츠 팩 → entitlement 규칙 바인딩
#    팩이 `i18n_rule` 로 신고한 섹션 id 는 반드시 규칙이 등록돼 있어야 한다.
#    (새 섹션 팩을 추가하면서 규칙을 빼먹으면 여기서 깨진다)
# ============================================================

_RULE_DECLARING_FILES = [
    "sections", "labels", "energy", "core", "lucky_code", "health",
    "love", "career", "wealth", "year", "monthly", "sinsal", "age_band",
    "personalization", "cross_insight", "premium_insights",
    "mbti_contrast",  # 3단계에서 추가 예정 (파일이 없으면 skip)
]


def _declared_i18n_rule(section_file: str, lang: str):
    p = DATA_DIR / lang / f"{section_file}.json"
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    rule = data.get("i18n_rule") if isinstance(data, dict) else None
    return rule if isinstance(rule, str) and rule else None


@pytest.mark.parametrize("name", _RULE_DECLARING_FILES)
def test_content_pack_i18n_rule_is_registered(name):
    rules = {r for r in (_declared_i18n_rule(name, lang) for lang in LANGS) if r}
    unregistered = sorted(r for r in rules if not is_section_rule_defined(r))
    assert unregistered == [], f"[{name}.json] 미등록 i18n_rule: {unregistered}"


# ============================================================
# 3-2) 콘텐츠 팩 구조 검사
#    data/{lang}/<x>.json 중 "섹션 팩" 구조(키가 전부 대문자 모듈 dict)인데
#    `i18n_rule` 신고가 없는 파일을 감지한다. 새 섹션을 만들고 규칙/신고를
#    빼먹으면 여기서 실패한다. (라벨·문구 전용 평면 팩은 대상 아님)
# ============================================================
# 섹션 팩이 아님이 명확한 파일(리포트 섹션 아님): 스타일/문구/설정 팩
_NON_SECTION_PACKS = {
    "sections", "labels", "errors", "telegram", "free_gating",
}

# 섹션 팩이지만 규칙 신고를 하지 않는 기존 예외(평면 구조라 위 판별에 안 걸림)
_KNOWN_SECTION_PACKS_WITHOUT_RULE = {
    # 리포트에 아직 조립되지 않는 프리미엄 문구 팩. 3단계(MBTI 대조)에서
    # 규칙 신고와 함께 처리한다 — 그때 이 목록에서 제거할 것.
    "premium_insights",
}


def _looks_like_section_pack(data) -> bool:
    """키가 전부 대문자/숫자/언더스코어 모듈 이름이고, 값이 dict 인 구조."""
    if not isinstance(data, dict) or not data:
        return False
    module_keys = 0
    for k, v in data.items():
        if not isinstance(k, str) or k.isupper() is False:
            return False
        if not isinstance(v, dict):
            return False
        module_keys += 1
    return module_keys >= 1


def test_section_shaped_packs_declare_i18n_rule():
    problems = []
    for lang in LANGS:
        for p in sorted((DATA_DIR / lang).glob("*.json")):
            stem = p.stem
            if stem in _NON_SECTION_PACKS or stem in _KNOWN_SECTION_PACKS_WITHOUT_RULE:
                continue
            data = json.loads(p.read_text(encoding="utf-8"))
            if not _looks_like_section_pack(data):
                continue
            if not data.get("i18n_rule"):
                problems.append(f"{lang}/{p.name}")
    assert problems == [], f"섹션 구조 팩인데 i18n_rule 미선언: {problems}"


# ============================================================
# 4) 1단계 조사 항목 고정 (동작 변경 아님)
#    - `grant_addon` 호출부가 없다 → deep_report 애드온은 어떤 결제로도 지급되지 않는다.
#    - `POST /auth/me/purchase` 는 구매 *내역 조회*일 뿐, 권한을 부여하지 않는다.
#    아래 테스트는 "지금의 위험한 상태"를 문서화한다. 지급 경로를 만들면 갱신할 것.
# ============================================================

def test_no_code_path_grants_deep_report_addon():
    """결제 3채널 + 인증 라우터 어디에도 grant_addon 호출이 없어야 (현재) 참.

    지급 경로를 실제로 붙이면 이 테스트는 실패한다 —
    그때는 deep_report 해제 E2E 테스트로 교체해야 한다 (의도된 알람).
    """
    root = pathlib.Path(__file__).parent.parent
    callers = []
    for p in list((root / "app").rglob("*.py")) + list((root / "api").rglob("*.py")):
        text = p.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if ".grant_addon(" in stripped and not stripped.startswith("def "):
                callers.append(f"{p.relative_to(root)}:{i}")
    assert callers == [], (
        "grant_addon 호출부가 생겼다. deep_report 지급 E2E 테스트로 교체할 것: "
        + ", ".join(callers)
    )


def test_purchase_endpoint_does_not_grant_entitlement(fresh_auth):
    """POST /auth/me/purchase 는 구매 내역 조회이며 티어/크레딧/애드온을 바꾸지 않는다."""
    from app.auth.repository import get_repository

    a = client.post("/api/v1/auth/anonymous").json()
    uid, token = a["user"]["id"], a["access_token"]
    before = get_repository().get_user(uid)

    resp = client.post("/api/v1/auth/me/purchase", headers=_h(token))
    assert resp.status_code == 200

    after = get_repository().get_user(uid)
    assert after["tier"] == before["tier"] == "free"
    assert (after.get("onetime_credits") or 0) == (before.get("onetime_credits") or 0)
    assert get_repository().list_addons(uid) == []
    assert get_repository().list_purchases(uid) == []


# ============================================================
# 5) API 레벨 fail-closed 확인 — 실제 응답에서 유료 필드가 새지 않는지
# ============================================================

def test_api_free_response_has_no_ungated_section(fresh_auth):
    resp = client.post("/api/v1/saju/report", json={**BASE_PAYLOAD})
    assert resp.status_code == 200
    report = resp.json()["report"]
    served = set(report["sections"].keys())
    ungated = {sid for sid in served if not is_section_rule_defined(sid)}
    assert ungated == set(), f"응답에 규칙 미정의 섹션이 포함됨: {ungated}"


# ============================================================
# 6) 팩 전체 스캔 — i18n_rule 을 선언했으면 규칙이 등록돼 있어야 한다
# ============================================================

def test_data_pack_declared_rules_are_all_registered():
    """data/ 팩 전체 스캔 — i18n_rule 을 선언한 팩은 전부 등록돼 있어야 한다."""
    problems = []
    for lang in LANGS:
        for p in sorted((DATA_DIR / lang).glob("*.json")):
            data = json.loads(p.read_text(encoding="utf-8"))
            rule = data.get("i18n_rule") if isinstance(data, dict) else None
            if isinstance(rule, str) and rule and not is_section_rule_defined(rule):
                problems.append(f"{lang}/{p.name} -> {rule}")
    assert problems == [], f"미등록 규칙 선언: {problems}"



