"""SQLite / Postgres 스키마 마이그레이션 **대칭성** 정적 검사.

사고 배경
  `birth_time_mode` ALTER 를 SQLite `_init_schema` 블록에만 추가하고
  `PostgresRepository._init_schema` 에 빠뜨려, Neon(Postgres) 운영 DB 에
  컬럼이 생기지 않았고 upsert 가 UndefinedColumn 으로 실패했다.
  테스트는 전부 SQLite 만 돌기 때문에 이 결함이 잡히지 않았다.

그래서 여기서는 **소스를 직접 파싱**해 두 백엔드의 ALTER 목록을 비교한다.
(Postgres 서버 없이도 누락을 잡는 것이 목적)
"""
import ast
import pathlib
import re

import pytest

from app.auth import repository as repo_mod

SRC_PATH = pathlib.Path(repo_mod.__file__)


def _load_source() -> str:
    return SRC_PATH.read_text(encoding="utf-8")


def _class_method_source(cls, method: str) -> str:
    """클래스 메서드 본문 소스만 잘라낸다(다른 백엔드 블록과 섞이지 않게)."""
    tree = ast.parse(_load_source())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method:
                    segment = ast.get_source_segment(_load_source(), item)
                    assert segment, f"{cls}.{method} 소스를 찾을 수 없음"
                    return segment
    raise AssertionError(f"{cls}.{method} 정의를 찾을 수 없음")


_SQLITE_INIT = _class_method_source("Repository", "_init_schema")
_PG_INIT = _class_method_source("PostgresRepository", "_init_schema")


def _sqlite_altered_columns(src: str) -> set[tuple[str, str]]:
    """SQLite 블록에서 ALTER 하는 (테이블, 컬럼).

    `self._conn.execute("ALTER TABLE profiles ADD COLUMN mbti TEXT")`
    `self._conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")` (루프) 둘 다 인식.
    """
    found = set()
    for m in re.finditer(r'ALTER TABLE (\w+) ADD COLUMN (\w+)', src):
        found.add((m.group(1).lower(), m.group(2).lower()))
    # 루프로 컬럼명을 넣는 경우(f-string {col})는 실제 목록 리터럴을 따라간다.
    for loop in re.finditer(r'for col in \[([^\]]+)\]', src):
        cols = re.findall(r'"([a-z_]+)"', loop.group(1))
        for c in cols:
            found.add(("users", c.lower()))
    return found


def _pg_altered_columns(src: str) -> set[tuple[str, str]]:
    """Postgres 블록에서 ALTER 하는 (테이블, 컬럼). IF NOT EXISTS 형태 포함."""
    found = set()
    for m in re.finditer(r'ALTER TABLE (\w+) ADD COLUMN (?:IF NOT EXISTS )?(\w+)', src):
        found.add((m.group(1).lower(), m.group(2).lower()))
    # 두 줄로 쪼개진 문자열("... ADD COLUMN IF NOT EXISTS " + "dob_change_count ...") 대응
    for m in re.finditer(r'ADD COLUMN IF NOT EXISTS (?:"\s*\n\s*")?(\w+)', src):
        found.add(("profiles", m.group(1).lower()))
    for loop in re.finditer(r'for col in \[([^\]]+)\]', src):
        cols = re.findall(r'"([a-z_]+)"', loop.group(1))
        for c in cols:
            found.add(("users", c.lower()))
    return found


# ============================================================
# 1) 사고 재발 방지: birth_time_mode 가 Postgres 블록에도 있어야 한다
# ============================================================

def test_postgres_init_schema_adds_birth_time_mode():
    assert "birth_time_mode" in _PG_INIT, (
        "PostgresRepository._init_schema 에 birth_time_mode ALTER 누락 — "
        "Neon/Postgres 에서 upsert 가 UndefinedColumn 으로 실패한다"
    )
    assert ("profiles", "birth_time_mode") in _pg_altered_columns(_PG_INIT)


def test_sqlite_init_schema_adds_birth_time_mode():
    assert ("profiles", "birth_time_mode") in _sqlite_altered_columns(_SQLITE_INIT)


