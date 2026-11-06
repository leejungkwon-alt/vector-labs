# scripts/patch_fix_email.py
import ast
import shutil
import sys
from pathlib import Path

CLIENT_PATH = Path("app/services/lemonsqueezy_client.py")

def main():
    if not CLIENT_PATH.exists():
        sys.exit("파일을 찾을 수 없습니다.")

    src = CLIENT_PATH.read_text(encoding="utf-8")
    
    # 이미 이메일 로직이 제거되었는지 확인
    if "checkout_data[\"email\"]" not in src and "checkout_data['email']" not in src:
        print("✅ 이미 이메일 로직이 제거되어 있습니다.")
        return

    backup = CLIENT_PATH.with_suffix(".py.bak")
    shutil.copy2(CLIENT_PATH, backup)
    print(f"백업 생성: {backup}")

    # 이메일을 checkout_data에 추가하는 로직 제거
    old_logic = '''    checkout_data = {"custom": {"user_id": user_id}}
    if email:
        checkout_data["email"] = email'''
    new_logic = '''    checkout_data = {"custom": {"user_id": user_id}}
    # 이메일은 Lemon Squeezy 결제창에서 직접 입력받음 (형식 오류 방지)'''

    src = src.replace(old_logic, new_logic)
    
    # 혹시 남아있을 수 있는 다른 형태의 이메일 로직도 제거
    src = src.replace('    if email:\n        checkout_data["email"] = email\n', '')

    try:
        ast.parse(src)
    except SyntaxError as e:
        print(f"❌ 문법 오류: {e}")
        sys.exit(1)

    CLIENT_PATH.write_text(src, encoding="utf-8")
    print("✅ 이메일 전송 로직 제거 완료. 클라우드 런에 재배포하세요!")

if __name__ == "__main__":
    main()