"""
사용자 리포지토리 (SQLite / PostgreSQL).

- users: id, tier, is_anonymous, social_provider/subject, created_at
- profiles: user_id 1:1, 생년 정보 + 기본 옵션
- user_addons, push_tokens, telegram_subscribers

백엔드 선택
- SAJU_DATABASE_URL 이 있으면 PostgreSQL (Cloud SQL 등, 운영 권장)
- 없으면 SQLite (개발/테스트). 경로는 SAJU_AUTH_DB_PATH.

Cloud Run 등 컨테이너 파일시스템은 휘발성이므로 운영에서 SQLite 를
기본 경로로 쓰면 재배포마다 사용자/구독 데이터가 사라진다.
SAJU_ENV=production 이고 DATABASE_URL 도, 명시적 SAJU_AUTH_DB_PATH 도 없으면
기동 시 RuntimeError 를 낸다.

공개 API(메서드 시그니처)는 기존과 동일. SQL 은 `?` 플레이스홀더로 작성하고
PostgreSQL 백엔드에서 `%s` 로 변환한다.
"""
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DB_PATH = _PROJECT_ROOT / "data" / "auth.db"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_db_path() -> str:
    env = os.environ.get("SAJU_AUTH_DB_PATH")
    if env:
        return env
    return str(_DEFAULT_DB_PATH)


