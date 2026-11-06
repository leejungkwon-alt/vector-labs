# scripts/safe_add_email_column.py
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
REPO_PATH = Path("app/auth/repository.py")

if not REPO_PATH.exists():
    print(f"❌ 파일을 찾을 수 없습니다: {REPO_PATH}")
    sys.exit(1)

txt = REPO_PATH.read_text(encoding="utf-8")

# CREATE TABLE users 구문 찾기
start_idx = txt.find("CREATE TABLE IF NOT EXISTS users")
if start_idx == -1:
    print("❌ users 테이블 정의를 찾지 못했습니다.")
    sys.exit(1)

# 해당 구문의 닫는 괄호 위치 찾기
end_idx = txt.find(")", start_idx)
if end_idx == -1:
    print("❌ 닫는 괄호를 찾지 못했습니다.")
    sys.exit(1)

table_def = txt[start_idx:end_idx+1]

if "email" in table_def:
    print("ℹ️ 이미 email 컬럼이 존재합니다.")
    sys.exit(0)

# 닫는 괄호 바로 앞에 , email TEXT 추가
# 줄바꿈과 들여쓰기를 고려하여 문자열을 자름
prefix = txt[:end_idx].rstrip()
if not prefix.endswith(","):
    prefix += ","
    
suffix = "\n            email TEXT\n        " + txt[end_idx:]

new_txt = prefix + suffix

if not APPLY:
    print("🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
    print("\n[수정될 테이블 구조 미리보기]")
    # 대략적인 구조 출력
    print(new_txt[start_idx:end_idx+100])
    sys.exit(0)

REPO_PATH.write_text(new_txt, encoding="utf-8")
print("🎉 안전하게 email 컬럼 추가 완료")