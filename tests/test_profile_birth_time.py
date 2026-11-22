"""프로필 birth_time / birth_time_mode 덮어쓰기 핫픽스.

배경(사고)
  `PUT /auth/me/profile` 은 전체 교체인데, 재입력 화면(birth-input)이
  birth_date / birth_time_mode 를 payload 에 넣지 않았고 서버도 생략 필드를
  NULL 로 저장했다 → 설정에서 MBTI 류 필드만 바꿔도 저장된 시각이 사라졌다.

수정 원칙
  - 서버: `model_fields_set` 로 "키 생략 = 기존 값 유지", "명시적 null = 삭제".
          두 필드가 모두 왔을 때만 조합 모순(exact+null, noon+time)을 422.
  - 프론트: 세 필드를 항상 전송(시간 모름 = noon + null).
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

BASE = {
    "birth_date": "1974-02-24",
    "birth_time": "05:30:00",
    "birth_time_mode": "exact",
    "birth_location": "seoul",
    "timezone_str": "Asia/Seoul",
    "longitude": 126.978,
    "gender": "M",
    "jasi_boundary": 23,
    "correction_mode": "lmt",
}


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


def _db(uid):
    from app.auth.repository import get_repository
    return get_repository().get_profile(uid)


# ============================================================
# 1) 정상 갱신
# ============================================================

def test_normal_update_persists_all_three_fields(fresh_auth):
    uid, h = _new_user()
    r = client.put("/api/v1/auth/me/profile", headers=h, json=BASE)
    assert r.status_code == 200, r.text
    row = _db(uid)
    assert (row["birth_date"], row["birth_time"], row["birth_time_mode"]) == (
        "1974-02-24", "05:30:00", "exact"
    )

    r = client.put("/api/v1/auth/me/profile", headers=h,
                   json={**BASE, "birth_time": "07:15:00"})
    assert r.status_code == 200
    assert _db(uid)["birth_time"] == "07:15:00"


def test_time_unknown_is_noon_with_null_time(fresh_auth):
    """'시간 모름' = mode noon + birth_time null (프론트가 보내는 형태)."""
    uid, h = _new_user()
    r = client.put("/api/v1/auth/me/profile", headers=h,
                   json={**BASE, "birth_time_mode": "noon", "birth_time": None})
    assert r.status_code == 200, r.text
    row = _db(uid)
    assert row["birth_time_mode"] == "noon"
    assert row["birth_time"] is None


# ============================================================
# 2) 키 생략 = 기존 값 보존 (구버전 클라이언트)
# ============================================================

def test_omitted_birth_fields_keep_existing_values(fresh_auth):
    uid, h = _new_user()
    client.put("/api/v1/auth/me/profile", headers=h, json=BASE)

    # birth_date / birth_time / birth_time_mode 를 모르는 구버전 앱의 저장 요청
    resp = client.put(
        "/api/v1/auth/me/profile",
        headers=h,
        json={"gender": "F", "timezone_str": "Asia/Seoul", "longitude": 126.978,
              "jasi_boundary": 23, "correction_mode": "lmt", "birth_location": "seoul"},
    )
    assert resp.status_code == 200
    row = _db(uid)
    assert row["birth_date"] == "1974-02-24"
    assert row["birth_time"] == "05:30:00"
    assert row["birth_time_mode"] == "exact"
    assert row["gender"] == "F"


def test_partial_omission_keeps_each_field_independently(fresh_auth):
    uid, h = _new_user()
    client.put("/api/v1/auth/me/profile", headers=h, json=BASE)

    # time 만 바꾸고 mode 는 생략 → mode 는 기존(exact) 유지
    r = client.put("/api/v1/auth/me/profile", headers=h,
                   json={**BASE, "birth_time": "09:00:00", "birth_time_mode": None})
    assert r.status_code == 200
    assert _db(uid)["birth_time"] == "09:00:00"
    assert _db(uid)["birth_time_mode"] == "exact"  # null=보존

    # birth_time 키만 생략 → 시각 보존
    r = client.put("/api/v1/auth/me/profile", headers=h,
                   json={"birth_time_mode": "exact"})
    assert r.status_code == 200
    assert _db(uid)["birth_time_mode"] == "exact"
    assert _db(uid)["birth_time"] == "09:00:00"
    assert _db(uid)["birth_date"] == "1974-02-24"


# ============================================================
# 3) 명시적 null = 보존 (스펙 변경)
# ============================================================

def test_explicit_null_keeps_birth_time(fresh_auth):
    """스펙 변경: `birth_time`/`birth_time_mode` 의 명시적 null 도 **기존 값 보존**.

    이유
    - PUT 은 전체 교체지만 이 화면/구버전 앱은 시간 정보를 모른 채 저장할 수 있다.
      (실제 사고: 시간만 남고, 모드 컬럼조차 없던 시절 요청이 시각을 NULL 로 덮었다.)
    - "시간 삭제" 요구가 없고, "시간 모름"은 mode=noon(+ 0a2263b 이전 값과의 호환)으로
      표현되므로 COALESCE 보존이 사용자 데이터를 잃지 않는 쪽이다.
      (noon 으로 되돌리면 repo 가 birth_time 을 NULL 로 정리한다 — 별도 테스트)
    """
    uid, h = _new_user()
    client.put("/api/v1/auth/me/profile", headers=h, json=BASE)

    r = client.put("/api/v1/auth/me/profile", headers=h,
                   json={**BASE, "birth_time": None, "birth_time_mode": None})
    assert r.status_code == 200
    row = _db(uid)
    assert row["birth_time"] == "05:30:00"
    assert row["birth_time_mode"] == "exact"
    assert row["birth_date"] == "1974-02-24"


def test_time_known_to_unknown_reverts_to_noon_and_clears_time(fresh_auth):
    """'시간 입력(05:30/exact)' → '시간 모름'(noon + null) 되돌리기.

    COALESCE 로 시각이 남아 mode=noon + 시각 존재 모순이 되지 않도록,
    repo 가 mode=noon 이면 birth_time 을 NULL 로 저장한다.
    """
    uid, h = _new_user()
    client.put("/api/v1/auth/me/profile", headers=h, json=BASE)
    assert _db(uid)["birth_time"] == "05:30:00"

    r = client.put("/api/v1/auth/me/profile", headers=h,
                   json={**BASE, "birth_time_mode": "noon", "birth_time": None})
    assert r.status_code == 200, r.text
    row = _db(uid)
    assert row["birth_time_mode"] == "noon"
    assert row["birth_time"] is None

    # 이후 /report 는 12:00 가정으로 정상 계산된다
    r = client.post("/api/v1/saju/report", headers=h, json={
        "birth_date": "1974-02-24", "birth_time_mode": "noon", "lang": "en",
        "target_year": 2026,
    })
    assert r.status_code == 200, r.text


def test_noon_mode_ignores_stray_time_value(fresh_auth):
    """구버전 클라이언트가 noon 과 시각을 같이 보내도 저장은 모순 없는 상태가 된다."""
    uid, h = _new_user()
    client.put("/api/v1/auth/me/profile", headers=h, json=BASE)
    # 라우터 조합검사는 422 를 내므로, repo 레벨 방어를 직접 검증한다.
    from app.auth.repository import get_repository
    get_repository().upsert_profile(uid, {**BASE, "birth_time_mode": "noon", "birth_time": "05:30:00"})
    row = _db(uid)
    assert row["birth_time_mode"] == "noon"
    assert row["birth_time"] is None



# ============================================================
# 4) 모순 조합 422
# ============================================================

@pytest.mark.parametrize("mode,time_value", [
    ("exact", None),
    ("exact", ""),
    ("noon", "05:30:00"),
    ("day_only", "05:30:00"),
])
def test_conflicting_combination_rejected(fresh_auth, mode, time_value):
    _, h = _new_user()
    r = client.put("/api/v1/auth/me/profile", headers=h,
                   json={**BASE, "birth_time_mode": mode, "birth_time": time_value})
    assert r.status_code == 422, r.text


def test_invalid_mode_rejected(fresh_auth):
    _, h = _new_user()
    r = client.put("/api/v1/auth/me/profile", headers=h,
                   json={**BASE, "birth_time_mode": "sometime"})
    assert r.status_code == 422


# ============================================================
# 5) 복구: NULL/NULL 프로필에서 시간 재입력 → 정상 동작
# ============================================================

def test_recover_from_null_profile_by_reentering_time(fresh_auth):
    """이미 birth_time/mode 가 NULL 이 된 프로필도 시간을 다시 넣으면 복구된다."""
    from app.auth.repository import get_repository

    uid, h = _new_user()
    # 사고 상태 재현: birth_date 만 남고 time/mode NULL
    get_repository().upsert_profile(uid, {**BASE, "birth_time": None, "birth_time_mode": None})
    assert _db(uid)["birth_time"] is None

    # 재입력 화면이 보내는 형태 그대로 저장
    r = client.put("/api/v1/auth/me/profile", headers=h, json=BASE)
    assert r.status_code == 200, r.text
    row = _db(uid)
    assert row["birth_time"] == "05:30:00"
    assert row["birth_time_mode"] == "exact"
    assert row["birth_date"] == "1974-02-24"


def test_recovered_profile_can_generate_report(fresh_auth):
    """복구 후 /report 가 200 으로 시주까지 계산되는지."""
    from app.auth.repository import get_repository

    uid, h = _new_user()
    get_repository().upsert_profile(uid, {**BASE, "birth_time": None, "birth_time_mode": None})
    client.put("/api/v1/auth/me/profile", headers=h, json=BASE)

    r = client.post("/api/v1/saju/report", headers=h, json={
        "birth_date": "1974-02-24", "birth_time": "05:30:00", "birth_time_mode": "exact",
        "birth_location": "seoul", "gender": "M", "lang": "en", "target_year": 2026,
    })
    assert r.status_code == 200, r.text
    assert r.json()["report"]["sections"]["core"]["archetype"]["name"]


def test_null_mode_alone_keeps_report_working_if_time_present(fresh_auth):
    """mode 만 NULL 이고 time 이 있으면 /report 는 정상(프론트가 exact 로 보냄)."""
    from app.auth.repository import get_repository
    uid, h = _new_user()
    get_repository().upsert_profile(uid, {**BASE, "birth_time_mode": None})
    r = client.post("/api/v1/saju/report", headers=h, json={
        "birth_date": "1974-02-24", "birth_time": "05:30:00", "lang": "en",
    })
    assert r.status_code == 200


def test_null_time_with_exact_returns_422_at_report(fresh_auth):
    """time 이 NULL 인데 exact 면 /report 는 422 — 사용자가 보는 에러 화면의 원인."""
    from app.auth.repository import get_repository
    uid, h = _new_user()
    get_repository().upsert_profile(uid, {**BASE, "birth_time": None})
    r = client.post("/api/v1/saju/report", headers=h, json={
        "birth_date": "1974-02-24", "birth_time_mode": "exact", "lang": "en",
    })
    assert r.status_code == 422


