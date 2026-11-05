#!/usr/bin/env python3
"""
SAJU 프로젝트 자동 수정 스크립트 (제자리 수정 / 멱등 / 실행 전 .orig 백업은 만들지 않음 -> git 커밋 후 실행 권장)

사용:  프로젝트 루트(C:\\Users\\lenovo\\Desktop\\SAJU)에서
        python apply_fixes.py            # 적용
        python apply_fixes.py --check    # 변경 없이 무엇이 바뀔지만 확인
파일 전체를 덮어쓰지 않고 '해당 부분만' 치환하므로 .env/시크릿/토큰키 등 기존 값은 건드리지 않습니다.
"""
import shutil, sys
from pathlib import Path

CHECK = "--check" in sys.argv
ROOT = Path(".")
HERE = Path(__file__).resolve().parent
changed = []

def rd(p): return (ROOT / p).read_text(encoding="utf-8")
def wr(p, t):
    if not CHECK: (ROOT / p).write_text(t, encoding="utf-8", newline="\n")
    changed.append(p)

def between(t, start, end):
    a = t.index(start); b = t.index(end, a); return a, b

# 1) DB 커넥션 풀 — 500 에러의 직접 원인 --------------------------------------
p = "app/auth/repository.py"; t = rd(p)
if 'os.environ.get("SAJU_DB_POOL_MIN", "1", check=' in t:
    a, b = between(t, "        self._pool = ConnectionPool(", "        self._init_schema()\n\n    @staticmethod")
    t = t[:a] + '''        self._pool = ConnectionPool(
            conninfo=database_url,
            min_size=int(os.environ.get("SAJU_DB_POOL_MIN", "1")),
            max_size=int(os.environ.get("SAJU_DB_POOL_MAX", "5")),
            # prepare_threshold=None: Supabase pgbouncer(transaction 모드)에서도 안전
            kwargs={"row_factory": dict_row, "prepare_threshold": None},
            check=ConnectionPool.check_connection,  # 끊어진 연결 자동 폐기
            max_idle=60,
            open=True,
            timeout=10,
        )
''' + t[b:]
    wr(p, t)

# 2) middleware.py — 내부 500 에도 CORS 헤더가 붙도록 ----------------------------
p = "app/ops/middleware.py"; t = rd(p)
if "JSONResponse" not in t:
    new = (HERE / "middleware.py.new").read_text(encoding="utf-8")
    wr(p, new)

# 3) main.py — 중복 CORS 블록 제거 + 정규식 env 화 -------------------------------
p = "app/main.py"; t = rd(p)
if t.count("_cors_origins = [") > 1:
    a = t.index("app.add_middleware(\n    RateLimitMiddleware")
    b = t.index("app.include_router(saju.router")
    t = t[:a] + '''# Starlette: 마지막에 add 한 미들웨어가 가장 바깥(outermost).
# 요청 흐름: CORS -> RequestContext -> RateLimit -> 라우터
# (그래서 429/500 응답에도 CORS 헤더가 붙는다.)
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

# 미리보기 배포(*.vercel.app) 허용 정규식. 빈 문자열이면 비활성화.
_cors_regex = os.getenv("SAJU_CORS_ORIGIN_REGEX", r"https://.*\\.vercel\\.app").strip() or None

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

''' + t[b:]
    wr(p, t)

