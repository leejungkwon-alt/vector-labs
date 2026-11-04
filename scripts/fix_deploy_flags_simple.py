import re
from pathlib import Path

p = Path("deploy.ps1")
t = p.read_text(encoding="utf-8")

# gcloud run deploy 라인만 찾아서 깔끔하게 교체
pattern = re.compile(r'gcloud run deploy \$SERVICE[^\r\n]*', re.MULTILINE)
match = pattern.search(t)

if match:
    old_line = match.group(0)
    new_line = 'gcloud run deploy $SERVICE --image "${IMAGE}:${TAG}" --region $REGION --platform managed --project $PROJECT --port 8080 --memory 512Mi --timeout 300 --allow-unauthenticated --quiet --set-env-vars="SAJU_ENV=production,SAJU_JWT_SECRET=this_is_a_brand_new_secret_key_32_chars_long_for_cloud,SAJU_ASSET_BASE_URL=https://placeholder.example.com,SAJU_CORS_ORIGINS=*,SAJU_DB_PATH=/tmp/auth.db"'
    t = t.replace(old_line, new_line)
    p.write_text(t, encoding="utf-8")
    print("[OK] deploy.ps1 수정 완료 (플래그 충돌 제거)")
    print("---")
    print("새 gcloud 명령어:")
    print(new_line)
else:
    print("[ERR] gcloud run deploy 라인을 찾지 못했습니다. deploy.ps1을 확인해주세요.")
