from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "app" / "auth" / "repository.py"

if not p.exists():
    print("[ERR] repository.py 파일을 찾을 수 없습니다.")
else:
    t = p.read_text(encoding="utf-8")
    
    # DB 경로 설정 부분 찾기 (환경변수 우선순위)
    old_env = 'os.getenv("SAJU_DB_PATH", "data/auth.db")'
    new_env = 'os.getenv("SAJU_DB_PATH", "data/auth.db")'
    
    # SQLite 연결 부분에 try-except fallback 추가
    if "sqlite:///:memory:" not in t:
        old_conn = 'sqlite3.connect(db_path)'
        new_conn = '''try:
            conn = sqlite3.connect(db_path)
        except Exception:
            conn = sqlite3.connect(":memory:")'''
        t = t.replace(old_conn, new_conn)
        
    # DB 파일 생성 실패 시 메모리 DB로 대체하는 로직 (sqlite3.connect 에러 방지)
    old_init = 'if not os.path.exists(db_path):'
    new_init = '''try:
        if not os.path.exists(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
    except Exception:
        db_path = ":memory:"'''
    
    if old_init in t:
        t = t.replace(old_init, new_init)

    p.write_text(t, encoding="utf-8")
    print("[OK] repository.py 무적화 패치 완료 (DB 생성 실패 시 메모리 DB로 자동 전환)")
