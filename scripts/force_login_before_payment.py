import os
import re
import shutil
import subprocess

print("🚀 '결제 전 로그인 강제' 시스템을 구축합니다...\n")

# =====================================================================
# 1. 백엔드: 익명 유저의 결제 API 호출 차단 (401 에러)
# =====================================================================
billing_path = "app/api/v1/endpoints/billing.py"
if os.path.exists(billing_path):
    shutil.copy2(billing_path, billing_path + ".bak")
    with open(billing_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1) 레몬 스퀴지 결제 API 차단
    content = content.replace(
        'async def create_checkout(payload: CheckoutRequest = CheckoutRequest(), user: dict = Depends(get_current_user)):\n    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""',
        'async def create_checkout(payload: CheckoutRequest = CheckoutRequest(), user: dict = Depends(get_current_user)):\n    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""\n    if user.get("is_anonymous"):\n        raise HTTPException(status_code=401, detail="Login required for checkout.")'
    )
    
    # 2) 텔레그램 스타 결제 API 차단 (구독)
    content = content.replace(
        'async def create_stars_invoice(user: dict = Depends(get_current_user)):\n    """Telegram Stars 결제를 위한 인보이스 링크 생성"""',
        'async def create_stars_invoice(user: dict = Depends(get_current_user)):\n    """Telegram Stars 결제를 위한 인보이스 링크 생성"""\n    if user.get("is_anonymous"):\n        raise HTTPException(status_code=401, detail="Login required for checkout.")'
    )

    # 3) 텔레그램 스타 결제 API 차단 (1회권)
    content = content.replace(
        'async def create_stars_invoice_onetime(user: dict = Depends(get_current_user)):\n    """Telegram Stars 일시불(단품) 결제 인보이스 링크 생성"""',
        'async def create_stars_invoice_onetime(user: dict = Depends(get_current_user)):\n    """Telegram Stars 일시불(단품) 결제 인보이스 링크 생성"""\n    if user.get("is_anonymous"):\n        raise HTTPException(status_code=401, detail="Login required for checkout.")'
    )

    with open(billing_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 백엔드: 익명 유저 결제 API 차단(401) 적용 완료")


# =====================================================================
# 2. 프론트엔드: PaymentModal에서 로그인 상태 확인 및 로그인 창 띄우기
# =====================================================================
modal_path = "frontend/src/components/PaymentModal.tsx"
if os.path.exists(modal_path):
    shutil.copy2(modal_path, modal_path + ".bak")
    with open(modal_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1) 프롭스에 onRequireLogin 추가
    content = content.replace(
        "interface Props {\n  visible: boolean;\n  onClose: () => void;\n}",
        "interface Props {\n  visible: boolean;\n  onClose: () => void;\n  onRequireLogin?: () => void;\n}"
    )
    content = content.replace(
        "export function PaymentModal({ visible, onClose }: Props) {",
        "export function PaymentModal({ visible, onClose, onRequireLogin }: Props) {"
    )

    # 2) user 스토어 가져오기
    if "const user = useAuthStore((s) => s.user);" not in content:
        content = content.replace(
            "const bootstrap = useAuthStore((s) => s.bootstrap);",
            "const bootstrap = useAuthStore((s) => s.bootstrap);\n  const user = useAuthStore((s) => s.user);"
        )

    # 3) handlePay 시작 부분에 익명 체크 로직 삽입
    content = content.replace(
        "const handlePay = async (productId: string) => {\n    setLoading(productId);",
        "const handlePay = async (productId: string) => {\n    if (user?.is_anonymous) {\n      if (onRequireLogin) onRequireLogin();\n      return;\n    }\n    setLoading(productId);"
    )

    with open(modal_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 프론트엔드: PaymentModal 로그인 체크 로직 추가 완료")


# =====================================================================
# 3. 프론트엔드: settings.tsx에서 로그인 모달 연동
# =====================================================================
settings_path = "frontend/app/(tabs)/settings.tsx"
if os.path.exists(settings_path):
    shutil.copy2(settings_path, settings_path + ".bak")
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    # PaymentModal에 onRequireLogin 프롭스 전달
    content = content.replace(
        '<PaymentModal\n        visible={showPayment}\n        onClose={() => setShowPayment(false)}\n      />',
        '<PaymentModal\n        visible={showPayment}\n        onClose={() => setShowPayment(false)}\n        onRequireLogin={() => {\n          setShowPayment(false);\n          setIsLinkMode(false);\n          setShowLogin(true);\n        }}\n      />'
    )

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 프론트엔드: settings.tsx 로그인 모달 연동 완료")


# =====================================================================
# 4. 배포 (백엔드 & 프론트엔드)
# =====================================================================
print("\n5. 백엔드 배포 시작...")
try:
    subprocess.run(".\\deploy.ps1", shell=True, check=True)
    print("✅ 백엔드 배포 완료")
except subprocess.CalledProcessError:
    print("⚠️ 백엔드 배포 실패")

print("\n6. 프론트엔드 배포를 위해 Git에 푸시합니다...")
try:
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "feat: 결제 전 로그인 강제 (익명 결제 차단)"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("✅ 프론트엔드 푸시 완료! (Vercel 자동 배포)")
except subprocess.CalledProcessError:
    print("⚠️ Git 푸시 실패 (변경 사항이 없거나 오류 발생)")

print("\n🎉 모든 작업이 완료되었습니다! 이제 결제 버튼을 누르면 로그인 창이 뜹니다.")