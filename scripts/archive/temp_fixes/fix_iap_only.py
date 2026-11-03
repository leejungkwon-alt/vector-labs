import re
from pathlib import Path

def fix_iap():
    path = Path("app/services/iap.py")
    if not path.exists():
        print("❌ 파일 없음: app/services/iap.py")
        return
        
    content = path.read_text(encoding="utf-8")
    
    # 1. 이전 스크립트가 잘못 삽입했을 수 있는 로직 제거
    content = re.sub(
        r'\s*env = os\.environ\.get\("SAJU_ENV", ""\)\.strip\(\)\.lower\(\)\s*'
        r'if "mock" in str\(receipt\)\.lower\(\) and env not in \("development", "test"\):\s*'
        r'raise IAPVerificationError\("Mock receipts are only allowed in development or test environments\."\)\s*',
        '\n', content
    )
    
    # 2. DB 호출 직전에 확실하게 삽입
    target = "    repo = get_repository()"
    if target in content:
        check_logic = '''    env = os.environ.get("SAJU_ENV", "").strip().lower()
    if "mock" in str(receipt).lower() and env not in ("development", "test"):
        raise IAPVerificationError("Mock receipts are only allowed in development or test environments.")
'''
        # 첫 번째 발견되는 repo = get_repository() 앞에 삽입
        content = content.replace(target, check_logic + target, 1)
        path.write_text(content, encoding="utf-8")
        print("✅ app/services/iap.py 타겟팅 패치 완료")
    else:
        print("❌ 'repo = get_repository()' 구문을 찾을 수 없습니다. 수동 확인 필요.")

if __name__ == "__main__":
    print("🚀 iap.py 최종 패치 시작...")
    fix_iap()
    print("🎉 완료. 'python -m pytest -q'를 실행하세요.")