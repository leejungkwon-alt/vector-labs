from pathlib import Path

p = Path("app/auth/repository.py")
t = p.read_text(encoding="utf-8")

# 1. 잘못된 import 문 수정
t = t.replace(
    "from psycopg_pool import ConnectionPool, check_connection",
    "from psycopg_pool import ConnectionPool"
)

# 2. check=check_connection 을 ConnectionPool.check_connection 로 수정
t = t.replace(
    "check=check_connection",
    "check=ConnectionPool.check_connection"
)

# 3. 혹시 남아있을 수 있는 다른 형태도 수정
t = t.replace(
    ", check_connection",
    ""
)

p.write_text(t, encoding="utf-8")
print("[OK] repository.py ImportError 수정 완료")
