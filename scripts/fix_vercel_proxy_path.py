from pathlib import Path
import json
import subprocess

BASE = Path.cwd()
VERCEL_JSON = BASE / "vercel.json"

# Cloud Run 백엔드 주소 (이전 단계에서 확인한 주소)
CLOUDRUN_URL = "https://vector-labs-api-787049663118.asia-northeast3.run.app"

# 수정된 rewrite 설정: /api/(.*) → Cloud Run의 /$1 (즉, /api/v1/... → /v1/...)
config = {
    "buildCommand": "npm run build",
    "outputDirectory": "dist",
    "framework": "vite",
    "rewrites": [
        {
            "source": "/api/(.*)",
            "destination": f"{CLOUDRUN_URL}/$1"
        }
    ]
}
VERCEL_JSON.write_text(json.dumps(config, indent=2), encoding="utf-8")
print("✅ vercel.json의 destination 경로가 수정되었습니다. (/api 프리픽스 제거)")

# 깃허브 푸시
print("\n[2] 깃허브 푸시")
subprocess.run(["git", "add", "vercel.json"], check=True)
subprocess.run(["git", "commit", "-m", "fix: correct Vercel proxy destination path for Cloud Run"], check=True)
subprocess.run(["git", "push", "origin", "main"], check=True)
print("\n✅ 깃허브 업로드 완료! Vercel이 자동으로 재배포합니다.")