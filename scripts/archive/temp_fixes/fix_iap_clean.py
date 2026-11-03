import re
from pathlib import Path

def fix_iap_cleanly():
    path = Path("app/services/iap.py")
    if not path.exists():
        print("❌ 파일 없음")
        return
        
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    # 1. 이전 스크립트가 망가뜨린 코드(중복 주입된 부분) 완벽히 제거
    clean_lines = []
    for line in lines:
        s = line.strip()
        # 이전 스크립트들이 넣었던 쓰레기 코드들을 모두 필터링
        if 'env = os.environ.get("SAJU_ENV"' in s: continue
        if "env = os.environ.get('SAJU_ENV'" in s: continue
        if 'if "mock" in str(receipt).lower()' in s: continue
        if 'raise IAPVerificationError("Mock receipts' in s: continue
        if s == '# Fail-closed mock check': continue
        clean_lines.append(line)
        
    # 2. verify_and_grant 함수의 시작점을 찾아 안전하게 삽입
    final_lines = []
    in_func = False
    injected = False
    
    for line in clean_lines:
        final_lines.append(line)
        
        # 함수 정의 시작 감지
        if line.startswith("def verify_and_grant"):
            in_func = True
            
        # 함수 시그니처(매개변수 부분)가 끝나는 지점 (콜론으로 끝날 때)
        if in_func and line.strip().endswith(":"):
            # 정확히 4칸 들여쓰기로 검사 로직 삽입
            final_lines.append('    # Fail-closed mock check')
            final_lines.append('    env = os.environ.get("SAJU_ENV", "").strip().lower()')
            final_lines.append('    if "mock" in str(receipt).lower() and env not in ("development", "test"):')
            final_lines.append('        raise IAPVerificationError("Mock receipts are only allowed in development or test environments.")')
            final_lines.append('')
            in_func = False
            injected = True
            
    if injected:
        path.write_text("\n".join(final_lines) + "\n", encoding="utf-8")
        print("✅ app/services/iap.py 완벽하게 복구 및 패치되었습니다!")
    else:
        print("❌ verify_and_grant 함수를 찾지 못했습니다. 수동 확인이 필요합니다.")
        # 디버깅용: 30~50번째 줄 출력
        print("--- 파일 30~50번째 줄 ---")
        for i, l in enumerate(clean_lines[29:50]):
            print(f"{i+30}: {l}")

if __name__ == "__main__":
    print("🚀 iap.py 최종 클린 복구 시작...")
    fix_iap_cleanly()
    print("🎉 'python -m pytest -q'를 실행하세요.")