# scripts/fix_auth_email_final.py
"""
백엔드 이메일 저장 완벽 패치:
1) users 테이블 스키마에 email 컬럼 추가
2) link_social_identity 함수에 email 파라미터 + UPDATE 쿼리 반영
3) providers.py가 identity에 email을 포함하는지 검증
"""
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
REPO = Path("app/auth/repository.py")
PROVIDERS = Path("app/auth/providers.py")

print("=" * 60)
print("1) users 테이블 스키마 패치")
print("=" * 60)

if not REPO.exists():
    print(f"❌ {REPO} 없음")
    sys.exit(1)

txt = REPO.read_text(encoding="utf-8")
orig_txt = txt

# ---- (1) users 테이블에 email TEXT 추가 ----
start_idx = txt.find("CREATE TABLE IF NOT EXISTS users (")
if start_idx == -1:
    print("❌ users CREATE TABLE 구문 없음")
    sys.exit(1)
end_idx = txt.find(")", start_idx)
users_block = txt[start_idx:end_idx+1]

if "email TEXT" in users_block:
    print("ℹ️ users.email 컬럼이 이미 존재")
else:
    OLD = "created_at TEXT NOT NULL,"
    NEW = "created_at TEXT NOT NULL,\n          email TEXT,"
    if OLD not in users_block:
        print(f"❌ users 블록에 '{OLD}' 없음")
        print(users_block)
        sys.exit(1)
    new_users_block = users_block.replace(OLD, NEW, 1)
    txt = txt[:start_idx] + new_users_block + txt[end_idx+1:]
    print("✅ users.email 컬럼 추가")

print("=" * 60)
print("2) link_social_identity 함수 패치")
print("=" * 60)

# ---- (2) 함수 시그니처에 email 파라미터 추가 ----
old_sig = 'self, user_id: str, provider: str, subject: str, email: str\n    ) -> dict:'
new_sig = 'self, user_id: str, provider: str, subject: str, email: str | None = None\n    ) -> dict:'

if old_sig in txt:
    txt = txt.replace(old_sig, new_sig, 1)
    print("✅ 함수 시그니처: email 기본값(None) 추가")
elif 'email: str | None = None' in txt:
    print("ℹ️ 함수 시그니처는 이미 수정됨")
else:
    print("❌ 함수 시그니처 패턴 불일치. 아래 실제 시그니처 확인 필요")
    m = re.search(r'def link_social_identity\(([^)]+)\)', txt)
    if m:
        print(m.group(0))

# ---- (3) UPDATE 쿼리에 email 저장 반영 ----
old_update = '''        try:
            self._run(
                "UPDATE users SET social_provider = ?, social_subject = ?, "
                "is_anonymous = 0 WHERE id = ?",
                (provider, subject, user_id),
            )'''
new_update = '''        try:
            if email:
                self._run(
                    "UPDATE users SET social_provider = ?, social_subject = ?, "
                    "is_anonymous = 0, email = ? WHERE id = ?",
                    (provider, subject, email, user_id),
                )
            else:
                self._run(
                    "UPDATE users SET social_provider = ?, social_subject = ?, "
                    "is_anonymous = 0 WHERE id = ?",
                    (provider, subject, user_id),
                )'''

if old_update in txt:
    txt = txt.replace(old_update, new_update, 1)
    print("✅ UPDATE 쿼리에 email 저장 로직 추가")
elif "email = ?" in txt:
    print("ℹ️ UPDATE 쿼리는 이미 수정됨")
else:
    print("❌ UPDATE 쿼리 패턴 불일치. 아래 실제 쿼리 확인 필요")
    m = re.search(r'UPDATE users SET[^"]+', txt)
    if m:
        print(m.group(0))

print("=" * 60)
print("3) providers.py 가 email 을 반환하는지 확인")
print("=" * 60)

if PROVIDERS.exists():
    pv = PROVIDERS.read_text(encoding="utf-8")
    # identity dict 를 반환하는 부분에서 email 키가 있는지
    has_email = '"email"' in pv or "'email'" in pv
    if has_email:
        print("✅ providers.py 에 email 키 반환 로직 있음")
    else:
        print("⚠️ providers.py 에 email 반환 로직이 안 보입니다.")
        print("   (아래 코드를 확인 후 알려주세요)")
        print("-" * 60)
        print(pv[:2000])
        print("-" * 60)
else:
    print(f"⚠️ {PROVIDERS} 파일 없음. 실제 프로바이더 경로를 알려주세요.")

# ---- 결과 저장 ----
if txt != orig_txt:
    if not APPLY:
        print("\n🧪 미리보기 모드. 실제 적용하려면 --apply")
        sys.exit(0)
    REPO.write_text(txt, encoding="utf-8")
    print("\n🎉 repository.py 패치 완료")
else:
    print("\nℹ️ repository.py 변경 사항 없음 (이미 반영됨)")