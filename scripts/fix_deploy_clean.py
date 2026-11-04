import re
from pathlib import Path
p = Path("deploy.ps1")
t = p.read_text(encoding="utf-8")

# 기존 환경변수 옵션 모두 제거
t = re.sub(r'--update-env-vars="[^"]*"', '', t)
t = re.sub(r'--set-env-vars="[^"]*"', '', t)

# 필요한 변수만 정확히 세팅 (빈 SAJU_DATABASE_URL 제거)
env_vars = '--set-env-vars="SAJU_ENV=production,SAJU_JWT_SECRET=this_is_a_brand_new_secret_key_32_chars_long_for_cloud,SAJU_ASSET_BASE_URL=https://placeholder.example.com,SAJU_CORS_ORIGINS=*,SAJU_DB_PATH=/tmp/auth.db"'

old_cmd = '--allow-unauthenticated --quiet'
t = t.replace(old_cmd, old_cmd + ' ' + env_vars)
p.write_text(t, encoding="utf-8")
print("[OK] deploy.ps1 환경변수 깔끔하게 재설정 완료")
