import re
import os
from pathlib import Path

def patch_jwt():
    path = Path("app/auth/jwt_utils.py")
    if not path.exists():
        print("❌ app/auth/jwt_utils.py 파일이 없습니다.")
        return
    content = path.read_text(encoding="utf-8")
    
    # is_production import 추가
    if "from app.ops.env import is_production" not in content:
        content = content.replace("import os", "import os\nfrom app.ops.env import is_production", 1)
        
    # _secret 함수 전체를 완벽하게 덮어쓰기
    new_secret_func = '''def _secret() -> str:
    s = os.environ.get("SAJU_JWT_SECRET", "").strip()
    if not s:
        if is_production():
            raise RuntimeError("SAJU_JWT_SECRET is not set in production. Failing closed.")
        return "dev-secret-key-for-local-only"
    if is_production() and len(s) < 32:
        raise RuntimeError("SAJU_JWT_SECRET must be at least 32 characters in production.")
    return s'''
    
    # def _secret() 부터 다음 def 가 나오기 전까지 통째로 교체
    pattern = r"def _secret\(\)[^:]*:.*?(?=\ndef |\Z)"
    if re.search(pattern, content, flags=re.DOTALL):
        content = re.sub(pattern, new_secret_func + "\n\n", content, flags=re.DOTALL)
        path.write_text(content, encoding="utf-8")
        print("✅ app/auth/jwt_utils.py 완벽 패치 완료")
    else:
        print("❌ _secret 함수를 찾을 수 없습니다.")

def patch_iap():
    path = Path("app/services/iap.py")
    if not path.exists():
        print("❌ app/services/iap.py 파일이 없습니다.")
        return
    content = path.read_text(encoding="utf-8")
    
    # verify_and_grant 함수 진입 직후에 mock 검사 로직 삽입
    pattern = r"(def verify_and_grant\([^)]*\):[^\n]*\n)"
    
    check_logic = '''    env = os.environ.get("SAJU_ENV", "").strip().lower()
    if "mock" in str(receipt).lower() and env not in ("development", "test"):
        raise IAPVerificationError("Mock receipts are only allowed in development or test environments.")
'''
    if "Mock receipts are only allowed" not in content:
        content = re.sub(pattern, r"\1" + check_logic, content, count=1)
        path.write_text(content, encoding="utf-8")
        print("✅ app/services/iap.py 패치 완료")
    else:
        print("ℹ️ app/services/iap.py는 이미 패치되어 있습니다.")

def patch_main():
    path = Path("app/main.py")
    if not path.exists():
        print("❌ app/main.py 파일이 없습니다.")
        return
    content = path.read_text(encoding="utf-8")
    
    # validate_startup 함수 내부 로직 교체
    pattern = r"def validate_startup\(\):"
    if pattern in content:
        if "raise RuntimeError" not in content.split(pattern)[1].split("\ndef ")[0]:
            new_logic = '''def validate_startup():
    from app.ops.env import is_production
    if is_production():
        secret = os.environ.get("SAJU_JWT_SECRET", "").strip()
        if not secret:
            raise RuntimeError("SAJU_JWT_SECRET must be set in production.")
        if len(secret) < 32:
            raise RuntimeError("SAJU_JWT_SECRET must be at least 32 characters in production.")
'''
            content = content.replace(pattern + "\n", new_logic, 1)
            path.write_text(content, encoding="utf-8")
            print("✅ app/main.py 패치 완료")
        else:
            print("ℹ️ app/main.py validate_startup은 이미 패치되어 있습니다.")
    else:
        print("❌ validate_startup 함수를 찾을 수 없습니다.")

if __name__ == "__main__":
    print("🚀 Fail-closed 보안 패치 스크립트 v2 시작...")
    patch_jwt()
    patch_iap()
    patch_main()
    print("🎉 모든 패치 완료. 'python -m pytest -q'를 실행하세요.")