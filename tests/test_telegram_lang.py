# tests/test_telegram_lang.py
"""Phase 4-B: telegram 구독자 language_code 저장 + push-daily row별 렌더."""
import hashlib
import hmac
import json
import time
from pathlib import Path
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
    monkeypatch.setenv("SAJU_CRON_SECRET", CRON)
    monkeypatch.delenv("SAJU_ENV", raising=False)
    from app.auth.repository import reset_repository

    reset_repository()
    yield
    reset_repository()


def _make_init_data(user_id=777, bot_token=BOT):
    fields = {
        "auth_date": str(int(time.time())),
        "query_id": "AAH",
        "user": json.dumps({"id": user_id, "first_name": "T"}, separators=(",", ":")),
    }
    check = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


def _auth():
    t = client.post("/api/v1/auth/anonymous").json()["access_token"]
    return {"Authorization": f"Bearer {t}"}


def _save_profile(headers, birth_date="1990-05-05"):
    r = client.put(
        "/api/v1/auth/me/profile",
        headers=headers,
        json={
            "birth_date": birth_date,
            "birth_time": "14:30:00",
            "birth_location": "seoul",
        },
    )
    assert r.status_code == 200, r.text


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


# ---- register 저장 ----
def test_register_stores_lang(env):
    from app.auth.repository import get_repository

    h = _auth()
    _save_profile(h)
    r = client.post(
        "/api/v1/telegram/register",
        headers=h,
        json={"init_data": _make_init_data(777), "lang": "en"},
    )
    assert r.status_code == 200, r.text
    subs = get_repository().list_telegram_subscribers()
    assert len(subs) == 1
    assert subs[0]["language_code"] == "en"


def test_register_defaults_to_ko(env):
    from app.auth.repository import get_repository

    h = _auth()
    _save_profile(h)
    r = client.post(
        "/api/v1/telegram/register",
        headers=h,
        json={"init_data": _make_init_data(777)},
    )
    assert r.status_code == 200
    subs = get_repository().list_telegram_subscribers()
    assert subs[0]["language_code"] == "ko"


def test_register_updates_lang_on_re_registration(env):
    from app.auth.repository import get_repository

    h = _auth()
    _save_profile(h)
    client.post(
        "/api/v1/telegram/register",
        headers=h,
        json={"init_data": _make_init_data(777), "lang": "ko"},
    )
    client.post(
        "/api/v1/telegram/register",
        headers=h,
        json={"init_data": _make_init_data(777), "lang": "en"},
    )
    subs = get_repository().list_telegram_subscribers()
    assert len(subs) == 1
    assert subs[0]["language_code"] == "en"


# ---- push-daily row별 렌더 ----
def test_push_daily_uses_per_row_lang(env, monkeypatch):
    monkeypatch.setattr(tg.time, "sleep", lambda s: None)

    h_a = _auth()
    _save_profile(h_a)
    client.post(
        "/api/v1/telegram/register",
        headers=h_a,
        json={"init_data": _make_init_data(1001), "lang": "ko"},
    )

    h_b = _auth()
    _save_profile(h_b)
    client.post(
        "/api/v1/telegram/register",
        headers=h_b,
        json={"init_data": _make_init_data(2002), "lang": "en"},
    )

    calls = []
    monkeypatch.setattr(tg.httpx, "Client", _fake_client([200, 200], calls))

    r = client.post(
        "/api/v1/telegram/push-daily",
        headers={"Authorization": f"Bearer {CRON}"},
    )
    assert r.status_code == 200
    assert r.json()["sent"] == 2

    caps = {c[1]["chat_id"]: c[1]["caption"] for c in calls}
    assert "1001" in caps and "2002" in caps
    assert caps["1001"] != caps["2002"], "ko/en 캡션이 같음"


def test_push_daily_falls_back_to_query_lang_for_null(env, monkeypatch):
    """language_code IS NULL 인 row 는 ?lang= 폴백을 사용."""
    monkeypatch.setattr(tg.time, "sleep", lambda s: None)
    from app.auth.repository import get_repository

    repo = get_repository()
    h = _auth()
    uid = client.get("/api/v1/auth/me", headers=h).json()["user"]["id"]
    _save_profile(h)

    # Phase 4-B 이전 row 시뮬레이션: language_code 명시 안 함 → NULL
    repo._run(
        "INSERT INTO telegram_subscribers (telegram_id, user_id, created_at) "
        "VALUES (?, ?, ?)",
        ("9999", uid, "2020-01-01T00:00:00+00:00"),
    )
    assert repo.list_telegram_subscribers()[0]["language_code"] is None

    calls = []
    monkeypatch.setattr(tg.httpx, "Client", _fake_client([200], calls))
    r = client.post(
        "/api/v1/telegram/push-daily?lang=en",
        headers={"Authorization": f"Bearer {CRON}"},
    )
    assert r.status_code == 200
    assert r.json()["sent"] == 1
    cap = calls[0][1]["caption"]
    assert "Today's energy update" in cap or "Download today's" in cap, cap


# ---- migration idempotent ----
def test_migration_adds_column_idempotently(env):
    import os

    from app.auth.repository import Repository

    db = Path(os.environ["SAJU_AUTH_DB_PATH"])
    r1 = Repository(str(db))
    r1.close()
    r2 = Repository(str(db))
    cols = {
        row[1]
        for row in r2._conn.execute(
            "PRAGMA table_info(telegram_subscribers)"
        ).fetchall()
    }
    assert "language_code" in cols
    r2.close()


# ---- 스캐너용: json 포맷 깨지지 않도록 보장 ----
def test_schema_note_in_docstring():
    """load_pack('en','telegram')이 여전히 유효."""
    from app.services.content.loader import load_pack

    for lang in ("ko", "en"):
        pack = load_pack(lang, "telegram")
        assert "PUSH_DAILY_CAPTION" in pack
        assert "{url}" in pack["PUSH_DAILY_CAPTION"]
