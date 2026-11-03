import os
import re
from pathlib import Path

def patch_iap():
    path = Path("app/services/iap.py")
    if not path.exists(): return print("❌ iap.py 없음")
    
    content = path.read_text(encoding="utf-8")
    
    # 1. get_repository() 호출 전에 mock 검사 로직 삽입
    pattern = r"(def verify_and_grant\([^)]*\):.*?)(\n\s*repo\s*=\s*get_repository\(\))"
    
    def repl(match):
        func_start = match.group(1)
        repo_call = match.group(2)
        # 이미 mock 검사가 있는지 확인
        if "is_production()" in func_start or "Mock receipts" in func_start:
            return match.group(0)
        
        check_logic = """
    env = os.environ.get("SAJU_ENV", "").strip().lower()
    if "mock" in receipt.lower() and env not in ("development", "test"):
        raise IAPVerificationError("Mock receipts are only allowed in development or test environments.")
"""
        return func_start + check_logic + repo_call

    new_content = re.sub(pattern, repl, content, flags=re.DOTALL)
    path.write_text(new_content, encoding="utf-8")
    print("✅ iap.py 패치 완료")

def patch_jwt_utils():
    path = Path("app/auth/jwt_utils.py")
    if not path.exists(): return print("❌ jwt_utils.py 없음")
    
    content = path.read_text(encoding="utf-8")
    
    # 2. _secret() 함수에 is_production() 검사 추가
    if "from app.ops.env import is_production" not in content:
        content = content.replace("import os", "import os\nfrom app.ops.env import is_production", 1)
    
    pattern = r"(def _secret\(\).*?:\s*)(.*?)(\n\s*return)"
    
    def repl(match):
        func_start = match.group(1)
        body = match.group(2)
        return_stmt = match.group(3)
        
        if "is_production()" in body:
            return match.group(0) # 이미 패치됨
            
        secret_logic = """
    secret = os.environ.get("SAJU_JWT_SECRET", "").strip()
    if not secret:
        if is_production():
            raise RuntimeError("SAJU_JWT_SECRET is not set in production. Failing closed.")
        return "dev-secret-key-for-local-only"
"""
        return func_start + secret_logic + return_stmt

    new_content = re.sub(pattern, repl, content, flags=re.DOTALL)
    path.write_text(new_content, encoding="utf-8")
    print("✅ jwt_utils.py 패치 완료")

def patch_main():
    path = Path("app/main.py")
    if not path.exists(): return print("❌ main.py 없음")
    
    content = path.read_text(encoding="utf-8")
    
    # 3. validate_startup() 에서 JWT_SECRET 없을 시 RuntimeError 발생
    pattern = r"(def validate_startup\(\):.*?)(SAJU_JWT_SECRET.*?경고|SAJU_JWT_SECRET.*?missing|JWT_SECRET.*?없)"
    
    # 정규식으로 잡기 어려울 수 있으므로, 문자열 단순 치환 방식 사용
    if "raise RuntimeError(\"SAJU_JWT_SECRET" not in content:
        # 경고 로그를 찍는 부분을 찾아서 바로 뒤에 raise 추가
        target_msg = 'logger.warning("SAJU_JWT_SECRET is missing!")'
        if target_msg in content:
            content = content.replace(
                target_msg, 
                target_msg + '\n            raise RuntimeError("SAJU_JWT_SECRET must be set in production.")'
            )
        else:
            # 만약 로그 메시지가 다르다면 validate_startup 함수 내부에 강제 주입
            content = re.sub(
                r"(def validate_startup\(\):\n)",
                r"\1    if is_production() and not os.environ.get('SAJU_JWT_SECRET'):\n        raise RuntimeError('SAJU_JWT_SECRET must be set in production.')\n",
                content,
                count=1
            )
            
    path.write_text(content, encoding="utf-8")
    print("✅ main.py 패치 완료")

if __name__ == "__main__":
    print("🚀 Fail-closed 보안 패치 스크립트 시작...")
    patch_iap()
    patch_jwt_utils()
    patch_main()
    print("🎉 모든 패치 완료. 'python -m pytest -q'를 실행하세요.")