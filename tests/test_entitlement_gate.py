"""티어 게이팅 단위 + API 통합 테스트 (Teaser 방식, Step 2)."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.entitlements import apply_entitlement_gate
from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import generate_full_report


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


def _report():
    result = calculate_saju(
        birth_date="1974-02-24", birth_time="05:30:00",
        timezone_str="Asia/Seoul", longitude=126.9780,
        correction_mode="lmt", jasi_boundary=23, gender="M",
        target_year=2026,
    )
    profile = build_semantic_profile(result)
    return generate_full_report(profile, lang="en")


@pytest.fixture
def fresh_auth(tmp_path, monkeypatch):
    monkeypatch.setenv("SAJU_AUTH_DB_PATH", str(tmp_path / "auth.db"))
    from app.auth.repository import reset_repository
    reset_repository()
    yield
    reset_repository()


def _h(token):
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# Ungated tiers
# ============================================================

def test_preview_tier_now_gated():
    """preview 티어는 더 이상 ungated가 아님 (Step 4-A)."""
    r = _report()
    out = apply_entitlement_gate(r, "preview")
    assert out["meta"]["tier"] == "preview"
    assert len(out["meta"]["locked_sections"]) > 0
    assert len(out["sections"]["core"]["narrative"]) == 1



def test_subscription_tier_ungated():
    r = _report()
    full = set(r["sections"].keys())
    out = apply_entitlement_gate(r, "subscription")
    assert out["meta"]["tier"] == "subscription"
    assert out["meta"]["locked_sections"] == []
    assert set(out["sections"].keys()) == full


def test_premium_tier_ungated():
    r = _report()
    full = set(r["sections"].keys())
    out = apply_entitlement_gate(r, "premium")
    assert out["meta"]["tier"] == "premium"
    assert set(out["sections"].keys()) == full


# ============================================================
# Free tier — Teaser 방식
# ============================================================

def test_free_tier_keeps_all_sections_as_teaser():
    """free 유저도 모든 섹션이 teaser 형태로 남아있어야 함."""
    r = _report()
    full = set(r["sections"].keys())
    out = apply_entitlement_gate(r, "free")
    assert out["meta"]["tier"] == "free"
    assert set(out["sections"].keys()) == full


def test_free_tier_locked_sections_list():
    """locked_sections에 teaser 적용된 섹션들이 나열됨."""
    r = _report()
    out = apply_entitlement_gate(r, "free")
    locked = set(out["meta"]["locked_sections"])
    assert "core" in locked
    assert "energy" in locked
    assert "money" in locked
    assert "timeline" in locked
    assert "monthly" in locked
    # 완전 무료 섹션은 제외
    assert "chart" not in locked
    assert "age_band" not in locked


def test_free_tier_core_teaser():
    """core: narrative 1, shadows 1, advice 1만 노출."""
    r = _report()
    out = apply_entitlement_gate(r, "free")
    core = out["sections"]["core"]

    # 필수 필드 유지
    assert core["id"] == "core"
    assert "archetype" in core
    assert "hero" in core

    # teaser: 1개씩만
    assert len(core["narrative"]) == 1
    assert len(core["shadows"]) == 1
    assert len(core["advice"]) == 1

    # 잠금 표시
    assert "narrative" in core["locked_fields"]
    assert "shadows" in core["locked_fields"]
    assert "advice" in core["locked_fields"]
    assert "personalized_insights" in core["locked_fields"]

    # keep에 없던 필드는 teaser에 없음
    assert "keywords" not in core


def test_free_tier_energy_1_block():
    r = _report()
    out = apply_entitlement_gate(r, "free")
    energy = out["sections"]["energy"]
    assert len(energy["blocks"]) == 1
    assert "blocks" in energy["locked_fields"]
    assert "percentages" in energy


def test_free_tier_timeline_3_items():
    r = _report()
    out = apply_entitlement_gate(r, "free")
    timeline = out["sections"]["timeline"]
    assert len(timeline["items"]) == 3
    assert "items" in timeline["locked_fields"]


def test_free_tier_monthly_2_items_truncated_fields():
    r = _report()
    out = apply_entitlement_gate(r, "free")
    monthly = out["sections"]["monthly"]
    assert len(monthly["items"]) == 2
    first = monthly["items"][0]
    # item_keep_fields 화이트리스트만 유지
    assert "name" in first
    assert "headline" in first
    assert "grade_label" in first
    # 그 외 필드는 잘려야 함
    assert "body" not in first
    assert "watch_for" not in first
    assert "lean_into" not in first


def test_free_tier_money_1_paragraph():
    r = _report()
    out = apply_entitlement_gate(r, "free")
    money = out["sections"]["money"]
    # body 첫 문단만
    paras = [p for p in money["body"].split("\n\n") if p.strip()]
    assert len(paras) == 1
    # action은 잠금
    assert "action" not in money
    assert "action" in money["locked_fields"]


def test_free_tier_lucky_code_power_minimal():
    r = _report()
    out = apply_entitlement_gate(r, "free")
    lc = out["sections"]["lucky_code"]
    # hero는 유지
    assert "hero" in lc
    # power는 최소 필드만
    assert "power" in lc
    assert "signature" in lc["power"]
    assert "element" in lc["power"]
    assert "keywords" in lc["power"]
    # 잠긴 상세 필드
    assert "colors" not in lc["power"]
    assert "practices" not in lc["power"]
    assert "domains" not in lc["power"]
    assert "support" not in lc
    assert "watch_out" not in lc
    assert "power.domains" in lc["locked_fields"]


def test_free_tier_sinsal_1_item_truncated_fields():
    r = _report()
    out = apply_entitlement_gate(r, "free")
    sinsal = out["sections"]["sinsal"]
    if not sinsal.get("items"):
        pytest.skip("1974 케이스에 신살 없음")
    assert len(sinsal["items"]) == 1
    first = sinsal["items"][0]
    assert "name" in first
    assert "headline" in first
    # body/advice는 잠금
    assert "body" not in first
    assert "advice" not in first


def test_free_tier_chart_fully_free():
    r = _report()
    out = apply_entitlement_gate(r, "free")
    chart = out["sections"]["chart"]
    # 4 layers 유지
    assert len(chart["layers"]) == 4
    assert "notes" in chart


def test_free_tier_year_headline_only():
    r = _report()
    out = apply_entitlement_gate(r, "free")
    year = out["sections"]["year"]
    assert "name" in year
    assert "headline" in year
    assert "watch_for" in year
    # body/lean_into는 잠금
    assert "body" not in year
    assert "lean_into" not in year
    assert "body" in year["locked_fields"]
    assert "lean_into" in year["locked_fields"]


def test_free_tier_health_1_block():
    r = _report()
    out = apply_entitlement_gate(r, "free")
    health = out["sections"]["health"]
    assert len(health["blocks"]) == 1
    assert len(health["practices"]) == 1
    # disclaimer / framework_note는 유지 (컴플라이언스 필수)
    assert "disclaimer" in health
    assert "framework_note" in health


# ============================================================
# Unknown tier
# ============================================================

def test_unknown_tier_defaults_to_teaser_gating():
    r = _report()
    full = set(r["sections"].keys())
    out = apply_entitlement_gate(r, "vip_unknown")
    assert out["meta"]["tier"] == "vip_unknown"
    # 모든 섹션 유지 (teaser 형태)
    assert set(out["sections"].keys()) == full
    # teaser 적용됨
    assert len(out["meta"]["locked_sections"]) > 0


# ============================================================
# Schema version & 메타 안정성
# ============================================================

def test_schema_version_is_1_2():
    r = _report()
    assert r["meta"]["schema_version"] == "1.2"
    assert r["meta"]["tier"] == "preview"
    assert r["meta"]["locked_sections"] == []


# ============================================================
# API level
# ============================================================

def test_api_no_auth_returns_free_tier():
    """미인증 요청은 free 티어로 처리 (Step 4-A)."""
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    assert resp.status_code == 200
    body = resp.json()["report"]
    meta = body["meta"]
    assert meta["tier"] == "free"
    assert len(meta["locked_sections"]) > 0
    # teaser: energy.blocks는 1개
    assert "energy" in body["sections"]
    assert len(body["sections"]["energy"]["blocks"]) == 1
    # summary_cards teaser: 뒤쪽 카드는 locked
    cards = body["summary_cards"]
    assert len(cards) >= 4
    assert any(c.get("locked") is True for c in cards[2:])



def test_api_free_tier_teaser(fresh_auth):
    a = client.post("/api/v1/auth/anonymous").json()
    resp = client.post(
        "/api/v1/saju/report",
        headers=_h(a["access_token"]),
        json=BASE_PAYLOAD,
    )
    assert resp.status_code == 200
    report = resp.json()["report"]
    assert report["meta"]["tier"] == "free"
    # 모든 섹션 노출
    assert "energy" in report["sections"]
    assert "money" in report["sections"]
    # teaser 적용
    assert "blocks" in report["sections"]["energy"].get("locked_fields", [])
    assert len(report["sections"]["timeline"]["items"]) == 3
    assert len(report["sections"]["core"]["narrative"]) == 1


def test_api_subscription_tier_ungated(fresh_auth):
    a = client.post("/api/v1/auth/anonymous").json()
    from app.auth.repository import get_repository
    get_repository().set_tier(a["user"]["id"], "subscription")
    resp = client.post(
        "/api/v1/saju/report",
        headers=_h(a["access_token"]),
        json=BASE_PAYLOAD,
    )
    assert resp.status_code == 200
    report = resp.json()["report"]
    assert report["meta"]["tier"] == "subscription"
    assert report["meta"]["locked_sections"] == []
    # 전체 데이터
    assert len(report["sections"]["core"]["narrative"]) >= 3
    assert "locked_fields" not in report["sections"]["core"]


def test_api_require_auth_env_blocks_anonymous(fresh_auth, monkeypatch):
    monkeypatch.setenv("SAJU_REQUIRE_AUTH_FOR_REPORT", "true")
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    assert resp.status_code == 401


def test_api_require_auth_env_allows_authed(fresh_auth, monkeypatch):
    monkeypatch.setenv("SAJU_REQUIRE_AUTH_FOR_REPORT", "true")
    a = client.post("/api/v1/auth/anonymous").json()
    resp = client.post(
        "/api/v1/saju/report",
        headers=_h(a["access_token"]),
        json=BASE_PAYLOAD,
    )
    assert resp.status_code == 200
    assert resp.json()["report"]["meta"]["tier"] == "free"


def test_free_tier_summary_cards_gated():
    """free 티어 summary_cards: 앞 두 개만 전체 노출 (Step 4-A)."""
    r = _report()
    out = apply_entitlement_gate(r, "free")
    cards = out["summary_cards"]
    assert len(cards) >= 4
    assert "locked" not in cards[0]
    assert "locked" not in cards[1]
    for card in cards[2:]:
        assert card.get("locked") is True
        assert card.get("body") == ""
        assert card.get("headline")  # headline은 티저로 유지


def test_subscription_summary_cards_ungated():
    r = _report()
    out = apply_entitlement_gate(r, "subscription")
    for card in out["summary_cards"]:
        assert not card.get("locked")
        assert card.get("body")


def test_unknown_tier_summary_cards_gated():
    r = _report()
    out = apply_entitlement_gate(r, "vip_unknown")
    cards = out["summary_cards"]
    assert any(c.get("locked") is True for c in cards[2:])
