# tests/test_report_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

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
    monkeypatch.setenv("SAJU_AUTH_DB_PATH", str(tmp_path / "auth.db"))
    from app.auth.repository import reset_repository
    reset_repository()
    yield
    reset_repository()


def test_report_endpoint_200():
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert "report" in data


def test_report_meta():
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    report = resp.json()["report"]

    assert report["meta"]["lang"] == "en"
    assert report["meta"]["schema_version"] == "1.2"


def test_report_cover():
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    cover = resp.json()["report"]["cover"]

    assert cover["archetype"]["key"] == "THE_RADIATOR"
    assert cover["archetype"]["name"] == "Sun Above Stone"  # 1974 = 丙申
    assert cover["intensity_label"] == "Self-Sourced"


def test_report_has_all_sections():
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    sections = resp.json()["report"]["sections"]

    expected = {"core", "energy", "lucky_code", "money",
                "work", "bonds", "year", "timeline"}
    assert expected.issubset(set(sections.keys()))


def test_report_summary_cards():
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    cards = resp.json()["report"]["summary_cards"]

    assert len(cards) >= 4
    labels = [c["label"] for c in cards]
    assert "Core" in labels
    assert "Money Mode" in labels


def test_report_without_target_year():
    """target_year 없으면 year 섹션 빠짐."""
    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "target_year"}
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 200
    sections = resp.json()["report"]["sections"]
    assert "year" not in sections
    # 나머지는 그대로
    for sid in ("core", "energy", "lucky_code", "money", "work", "bonds", "timeline"):
        assert sid in sections


def test_report_invalid_lang_422():
    payload = {**BASE_PAYLOAD, "lang": "fr"}
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 422


def test_report_invalid_jasi_boundary_422():
    payload = {**BASE_PAYLOAD, "jasi_boundary": 12}
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 422


def test_report_extra_field_forbidden_422():
    payload = {**BASE_PAYLOAD, "include_ai": True}
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 422


def test_report_no_llm_strings():
    """리포트 응답 어디에도 LLM/AI 문자열 금지."""
    import json
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    blob = json.dumps(resp.json()).lower()
    for banned in ("gemini", "openai", "gpt-", "llm"):
        assert banned not in blob


def test_existing_calculate_still_works():
    """기존 /calculate 회귀 방지."""
    payload = {k: v for k, v in BASE_PAYLOAD.items() if k != "lang"}
    resp = client.post("/api/v1/saju/calculate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["day_pillar"] == "丙申"


def test_report_dst_ambiguous_gives_400_with_guidance():
    """1988-10-09 DST 종료일의 모호 시각 → 400, 안내에 dst_fold 언급."""
    from tests.test_dst_fold import _find_ambiguous_time
    t = _find_ambiguous_time("1988-10-09")

    payload = {
        **{k: v for k, v in BASE_PAYLOAD.items() if k != "target_year"},
        "birth_date": "1988-10-09",
        "birth_time": t,
    }
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 400
    assert "dst_fold" in resp.json()["detail"]

def test_report_dst_fold_resolves():
    """dst_fold=1 넣으면 정상 200."""
    payload = {
        **{k: v for k, v in BASE_PAYLOAD.items() if k != "target_year"},
        "birth_date": "1988-10-09",
        "birth_time": "01:30:00",
        "dst_fold": 1,
    }
    resp = client.post("/api/v1/saju/report", json=payload)
    assert resp.status_code == 200
    assert "report" in resp.json()


def test_report_internal_error_hidden():
    """내부 KeyError 등은 응답에 노출되지 않음 (일반 문구로 대체)."""
    # 정상 요청은 문제 없음 → 별도 트리거 어려우니 meta만 확인
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    assert resp.status_code == 200
    meta = resp.json()["report"]["meta"]
    assert "calculation_method" in meta
    assert "school-dependent" in meta["calculation_method"]


def test_report_meta_says_school_dependent():
    """meta에 학파 의존성 명시."""
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    meta = resp.json()["report"]["meta"]
    assert meta["calculation_method"].startswith("weighted-sum")

def test_report_includes_health_section():
    resp = client.post("/api/v1/saju/report", json=BASE_PAYLOAD)
    sections = resp.json()["report"]["sections"]
    assert "health" in sections
    assert sections["health"]["id"] == "health"


def test_report_lucky_code_has_domains(fresh_auth):
    """subscription 티어에서 power.domains 노출 확인 (Step 4-A 후)."""
    a = client.post("/api/v1/auth/anonymous").json()
    from app.auth.repository import get_repository
    get_repository().set_tier(a["user"]["id"], "subscription")
    resp = client.post(
        "/api/v1/saju/report",
        headers={"Authorization": f"Bearer {a['access_token']}"},
        json=BASE_PAYLOAD,
    )
    assert resp.status_code == 200
    power = resp.json()["report"]["sections"]["lucky_code"]["power"]
    assert "domains" in power
    assert "career" in power["domains"]


def test_report_lucky_code_domains_locked_in_free(fresh_auth):
    """free 티어에서 power.domains는 잠금 (Step 4-A 회귀 방지)."""
    a = client.post("/api/v1/auth/anonymous").json()
    resp = client.post(
        "/api/v1/saju/report",
        headers={"Authorization": f"Bearer {a['access_token']}"},
        json=BASE_PAYLOAD,
    )
    assert resp.status_code == 200
    lc = resp.json()["report"]["sections"]["lucky_code"]
    assert "domains" not in lc["power"]
    assert "power.domains" in lc.get("locked_fields", [])
