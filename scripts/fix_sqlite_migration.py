import os
import shutil

filepath = "app/auth/repository.py"

if os.path.exists(filepath):
    shutil.copy2(filepath, filepath + ".bak")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # SQLite 마이그레이션 부분을 try-except로 감싸서 중복 에러 방지
    old_code = '''            if "onetime_credits" not in u_cols:
                self._conn.execute("ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0")'''
    
    new_code = '''            try:
                self._conn.execute("ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass  # 이미 컬럼이 존재하면 무시'''

    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ SQLite 마이그레이션 예외 처리(try-except) 적용 완료!")
    else:
        # 혹시나 코드 모양이 다를 경우를 대비한 2차 시도
        import re
        pattern = r"if\s+\"onetime_credits\"\s+not\s+in\s+u_cols:\s*self\._conn\.execute\(\"ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0\"\)"
        new_content, count = re.subn(pattern, new_code.strip(), content)
        if count > 0:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("✅ (정규식) SQLite 마이그레이션 예외 처리 적용 완료!")
        else:
            print("⚠️ 코드를 찾지 못했습니다. 이미 수정되었거나 코드가 다릅니다.")
else:
    print(f"❌ 파일을 찾을 수 없습니다: {filepath}")