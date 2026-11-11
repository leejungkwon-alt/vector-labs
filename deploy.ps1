# deploy.ps1 — 백엔드 배포 + 스모크 테스트 (Phase 4)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8
$OutputEncoding           = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

$ErrorActionPreference = "Stop"
$PROJECT      = "vector-labs-api"
$REGION       = "asia-northeast3"
$SERVICE      = "saju-backend"
$IMAGE        = "asia-northeast3-docker.pkg.dev/$PROJECT/cloud-run-source-deploy/$SERVICE"
$TAG          = Get-Date -Format "yyyyMMdd_HHmmss"
$BASE_URL     = "https://saju-backend-787049663118.asia-northeast3.run.app"
$FRONTEND_URL = "https://gyeol-blond.vercel.app"
$GOOGLE_CLIENT_ID = "787049663118-0tv6r1bbi28lli6mr027ruo55l6esofo.apps.googleusercontent.com"

Write-Host "`n=== 1. 테스트 실행 ===" -ForegroundColor Cyan
python -m pytest tests/ -q
if ($LASTEXITCODE -ne 0) { Write-Host "테스트 실패. 배포를 중단합니다." -ForegroundColor Red; exit 1 }

Write-Host "`n=== 2. 이미지 빌드 ($TAG) ===" -ForegroundColor Cyan
gcloud builds submit --tag "${IMAGE}:${TAG}" --project $PROJECT --region $REGION
if ($LASTEXITCODE -ne 0) { Write-Host "빌드 실패. 배포를 중단합니다." -ForegroundColor Red; exit 1 }

Write-Host "`n=== 3. Cloud Run 배포 ===" -ForegroundColor Cyan
gcloud run deploy $SERVICE `
    --image "${IMAGE}:${TAG}" `
    --region $REGION `
    --platform managed `
    --project $PROJECT `
    --port 8080 `
    --memory 512Mi `
    --timeout 300 `
    --allow-unauthenticated `
    --quiet `
    --update-env-vars="SAJU_ENV=production,SAJU_ASSET_BASE_URL=$FRONTEND_URL,SAJU_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID,LEMONSQUEEZY_STORE_ID=516056,LEMONSQUEEZY_VARIANT_ID=2341690,LEMONSQUEEZY_ONETIME_VARIANT_ID=2357370" `
    --set-secrets="SAJU_DATABASE_URL=saju-database-url:latest,SAJU_JWT_SECRET=saju-jwt-secret:latest,SAJU_TELEGRAM_BOT_TOKEN=saju-telegram-bot-token:latest,LEMONSQUEEZY_API_KEY=lemonsqueezy-api-key:latest,LEMONSQUEEZY_WEBHOOK_SECRET=lemonsqueezy-webhook-secret:latest" `
    --startup-probe="httpGet.path=/healthz,initialDelaySeconds=2,timeoutSeconds=2,periodSeconds=3,failureThreshold=10"
if ($LASTEXITCODE -ne 0) { Write-Host "배포 실패." -ForegroundColor Red; exit 1 }

Write-Host "`n=== 4. 스모크 테스트 ===" -ForegroundColor Cyan

# (a) /ready — DB SELECT 1 (Cloud Run 트래픽 전환 대기 포함 최대 60초)
$ready = $null
for ($i = 0; $i -lt 30; $i++) {
    try {
        $ready = Invoke-RestMethod -Uri "$BASE_URL/ready" -Method GET -TimeoutSec 5
        if ($ready.status -eq "ready") { break }
    } catch { }
    Start-Sleep -Seconds 2
}
if ($null -eq $ready -or $ready.status -ne "ready") {
    Write-Host "READY FAILED: $($ready | ConvertTo-Json -Compress)" -ForegroundColor Red
    exit 1
}
Write-Host "  /ready OK - db=$($ready.db)" -ForegroundColor Green

# (b) 익명 로그인 + CORS 헤더 확인
try {
    $resp = Invoke-WebRequest -Uri "$BASE_URL/api/v1/auth/anonymous" `
        -Method POST `
        -Headers @{ Origin = $FRONTEND_URL } `
        -TimeoutSec 10
} catch {
    Write-Host "AUTH FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
if ($resp.StatusCode -ne 200) {
    Write-Host "AUTH STATUS: $($resp.StatusCode)" -ForegroundColor Red
    exit 1
}
$acao = $resp.Headers["Access-Control-Allow-Origin"]
if (-not $acao) {
    Write-Host "CORS HEADER MISSING (Access-Control-Allow-Origin)" -ForegroundColor Red
    exit 1
}
Write-Host "  /auth/anonymous OK - ACAO=$acao" -ForegroundColor Green

Write-Host "`n배포 성공! 스모크 테스트 통과." -ForegroundColor Green
Write-Host "URL: $BASE_URL" -ForegroundColor Green
