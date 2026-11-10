import os
import re
import glob
import shutil

def patch_file(filepath, pattern, replacement, desc):
    if not os.path.exists(filepath):
        print(f"❌ 파일을 찾을 수 없습니다: {filepath}")
        return
    
    shutil.copy2(filepath, filepath + ".bak")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    
    if count > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ {desc} 수정 완료: {filepath}")
    else:
        print(f"⚠️ {desc} 패턴을 찾지 못했습니다: {filepath}")

print("🚀 /me 응답에 onetime_credits를 포함시키는 수정을 시작합니다...\n")

# 1. app/auth/router.py 의 _user_public 함수 수정
router_path = "app/auth/router.py"
if os.path.exists(router_path):
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # _user_public 함수 내부를 찾아서 onetime_credits 추가
    # 보통 return { "id": user["id"], "tier": user["tier"], ... } 형태
    pattern = r"(def _user_public\(.*?\)\s*->\s*dict:\s*.*?return\s*\{)(.*?)(\})"
    
    def repl(m):
        body = m.group(2)
        if "onetime_credits" not in body:
            # 기존 반환 딕셔너리에 onetime_credits 추가
            return m.group(1) + body.rstrip() + ',\n        "onetime_credits": user.get("onetime_credits", 0),\n    ' + m.group(3)
        return m.group(0)

    patch_file(router_path, pattern, repl, "_user_public 함수에 onetime_credits 추가")
else:
    print(f"❌ 파일을 찾을 수 없습니다: {router_path}")

# 2. Pydantic 스키마(MeResponse) 수정
schema_files = glob.glob("app/schemas/*.py")
patched_schema = False

for filepath in schema_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # class MeResponse 또는 class UserResponse 찾기
    if "class MeResponse" in content or "class UserResponse" in content:
        # 클래스 내부에 tier: str 이 있는지 확인
        if "tier:" in content and "onetime_credits" not in content:
            # tier 필드 바로 아래에 onetime_credits 필드 추가
            patch_file(
                filepath,
                r"(tier:\s*[^\n]+)",
                r"\1\n    onetime_credits: int = 0",
                "Pydantic 스키마(MeResponse/UserResponse)에 onetime_credits 추가"
            )
            patched_schema = True
            break

if not patched_schema:
    print("ℹ️ 스키마 파일에서 MeResponse/UserResponse를 찾지 못했거나 이미 수정되었습니다.")

print("\n✨ 수정이 완료되었습니다! 백엔드를 다시 배포하세요.")