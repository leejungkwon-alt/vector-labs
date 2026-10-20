#!/usr/bin/env python3
"""
scripts/fix_iap_test.py

iap.py의 상품 ID 변경(sub_monthly_299)에 맞춰 테스트 코드(test_security_hardening.py)를 업데이트합니다.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "tests" / "test_security_hardening.py"

def main():
    if not TARGET.exists():
        print(f"[-] {TARGET} 파일이 없습니다.")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8")
    
    # 옛날 상품 ID를 새로운 상품 ID로 변경
    text = text.replace('"premium_monthly"', '"sub_monthly_299"')
    
    TARGET.write_text(text, encoding="utf-8")
    print("[OK] tests/test_security_hardening.py의 상품 ID가 업데이트되었습니다.")
    print("다음 명령으로 전체 테스트를 다시 실행해 보세요:")
    print("  python -m pytest -q")

if __name__ == "__main__":
    main()