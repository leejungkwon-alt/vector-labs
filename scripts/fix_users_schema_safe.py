# scripts/fix_users_schema_safe.py
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
REPO_PATH = Path("app/auth/repository.py")

if not REPO_PATH.exists():
    print(f"❌ 파일을 찾을 수 없습니다: {REPO_PATH}")
    sys.exit(1)

txt = REPO_PATH.read_text(encoding="utf-8")

# 1. users 테이블 블록만 정확히 추출
START_MARK = "CREATE TABLE IF NOT EXISTS users ("
start_idx = txt.find(START_MARK)
if start_idx == -1:
    print("❌ users 테이블 정의를 찾지 못했습니다.")
    sys.exit(1)

# 첫 번째 닫는 괄호 위치 찾기
end_idx = txt.find(")", start_idx)
if end_idx == -1:
    print("❌ users 테이블 닫는 괄호를 찾지 못했습니다.")
    sys.exit(1)

users_block = txt[start_idx:end_idx+1]

# 2. 이미 email 컬럼이 있는지 확인
if "email TEXT" in users_block:
    print("ℹ️ users 테이블에 이미 email 컬럼이 존재합니다.")
    sys.exit(0)

# 3. 정확한 삽입 위치: users 블록 안의 "created_at TEXT NOT NULL," 다음
OLD_IN_BLOCK = "created_at TEXT NOT NULL,"
if OLD_IN_BLOCK not in users_block:
    print("❌ users 블록 내에 'created_at TEXT NOT NULL,' 패턴이 없습니다.")
    print(users_block)
    sys.exit(1)

NEW_IN_BLOCK = "created_at TEXT NOT NULL,\n          email TEXT,"
new_users_block = users_block.replace(OLD_IN_BLOCK, NEW_IN_BLOCK, 1)

# 4. 전체 파일에 반영
new_txt = txt[:start_idx] + new_users_block + txt[end_idx+1:]

# 5. 결과 미리보기
print("🩺 변경될 users 테이블 구조 (미리보기):")
print(new_users_block)
print()

if not APPLY:
    print("🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    sys.exit(0)

REPO_PATH.write_text(new_txt, encoding="utf-8")
print("🎉 users 테이블 스키마에 email 컬럼 추가 완료")