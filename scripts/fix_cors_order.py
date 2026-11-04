from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "app" / "main.py"

t = p.read_text(encoding="utf-8")

# 1. 기존 RequestContextMiddleware 추가 줄 제거
t = t.replace("app.add_middleware(RequestContextMiddleware)\n", "")

# 2. CORSMiddleware 추가 블록 뒤에 RequestContextMiddleware를 다시 추가 (CORS가 outermost가 되도록)
anchor = "app.add_middleware(\n    CORSMiddleware,"
if anchor in t:
    # CORSMiddleware 블록의 끝을 찾기 위해 ')' 위치를 찾음
    start = t.find(anchor)
    end = t.find(")\n", start) + 2
    # CORSMiddleware 블록 뒤에 RequestContextMiddleware 추가
    t = t[:end] + "\napp.add_middleware(RequestContextMiddleware)\n" + t[end:]
    
    # 이제 RequestContextMiddleware가 CORS보다 먼저 추가되었으므로, CORS가 outermost가 됨 (마지막 추가 = outermost)
    # 하지만 현재는 RequestContextMiddleware가 CORS 뒤에 있음. 즉, RequestContextMiddleware가 outermost가 됨.
    # 우리는 CORS를 outermost로 만들고 싶으므로, CORS 블록을 RequestContextMiddleware 뒤로 옮겨야 함.
    
    # 더 간단한 방법: RequestContextMiddleware를 CORS 앞으로 이동
    # 현재: CORS ... RequestContext
    # 목표: RequestContext ... CORS (CORS가 마지막에 추가되어 outermost)
    
    # 기존 RequestContext 줄 제거
    t = t.replace("app.add_middleware(RequestContextMiddleware)\n", "")
    
    # CORS 블록 앞에 RequestContext 추가
    t = t.replace(anchor, "app.add_middleware(RequestContextMiddleware)\n\n" + anchor, 1)

p.write_text(t, encoding="utf-8")
print("[OK] main.py 미들웨어 순서 수정 완료 (CORS가 outermost가 됨)")
