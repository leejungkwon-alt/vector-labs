import re
from pathlib import Path

p = Path("deploy.ps1")
t = p.read_text(encoding="utf-8")

# 기존 --set-secrets 라인 제거
t = re.sub(r'--set-secrets="[^"]*"', '', t)

# gcloud run deploy 라인에 Neon Secret 참조 추가
pattern = re.compile(r'(gcloud run deploy \$SERVICE[^\r\n]*)', re.MULTILINE)
match = pattern.search(t)
if match:
    old_line = match.group(1)
    new_line = old_line + ' --set-secrets="SAJU_DATABASE_URL=saju-database-url:latest"'
    t = t.replace(old_line, new_line)
    p.write_text(t, encoding="utf-8")
    print("[OK] deploy.ps1 → Neon Secret(saju-database-url) 참조로 변경")
else:
    print("[ERR] gcloud run deploy 라인을 찾지 못했습니다.")

# 최종 확인 출력
print("\n--- 최종 gcloud run deploy 라인 ---")
for line in p.read_text(encoding="utf-8").splitlines():
    if "gcloud run deploy $SERVICE" in line:
        print(line)
