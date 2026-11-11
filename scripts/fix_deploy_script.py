import re

print("🚀 deploy.ps1 스크립트의 환경변수/시크릿 설정을 수리합니다...\n")

with open("deploy.ps1", "r", encoding="utf-8") as f:
    content = f.read()

# 기존 gcloud run deploy 블록을 정규식으로 찾아서 새 블록으로 교체
pattern = r"gcloud run deploy \$SERVICE `.*?--startup-probe=\"[^\"]+\""

replacement = '''gcloud run deploy $SERVICE `
    --image "${IMAGE}:${TAG}" `
    --region $REGION `
    --platform managed `
    --project $PROJECT `
    --port 8080 `
    --memory 512Mi `
    --timeout 300 `
    --allow-unauthenticated `
    --quiet `
    --update-env-vars="SAJU_ENV=production,SAJU_ASSET_BASE_URL=$FRONTEND_URL,SAJU_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" `
    --set-secrets="SAJU_DATABASE_URL=saju-database-url:latest,SAJU_JWT_SECRET=saju-jwt-secret:latest,SAJU_TELEGRAM_BOT_TOKEN=saju-telegram-bot-token:latest,LEMONSQUEEZY_API_KEY=lemonsqueezy-api-key:latest,LEMONSQUEEZY_WEBHOOK_SECRET=lemonsqueezy-webhook-secret:latest" `
    --startup-probe="httpGet.path=/healthz,initialDelaySeconds=2,timeoutSeconds=2,periodSeconds=3,failureThreshold=10"'''

new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)

if count > 0:
    with open("deploy.ps1", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ deploy.ps1 수리 완료! (모든 시크릿 및 SAJU_ENV=production 추가됨)")
    print("👉 이제 다시 배포를 실행하세요: .\\deploy.ps1")
else:
    print("⚠️ deploy.ps1의 gcloud run deploy 패턴을 찾지 못했습니다. 파일을 직접 확인해주세요.")