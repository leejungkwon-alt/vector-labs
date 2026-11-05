from pathlib import Path

p = Path("app/auth/repository.py")
t = p.read_text(encoding="utf-8")

# 1. 잘못 들어간 check / max_idle 제거 (os.environ.get 내부)
t = t.replace(
    'int(os.environ.get("SAJU_DB_POOL_MIN", "1", check=ConnectionPool.check_connection, max_idle=60))',
    'int(os.environ.get("SAJU_DB_POOL_MIN", "1"))'
)

# 2. ConnectionPool(...) 호출에 check / max_idle 추가 (제대로 된 위치)
# 우선 현재 ConnectionPool 호출 모양 확인
import re
# ConnectionPool(...) 블록의 마지막 인자 뒤에 추가
pattern = re.compile(
    r'(ConnectionPool\()([^)]*)(\))',
    re.DOTALL
)
def repl(m):
    args = m.group(2)
    if "check=" in args and "max_idle=" in args:
        return m.group(0)
    # 기존 args 정리
    args = args.strip()
    if args and not args.endswith(','):
        args += ', '
    else:
        args += ' '
    # check와 max_idle이 없으면 추가
    extras = []
    if "check=" not in args:
        extras.append("check=ConnectionPool.check_connection")
    if "max_idle=" not in args:
        extras.append("max_idle=60")
    if extras:
        args = args.rstrip(', ') + ', ' + ', '.join(extras)
    return f"ConnectionPool({args})"

t = pattern.sub(repl, t)

p.write_text(t, encoding="utf-8")
print("[OK] repository.py ConnectionPool 인자 위치 정확히 수정 완료")
