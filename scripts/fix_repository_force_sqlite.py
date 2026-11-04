import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "app" / "auth" / "repository.py"

t = p.read_text(encoding="utf-8")

# _build_repository 함수에서 SAJU_DATABASE_URL을 아예 무시하도록 수정
old = '''def _build_repository():
    url = os.getenv("SAJU_DATABASE_URL", "").strip()
    if url:
        return PostgresRepository(url)'''
new = '''def _build_repository():
    # Phase 3 hotfix: Cloud Run에서 잘못된 SAJU_DATABASE_URL(Secret)로 인한
    # PoolTimeout 방지를 위해, SQLite 전용으로 강제합니다.
    # PostgreSQL은 향후 정식 마이그레이션 시 재활성화합니다.
    db_path = os.getenv("SAJU_DB_PATH", "data/auth.db")
    return SQLiteRepository(db_path)'''

if old in t:
    t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print("[OK] repository.py 수정 완료 (SAJU_DATABASE_URL 무시, SQLite 강제)")
else:
    # 다른 패턴으로 시도
    pattern = re.compile(r'def _build_repository\(\):.*?return PostgresRepository\(url\)', re.DOTALL)
    if pattern.search(t):
        t = pattern.sub(new, t)
        p.write_text(t, encoding="utf-8")
        print("[OK] repository.py 수정 완료 (패턴2)")
    else:
        print("[ERR] _build_repository 함수를 찾지 못했습니다. 파일을 확인해주세요.")
