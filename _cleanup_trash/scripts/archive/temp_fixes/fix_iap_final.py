import re
from pathlib import Path

def fix_iap_completely():
    path = Path("app/services/iap.py")
    if not path.exists():
        print("❌ 파일 없음")
        return
        
    content = path.read_text(encoding="utf-8")
    
    # 1. 이전 스크립트가 망가뜨린 코드 흔적 완벽히 제거
    # (들여쓰기 오류를 유발한 이전 주입 코드를 모두 찾아 삭제)
    content = re.sub(
        r'[ \t]*env = os\.environ\.get\("SAJU_ENV", ""\)\.strip\(\)\.lower\(\)\n[ \t]*if "mock" in str\(receipt\)\.lower\(\) and env not in \("development", "test"\):\n[ \t]*raise IAPVerificationError\("Mock receipts are only allowed in development or test environments\."\)\n',
        '',
        content
    )
    
    # 2. verify_and_grant 함수의 정의부 찾기
    match = re.search(r'(def verify_and_grant\([^)]*\):[^\n]*\n)', content)
    if not match:
        print("❌ verify_and_grant 함수를 찾을 수 없습니다.")
        return
        
    func_header = match.group(1)
    
    # 3. 함수 시작 직후에 안전하게 검사 로직 삽입 (들여쓰기 4칸 고정)
    check_block = '''    env = os.environ.get("SAJU_ENV", "").strip().lower()
    if "mock" in str(receipt).lower() and env not in ("development", "test"):
        raise IAPVerificationError("Mock receipts are only allowed in development or test environments.")
'''
    
    # 이미 제대로 삽입되어 있는지 확인
    start_idx = match.end()
    next_lines = content[start_idx:start_idx+500]
    if 'if "mock" in str(receipt).lower()' in next_lines and 'Mock receipts' in next_lines:
        print("ℹ️ 이미 검사 로직이 존재합니다. 패치 건너뜀.")
    else:
        content = content.replace(func_header, func_header + check_block, 1)
        path.write_text(content, encoding="utf-8")
        print("✅ iap.py 들여쓰기 복구 및 최종 패치 완료!")

if __name__ == "__main__":
    print("🚀 iap.py 최종 복구 시작...")
    fix_iap_completely()