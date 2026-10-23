"""텔레그램 엔드포인트 보안: initData HMAC 검증, 크론 시크릿, 구독 영속화."""
import hashlib
import hmac
import json
import time
from datetime import date
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import telegram as tg
from app.main import app

client = TestClient(app)
BOT = "123456:TEST-BOT-TOKEN"
CRON = "c" * 32


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("SAJU_AUTH_DB_PATH", str(tmp_path / "auth.db"))
    monkeypatch.setenv("SAJU_TELEGRAM_BOT_TOKEN", BOT)
    monkeypatch.delenv("SAJU_CRON_SECRET", raising=False)
    monkeypatch.delenv("SAJU_ENV", raising=False)
    from app.auth.repository import reset_repository

    reset_repository()
    yield
    reset_repository()


def make_init_data(user_id=777, auth_date=None, bot_token=BOT, tamper=False):
    fields = {
        "auth_date": str(int(auth_date if auth_date is not None else time.time())),
        "query_id": "AAH",
        "user": json.dumps({"id": user_id, "first_name": "T"}, separators=(",", ":")),
    }
    check = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if tamper:
        fields["user"] = json.dumps({"id": 999}, separators=(",", ":"))
    return urlencode(fields)


def _auth():
    t = client.post("/api/v1/auth/anonymous").json()["access_token"]
    return {"Authorization": f"Bearer {t}"}


def _save_profile(headers, birth_date="1990-05-05"):
    r = client.put(
        "/api/v1/auth/me/profile",
        headers=headers,
        json={"birth_date": birth_date, "birth_time": "14:30:00", "birth_location": "seoul"},
    )
    assert r.status_code == 200, r.text


# ---- verify_init_data ----
def test_verify_init_data_ok():
    assert tg.verify_init_data(make_init_data(42), BOT)["id"] == 42


def test_verify_init_data_rejects_tamper_wrong_token_expired():
    with pytest.raises(ValueError):
        tg.verify_init_data(make_init_data(tamper=True), BOT)
    with pytest.raises(ValueError):
        tg.verify_init_data(make_init_data(), "999:OTHER")
    with pytest.raises(ValueError):
        tg.verify_init_data(make_init_data(auth_date=time.time() - 3 * 86400), BOT)
    with pytest.raises(ValueError):
        tg.verify_init_data("auth_date=1&user=%7B%7D", BOT)  # hash 없음


# ---- cron ----
def test_push_daily_disabled_without_secret(env):
    # 과거 기본값 "my-cron-secret" 으로도 열리면 안 된다
    r = client.post("/api/v1/telegram/push-daily", headers={"Authorization": "Bearer my-cron-secret"})
    assert r.status_code == 503


def test_push_daily_rejects_short_secret(env, monkeypatch):
    monkeypatch.setenv("SAJU_CRON_SECRET", "short")
    r = client.post("/api/v1/telegram/push-daily", headers={"Authorization": "Bearer short"})
    assert r.status_code == 503


def test_push_daily_wrong_and_missing_secret(env, monkeypatch):
    monkeypatch.setenv("SAJU_CRON_SECRET", CRON)
    assert client.post("/api/v1/telegram/push-daily").status_code == 401
    r = client.post("/api/v1/telegram/push-daily", headers={"Authorization": "Bearer nope"})
    assert r.status_code == 401


def test_push_daily_ok_no_subscribers(env, monkeypatch):
    monkeypatch.setenv("SAJU_CRON_SECRET", CRON)
    r = client.post("/api/v1/telegram/push-daily", headers={"Authorization": f"Bearer {CRON}"})
    assert r.status_code == 200 and r.json()["sent"] == 0


# ---- register / unregister ----
def test_register_requires_login(env):
    r = client.post("/api/v1/telegram/register", json={"init_data": make_init_data()})
    assert r.status_code == 401


def test_register_rejects_forged_init_data(env):
    h = _auth()
    r = client.post("/api/v1/telegram/register", headers=h, json={"init_data": make_init_data(tamper=True)})
    assert r.status_code == 401


def test_register_requires_profile(env):
    r = client.post("/api/v1/telegram/register", headers=_auth(), json={"init_data": make_init_data()})
    assert r.status_code == 409


def test_register_blocks_under_14(env):
    from app.auth.repository import get_repository

    h = _auth()
    uid = client.get("/api/v1/auth/me", headers=h).json()["user"]["id"]
    today = date.today()
    get_repository().upsert_profile(uid, {"birth_date": f"{today.year - 10}-01-01"})
    r = client.post("/api/v1/telegram/register", headers=h, json={"init_data": make_init_data()})
    assert r.status_code == 403


def test_register_persists_and_unregister_removes(env):
    from app.auth.repository import get_repository, reset_repository

    h = _auth()
    _save_profile(h)
    r = client.post("/api/v1/telegram/register", headers=h, json={"init_data": make_init_data(777)})
    assert r.status_code == 200
    assert [s["telegram_id"] for s in get_repository().list_telegram_subscribers()] == ["777"]

    reset_repository()  # 인스턴스 재시작 시뮬레이션: DB 라서 유지돼야 함
    assert len(get_repository().list_telegram_subscribers()) == 1

    r = client.post("/api/v1/telegram/unregister", json={"init_data": make_init_data(777)})
    assert r.status_code == 200 and r.json()["removed"] is True
    assert get_repository().list_telegram_subscribers() == []


def test_account_delete_cascades_subscription(env):
    from app.auth.repository import get_repository

    h = _auth()
    _save_profile(h)
    client.post("/api/v1/telegram/register", headers=h, json={"init_data": make_init_data(777)})
    assert client.delete("/api/v1/auth/me", headers=h).status_code in (200, 204)
    assert get_repository().list_telegram_subscribers() == []


# ---- push 동작 (텔레그램 API 모킹) ----
class _Resp:
    def __init__(self, code):
        self.status_code = code


def _fake_client(codes, calls):
    class FakeClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None):
            calls.append((url, json))
            return _Resp(codes.pop(0))

    return FakeClient


def test_push_uses_profile_wallpaper_and_prunes_blocked(env, monkeypatch):
    monkeypatch.setenv("SAJU_CRON_SECRET", CRON)
    monkeypatch.setattr(tg.time, "sleep", lambda s: None)
    from app.auth.repository import get_repository

    h = _auth()
    _save_profile(h, "1990-05-05")  # EDGE + THE_CHALLENGER
    client.post("/api/v1/telegram/register", headers=h, json={"init_data": make_init_data(777)})

    calls = []
    monkeypatch.setattr(tg.httpx, "Client", _fake_client([200], calls))
    r = client.post("/api/v1/telegram/push-daily", headers={"Authorization": f"Bearer {CRON}"})
    assert r.json()["sent"] == 1
    url, body = calls[0]
    assert url.endswith("/sendPhoto") and body["chat_id"] == "777"
    assert body["photo"].endswith("bg_metal_challenger.webp")  # 고정 generalist.jpg 아님

    calls.clear()
    monkeypatch.setattr(tg.httpx, "Client", _fake_client([403], calls))  # 봇 차단
    r = client.post("/api/v1/telegram/push-daily", headers={"Authorization": f"Bearer {CRON}"})
    assert r.json()["removed"] == 1
    assert get_repository().list_telegram_subscribers() == []
