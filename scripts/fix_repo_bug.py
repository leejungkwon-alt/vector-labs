import os
import re
import shutil

repo_path = "app/auth/repository.py"
if os.path.exists(repo_path):
    shutil.copy2(repo_path, repo_path + ".bak")
    with open(repo_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. get_onetime_credits 수정 ( _one 사용 )
    old_get = r"def get_onetime_credits\(.*?return 0\n"
    new_get = '''def get_onetime_credits(self, user_id: str) -> int:
        """유저의 1회 이용권(크레딧) 잔액을 조회합니다."""
        row = self._one("SELECT onetime_credits FROM users WHERE id = ?", (user_id,))
        return row["onetime_credits"] if row and row["onetime_credits"] else 0
'''
    content, count1 = re.subn(old_get, new_get, content, flags=re.DOTALL)

    # 2. deduct_onetime_credit 수정 ( 정수 반환값 비교 )
    old_deduct = r"def deduct_onetime_credit\(.*?return cursor\.rowcount > 0\n"
    new_deduct = '''def deduct_onetime_credit(self, user_id: str) -> bool:
        """1회 이용권을 1개 차감합니다. 차감 성공 시 True 반환"""
        updated = self._run(
            "UPDATE users SET onetime_credits = onetime_credits - 1 WHERE id = ? AND onetime_credits > 0",
            (user_id,)
        )
        return updated > 0
'''
    content, count2 = re.subn(old_deduct, new_deduct, content, flags=re.DOTALL)

    if count1 > 0 and count2 > 0:
        with open(repo_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ repository.py 크레딧 메서드 버그 수정 완료!")
    else:
        print(f"⚠️ 수정 실패 (get: {count1}, deduct: {count2}). 직접 코드를 확인해주세요.")
else:
    print(f"❌ 파일을 찾을 수 없습니다: {repo_path}")