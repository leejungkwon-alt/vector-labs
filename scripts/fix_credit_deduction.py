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

print("🚀 1회권 차감 로직 적용 스크립트를 시작합니다...\n")

# =====================================================================
# 1. app/api/v1/endpoints/report.py 수정 (1회권 차감 로직 추가)
# =====================================================================
report_path = "app/api/v1/endpoints/report.py"
old_report_code = '''    tier = "free" if current_user is None else (current_user.get("tier") or "free")
    uid = current_user.get("id") if current_user else None
    from app.auth.repository import get_repository
    addons = get_repository().list_addons(uid) if uid else []
    report = apply_entitlement_gate(report, tier, addons)
    return {"report": report}'''

new_report_code = '''    tier = "free" if current_user is None else (current_user.get("tier") or "free")
    uid = current_user.get("id") if current_user else None
    
    from app.auth.repository import get_repository
    repo = get_repository()
    
    # 💡 1회권(크레딧) 결제 유저 처리
    if uid and tier == "free":
        credits = repo.get_onetime_credits(uid)
        if credits and credits > 0:
            # 원자적 차감 성공 시 이번 리포트는 프리미엄으로 취급
            if repo.deduct_onetime_credit(uid):
                tier = "premium"
                logger.info(f"User {uid} used 1 onetime credit. Remaining: {credits - 1}")

    addons = repo.list_addons(uid) if uid else []
    report = apply_entitlement_gate(report, tier, addons)
    return {"report": report}'''

patch_file(
    filepath=report_path,
    regex_pattern=re.escape(old_report_code),
    replacement=new_report_code,
    desc="리포트 API 1회권 차감 로직"
)

# =====================================================================
# 2. app/auth/repository.py 수정 (크레딧 조회 및 차감 메서드 추가)
# =====================================================================
repo_path = "app/auth/repository.py"
if os.path.exists(repo_path):
    with open(repo_path, "r", encoding="utf-8") as f:
        repo_content = f.read()
        
    if "def deduct_onetime_credit" not in repo_content:
        # update_subscription 메서드 위에 새로운 메서드 2개 삽입
        new_methods = '''def get_onetime_credits(self, user_id: str) -> int:
        """유저의 1회 이용권(크레딧) 잔액을 조회합니다."""
        try:
            row = self._run(
                "SELECT onetime_credits FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return row["onetime_credits"] if row and row["onetime_credits"] else 0
        except Exception:
            return 0

    def deduct_onetime_credit(self, user_id: str) -> bool:
        """1회 이용권을 1개 차감합니다. 차감 성공 시 True 반환"""
        cursor = self._run(
            "UPDATE users SET onetime_credits = onetime_credits - 1 WHERE id = ? AND onetime_credits > 0",
            (user_id,)
        )
        # sqlite3 기준 rowcount > 0 이면 차감 성공
        return cursor.rowcount > 0

    def update_subscription('''
        
        new_content, count = re.subn(r"def update_subscription\(", new_methods, repo_content, count=1)
        if count > 0:
            with open(repo_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ DB 크레딧 조회/차감 메서드 추가 완료: {repo_path}")
        else:
            print(f"⚠️ update_subscription 메서드를 찾지 못해 수동 추가가 필요합니다: {repo_path}")
    else:
        print(f"ℹ️ DB 크레딧 메서드가 이미 존재합니다: {repo_path}")
else:
    print(f"❌ 파일을 찾을 수 없습니다: {repo_path}")

print("\n✨ 모든 수정이 완료되었습니다. 백엔드를 다시 배포하세요!")