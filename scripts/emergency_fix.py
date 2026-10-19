from pathlib import Path
import json
import subprocess
import re

BASE = Path.cwd()

# ============================================================
# 1. main.py CORS 설정 강제 재작성 (역슬래시 문제 해결)
# ============================================================
MAIN_PY = BASE / "app" / "main.py"
text = MAIN_PY.read_text(encoding="utf-8")

# 기존 add_middleware(CORSMiddleware, ...) 블록을 통째로 교체
pattern = re.compile(
    r"app\.add_middleware\(\s*CORSMiddleware,.*?\n\)",
    re.DOTALL
)

# 정규식 패턴은 r"..." 로 raw string 사용 (역슬래시 이스케이프 방지)
new_cors_block = (
    'app.add_middleware(\n'
    '    CORSMiddleware,\n'
    '    allow_origins=_cors_origins,\n'
    '    allow_origin_regex=r"https://.*\\.vercel\\.app",\n'
    '    allow_credentials=False,\n'
    '    allow_methods=["*"],\n'
    '    allow_headers=["*"],\n'
    '    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],\n'
    ')'
)

if pattern.search(text):
    text = pattern.sub(new_cors_block, text, count=1)
    MAIN_PY.write_text(text, encoding="utf-8")
    print("✅ main.py CORS 설정 재작성 완료")
else:
    print("⚠️ CORSMiddleware 블록을 찾지 못했습니다. 수동 확인 필요")

# 문법 검사
import py_compile
try:
    py_compile.compile(str(MAIN_PY), doraise=True)
    print("✅ main.py 문법 OK")
except py_compile.PyCompileError as e:
    print(f"❌ main.py 문법 오류: {e}")
    print("   VSCode에서 main.py 68~70번째 줄의 allow_origin_regex 부분을 확인하세요.")
    print("   반드시 r\"https://.*\\.vercel\\.app\" 형태(앞에 r)여야 합니다.")

# ============================================================
# 2. vercel.json 원상 복구 (/api/$1)
# ============================================================
VERCEL_JSON = BASE / "vercel.json"
CLOUDRUN_URL = "https://vector-labs-api-787049663118.asia-northeast3.run.app"

config = {
    "buildCommand": "npm run build",
    "outputDirectory": "dist",
    "framework": "vite",
    "rewrites": [
        {
            "source": "/api/(.*)",
            "destination": f"{CLOUDRUN_URL}/api/$1"  # ✅ /api/$1 이 올바른 경로입니다
        }
    ]
}
VERCEL_JSON.write_text(json.dumps(config, indent=2), encoding="utf-8")
print(f"\n✅ vercel.json 복구 완료 (destination: {CLOUDRUN_URL}/api/$1)")

# ============================================================
# 3. 강제 커밋 & 푸시 (--allow-empty 사용)
# ============================================================
print("\n[3] 강제 커밋 & 푸시")
subprocess.run(["git", "add", "-A"], check=True)
try:
    subprocess.run(
        ["git", "commit", "-m", "fix: correct CORS regex in main.py & vercel proxy path"],
        check=True,
    )
except subprocess.CalledProcessError:
    print("  변경 사항이 없어 --allow-empty로 재시도")
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "fix: correct CORS regex & proxy path"],
        check=True,
    )

subprocess.run(["git", "push", "origin", "main"], check=True)
print("✅ 깃허브 업로드 완료! Vercel 자동 재배포 시작.")

print("\n" + "=" * 60)
print("  🚀 다음 단계 (수동 실행 필요):")
print("=" * 60)
print("  1. Cloud Run 백엔드 재배포:")
print("     gcloud run deploy vector-labs-api --source . --region asia-northeast3 --allow-unauthenticated --memory 512Mi --cpu 1 --min-instances 0 --max-instances 3 --cpu-boost --port 8000 --set-env-vars \"SAJU_ENV=production,SAJU_CORS_ORIGINS=*\" --set-secrets \"SAJU_JWT_SECRET=SAJU_JWT_SECRET:latest\"")
print("\n  2. 백엔드 서버 깨우기 (브라우저에서 접속):")
print(f"     {CLOUDRUN_URL}/docs")
print("\n  3. 텔레그램 봇에서 [Open] 버튼 재클릭")