"""Step 4-E 다국어 및 궁합 확장 테스트."""
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
}

@pytest.fixture
def fresh_auth(tmp_path, monkeypatch):
    monkeypatch.setenv("SAJU_AUTH_DB_PATH", str(tmp_path / "auth.db"))
    from app.auth.repository import reset_repository
    reset_repository()
    yield
    reset_repository()

def test_unsupported_lang_rejected():
    for bad_lang in ("zh_tw", "fr", "ja_JP"):
        resp = client.post("/api/v1/saju/report", json={**BASE_PAYLOAD, "lang": bad_lang})
        assert resp.status_code == 422, f"lang={bad_lang} should be rejected"

def test_supported_lang_accepted():
    for good_lang in ("en", "ko", "ja", "zh_cn", "es"):
        resp = client.post("/api/v1/saju/report", json={**BASE_PAYLOAD, "lang": good_lang})
        assert resp.status_code == 200

def test_compat_new_relationship_types(fresh_auth):
    a = client.post("/api/v1/auth/anonymous").json()
    from app.auth.repository import get_repository
    get_repository().grant_addon(a["user"]["id"], "compatibility")
    
    pair = {
        "person_a": BASE_PAYLOAD,
        "person_b": BASE_PAYLOAD,
        "lang": "ko",
    }
    
    for rel_type in ("friend", "family"):
        resp = client.post(
            "/api/v1/saju/compatibility",
            headers={"Authorization": f"Bearer {a['access_token']}"},
            json={**pair, "relationship_type": rel_type}
        )
        assert resp.status_code == 200, f"relationship_type={rel_type} failed"
        body = resp.json()["compatibility"]
        assert body["meta"]["relationship_type"] == rel_type
        assert body["relationship_advice"] != ""

def test_compat_invalid_relationship_type(fresh_auth):
    a = client.post("/api/v1/auth/anonymous").json()
    from app.auth.repository import get_repository
    get_repository().grant_addon(a["user"]["id"], "compatibility")
    
    pair = {
        "person_a": BASE_PAYLOAD,
        "person_b": BASE_PAYLOAD,
        "lang": "en",
        "relationship_type": "enemy"
    }
    resp = client.post(
        "/api/v1/saju/compatibility",
        headers={"Authorization": f"Bearer {a['access_token']}"},
        json=pair
    )
    assert resp.status_code == 422
