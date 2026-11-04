from pathlib import Path
p = Path("deploy.ps1")
t = p.read_text(encoding="utf-8")

# 기존에 혹시 있을 수 있는 --update-env-vars 부분을 제거 (중복 방지)
import re
t = re.sub(r'--update-env-vars="[^"]*"', '', t)

# 필요한 모든 환경변수 세팅
env_vars = '--update-env-vars="SAJU_ENV=production,SAJU_JWT_SECRET=this_is_a_brand_new_secret_key_32_chars_long_for_cloud,SAJU_ASSET_BASE_URL=https://placeholder.example.com,SAJU_CORS_ORIGINS=*,SAJU_DB_PATH=/tmp/auth.db"'

# gcloud run deploy 명령어 끝에 추가
old_cmd = '--allow-unauthenticated --quiet'
new_cmd = old_cmd + ' ' + env_vars
t = t.replace(old_cmd, new_cmd)

p.write_text(t, encoding="utf-8")
print("[OK] deploy.ps1 환경변수 업데이트 완료")
