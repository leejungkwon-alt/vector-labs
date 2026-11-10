# scripts/fix_client_api_v2.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/src/api/client.ts")
if not PATH.exists():
    print("❌ client.ts 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

if "createStarsInvoice" in src:
    print("⚠️ 이미 createStarsInvoice가 존재합니다.")
    sys.exit(0)

# 'anonymous' 함수 라인을 찾아서 그 바로 아래에 추가
pattern = r'(anonymous:\s*\(\)\s*=>\s*request<AuthResponse>\("/auth/anonymous".*?\),)'
match = re.search(pattern, src)

if match:
    new_line = '\n  createStarsInvoice: () => request<{ invoice_link: string }>("/billing/stars/invoice", { method: "POST" }),'
    src = src.replace(match.group(1), match.group(1) + new_line, 1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ client.ts에 createStarsInvoice 함수 추가 완료 (anonymous 아래에 삽입)")
else:
    print("❌ anonymous 라인을 찾을 수 없습니다. 수동 확인이 필요합니다.")