# scripts/fix_route_order_v2.py
from pathlib import Path
import re
import sys

PATH = Path("app/auth/router.py")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 텔레그램 라우트 블록 찾기 (다음 @router.post가 나오기 전까지)
tg_pattern = r'(@router\.post\("/login/telegram"\)[\s\S]*?)(?=@router\.post|\Z)'
match_tg = re.search(tg_pattern, src)

if not match_tg:
    print("❌ 텔레그램 라우트를 찾을 수 없습니다."); sys.exit(1)

tg_block = match_tg.group(1).strip()
# 원본에서 텔레그램 라우트 일단 삭제
src = src.replace(match_tg.group(1), "")

# 2. provider 라우트 블록 찾기 (이번엔 response_model 등 뒤에 오는 옵션까지 포함)
prov_pattern = r'(@router\.post\("/login/\{provider\}".*?)(?=@router\.post|\Z)'
match_prov = re.search(prov_pattern, src, flags=re.DOTALL)

if not match_prov:
    print("❌ 기존 provider 라우트를 찾을 수 없습니다."); sys.exit(1)

prov_block = match_prov.group(1)

# 3. 텔레그램 블록을 provider 라우트 위에 삽입
src = src.replace(prov_block, tg_block + "\n\n\n" + prov_block, 1)

# 4. 보기 좋게 줄바꿈 정리 (연속된 4개 이상의 빈 줄을 3개로 축소)
src = re.sub(r'\n{4,}', '\n\n\n', src)

PATH.write_text(src, encoding="utf-8")
print("✅ 백엔드 라우트 순서 수정 완료 (텔레그램 라우트가 최상단으로 이동)")