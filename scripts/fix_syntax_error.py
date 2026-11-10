import os
import shutil

filepath = "app/auth/router.py"

if os.path.exists(filepath):
    shutil.copy2(filepath, filepath + ".bak")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 연속된 쉼표(,,)를 하나의 쉼표(,)로 변경
    if ",," in content:
        content = content.replace(",,", ",")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 문법 에러(,,) 수정 완료!")
    else:
        print("ℹ️ 연속된 쉼표를 찾지 못했습니다. 코드를 직접 확인해 주세요.")
else:
    print(f"❌ 파일을 찾을 수 없습니다: {filepath}")