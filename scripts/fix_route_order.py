# scripts/fix_route_order.py
from pathlib import Path
import re
import sys

PATH = Path("app/auth/router.py")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 텔레그램 로그인 블록 추출
tg_pattern = r'(@router\.post\("/login/telegram"\)[\s\S]*?)(?=@router\.post|\Z)'
match_tg = re.search(tg_pattern, src)

if not match_tg:
    print("❌ 텔레그램 라우트를 찾을 수 없습니다."); sys.exit(1)

tg_block = match_tg.group(1).strip()
# 원래 위치에서 제거
src = src.replace(match_tg.group(1), "")

# 2. 기존 로그인 라우트 블록 찾기
prov_pattern = r'(@router\.post\("/login/\{provider\}"\)[\s\S]*?)(?=@router\.post|\Z)'
match_prov = re.search(prov_pattern, src)

if not match_prov:
    print("❌ 기존 provider 라우트를 찾을 수 없습니다."); sys.exit(1)

prov_block = match_prov.group(1)

# 3. 텔레그램 블록을 provider 라우트 위에 삽입
src = src.replace(prov_block, tg_block + "\n\n\n" + prov_block, 1)

PATH.write_text(src, encoding="utf-8")
print("✅ 백엔드 라우트 순서 수정 완료 (텔레그램 라우트를 최상단으로 이동)")