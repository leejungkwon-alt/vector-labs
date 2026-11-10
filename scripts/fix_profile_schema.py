# scripts/fix_profile_schema.py
"""
ProfileResponse 스키마 완화:
- 필수 필드 → Optional + 기본값
- 예전 DB 행이든 신규든 422 안 남
"""
import ast
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
AUTH_SCHEMA = Path("app/schemas/auth.py")

if not AUTH_SCHEMA.exists():
    print(f"❌ {AUTH_SCHEMA} 없음")
    sys.exit(1)

txt = AUTH_SCHEMA.read_text(encoding="utf-8")

# ─── 기존 ProfileResponse 찾기 ───
OLD = '''class ProfileResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    birth_date: Optional[str]
    birth_time: Optional[str]
    birth_location: Optional[str]
    timezone_str: str
    longitude: float
    gender: str
    jasi_boundary: int
    correction_mode: str
    updated_at: str'''

NEW = '''class ProfileResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: Optional[str] = None
    timezone_str: str = "Asia/Seoul"
    longitude: float = 126.978
    gender: str = "M"
    jasi_boundary: int = 23
    correction_mode: str = "lmt"
    updated_at: str = ""'''

if OLD in txt:
    txt = txt.replace(OLD, NEW, 1)
    print("✅ ProfileResponse 스키마 완화 (모든 필드 기본값)")
elif "timezone_str: str = \"Asia/Seoul\"" in txt:
    print("ℹ️ 이미 완화됨")
    sys.exit(0)
else:
    print("⚠️ ProfileResponse 패턴 불일치")
    print("   다음 명령으로 확인:")
    print("   Get-Content 'app/schemas/auth.py' | Select-String 'class ProfileResponse' -Context 0,15")
    sys.exit(1)

try:
    ast.parse(txt)
    print("✅ 문법 검증 통과")
except SyntaxError as e:
    print(f"❌ 문법 오류: {e.lineno}")
    sys.exit(1)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_profile_schema.py --apply")
    sys.exit(0)

AUTH_SCHEMA.write_text(txt, encoding="utf-8")
print(f"\n🎉 저장: {AUTH_SCHEMA}")
print("\n다음:")
print("   .\\deploy.ps1  (백엔드 재배포)")