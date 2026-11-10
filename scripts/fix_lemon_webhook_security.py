#!/usr/bin/env python3
"""
scripts/fix_lemon_webhook_security.py

Lemon Squeezy 웹훅 보안 및 멱등성(Idempotency) 강화 패치 스크립트:
1. app/auth/repository.py:
   - log_purchase()에 purchase_id 매개변수 및 'ON CONFLICT (id) DO NOTHING' 적용
   - add_onetime_purchase_idempotent() 신규 메서드 추가 (중복 웹훅 재전송 시 크레딧 중복 충전 원천 차단)
2. app/api/v1/endpoints/billing.py:
   - order_created 시 status == 'paid' 및 refunded 검증
   - LEMONSQUEEZY_ONETIME_VARIANT_ID 및 구독용 LEMONSQUEEZY_VARIANT_ID 매핑 분기
   - 멱등적 add_onetime_purchase_idempotent() 호출
   - subscription_created 시에도 lemon_sub_{sub_id}로 중복 구매 기록 방지
3. 자동 검증 테스트 및 pytest 수행
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Windows cp949 인코딩 에러 방지
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
os.chdir(ROOT_DIR)

print("=" * 70)
print("[*] Lemon Squeezy 웹훅 1회권 결제 취약점 및 멱등성 패치 시작...")
print("=" * 70)

# --------------------------------------------------------------------------
# 1. app/auth/repository.py 패치
# --------------------------------------------------------------------------
repo_path = ROOT_DIR / "app" / "auth" / "repository.py"
print(f"\n[1/3] {repo_path} 패치 진행 중...")

with open(repo_path, "r", encoding="utf-8") as f:
    repo_content = f.read()

# 백업 생성
shutil.copy2(repo_path, str(repo_path) + ".bak")
print("  -> 백업 생성 완료 (repository.py.bak)")

# 1-1. log_purchase 및 add_onetime_purchase_idempotent 정의
OLD_PURCHASE_DEF = '''    # ---- purchases ----
    def log_purchase(self, user_id: str, product_id: str, platform: str) -> dict:
        pid = uuid.uuid4().hex
        self._run(
            "INSERT INTO purchases (id, user_id, product_id, platform, purchased_at) VALUES (?, ?, ?, ?, ?)",
            (pid, user_id, product_id, platform, _now_iso())
        )
        return self._one("SELECT * FROM purchases WHERE id = ?", (pid,))'''

NEW_PURCHASE_DEF = '''    # ---- purchases ----
    def log_purchase(
        self, user_id: str, product_id: str, platform: str, purchase_id: Optional[str] = None
    ) -> dict:
        """구매 내역 기록. purchase_id가 주어지면 멱등적(ON CONFLICT DO NOTHING)으로 삽입."""
        pid = purchase_id or uuid.uuid4().hex
        self._run(
            "INSERT INTO purchases (id, user_id, product_id, platform, purchased_at) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT (id) DO NOTHING",
            (pid, user_id, product_id, platform, _now_iso()),
        )
        return self._one("SELECT * FROM purchases WHERE id = ?", (pid,))

    def add_onetime_purchase_idempotent(
        self, user_id: str, order_id: str, platform: str = "lemon_squeezy"
    ) -> bool:
        """
        1회권 구매 원자적 멱등 처리:
        동일 purchase_id(lemon_order_{order_id})가 이미 purchases에 존재하면
        중복 크레딧을 지급하지 않고 False 반환.
        신규 주문이면 purchases 기록 및 onetime_credits +1 증가 후 True 반환.
        """
        purchase_id = f"lemon_order_{order_id}" if not str(order_id).startswith("lemon_") else str(order_id)
        
        # 1. purchases에 삽입 시도 (idempotency anchor)
        inserted = self._run(
            "INSERT INTO purchases (id, user_id, product_id, platform, purchased_at) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT (id) DO NOTHING",
            (purchase_id, user_id, "lemon_onetime", platform, _now_iso()),
        )
        if inserted == 0:
            # 이미 처리된 주문 (중복 웹훅)
            return False

        # 2. 신규 주문에 한해서만 크레딧 +1 증가
        self.add_onetime_credit(user_id)
        return True'''

if OLD_PURCHASE_DEF in repo_content:
    repo_content = repo_content.replace(OLD_PURCHASE_DEF, NEW_PURCHASE_DEF)
    with open(repo_path, "w", encoding="utf-8") as f:
        f.write(repo_content)
    print("  [OK] repository.py log_purchase & add_onetime_purchase_idempotent 패치 성공")
elif "add_onetime_purchase_idempotent" in repo_content:
    print("  [INFO] repository.py에 이미 add_onetime_purchase_idempotent가 존재합니다.")
else:
    print("  [FAIL] repository.py 패턴 매칭 실패! 직접 확인이 필요합니다.")
    sys.exit(1)

# --------------------------------------------------------------------------
# 2. app/api/v1/endpoints/billing.py 패치
# --------------------------------------------------------------------------
billing_path = ROOT_DIR / "app" / "api" / "v1" / "endpoints" / "billing.py"
print(f"\n[2/3] {billing_path} 패치 진행 중...")

with open(billing_path, "r", encoding="utf-8") as f:
    billing_content = f.read()

# 백업 생성
shutil.copy2(billing_path, str(billing_path) + ".bak")
print("  -> 백업 생성 완료 (billing.py.bak)")

# billing.py의 order_created 처리 블록 정규식 교체
OLD_WEBHOOK_SUB_LOG = 'if event_name == "subscription_created":\n            repo.log_purchase(user_id, "lemon_sub", "lemon_squeezy")'
NEW_WEBHOOK_SUB_LOG = 'if event_name == "subscription_created":\n            repo.log_purchase(user_id, "lemon_sub", "lemon_squeezy", purchase_id=f"lemon_sub_{event[\'data\'][\'id\']}")'

if OLD_WEBHOOK_SUB_LOG in billing_content:
    billing_content = billing_content.replace(OLD_WEBHOOK_SUB_LOG, NEW_WEBHOOK_SUB_LOG)

ORDER_CREATED_REGEX = r'    elif event_name == "order_created":.*?(?=    return \{"status": "ok"\})'

NEW_ORDER_CREATED_CODE = '''    elif event_name == "order_created":
        order_id = str(event["data"]["id"])
        order_attrs = event["data"].get("attributes", {})
        status = order_attrs.get("status")

        # 1. 결제 완료 상태(paid) 및 비환불 건 확인
        if status != "paid" or order_attrs.get("refunded"):
            return {
                "status": "ignored",
                "reason": f"unpaid_or_refunded (status={status}, refunded={order_attrs.get('refunded')})",
            }

        # 2. 주문 상품의 variant_id 확인
        first_item = order_attrs.get("first_order_item") or {}
        variant_id = str(first_item.get("variant_id") or "")

        onetime_variant = str(os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID", "")).strip()
        sub_variant = str(os.environ.get("LEMONSQUEEZY_VARIANT_ID", "")).strip()

        # 구독 결제의 첫 주문(order_created)인 경우 -> subscription_created에서 처리하므로 스킵
        if sub_variant and variant_id == sub_variant:
            return {"status": "ignored", "reason": "subscription_order_delegated"}

        # 1회권 variant_id가 환경변수에 설정되어 있는 경우 불일치 시 스킵
        if onetime_variant and variant_id != onetime_variant:
            return {
                "status": "ignored",
                "reason": f"variant_mismatch (got {variant_id}, expected {onetime_variant})",
            }

        # 3. 멱등적(Idempotent) 크레딧 지급 및 구매 기록
        try:
            applied = repo.add_onetime_purchase_idempotent(
                user_id=user_id, order_id=order_id, platform="lemon_squeezy"
            )
            if applied:
                print(f"[Webhook] User {user_id} 1회권 결제 완료 (Order: {order_id})")
                return {"status": "ok", "action": "credit_added", "order_id": order_id}
            else:
                print(f"[Webhook] User {user_id} 이미 처리된 주문 건 (Order: {order_id})")
                return {"status": "ok", "action": "duplicate_ignored", "order_id": order_id}
        except Exception as e:
            print(f"[Webhook] DB 업데이트 실패 (Order: {order_id}): {e}")
            raise HTTPException(status_code=500, detail="Database update failed")
            
'''

new_billing_content, count = re.subn(ORDER_CREATED_REGEX, NEW_ORDER_CREATED_CODE, billing_content, flags=re.DOTALL)
if count > 0:
    with open(billing_path, "w", encoding="utf-8") as f:
        f.write(new_billing_content)
    print("  [OK] billing.py order_created 보안/멱등성 로직 적용 완료")
else:
    print("  [FAIL] billing.py의 order_created 정규식 치환에 실패했습니다.")
    sys.exit(1)

# --------------------------------------------------------------------------
# 3. 회귀 테스트 및 검증
# --------------------------------------------------------------------------
print("\n[3/3] 단위 테스트 및 멱등성 검증 수행 중...")

# 로컬 SQLite 테스트 검증을 위해 환경변수 보정
if "SAJU_DATABASE_URL" not in os.environ:
    os.environ["SAJU_ENV"] = "development"

# 간이 검증 테스트
import uuid
from app.auth.repository import get_repository
test_repo = get_repository()
test_user = test_repo.create_anonymous_user()
uid = test_user["id"]
test_order_id = f"test_{uuid.uuid4().hex[:12]}"

try:
    # 1회차: 신규 주문이므로 성공(True)
    ok1 = test_repo.add_onetime_purchase_idempotent(uid, test_order_id)
    # 2회차 (중복 웹훅 전송 시뮬레이션): 동일 주문 ID이므로 거절(False)
    ok2 = test_repo.add_onetime_purchase_idempotent(uid, test_order_id)

    user_after = test_repo.get_user(uid)
    credits = user_after.get("onetime_credits", 0)

    if ok1 is True and ok2 is False and credits == 1:
        print("  [OK] 멱등성 검증 통과: 동일 주문 2회 중복 호출에도 크레딧은 정확히 1만 증가함.")
    else:
        print(f"  [FAIL] 멱등성 검증 실패: ok1={ok1}, ok2={ok2}, credits={credits}")
        sys.exit(1)
finally:
    # 테스트 데이터 정리 (Clean up)
    try:
        test_repo.delete_user(uid)
        test_repo._run("DELETE FROM purchases WHERE id = ?", (f"lemon_order_{test_order_id}",))
    except Exception:
        pass

# 전체 pytest 실행
print("\n전체 pytest 스위트 확인 중...")
res = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"])
if res.returncode == 0:
    print("\n[SUCCESS] 모든 테스트(589+) 통과! 패치가 안전하게 완료되었습니다.")
    print("\n다음 명령어로 변경사항을 커밋하고 배포할 수 있습니다:")
    print("  git add app/auth/repository.py app/api/v1/endpoints/billing.py")
    print("  git commit -m 'fix(billing): add variant verification and webhook idempotency for lemon squeezy'")
    print("  .\\deploy.ps1")
else:
    print("\n[ERROR] pytest 실패 발생. repository.py.bak 및 billing.py.bak을 복원해주세요.")
    sys.exit(res.returncode)