# ============================================================
# 2) 대칭성: 두 백엔드의 ALTER 목록이 동일해야 한다
# ============================================================

def test_alter_lists_are_symmetric():
    sqlite_cols = _sqlite_altered_columns(_SQLITE_INIT)
    pg_cols = _pg_altered_columns(_PG_INIT)

    missing_in_pg = sorted(sqlite_cols - pg_cols)
    missing_in_sqlite = sorted(pg_cols - sqlite_cols)
    assert missing_in_pg == [], f"SQLite 에만 있는 ALTER(Postgres 누락): {missing_in_pg}"
    assert missing_in_sqlite == [], f"Postgres 에만 있는 ALTER(SQLite 누락): {missing_in_sqlite}"


# ============================================================
# 3) _SCHEMA_STATEMENTS 컬럼 ⊂ (CREATE + ALTER) 인지 (양쪽 공통)
# ============================================================

def _columns_declared_in_schema_statements() -> dict[str, set[str]]:
    """_SCHEMA_STATEMENTS 의 CREATE TABLE 컬럼 목록."""
    out: dict[str, set[str]] = {}
    for stmt in repo_mod._SCHEMA_STATEMENTS:
        m = re.search(r"CREATE TABLE IF NOT EXISTS (\w+)\s*\((.*)\)", stmt, re.S)
        if not m:
            continue
        table, body = m.group(1).lower(), m.group(2)
        for line in body.splitlines():
            line = line.strip().rstrip(",")
            if not line:
                continue
            first = line.split()[0].lower()
            if first in ("primary", "unique", "foreign", "check", "constraint"):
                continue
            out.setdefault(table, set()).add(first)
    return out


# CREATE TABLE(_SCHEMA_STATEMENTS)에는 없고 ALTER 로만 추가되는 "허용된" 컬럼.
# (2026-11 Stripe/크레딧: 기존·신규 DB 모두 ALTER 를 거치므로 모양은 같다.
#  CREATE 에 넣지 않는 이유는 기존 테이블 정의를 건드리지 않기 위함 — 운영 관례 유지)
_ALTER_ONLY_ALLOWED = {
    ("users", "stripe_customer_id"),
    ("users", "stripe_subscription_id"),
    ("users", "subscription_status"),
    ("users", "current_period_end"),
    ("users", "onetime_credits"),
}


def test_schema_columns_covered_by_migrations():
    """ALTER 로만 추가되는 컬럼은 **허용 목록에만** 있어야 한다.

    새 컬럼을 ALTER 로만 추가하면 여기서 실패한다 → CREATE TABLE 에도 넣거나
    의도적으로 허용 목록에 추가(=리뷰 강제)하도록 만든다.
    """
    declared = _columns_declared_in_schema_statements()
    altered_both = _sqlite_altered_columns(_SQLITE_INIT) | _pg_altered_columns(_PG_INIT)
    for table, cols in declared.items():
        altered = {c for (t, c) in altered_both if t == table}
        missing = sorted(c for c in (altered - cols) if (table, c) not in _ALTER_ONLY_ALLOWED)
        assert missing == [], (
            f"[{table}] ALTER 로만 추가되고 CREATE TABLE 에 없는 컬럼: {missing} "
            "(CREATE 에 추가하거나 _ALTER_ONLY_ALLOWED 에 근거와 함께 등록)"
        )




def test_profiles_required_columns_present_in_both_creates():
    """profiles 의 upsert 가 쓰는 핵심 컬럼이 CREATE/ALTER 어딘가에는 정의돼야 한다."""
    declared = _columns_declared_in_schema_statements().get("profiles", set())
    altered = {c for (t, c) in _sqlite_altered_columns(_SQLITE_INIT) | _pg_altered_columns(_PG_INIT) if t == "profiles"}
    available = declared | altered
    for col in ("user_id", "birth_date", "birth_time", "birth_time_mode", "updated_at"):
        assert col in available, f"profiles.{col} 이 CREATE/ALTER 어디에도 없음"
