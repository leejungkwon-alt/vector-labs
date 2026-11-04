import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "app" / "main.py"
t = p.read_text(encoding="utf-8")

# 1. 모든 add_middleware 호출 제거
t = re.sub(r'app\.add_middleware\(.*?\)\n', '', t, flags=re.DOTALL)

# 2. add_middleware를 다시 배치 (CORSMiddleware가 가장 마지막 = Outermost)
middlewares = """
app.add_middleware(
    RateLimitMiddleware,
    max_requests=int(os.getenv("SAJU_RATE_LIMIT_MAX", "120")),
    window_seconds=int(os.getenv("SAJU_RATE_LIMIT_WINDOW", "60")),
)

app.add_middleware(RequestContextMiddleware)

_cors_origins = [
    o.strip()
    for o in os.getenv("SAJU_CORS_ORIGINS", "*").split(",")
    if o.strip()
]
if "*" in _cors_origins and is_production():
    logging.getLogger("saju.security").warning(
        "SAJU_CORS_ORIGINS=* in production. Set explicit origins."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"https://.*\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)
"""

# 3. app 변수 정의 부분을 찾아서 그 뒤에 미들웨어 삽입
anchor = 'app = FastAPI('
idx = t.find(anchor)
if idx != -1:
    # FastAPI(...) 블록의 끝 찾기
    end_idx = t.find(')\n', idx) + 2
    t = t[:end_idx] + middlewares + t[end_idx:]
    p.write_text(t, encoding="utf-8")
    print("[OK] main.py 미들웨어 순서 완벽 수정 완료 (CORS가 Outermost)")
else:
    print("[ERR] app = FastAPI( 앵커를 찾을 수 없습니다.")
