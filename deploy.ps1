# deploy.ps1
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8
$OutputEncoding           = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

$ErrorActionPreference = "Stop"
$PROJECT = "vector-labs-api"
$REGION  = "asia-northeast3"
$SERVICE = "saju-backend"
$IMAGE   = "asia-northeast3-docker.pkg.dev/$PROJECT/cloud-run-source-deploy/$SERVICE"
$TAG     = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "`n=== 1. ?뚯뒪???ㅽ뻾 ===" -ForegroundColor Cyan
python -m pytest tests/ -q
if ($LASTEXITCODE -ne 0) { Write-Host "?뚯뒪???ㅽ뙣. 諛고룷瑜?以묐떒?⑸땲??" -ForegroundColor Red; exit 1 }

Write-Host "`n=== 2. ?대?吏 鍮뚮뱶 ($TAG) ===" -ForegroundColor Cyan
gcloud builds submit --tag "${IMAGE}:${TAG}" --project $PROJECT --region $REGION
if ($LASTEXITCODE -ne 0) { Write-Host "鍮뚮뱶 ?ㅽ뙣. 諛고룷瑜?以묐떒?⑸땲??" -ForegroundColor Red; exit 1 }

Write-Host "`n=== 3. Cloud Run 諛고룷 ===" -ForegroundColor Cyan
# ?먮옒 Secret(saju-database-url-supabase) 李몄“ ?좎? + SAJU_ASSET_BASE_URL 異붽?
gcloud run deploy $SERVICE --image "${IMAGE}:${TAG}" --region $REGION --platform managed --project $PROJECT --port 8080 --memory 512Mi --timeout 300 --allow-unauthenticated --quiet --update-env-vars="SAJU_ASSET_BASE_URL=https://placeholder.example.com"  --set-secrets="SAJU_DATABASE_URL=saju-database-url:latest"
if ($LASTEXITCODE -ne 0) { Write-Host "諛고룷 ?ㅽ뙣." -ForegroundColor Red; exit 1 }

Write-Host "`n諛고룷 ?깃났!" -ForegroundColor Green
Write-Host "URL: https://saju-backend-787049663118.asia-northeast3.run.app" -ForegroundColor Green
Write-Host "Health check ?ㅽ뻾 以?.." -ForegroundColor Yellow
curl.exe https://saju-backend-787049663118.asia-northeast3.run.app/health

