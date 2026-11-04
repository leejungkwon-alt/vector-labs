import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "deploy.ps1"

# 백업
if p.exists():
    shutil.copy2(p, p.with_suffix(".ps1.broken"))

# 원래 잘 돌던 형태로 복원 + SAJU_ASSET_BASE_URL만 추가
new_content = '''# deploy.ps1
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
if ($LASTEXITCODE -ne 0) { Write-Host "테스트 실패. 배포를 중단합니다." -ForegroundColor Red; exit 1 }

Write-Host "`n=== 2. 이미지 빌드 ($TAG) ===" -ForegroundColor Cyan
gcloud builds submit --tag "${IMAGE}:${TAG}" --project $PROJECT --region $REGION
if ($LASTEXITCODE -ne 0) { Write-Host "빌드 실패. 배포를 중단합니다." -ForegroundColor Red; exit 1 }

Write-Host "`n=== 3. Cloud Run 배포 ===" -ForegroundColor Cyan
# 원래 Secret(saju-database-url-supabase) 참조 유지 + SAJU_ASSET_BASE_URL 추가
gcloud run deploy $SERVICE --image "${IMAGE}:${TAG}" --region $REGION --platform managed --project $PROJECT --port 8080 --memory 512Mi --timeout 300 --allow-unauthenticated --quiet --update-env-vars="SAJU_ASSET_BASE_URL=https://placeholder.example.com" --set-secrets="SAJU_DATABASE_URL=saju-database-url-supabase:latest"
if ($LASTEXITCODE -ne 0) { Write-Host "배포 실패." -ForegroundColor Red; exit 1 }

Write-Host "`n배포 성공!" -ForegroundColor Green
Write-Host "URL: https://saju-backend-787049663118.asia-northeast3.run.app" -ForegroundColor Green
Write-Host "Health check 실행 중..." -ForegroundColor Yellow
curl.exe https://saju-backend-787049663118.asia-northeast3.run.app/health
'''

p.write_text(new_content, encoding="utf-8")
print("[OK] deploy.ps1 원상복구 완료")
print(" - Supabase Secret(saju-database-url-supabase) 참조 유지")
print(" - SAJU_ASSET_BASE_URL만 추가")
