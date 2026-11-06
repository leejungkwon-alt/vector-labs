# scripts/fix_social_email_v3.py
"""
repository.py 정밀 패치:
1) users 테이블에 email TEXT 컬럼 추가
2) link_social_identity 시그니처에 email: str | None = None 추가
3) UPDATE 쿼리에 email = COALESCE(?, email) 적용 (email=None이면 기존 값 유지)
"""
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
REPO = Path("app/auth/repository.py")

if not REPO.exists():
    print(f"❌ {REPO} 없음")
    sys.exit(1)

txt = REPO.read_text(encoding="utf-8")
original = txt

# ---------- (1) users 테이블에 email TEXT 추가 ----------
start = txt.find("CREATE TABLE IF NOT EXISTS users (")
if start == -1:
    print("❌ users CREATE TABLE 구문 없음")
    sys.exit(1)
end = txt.find(")", start)
users_block = txt[start:end+1]

if "email TEXT" in users_block:
    print("ℹ️ users.email 이미 존재")
else:
    old_line = "created_at TEXT NOT NULL,"
    new_line = "created_at TEXT NOT NULL,\n          email TEXT,"
    if old_line not in users_block:
        print(f"❌ '{old_line}' not in users block")
        sys.exit(1)
    new_block = users_block.replace(old_line, new_line, 1)
    txt = txt[:start] + new_block + txt[end+1:]
    print("✅ users.email 컬럼 추가")

# ---------- (2) link_social_identity 시그니처 ----------
if 'email: str | None = None' not in txt:
    sig_pat = re.compile(
        r'(def link_social_identity\(\s*self,\s*user_id:\s*str,\s*provider:\s*str,\s*subject:\s*str)(\s*\)\s*->\s*dict:)',
        re.DOTALL,
    )
    new_txt, n = sig_pat.subn(r'\1, email: str | None = None\2', txt, count=1)
    if n != 1:
        print(f"❌ 시그니처 매칭 횟수: {n}")
        sys.exit(1)
    txt = new_txt
    print("✅ 시그니처 수정 (email param 추가)")
else:
    print("ℹ️ 시그니처 이미 수정됨")

# ---------- (3) UPDATE 쿼리 (COALESCE) ----------
fn_start = txt.find("def link_social_identity")
if fn_start == -1:
    print("❌ link_social_identity 함수 없음")
    sys.exit(1)
next_def = txt.find("\n    def ", fn_start + 20)
if next_def == -1:
    next_def = len(txt)
fn_body = txt[fn_start:next_def]

old_sql = '"is_anonymous = 0 WHERE id = ?",'
new_sql = '"is_anonymous = 0, email = COALESCE(?, email) WHERE id = ?",'
old_params = "(provider, subject, user_id),"
new_params = "(provider, subject, email, user_id),"

if old_sql in fn_body:
    if old_params not in fn_body:
        print(f"❌ '{old_params}' 없음")
        sys.exit(1)
    new_body = fn_body.replace(old_sql, new_sql, 1).replace(old_params, new_params, 1)
    txt = txt[:fn_start] + new_body + txt[next_def:]
    print("✅ UPDATE 쿼리 수정 (COALESCE 사용)")
elif "COALESCE(?, email)" in fn_body:
    print("ℹ️ UPDATE 쿼리 이미 수정됨")
else:
    print("❌ UPDATE 쿼리 패턴 불일치. 현재 함수 본문:")
    print(fn_body[:800])
    sys.exit(1)

# ---------- 결과 ----------
if txt == original:
    print("\nℹ️ 변경 사항 없음")
    sys.exit(0)

# 수정 후 함수 미리보기
fn_start = txt.find("def link_social_identity")
next_def = txt.find("\n    def ", fn_start + 20)
print("\n[패치 후 함수]")
print(txt[fn_start:next_def])

if not APPLY:
    print("\n🧪 미리보기.  적용: python scripts/fix_social_email_v3.py --apply")
    sys.exit(0)

REPO.write_text(txt, encoding="utf-8")
print("\n🎉 repository.py 패치 완료")