"""궁합 friend, family 관계 심층 데이터 확인 (en/ko 모두)."""
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


@pytest.mark.parametrize("lang", ["en", "ko"])
@pytest.mark.parametrize("rel_type", ["friend", "family"])
def test_compat_friend_family_axes_not_empty(fresh_auth, lang, rel_type):
    """friend/family 관계에서 4축 headline/body가 언어별로 비어있지 않아야 함."""
    a = client.post("/api/v1/auth/anonymous").json()
    from app.auth.repository import get_repository
    get_repository().grant_addon(a["user"]["id"], "compatibility")

    resp = client.post(
        "/api/v1/saju/compatibility",
        headers={"Authorization": f"Bearer {a['access_token']}"},
        json={
            "person_a": BASE_PAYLOAD,
            "person_b": BASE_PAYLOAD,
            "lang": lang,
            "relationship_type": rel_type,
        },
    )
    assert resp.status_code == 200, f"{lang}/{rel_type}: {resp.text}"
    body = resp.json()["compatibility"]

    for axis_name, axis in body["axes"].items():
        assert axis["headline"], f"{lang}/{rel_type}/{axis_name} headline empty"
        assert axis["body"], f"{lang}/{rel_type}/{axis_name} body empty"