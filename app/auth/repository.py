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
from datetime import datetime, timedelta, timezone
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
          email TEXT,
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
        created_at TEXT NOT NULL,
        language_code TEXT
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

    def ping(self) -> bool:
        """DB 연결 확인 (SELECT 1). 실패 시 예외 — /ready 전용."""
        self._one("SELECT 1 AS ok")
        return True

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

    def set_user_not_anonymous(self, user_id: str) -> None:
        self._run("UPDATE users SET is_anonymous = 0 WHERE id = ?", (user_id,))

    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[dict]:
        """텔레그램 ID로 유저 정보를 정확히 조회합니다 (계정 통합용)."""
        return self._one(
            "SELECT u.* FROM users u "
            "JOIN telegram_subscribers t ON u.id = t.user_id "
            "WHERE t.telegram_id = ?",
            (telegram_id,)
        )

    def add_onetime_credit(self, user_id: str) -> None:
        """일시불 결제 시 단품 이용권(크레딧) +1 증가"""
        # 크레딧 컬럼이 없으면 추가 (마이그레이션)
        try:
            self._run("ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0")
        except Exception:
            pass # 이미 컬럼이 있으면 무시
        self._run("UPDATE users SET onetime_credits = COALESCE(onetime_credits, 0) + 1 WHERE id = ?", (user_id,))

    def get_user(self, user_id: str) -> Optional[dict]:
        return self._expire_stars_subscription(
            self._one("SELECT * FROM users WHERE id = ?", (user_id,))
        )

    # 텔레그램 Stars 구독은 취소해도 만료 이벤트가 오지 않는다(갱신 결제만 안 올 뿐).
    # 그래서 만료일(current_period_end)이 지난 stars_ 구독은 조회 시점에 free로 내린다.
    # 갱신 결제가 약간 늦게 도착하는 경우를 위해 24시간 여유를 둔다.
    # (Lemon Squeezy는 웹훅으로, 구글 구독은 별도 흐름으로 처리하므로 여기서는 건드리지 않는다.)
    _STARS_EXPIRY_GRACE = timedelta(hours=24)

    def _expire_stars_subscription(self, user: Optional[dict]) -> Optional[dict]:
        if not user or user.get("tier") != "premium":
            return user
        sub_id = str(user.get("stripe_subscription_id") or "")
        if not sub_id.startswith("stars_"):
            return user
        end_raw = user.get("current_period_end")
        if not end_raw:
            return user
        try:
            end = datetime.fromisoformat(str(end_raw).replace("Z", "+00:00"))
        except ValueError:
            return user
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if end + self._STARS_EXPIRY_GRACE >= datetime.now(timezone.utc):
            return user
        self.update_subscription(
            user_id=user["id"], subscription_id=sub_id,
            status="expired", current_period_end=str(end_raw), is_premium=False,
        )
        user = dict(user)
        user["tier"] = "free"
        user["subscription_status"] = "expired"
        return user

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
        self, user_id: str, provider: str, subject: str, email: str | None = None
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
                "is_anonymous = 0, email = COALESCE(?, email) WHERE id = ?",
                (provider, subject, email, user_id),
            )
        except self._integrity_errors as e:
            raise ValueError(f"Link failed: {e}") from e
        return self.get_user(user_id)

    def delete_user(self, user_id: str) -> bool:
        """계정 및 연관 데이터(프로필, 애드온, 푸시 토큰, 텔레그램 구독) 삭제."""
        return self._run("DELETE FROM users WHERE id = ?", (user_id,)) > 0


    # ---- shared compatibility ----
    def save_shared_compatibility(self, result_data: str) -> str:
        """궁합 결과를 저장하고 고유 ID를 반환합니다."""
        import uuid
        share_id = uuid.uuid4().hex
        # 테이블이 없으면 자동 생성 (안전장치)
        try:
            self._run(
                "CREATE TABLE IF NOT EXISTS shared_compatibilities (id TEXT PRIMARY KEY, result_data TEXT NOT NULL, created_at TEXT NOT NULL)",
                (),
            )
        except Exception:
            pass
        self._run(
            "INSERT INTO shared_compatibilities (id, result_data, created_at) VALUES (?, ?, ?)",
            (share_id, result_data, _now_iso()),
        )
        return share_id

    def get_shared_compatibility(self, share_id: str) -> Optional[dict]:
        """공유된 궁합 결과를 조회합니다."""
        return self._one(
            "SELECT * FROM shared_compatibilities WHERE id = ?", (share_id,)
        )

    def set_tier(self, user_id: str, tier: str) -> dict:
        """관리/테스트용. 실제 결제 연동은 IAP 스텝에서."""
        self._run("UPDATE users SET tier = ? WHERE id = ?", (tier, user_id))
        return self.get_user(user_id)


    # ---- Stripe ----
    def get_stripe_customer_id(self, user_id: str) -> Optional[str]:
        row = self._one("SELECT stripe_customer_id FROM users WHERE id = ?", (user_id,))
        return row["stripe_customer_id"] if row else None

    def set_stripe_customer_id(self, user_id: str, customer_id: str) -> None:
        self._run("UPDATE users SET stripe_customer_id = ? WHERE id = ?", (customer_id, user_id))

    def get_onetime_credits(self, user_id: str) -> int:
        """유저의 1회 이용권(크레딧) 잔액을 조회합니다."""
        row = self._one("SELECT onetime_credits FROM users WHERE id = ?", (user_id,))
        return row["onetime_credits"] if row and row["onetime_credits"] else 0

    def deduct_onetime_credit(self, user_id: str) -> bool:
        """1회 이용권을 1개 차감합니다. 차감 성공 시 True 반환"""
        updated = self._run(
            "UPDATE users SET onetime_credits = onetime_credits - 1 WHERE id = ? AND onetime_credits > 0",
            (user_id,)
        )
        return updated > 0

    def update_subscription(self, user_id: str, *, subscription_id: Optional[str],
                            status: str, current_period_end: Optional[str], is_premium: bool) -> None:
        self._run(
            "UPDATE users SET tier = ?, stripe_subscription_id = ?, "
            "subscription_status = ?, current_period_end = ? WHERE id = ?",
            ("premium" if is_premium else "free", subscription_id, status, current_period_end, user_id),
        )

    def record_stripe_event(self, event_id: str, event_type: str) -> bool:
        inserted = self._run(
            "INSERT INTO stripe_events (id, type, processed_at) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
            (event_id, event_type, _now_iso()),
        )
        return inserted > 0

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
    def log_purchase(
        self, user_id: str, product_id: str, platform: str, purchase_id: Optional[str] = None
    ) -> dict:
        """구매 내역 기록. purchase_id가 주어지면 멱등적(ON CONFLICT DO NOTHING)으로 삽입."""
        pid = purchase_id or uuid.uuid4().hex
        self._run(
            "INSERT INTO purchases (id, user_id, product_id, platform, purchased_at) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT (id) DO NOTHING",
            (pid, user_id, product_id, platform, _now_iso()),
        )
        return self._one("SELECT * FROM purchases WHERE id = ?", (pid,))

    def add_onetime_purchase_idempotent(
        self, user_id: str, order_id: str, platform: str = "lemon_squeezy",
        product_id: str = "lemon_onetime",
    ) -> bool:
        """
        1회권 구매 원자적 멱등 처리:
        동일 purchase_id(lemon_order_{order_id})가 이미 purchases에 존재하면
        중복 크레딧을 지급하지 않고 False 반환.
        신규 주문이면 purchases 기록 및 onetime_credits +1 증가 후 True 반환.
        """
        purchase_id = f"lemon_order_{order_id}" if not str(order_id).startswith("lemon_") else str(order_id)
        
        # 1. purchases에 삽입 시도 (idempotency anchor)
        inserted = self._run(
            "INSERT INTO purchases (id, user_id, product_id, platform, purchased_at) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT (id) DO NOTHING",
            (purchase_id, user_id, product_id, platform, _now_iso()),
        )
        if inserted == 0:
            # 이미 처리된 주문 (중복 웹훅)
            return False

        # 2. 신규 주문에 한해서만 크레딧 +1 증가
        try:
            self.add_onetime_credit(user_id)
        except Exception:
            # 크레딧 지급 실패 시 구매 기록을 되돌려 재시도가 가능하게 함
            self._run("DELETE FROM purchases WHERE id = ?", (purchase_id,))
            raise
        return True

    def record_purchase_once(
        self, user_id: str, product_id: str, platform: str, purchase_id: str
    ) -> bool:
        """결제 1건을 멱등적으로 기록. 새로 기록했으면 True, 이미 있던 결제면 False."""
        inserted = self._run(
            "INSERT INTO purchases (id, user_id, product_id, platform, purchased_at) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT (id) DO NOTHING",
            (purchase_id, user_id, product_id, platform, _now_iso()),
        )
        return inserted != 0

    def delete_purchase(self, purchase_id: str) -> None:
        """지급 처리에 실패했을 때 기록을 되돌려 재시도가 가능하게 한다."""
        self._run("DELETE FROM purchases WHERE id = ?", (purchase_id,))

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
    def upsert_telegram_subscriber(
        self, telegram_id: str, user_id: str, lang: str = "ko"
    ) -> None:
        """검증된 telegram_id 를 사용자 계정에 연결 (재등록 시 소유자·lang 갱신)."""
        self._run(
            "INSERT INTO telegram_subscribers "
            "(telegram_id, user_id, created_at, language_code) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(telegram_id) DO UPDATE SET "
            "user_id = excluded.user_id, "
            "language_code = excluded.language_code",
            (telegram_id, user_id, _now_iso(), lang),
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
        """[{telegram_id, user_id, language_code}] — 프로필이 있는 구독자만 푸시 대상.

        language_code 는 NULL 가능 (Phase 4-B 이전 등록 row). 이 경우
        호출자가 전역 lang 폴백을 적용한다.
        """
        return self._all(
            "SELECT telegram_id, user_id, language_code "
            "FROM telegram_subscribers ORDER BY created_at"
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
            # migration (Phase 4-B): existing DBs need ADD COLUMN
            cols = {
                r[1]
                for r in self._conn.execute(
                    "PRAGMA table_info(telegram_subscribers)"
                ).fetchall()
            }
            if "language_code" not in cols:
                self._conn.execute(
                    "ALTER TABLE telegram_subscribers "
                    "ADD COLUMN language_code TEXT"
                )


            # migration (2026-11 Stripe)
            u_cols = {r[1] for r in self._conn.execute("PRAGMA table_info(users)").fetchall()}
            for col in ["stripe_customer_id", "stripe_subscription_id", "subscription_status", "current_period_end", "email"]:
                if col not in u_cols:
                    self._conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
            try:
                self._conn.execute("ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass  # 이미 컬럼이 존재하면 무시
            try:
                self._conn.execute("ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass  # 이미 컬럼이 존재하면 무시
            self._conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_stripe_customer ON users(stripe_customer_id) WHERE stripe_customer_id IS NOT NULL")
            self._conn.execute("CREATE TABLE IF NOT EXISTS stripe_events (id TEXT PRIMARY KEY, type TEXT NOT NULL, processed_at TEXT NOT NULL)")
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
            # prepare_threshold=None: Supabase pgbouncer(transaction 모드)에서도 안전
            kwargs={"row_factory": dict_row, "prepare_threshold": None},
            check=ConnectionPool.check_connection,  # 끊어진 연결 자동 폐기
            max_idle=60,
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
            # migration (Phase 4-B)
            row = conn.execute(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = 'telegram_subscribers' "
                "AND column_name = 'language_code' "
                "AND table_schema = current_schema()"
            ).fetchone()
            if row is None:
                conn.execute(
                    "ALTER TABLE telegram_subscribers "
                    "ADD COLUMN language_code TEXT"
                )


            # migration (2026-11 Stripe)
            for col in ["stripe_customer_id", "stripe_subscription_id", "subscription_status", "current_period_end", "email"]:
                r = conn.execute("SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name=%s AND table_schema=current_schema()", (col,)).fetchone()
                if r is None:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
            r = conn.execute("SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='onetime_credits' AND table_schema=current_schema()").fetchone()
            if r is None:
                conn.execute("ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0")
            r = conn.execute("SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='onetime_credits' AND table_schema=current_schema()").fetchone()
            if r is None:
                conn.execute("ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0")
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_stripe_customer ON users(stripe_customer_id) WHERE stripe_customer_id IS NOT NULL")
            conn.execute("CREATE TABLE IF NOT EXISTS stripe_events (id TEXT PRIMARY KEY, type TEXT NOT NULL, processed_at TEXT NOT NULL)")
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
    from app.ops.env import is_production
    is_prod = is_production()
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