# 4) frontend/src/api/client.ts ---------------------------------------------------
p = "frontend/src/api/client.ts"; t = rd(p)
if "function extractDetail" not in t:
    a, b = between(t, "    if (res.status === 204)", "export const api = {")
    t = t[:a] + '''    if (res.status === 204) return undefined as T;

    const text = await res.text();
    // 502/404 등 HTML 응답이 와도 SyntaxError 로 터지지 않게 방어
    let body: any = null;
    if (text) {
      try { body = JSON.parse(text); } catch { body = null; }
    }

    if (!res.ok) {
      throw new ApiError(res.status, extractDetail(body, res.status));
    }
    return body as T;
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err instanceof ApiError) throw err;
    if (err?.name === "AbortError") {
      throw new ApiError(408, "서버 응답 시간이 초과되었습니다. 네트워크 상태를 확인해주세요.");
    }
    // fetch 자체가 실패(서버 다운 / CORS / 오프라인) -> 브라우저는 그냥 TypeError("Failed to fetch")
    if (err instanceof TypeError) {
      throw new ApiError(0, "서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.");
    }
    throw err;
  }
}

// FastAPI 의 422 는 detail 이 객체 배열이라 String() 하면 "[object Object]" 가 된다.
function extractDetail(body: any, status: number): string {
  const d = body && (body.detail ?? body.message);
  if (Array.isArray(d)) {
    return d.map((x: any) => x?.msg ?? JSON.stringify(x)).join("\\n");
  }
  if (d && typeof d === "object") return JSON.stringify(d);
  return d ? String(d) : `HTTP ${status}`;
}

''' + t[b:]
    wr(p, t)

# 5) frontend/src/store/authStore.ts — 일시 장애 때 계정이 갈아끼워지는 버그 ------
#    (TOKEN_KEY / 카카오 엔드포인트 등 기존 값은 그대로 둠)
p = "frontend/src/store/authStore.ts"; t = rd(p)
if "authError" not in t:
    t = t.replace("import { api, setAuthToken } from '../api/client';",
                  "import { api, setAuthToken, ApiError } from '../api/client';")
    a, b = between(t, "  bootstrap: async () => {", "  linkAccount: async")
    t = t[:a] + '''  bootstrap: async () => {
    const createAnonymous = async () => {
      const res = await api.anonymous();
      await storage.setItem(TOKEN_KEY, res.access_token);
      setAuthToken(res.access_token);
      set({ user: res.user, ready: true, authError: null });
    };

    try {
      const t = await storage.getItem(TOKEN_KEY);

      // 1. 저장된 토큰이 없으면 새 익명 계정
      if (!t) {
        await createAnonymous();
        return;
      }

      // 2. 토큰이 있으면 유효성 검사
      setAuthToken(t);
      try {
        const me = await api.me();
        set({ user: me.user, ready: true, authError: null });
      } catch (e) {
        // 토큰이 "진짜로" 무효일 때(401)만 새 계정을 만든다.
        // 네트워크/500 같은 일시 장애에서 새 계정을 만들면 기존 계정(구독 포함)을 잃는다.
        if (e instanceof ApiError && e.status === 401) {
          await createAnonymous();
        } else {
          throw e;
        }
      }
    } catch (e: any) {
      console.warn('[auth] bootstrap failed:', e);
      set({ ready: true, authError: e?.detail ?? e?.message ?? 'auth failed' });
    }
  },
''' + t[b:]
    t = t.replace("  ready: boolean;\n  bootstrap", "  ready: boolean;\n  authError: string | null;\n  bootstrap")
    t = t.replace("  user: null,\n  ready: false,\n  bootstrap", "  user: null,\n  ready: false,\n  authError: null,\n  bootstrap")
    wr(p, t)

# 6) settings.tsx — 로그인 실패(user=null) 상태에서 '프리미엄 이용 중' 표시 ----------
p = "frontend/app/(tabs)/settings.tsx"; t = rd(p)
if '{user?.tier !== "free" && (' in t:
    wr(p, t.replace('{user?.tier !== "free" && (', '{!!user && user.tier !== "free" && ('))

# 7) 회귀 테스트 추가 --------------------------------------------------------------
dst = ROOT / "tests" / "test_regression_pool_cors.py"
if not dst.exists():
    changed.append("tests/test_regression_pool_cors.py (new)")
    if not CHECK: shutil.copy(HERE / "tests" / "test_regression_pool_cors.py", dst)

print(("[CHECK] 변경 예정" if CHECK else "[OK] 변경 완료") + f" {len(changed)}개:")
for c in changed: print("  -", c)
if not changed: print("  (이미 모두 적용됨)")