# 두 DB 에서 동일하게 동작하는 DDL (DOUBLE PRECISION 은 SQLite 에서 REAL affinity)
_SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        tier TEXT NOT NULL DEFAULT 'free',
        is_anonymous INTEGER NOT NULL DEFAULT 1,
        social_provider TEXT,
        social_subject TEXT,
        created_at TEXT NOT NULL,
        UNIQUE (social_provider, social_subject)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS profiles (
        user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        birth_date TEXT,
        birth_time TEXT,
        birth_location TEXT,
        timezone_str TEXT NOT NULL DEFAULT 'Asia/Seoul',
        longitude DOUBLE PRECISION NOT NULL DEFAULT 126.978,
        gender TEXT NOT NULL DEFAULT 'M',
        jasi_boundary INTEGER NOT NULL DEFAULT 23,
        correction_mode TEXT NOT NULL DEFAULT 'lmt',
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS user_addons (
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        addon TEXT NOT NULL,
        granted_at TEXT NOT NULL,
        PRIMARY KEY (user_id, addon)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS push_tokens (
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token TEXT NOT NULL,
        platform TEXT NOT NULL,
        device_id TEXT,
        created_at TEXT NOT NULL,
        PRIMARY KEY (user_id, token)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS purchases (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        product_id TEXT NOT NULL,
        platform TEXT NOT NULL,
        purchased_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS telegram_subscribers (
        telegram_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        created_at TEXT NOT NULL
    )
    """,
]


class _BaseRepository:
    """공통 비즈니스 로직. 하위 클래스가 _one/_all/_run 만 구현한다."""

    _integrity_errors: tuple = ()

    # -- 하위 클래스가 구현 --
    def _one(self, sql: str, params: tuple = ()) -> Optional[dict]:
        raise NotImplementedError

    def _all(self, sql: str, params: tuple = ()) -> list:
        raise NotImplementedError

    def _run(self, sql: str, params: tuple = ()) -> int:
        """쓰기. 영향받은 행 수 반환."""
        raise NotImplementedError

    def close(self) -> None:
        pass

    # ---- users ----
    def create_anonymous_user(self) -> dict:
        uid = uuid.uuid4().hex
        self._run(
            "INSERT INTO users (id, tier, is_anonymous, created_at) "
            "VALUES (?, 'free', 1, ?)",
            (uid, _now_iso()),
        )
        return self.get_user(uid)

    def get_user(self, user_id: str) -> Optional[dict]:
        return self._one("SELECT * FROM users WHERE id = ?", (user_id,))

    # ---- profiles ----
    def upsert_profile(self, user_id: str, data: dict) -> dict:
        self._run(
            """
            INSERT INTO profiles (
                user_id, birth_date, birth_time, birth_location,
                timezone_str, longitude, gender, jasi_boundary,
                correction_mode, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                birth_date = excluded.birth_date,
                birth_time = excluded.birth_time,
                birth_location = excluded.birth_location,
                timezone_str = excluded.timezone_str,
                longitude = excluded.longitude,
                gender = excluded.gender,
                jasi_boundary = excluded.jasi_boundary,
                correction_mode = excluded.correction_mode,
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                data.get("birth_date"),
                data.get("birth_time"),
                data.get("birth_location"),
                data.get("timezone_str", "Asia/Seoul"),
                data.get("longitude", 126.9780),
                data.get("gender", "M"),
                data.get("jasi_boundary", 23),
                data.get("correction_mode", "lmt"),
                _now_iso(),
            ),
        )
        return self.get_profile(user_id)

    def get_profile(self, user_id: str) -> Optional[dict]:
        return self._one("SELECT * FROM profiles WHERE user_id = ?", (user_id,))

    # ---- 소셜 링크 ----
    def find_user_by_social(self, provider: str, subject: str) -> Optional[dict]:
        return self._one(
            "SELECT * FROM users WHERE social_provider = ? AND social_subject = ?",
            (provider, subject),
        )

    def link_social_identity(
        self, user_id: str, provider: str, subject: str
    ) -> dict:
        """익명 → 소셜 승격. 다른 사용자가 이미 점유한 identity 면 ValueError."""
        existing = self.find_user_by_social(provider, subject)
        if existing is not None and existing["id"] != user_id:
            raise ValueError(
                f"This {provider} identity is already linked to another account."
            )
        try:
            self._run(
                "UPDATE users SET social_provider = ?, social_subject = ?, "
                "is_anonymous = 0 WHERE id = ?",
                (provider, subject, user_id),
            )
        except self._integrity_errors as e:
            raise ValueError(f"Link failed: {e}") from e
        return self.get_user(user_id)

    def delete_user(self, user_id: str) -> bool:
        """계정 및 연관 데이터(프로필, 애드온, 푸시 토큰, 텔레그램 구독) 삭제."""
        return self._run("DELETE FROM users WHERE id = ?", (user_id,)) > 0

    def set_tier(self, user_id: str, tier: str) -> dict:
        """관리/테스트용. 실제 결제 연동은 IAP 스텝에서."""
        self._run("UPDATE users SET tier = ? WHERE id = ?", (tier, user_id))
        return self.get_user(user_id)

    # ---- add-ons ----
    def grant_addon(self, user_id: str, addon: str) -> None:
        """1회성 애드온 부여 (idempotent)."""
        self._run(
            "INSERT INTO user_addons (user_id, addon, granted_at) "
            "VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
            (user_id, addon, _now_iso()),
        )

    def has_addon(self, user_id: str, addon: str) -> bool:
        row = self._one(
            "SELECT 1 AS ok FROM user_addons WHERE user_id = ? AND addon = ?",
            (user_id, addon),
        )
        return row is not None

    def list_addons(self, user_id: str) -> list:
        rows = self._all(
            "SELECT addon FROM user_addons WHERE user_id = ? ORDER BY granted_at",
            (user_id,),
        )
        return [r["addon"] for r in rows]

    # ---- purchases ----
    def log_purchase(self, user_id: str, product_id: str, platform: str) -> dict:
        pid = uuid.uuid4().hex
        self._run(
            "INSERT INTO purchases (id, user_id, product_id, platform, purchased_at) VALUES (?, ?, ?, ?, ?)",
            (pid, user_id, product_id, platform, _now_iso())
        )
        return self._one("SELECT * FROM purchases WHERE id = ?", (pid,))

    def list_purchases(self, user_id: str) -> list:
        return self._all(
            "SELECT * FROM purchases WHERE user_id = ? ORDER BY purchased_at DESC",
            (user_id,),
        )

    # ---- push tokens ----
    def register_push_token(
        self, user_id: str, token: str, platform: str, device_id: Optional[str] = None
    ) -> None:
        """다기기 지원. (user_id, token) PK — 같은 토큰 중복 등록 무시."""
        self._run(
            "INSERT INTO push_tokens (user_id, token, platform, device_id, created_at) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING",
            (user_id, token, platform, device_id, _now_iso()),
        )

    def unregister_push_token(self, user_id: str, token: str) -> bool:
        return (
            self._run(
                "DELETE FROM push_tokens WHERE user_id = ? AND token = ?",
                (user_id, token),
            )
            > 0
        )

    def list_push_tokens(self, user_id: str) -> list:
        return self._all(
            "SELECT token, platform, device_id, created_at FROM push_tokens "
            "WHERE user_id = ? ORDER BY created_at",
            (user_id,),
        )

    # ---- telegram subscribers ----
    def upsert_telegram_subscriber(self, telegram_id: str, user_id: str) -> None:
        """검증된 telegram_id 를 사용자 계정에 연결 (재등록 시 소유자 갱신)."""
        self._run(
            "INSERT INTO telegram_subscribers (telegram_id, user_id, created_at) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT(telegram_id) DO UPDATE SET user_id = excluded.user_id",
            (telegram_id, user_id, _now_iso()),
        )

    def delete_telegram_subscriber(self, telegram_id: str) -> bool:
        return (
            self._run(
                "DELETE FROM telegram_subscribers WHERE telegram_id = ?",
                (telegram_id,),
            )
            > 0
        )

    def list_telegram_subscribers(self) -> list:
        """[{telegram_id, user_id}] — 프로필이 있는 구독자만 푸시 대상."""
        return self._all(
            "SELECT telegram_id, user_id FROM telegram_subscribers ORDER BY created_at"
        )


class Repository(_BaseRepository):
    """SQLite 백엔드 (개발/테스트). 기존 클래스명 유지."""

    _integrity_errors = (sqlite3.IntegrityError,)

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _resolve_db_path()
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock, self._conn:
            for stmt in _SCHEMA_STATEMENTS:
                self._conn.execute(stmt)

    def _one(self, sql, params=()):
        with self._lock:
            row = self._conn.execute(sql, params).fetchone()
        return dict(row) if row else None

    def _all(self, sql, params=()):
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def _run(self, sql, params=()):
        with self._lock, self._conn:
            cur = self._conn.execute(sql, params)
            return cur.rowcount

    def close(self) -> None:
        self._conn.close()


class PostgresRepository(_BaseRepository):
    """PostgreSQL 백엔드 (psycopg 3 + psycopg_pool). Cloud SQL 권장."""

    def __init__(self, database_url: str):
        try:
            import psycopg
            from psycopg.rows import dict_row
            from psycopg_pool import ConnectionPool
        except ImportError as e:  # pragma: no cover
            raise RuntimeError(
                "SAJU_DATABASE_URL 사용에는 'psycopg[binary]' 와 'psycopg_pool' 이 필요합니다."
            ) from e
        self._integrity_errors = (psycopg.IntegrityError,)
        self._pool = ConnectionPool(
            conninfo=database_url,
            min_size=int(os.environ.get("SAJU_DB_POOL_MIN", "1")),
            max_size=int(os.environ.get("SAJU_DB_POOL_MAX", "5")),
            kwargs={"row_factory": dict_row},
            open=True,
            timeout=10,
        )
        self._init_schema()

    @staticmethod
    def _q(sql: str) -> str:
        # 이 모듈의 SQL 에는 리터럴 '?' / '%' 가 없다.
        return sql.replace("?", "%s")

    def _init_schema(self) -> None:
        with self._pool.connection() as conn:
            # 다중 인스턴스 동시 기동 시 DDL 경쟁 방지
            conn.execute("SELECT pg_advisory_xact_lock(7340301)")
            for stmt in _SCHEMA_STATEMENTS:
                conn.execute(stmt)

    def _one(self, sql, params=()):
        with self._pool.connection() as conn:
            return conn.execute(self._q(sql), params).fetchone()

    def _all(self, sql, params=()):
        with self._pool.connection() as conn:
            return list(conn.execute(self._q(sql), params).fetchall())

    def _run(self, sql, params=()):
        with self._pool.connection() as conn:
            return conn.execute(self._q(sql), params).rowcount

    def close(self) -> None:
        self._pool.close()


_singleton: Optional[_BaseRepository] = None
_singleton_lock = threading.Lock()


def _build_repository() -> _BaseRepository:
    url = os.environ.get("SAJU_DATABASE_URL", "").strip()
    if url:
        return PostgresRepository(url)
    is_prod = os.environ.get("SAJU_ENV", "").lower() == "production"
    if is_prod and not os.environ.get("SAJU_AUTH_DB_PATH"):
        raise RuntimeError(
            "SAJU_ENV=production 인데 SAJU_DATABASE_URL 이 없고 SAJU_AUTH_DB_PATH 도 "
            "지정되지 않았습니다. 컨테이너 로컬 SQLite 는 재배포 시 모든 사용자/구독 "
            "데이터가 사라집니다. PostgreSQL(SAJU_DATABASE_URL) 또는 영속 볼륨 경로"
            "(SAJU_AUTH_DB_PATH)를 지정하세요."
        )
    return Repository()


def get_repository() -> _BaseRepository:
    global _singleton
    if _singleton is None:
        with _singleton_lock:
            if _singleton is None:
                _singleton = _build_repository()
    return _singleton


def reset_repository() -> None:
    """테스트 격리용. 다음 get_repository() 호출 시 새로 생성."""
    global _singleton
    if _singleton is not None:
        try:
            _singleton.close()
        except Exception:
            pass
    _singleton = None
