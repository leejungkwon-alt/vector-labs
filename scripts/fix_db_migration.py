import os
import shutil

filepath = "app/auth/repository.py"

if os.path.exists(filepath):
    shutil.copy2(filepath, filepath + ".bak")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. SQLite Repository 마이그레이션 추가
    sqlite_old = """            for col in ["stripe_customer_id", "stripe_subscription_id", "subscription_status", "current_period_end", "email"]:
                if col not in u_cols:
                    self._conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")"""
    
    sqlite_new = """            for col in ["stripe_customer_id", "stripe_subscription_id", "subscription_status", "current_period_end", "email"]:
                if col not in u_cols:
                    self._conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
            if "onetime_credits" not in u_cols:
                self._conn.execute("ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0")"""

    # 2. Postgres Repository 마이그레이션 추가
    pg_old = """            for col in ["stripe_customer_id", "stripe_subscription_id", "subscription_status", "current_period_end", "email"]:
                r = conn.execute("SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name=%s AND table_schema=current_schema()", (col,)).fetchone()
                if r is None:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")"""
    
    pg_new = """            for col in ["stripe_customer_id", "stripe_subscription_id", "subscription_status", "current_period_end", "email"]:
                r = conn.execute("SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name=%s AND table_schema=current_schema()", (col,)).fetchone()
                if r is None:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
            r = conn.execute("SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='onetime_credits' AND table_schema=current_schema()").fetchone()
            if r is None:
                conn.execute("ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0")"""

    # 치환 적용
    if sqlite_old in content:
        content = content.replace(sqlite_old, sqlite_new)
        print("✅ SQLite 마이그레이션(onetime_credits) 추가 완료")
    else:
        print("⚠️ SQLite 마이그레이션 패턴을 찾지 못했습니다.")

    if pg_old in content:
        content = content.replace(pg_old, pg_new)
        print("✅ Postgres 마이그레이션(onetime_credits) 추가 완료")
    else:
        print("⚠️ Postgres 마이그레이션 패턴을 찾지 못했습니다.")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("\n✨ DB 마이그레이션 코드 수정 완료! 이제 다시 배포를 실행하세요.")
else:
    print(f"❌ 파일을 찾을 수 없습니다: {filepath}")