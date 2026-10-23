"""리포지토리: SQLite/PostgreSQL 동일 동작 + 운영 가드. PG 는 SAJU_TEST_DATABASE_URL 이 있을 때만."""
import os

import pytest

from app.auth import repository as repo_mod
from app.auth.repository import PostgresRepository, Repository


def _backends():
    params = ["sqlite"]
    if os.environ.get("SAJU_TEST_DATABASE_URL"):
        params.append("postgres")
    return params


@pytest.fixture(params=_backends())
def repo(request, tmp_path):
    if request.param == "sqlite":
        r = Repository(str(tmp_path / "t.db"))
    else:
        r = PostgresRepository(os.environ["SAJU_TEST_DATABASE_URL"])
    yield r
    r.close()


def test_user_profile_roundtrip(repo):
    u = repo.create_anonymous_user()
    assert u["tier"] == "free" and u["is_anonymous"] == 1
    p = repo.upsert_profile(u["id"], {"birth_date": "1990-05-05", "longitude": 127.5})
    assert p["birth_date"] == "1990-05-05" and p["longitude"] == 127.5
    p = repo.upsert_profile(u["id"], {"birth_date": "1991-01-01"})
    assert p["birth_date"] == "1991-01-01" and p["longitude"] == 126.978
    assert repo.set_tier(u["id"], "subscription")["tier"] == "subscription"


def test_addons_and_push_tokens_are_idempotent(repo):
    u = repo.create_anonymous_user()["id"]
    repo.grant_addon(u, "compatibility")
    repo.grant_addon(u, "compatibility")
    assert repo.list_addons(u) == ["compatibility"] and repo.has_addon(u, "compatibility")
    repo.register_push_token(u, "t1", "ios")
    repo.register_push_token(u, "t1", "ios")
    assert len(repo.list_push_tokens(u)) == 1
    assert repo.unregister_push_token(u, "t1") is True
    assert repo.unregister_push_token(u, "t1") is False


def test_social_link_conflict(repo):
    a = repo.create_anonymous_user()["id"]
    b = repo.create_anonymous_user()["id"]
    assert repo.link_social_identity(a, "google", "s-1")["is_anonymous"] == 0
    with pytest.raises(ValueError):
        repo.link_social_identity(b, "google", "s-1")


def test_delete_user_cascades(repo):
    u = repo.create_anonymous_user()["id"]
    repo.upsert_profile(u, {"birth_date": "1990-05-05"})
    repo.grant_addon(u, "x")
    repo.register_push_token(u, "t", "ios")
    repo.upsert_telegram_subscriber("42", u)
    assert repo.delete_user(u) is True
    assert repo.get_profile(u) is None and repo.list_addons(u) == []
    assert repo.list_push_tokens(u) == [] and repo.list_telegram_subscribers() == []
    assert repo.delete_user(u) is False


# ---- 운영 가드 ----
def test_production_without_database_is_rejected(monkeypatch):
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.delenv("SAJU_DATABASE_URL", raising=False)
    monkeypatch.delenv("SAJU_AUTH_DB_PATH", raising=False)
    repo_mod.reset_repository()
    with pytest.raises(RuntimeError, match="SAJU_DATABASE_URL"):
        repo_mod.get_repository()


def test_production_with_explicit_sqlite_path_is_allowed(monkeypatch, tmp_path):
    monkeypatch.setenv("SAJU_ENV", "production")
    monkeypatch.delenv("SAJU_DATABASE_URL", raising=False)
    monkeypatch.setenv("SAJU_AUTH_DB_PATH", str(tmp_path / "vol.db"))
    repo_mod.reset_repository()
    try:
        assert isinstance(repo_mod.get_repository(), Repository)
    finally:
        repo_mod.reset_repository()
