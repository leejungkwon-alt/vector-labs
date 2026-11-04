import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. main.py CORS 순서 수정 (CORS가 무조건 outermost가 되도록)
p_main = ROOT / "app" / "main.py"
t_main = p_main.read_text(encoding="utf-8")

# 기존 CORS 블록 찾기
cors_pattern = re.compile(r'app\.add_middleware\(\s*CORSMiddleware,.*?\)\n', re.DOTALL)
cors_match = cors_pattern.search(t_main)
if cors_match:
    cors_block = cors_match.group(0)
    # 기존 CORS 블록 제거
    t_main = t_main.replace(cors_block, "")
    
    # RequestContextMiddleware 제거 (중복 방지)
    t_main = t_main.replace("app.add_middleware(RequestContextMiddleware)\n", "")
    
    # RateLimitMiddleware 뒤에 RequestContextMiddleware 추가
    anchor = "app.add_middleware(\n    RateLimitMiddleware,"
    if anchor in t_main:
        # RateLimitMiddleware 블록 끝 찾기
        start = t_main.find(anchor)
        end = t_main.find(")\n", start) + 2
        # 그 뒤에 RequestContextMiddleware 삽입
        t_main = t_main[:end] + "\napp.add_middleware(RequestContextMiddleware)\n" + t_main[end:]
    
    # 마지막으로 CORS 블록을 맨 끝에 추가 (가장 outermost)
    t_main += "\n" + cors_block
    
    p_main.write_text(t_main, encoding="utf-8")
    print("[OK] main.py CORS 미들웨어 순서 수정 완료")
else:
    print("[SKIP] CORS 블록을 찾지 못했습니다.")

# 2. deploy.ps1 강제 세팅 (잘못된 DB URL 제거 및 SQLite 강제)
p_deploy = ROOT / "deploy.ps1"
t_deploy = p_deploy.read_text(encoding="utf-8")

# 기존 환경변수 옵션 제거
t_deploy = re.sub(r'--update-env-vars="[^"]*"', '', t_deploy)
t_deploy = re.sub(r'--set-env-vars="[^"]*"', '', t_deploy)

# 모든 필수 환경변수 세팅 (SAJU_DATABASE_URL을 빈 값으로 덮어씀)
env_vars = '--set-env-vars="SAJU_ENV=production,SAJU_JWT_SECRET=this_is_a_brand_new_secret_key_32_chars_long_for_cloud,SAJU_ASSET_BASE_URL=https://placeholder.example.com,SAJU_CORS_ORIGINS=*,SAJU_DB_PATH=/tmp/auth.db,SAJU_DATABASE_URL="'

# gcloud run deploy 명령어 끝에 추가
old_cmd = '--allow-unauthenticated --quiet'
new_cmd = old_cmd + ' ' + env_vars
t_deploy = t_deploy.replace(old_cmd, new_cmd)

p_deploy.write_text(t_deploy, encoding="utf-8")
print("[OK] deploy.ps1 환경변수 강제 세팅 완료 (SQLite 강제)")
