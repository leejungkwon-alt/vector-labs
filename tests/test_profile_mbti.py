"""자기신고 MBTI 프로필 필드 — 검증/왕복/구버전 호환/마이그레이션/삭제.

결정 사항
- MBTI 는 사용자 자기신고, **선택 입력**. 서버가 추정하지 않는다.
- 값 형식: `^[EI][NS][TF][JP]$` (4글자 대문자). 빈 값/공백은 null 로 정규화.
- 요청에 `mbti` 키가 **없으면** 기존 값 유지(구버전 앱 안전),
  키가 있고 null/"" 이면 미입력(null)으로 저장.
"""
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.auth import ProfilePayload
from app.schemas.saju import ReportRequest

client = TestClient(app)


@pytest.fixture
def fresh_auth(tmp_path, monkeypatch):
    monkeypatch.setenv("SAJU_AUTH_DB_PATH", str(tmp_path / "auth.db"))
    from app.auth.repository import reset_repository
    reset_repository()
    yield
    reset_repository()


def _new_user():
    a = client.post("/api/v1/auth/anonymous").json()
    return a["user"]["id"], {"Authorization": f"Bearer {a['access_token']}"}


PROFILE = {
    "birth_date": "1974-02-24",
    "birth_time": "05:30:00",
    "birth_location": "seoul",
    "timezone_str": "Asia/Seoul",
    "longitude": 126.978,
    "gender": "M",
    "jasi_boundary": 23,
    "correction_mode": "lmt",
}


# ============================================================
# 1) 스키마 검증 (Pydantic)
# ============================================================

@pytest.mark.parametrize("raw,expected", [
    ("INFJ", "INFJ"),
    ("enfp", "ENFP"),
    ("  intp  ", "INTP"),
    ("", None),
    ("   ", None),
    (None, None),
])
def test_profile_payload_normalizes_mbti(raw, expected):
    payload = ProfilePayload(**{**PROFILE, "mbti": raw})
    assert payload.mbti == expected


@pytest.mark.parametrize("bad", [
    "ABCD", "INFX", "IN", "INFJX", "IIII", "INFJ!", "1234", "I N F J",
])
def test_profile_payload_rejects_invalid_mbti(bad):
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ProfilePayload(**{**PROFILE, "mbti": bad})


def test_model_fields_set_distinguishes_omitted_key():
    omitted = ProfilePayload(**PROFILE)
    assert "mbti" not in omitted.model_fields_set

    explicit_null = ProfilePayload(**{**PROFILE, "mbti": None})
    assert "mbti" in explicit_null.model_fields_set
    assert explicit_null.mbti is None


def test_report_request_accepts_optional_mbti():
    """extra="ignore" 때문에 조용히 버려지지 않도록 명시 선언됐는지."""
    omitted = ReportRequest(**{**PROFILE, "lang": "ko"})
    assert "mbti" not in omitted.model_fields_set

    given = ReportRequest(**{**PROFILE, "lang": "ko", "mbti": "enfj"})
    assert given.mbti == "ENFJ"
    assert "mbti" in given.model_fields_set

    with pytest.raises(Exception):
        ReportRequest(**{**PROFILE, "lang": "ko", "mbti": "ZZZZ"})


# ============================================================
# 2) 요청 → 저장 → 응답 왕복
# ============================================================

