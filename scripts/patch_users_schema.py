# scripts/patch_users_schema.py
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
REPO_PATH = Path("app/auth/repository.py")

if not REPO_PATH.exists():
    print(f"❌ 파일을 찾을 수 없습니다: {REPO_PATH}")
    sys.exit(1)

txt = REPO_PATH.read_text(encoding="utf-8")
original = txt

# users 테이블 CREATE TABLE 구문 찾기
pattern = re.compile(r"(CREATE TABLE IF NOT EXISTS users\s*\(.*?\))", re.DOTALL)
match = pattern.search(txt)

if not match:
    print("❌ users 테이블 CREATE TABLE 구문을 찾지 못했습니다.")
    sys.exit(1)

table_def = match.group(1)

# 이미 email 컬럼이 있는지 확인
if "email" in table_def:
    print("ℹ️ users 테이블에 이미 email 컬럼이 존재합니다.")
    sys.exit(0)

# 마지막 컬럼 뒤에 email TEXT 추가
# 예: "created_at TEXT\n)" -> "created_at TEXT,\n            email TEXT\n)"
new_table_def = re.sub(r",?\s*\)", r",\n            email TEXT\n        )", table_def, count=1)

txt = txt.replace(table_def, new_table_def)

# find_user_by_social 등에서 SELECT 시 email도 조회하는지 확인 (SELECT * 이면 상관없음)
# 만약 SELECT 쿼리가 명시적이라면 여기서 추가 패치 필요

if txt == original:
    print("ℹ️ 변경 사항이 없습니다.")
    sys.exit(0)

if not APPLY:
    print("🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    print("\n[추가될 컬럼]")
    print(new_table_def)
    sys.exit(0)

REPO_PATH.write_text(txt, encoding="utf-8")
print("🎉 users 테이블 스키마에 email 컬럼 추가 완료")