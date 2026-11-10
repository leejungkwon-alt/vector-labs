import os
import re
import shutil

def patch_frontend_home():
    filepath = "frontend/app/(tabs)/home.tsx"
    if not os.path.exists(filepath):
        print(f"❌ 파일을 찾을 수 없습니다: {filepath}")
        return

    shutil.copy2(filepath, filepath + ".bak")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "useAuthStore" not in content:
        content = "import { useAuthStore } from '@/store/authStore';\n" + content
        print("✅ useAuthStore import 추가 완료")

    pattern = r"((?:const|let|var)\s+\w+\s*=\s*await\s+api\.report\([^;]*?\);|await\s+api\.report\([^;]*?\);)"
    
    def repl(m):
        matched = m.group(1)
        if "bootstrap" in matched:
            return matched
        indent_match = re.search(r"^(\s*)", matched)
        indent = indent_match.group(1) if indent_match else "  "
        return matched + f"\n{indent}// 1회권 차감 후 유저 정보(크레딧) 갱신\n{indent}useAuthStore.getState().bootstrap();"

    new_content, count = re.subn(pattern, repl, content, flags=re.MULTILINE)
    
    if count > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ 프론트엔드 home.tsx 수정 완료 (리포트 조회 후 크레딧 갱신 로직 주입)")
    else:
        print("⚠️ api.report 호출 패턴을 찾지 못했습니다.")

patch_frontend_home()