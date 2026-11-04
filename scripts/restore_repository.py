from pathlib import Path

p = Path("app/auth/repository.py")
t = p.read_text(encoding="utf-8")

# 제가 잘못 넣은 SQLite 강제 패치를 원래대로 되돌림
bad = '''def _build_repository():
    # Phase 3 hotfix: Cloud Run에서 잘못된 SAJU_DATABASE_URL(Secret)로 인한
    # PoolTimeout 방지를 위해, SQLite 전용으로 강제합니다.
    # PostgreSQL은 향후 정식 마이그레이션 시 재활성화합니다.
    db_path = os.getenv("SAJU_DB_PATH", "data/auth.db")
    return SQLiteRepository(db_path)'''

good = '''def _build_repository():
    url = os.getenv("SAJU_DATABASE_URL", "").strip()
    if url:
        return PostgresRepository(url)
    return SQLiteRepository(os.getenv("SAJU_DB_PATH", "data/auth.db"))'''

if bad in t:
    t = t.replace(bad, good)
    p.write_text(t, encoding="utf-8")
    print("[OK] repository.py 원상복구 완료 (Postgres 우선, SQLite 폴백)")
else:
    print("[SKIP] 이미 원래대로이거나 패턴 불일치")
