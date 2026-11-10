import os
import re
import shutil

def patch_file(filepath, regex_pattern, replacement, desc):
    if not os.path.exists(filepath):
        print(f"❌ 파일을 찾을 수 없습니다: {filepath}")
        return
    
    shutil.copy2(filepath, filepath + ".bak")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    new_content, count = re.subn(regex_pattern, replacement, content, flags=re.DOTALL)
    
    if count > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ {desc} 수정 완료: {filepath}")
    else:
        print(f"⚠️ {desc} 패턴을 찾지 못했습니다 (이미 수정되었거나 코드가 다름): {filepath}")

print("🚀 남은 버그 수정 스크립트를 시작합니다...\n")

# =====================================================================
# 1. frontend/types.ts - AuthResponse의 user 객체에 onetime_credits 추가
# =====================================================================
patch_file(
    filepath="frontend/types.ts",
    regex_pattern=r"(created_at:\s*string;)",
    replacement=r"\1\n    onetime_credits: number;",
    desc="프론트엔드 타입(AuthResponse)"
)

# =====================================================================
# 2. app/auth/repository.py - add_onetime_credits 메서드를 _run 방식으로 교체
# =====================================================================
repo_path = "app/auth/repository.py"
if os.path.exists(repo_path):
    shutil.copy2(repo_path, repo_path + ".bak")
    with open(repo_path, "r", encoding="utf-8") as f:
        repo_content = f.read()
        
    # 기존에 스크립트가 잘못 넣은 add_onetime_credits 메서드 전체를 찾아서 교체
    # def add_onetime_credits 부터 self.db.commit() 까지 매칭
    pattern = r"def add_onetime_credits\(.*?self\.db\.commit\(\)"
    new_method = '''def add_onetime_credits(self, user_id: str, amount: int = 1) -> None:
        """유저의 1회 이용권(크레딧)을 증가시킵니다."""
        self._run(
            "UPDATE users SET onetime_credits = COALESCE(onetime_credits, 0) + ? WHERE id = ?",
            (amount, user_id),
        )'''
        
    new_content, count = re.subn(pattern, new_method, repo_content, flags=re.DOTALL)
    if count > 0:
        with open(repo_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ 백엔드 DB 메서드(_run 방식 적용) 수정 완료: {repo_path}")
    else:
        print(f"⚠️ add_onetime_credits 메서드를 찾지 못했습니다 (이미 수정되었거나 코드가 다름).")
else:
    print(f"❌ 파일을 찾을 수 없습니다: {repo_path}")

print("\n✨ 수정 완료! 아래 DB 쿼리를 Neon에서 실행했는지 꼭 확인하세요:")
print("   ALTER TABLE users ADD COLUMN onetime_credits INTEGER DEFAULT 0;")
print("   (이미 실행하셨다면 무시하셔도 됩니다.)")