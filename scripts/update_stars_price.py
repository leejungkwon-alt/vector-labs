# scripts/update_stars_price.py
from pathlib import Path
import sys
import re

PATH = Path("app/api/v1/endpoints/billing.py")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 250을 400으로 변경 (정규식으로 유연하게 매칭)
old_price = r'"amount":\s*250'
new_price = '"amount": 400'

if re.search(old_price, src):
    src = re.sub(old_price, new_price, src, count=1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ 텔레그램 스타 가격 변경 완료 (250 -> 400)")
elif '"amount": 400' in src:
    print("⚠️ 이미 400 스타로 설정되어 있습니다.")
else:
    print("❌ 가격 설정 부분을 찾지 못했습니다. 수동 확인 필요.")