def test_roundtrip_mbti_saved_and_returned(fresh_auth):
    uid, h = _new_user()

    resp = client.put("/api/v1/auth/me/profile", headers=h, json={**PROFILE, "mbti": "infj"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["mbti"] == "INFJ"

    got = client.get("/api/v1/auth/me/profile", headers=h)
    assert got.status_code == 200
    assert got.json()["mbti"] == "INFJ"

    from app.auth.repository import get_repository
    assert get_repository().get_profile(uid)["mbti"] == "INFJ"


def test_roundtrip_invalid_mbti_is_422(fresh_auth):
    _, h = _new_user()
    resp = client.put("/api/v1/auth/me/profile", headers=h, json={**PROFILE, "mbti": "ABCD"})
    assert resp.status_code == 422


def test_profile_without_mbti_is_null(fresh_auth):
    """MBTI 를 건너뛴 사용자: null 로 저장/응답."""
    uid, h = _new_user()
    resp = client.put("/api/v1/auth/me/profile", headers=h, json=PROFILE)
    assert resp.status_code == 200
    assert resp.json()["mbti"] is None
    from app.auth.repository import get_repository
    assert get_repository().get_profile(uid)["mbti"] is None


# ============================================================
# 3) 구버전 앱 호환 — mbti 키가 없는 요청이 기존 값을 지우면 안 된다
# ============================================================

def test_legacy_client_omitting_mbti_keeps_existing_value(fresh_auth):
    uid, h = _new_user()
    client.put("/api/v1/auth/me/profile", headers=h, json={**PROFILE, "mbti": "ENTP"})

    # mbti 필드를 모르는 구버전 앱의 저장 요청 (키 자체가 없음)
    resp = client.put("/api/v1/auth/me/profile", headers=h, json=PROFILE)
    assert resp.status_code == 200
    assert resp.json()["mbti"] == "ENTP"

    from app.auth.repository import get_repository
    assert get_repository().get_profile(uid)["mbti"] == "ENTP"


def test_legacy_client_repo_level_keeps_existing_value(fresh_auth):
    """라우터를 거치지 않아도 repo 가 '키 없음'을 보존한다(방어선 2중화)."""
    from app.auth.repository import get_repository

    uid, _ = _new_user()
    repo = get_repository()
    repo.upsert_profile(uid, {**PROFILE, "mbti": "ISFP"})
    repo.upsert_profile(uid, {**PROFILE})  # 키 없음
    assert repo.get_profile(uid)["mbti"] == "ISFP"


def test_explicit_null_clears_mbti(fresh_auth):
    """사용자가 '모름/건너뛰기'를 눌러 명시적으로 null 을 보내면 값이 지워진다."""
    uid, h = _new_user()
    client.put("/api/v1/auth/me/profile", headers=h, json={**PROFILE, "mbti": "INTJ"})

    resp = client.put("/api/v1/auth/me/profile", headers=h, json={**PROFILE, "mbti": None})
    assert resp.status_code == 200
    assert resp.json()["mbti"] is None

    from app.auth.repository import get_repository
    assert get_repository().get_profile(uid)["mbti"] is None


def test_legacy_client_can_still_update_other_fields(fresh_auth):
    """구버전 앱이 mbti 없이 보내도 나이대/성별 등 기존 필드 갱신은 정상."""
    uid, h = _new_user()
    client.put("/api/v1/auth/me/profile", headers=h, json={**PROFILE, "mbti": "ESFJ"})

    resp = client.put(
        "/api/v1/auth/me/profile",
        headers=h,
        json={**PROFILE, "gender": "F"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["gender"] == "F"
    assert body["mbti"] == "ESFJ"


# ============================================================
# 4) 마이그레이션 — mbti 컬럼이 없는 기존 DB 에도 안전하게 추가
# ============================================================

def test_migration_adds_mbti_to_existing_profiles_table(tmp_path, monkeypatch):
    db = tmp_path / "legacy.db"
    # mbti 컬럼이 없는 "구버전" 스키마 + 기존 사용자 데이터
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE users (
            id TEXT PRIMARY KEY, tier TEXT NOT NULL DEFAULT 'free',
            is_anonymous INTEGER NOT NULL DEFAULT 1,
            social_provider TEXT, social_subject TEXT,
            created_at TEXT NOT NULL, email TEXT,
            UNIQUE (social_provider, social_subject)
        );
        CREATE TABLE profiles (
            user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            birth_date TEXT, birth_time TEXT, birth_location TEXT,
            timezone_str TEXT NOT NULL DEFAULT 'Asia/Seoul',
            longitude DOUBLE PRECISION NOT NULL DEFAULT 126.978,
            gender TEXT NOT NULL DEFAULT 'M',
            jasi_boundary INTEGER NOT NULL DEFAULT 23,
            correction_mode TEXT NOT NULL DEFAULT 'lmt',
            dob_change_count INTEGER NOT NULL DEFAULT 0,
            last_dob_change_at TEXT, updated_at TEXT NOT NULL
        );
        INSERT INTO users (id, created_at) VALUES ('legacy-user', '2026-01-01T00:00:00+00:00');
        INSERT INTO profiles (user_id, birth_date, gender, updated_at)
            VALUES ('legacy-user', '1990-05-05', 'F', '2026-01-01T00:00:00+00:00');
        """
    )
    conn.commit()
    conn.close()

    monkeypatch.setenv("SAJU_AUTH_DB_PATH", str(db))
    from app.auth.repository import reset_repository, get_repository
    reset_repository()
    repo = get_repository()

    prof = repo.get_profile("legacy-user")
    assert prof is not None
    # 기존 데이터가 그대로 살아 있고 mbti 는 NULL
    assert prof["birth_date"] == "1990-05-05"
    assert prof["gender"] == "F"
    assert prof["mbti"] is None

    # 신규 입력도 정상 동작
    repo.upsert_profile("legacy-user", {**PROFILE, "gender": "F", "mbti": "ENFP"})
    assert repo.get_profile("legacy-user")["mbti"] == "ENFP"
    reset_repository()


# ============================================================
# 5) 계정 삭제 시 mbti 동반 삭제
# ============================================================

def test_account_delete_removes_profile_with_mbti(fresh_auth):
    from app.auth.repository import get_repository

    uid, h = _new_user()
    client.put("/api/v1/auth/me/profile", headers=h, json={**PROFILE, "mbti": "INFP"})
    assert get_repository().get_profile(uid)["mbti"] == "INFP"

    resp = client.delete("/api/v1/auth/me", headers=h)
    assert resp.status_code == 204

    assert get_repository().get_profile(uid) is None
    assert get_repository().get_user(uid) is None

    # 삭제 후 프로필 조회는 401 (토큰의 user 가 사라짐)
    assert client.get("/api/v1/auth/me/profile", headers=h).status_code == 401


