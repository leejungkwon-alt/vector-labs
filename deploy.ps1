# deploy.ps1
# 한글 콘솔 인코딩 강제 (UTF-8)
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

Write-Host "`n=== 1. 테스트 실행 ===" -ForegroundColor Cyan
python -m pytest tests/ -q
if ($LASTEXITCODE -ne 0) { Write-Host "❌ 테스트 실패. 배포를 중단합니다." -ForegroundColor Red; exit 1 }

Write-Host "`n=== 2. 이미지 빌드 ($TAG) ===" -ForegroundColor Cyan
gcloud builds submit --tag "${IMAGE}:${TAG}" --project $PROJECT --region $REGION
if ($LASTEXITCODE -ne 0) { Write-Host "❌ 빌드 실패. 배포를 중단합니다." -ForegroundColor Red; exit 1 }

Write-Host "`n=== 3. Cloud Run 배포 ===" -ForegroundColor Cyan
gcloud run deploy $SERVICE --image "${IMAGE}:${TAG}" --region $REGION --platform managed --project $PROJECT --port 8080 --memory 512Mi --timeout 300 --allow-unauthenticated --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "❌ 배포 실패." -ForegroundColor Red; exit 1 }

Write-Host "`n✅ 배포 성공!" -ForegroundColor Green
Write-Host "URL: https://saju-backend-787049663118.asia-northeast3.run.app" -ForegroundColor Green
Write-Host "Health check 실행 중..." -ForegroundColor Yellow
curl.exe https://saju-backend-787049663118.asia-northeast3.run.app/health