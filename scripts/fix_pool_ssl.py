import re
from pathlib import Path

p = Path("app/auth/repository.py")
t = p.read_text(encoding="utf-8")

# 1. import 문 수정 (check_connection 추가)
if "check_connection" not in t:
    # 기존 psycopg_pool import 라인 찾기
    old_import_pattern = re.compile(r'from\s+psycopg_pool\s+import\s+([^\n]+)')
    match = old_import_pattern.search(t)
    if match:
        imports = match.group(1)
        if "check_connection" not in imports:
            t = t.replace(match.group(0), f"from psycopg_pool import {imports}, check_connection")
    else:
        # 혹시 import psycopg_pool 형태라면
        t = t.replace("import psycopg_pool", "import psycopg_pool\nfrom psycopg_pool import check_connection")

# 2. ConnectionPool(...) 생성자에 check와 max_idle 추가
pattern = re.compile(r'ConnectionPool\(([^)]*)\)')
def repl(m):
    args = m.group(1)
    # 이미 있으면 건너뜀
    if "check=" in args and "max_idle=" in args:
        return m.group(0)
    
    new_args = args.strip()
    if new_args and not new_args.endswith(','):
        new_args += ', '
    
    if "check=" not in new_args:
        new_args += "check=check_connection, "
    if "max_idle=" not in new_args:
        new_args += "max_idle=60"
    
    # 뒤에 쉼표가 남으면 제거
    new_args = new_args.rstrip(", ")
    return f"ConnectionPool({new_args})"

t = pattern.sub(repl, t)
p.write_text(t, encoding="utf-8")
print("[OK] repository.py 커넥션 풀 무적화 완료 (check_connection, max_idle=60)")
