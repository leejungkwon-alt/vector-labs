import os
from pathlib import Path

# 1. JWT Utils (기본 키 사용 차단)
jwt_path = Path("app/auth/jwt_utils.py")
jwt_code = jwt_path.read_text(encoding="utf-8")

new_secret_func = '''def _secret() -> str:
    s = os.environ.get("SAJU_JWT_SECRET", "").strip()
    env = os.environ.get("SAJU_ENV", "").lower()
    
    # Fail-Closed: development, test 가 명시된 경우에만 기본 키 허용
    is_dev_or_test = env in ("development", "test")

    if not is_dev_or_test:
        if not s:
            raise RuntimeError(
                "SAJU_JWT_SECRET must be set. "
                "The default development secret is only allowed when SAJU_ENV=development or test."
            )
        if len(s) < _MIN_SECRET_LEN:
            raise RuntimeError(
                f"SAJU_JWT_SECRET must be at least {_MIN_SECRET_LEN} characters."
            )
        return s

    return s or _DEFAULT_SECRET
'''

# 기존 _secret 함수를 새 함수로 교체
import re
jwt_code = re.sub(r"def _secret\(\) -> str:.*?return _DEFAULT_SECRET", new_secret_func, jwt_code, flags=re.DOTALL)
jwt_path.write_text(jwt_code, encoding="utf-8")
print("✅ app/auth/jwt_utils.py Fail-Closed 보안 패치 완료")


# 2. IAP (모의 영수증 검증 우회 차단)
iap_path = Path("app/services/iap.py")
iap_code = iap_path.read_text(encoding="utf-8")

old_iap = '''    # Step 4-B: 프로덕션에서 mock 영수증 거부
    if receipt == "mock_valid_receipt" and os.environ.get("SAJU_ENV", "").lower() == "production":
        raise IAPVerificationError(
            "Mock receipts are not allowed in production. "
            "Real Apple/Google receipt verification must be wired before deploying."
        )
    if receipt == "mock_valid_receipt":'''

new_iap = '''    # Fail-Closed: development, test 가 명시된 경우에만 mock 영수증 허용
    env = os.environ.get("SAJU_ENV", "").lower()
    is_dev_or_test = env in ("development", "test")
    
    if receipt == "mock_valid_receipt":
        if not is_dev_or_test:
            raise IAPVerificationError(
                "Mock receipts are strictly forbidden outside of development/test. "
                "SAJU_ENV must be explicitly set to 'development' or 'test' to use mocks."
            )'''

if old_iap in iap_code:
    iap_code = iap_code.replace(old_iap, new_iap)
    iap_path.write_text(iap_code, encoding="utf-8")
    print("✅ app/services/iap.py Fail-Closed 보안 패치 완료")
else:
    print("⚠️ iap.py 패턴을 찾지 못했습니다. 수동으로 확인해주세요.")