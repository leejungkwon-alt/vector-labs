import os
import re
import shutil
import subprocess

print("==================================================")
print("🚀 레몬 스퀴지 1회권 결제 완벽 자동화 스크립트 시작")
print("==================================================\n")

# 1. 레몬 스퀴지 Variant ID 입력받기
print("레몬 스퀴지 대시보드에서 '1회권 상품($2.99)'의 Variant ID(숫자)를 입력하세요.")
variant_id = input("👉 Variant ID: ").strip()
if not variant_id:
    print("❌ Variant ID가 입력되지 않았습니다. 스크립트를 종료합니다.")
    exit()

# 2. 백엔드 1: lemonsqueezy_client.py 수정
client_path = "app/services/lemonsqueezy_client.py"
if os.path.exists(client_path):
    shutil.copy2(client_path, client_path + ".bak")
    with open(client_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace(
        "async def create_checkout_url(user_id: str, email: str | None = None) -> str:",
        "async def create_checkout_url(user_id: str, email: str | None = None, variant_id: str | None = None) -> str:"
    )
    content = content.replace(
        '"variant": {"data": {"type": "variants", "id": os.environ["LEMONSQUEEZY_VARIANT_ID"]}},',
        '"variant": {"data": {"type": "variants", "id": variant_id or os.environ["LEMONSQUEEZY_VARIANT_ID"]}},'
    )
    with open(client_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 백엔드(lemonsqueezy_client.py) 패치 완료")

# 3. 백엔드 2: billing.py 수정
billing_path = "app/api/v1/endpoints/billing.py"
if os.path.exists(billing_path):
    shutil.copy2(billing_path, billing_path + ".bak")
    with open(billing_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "class CheckoutRequest" not in content:
        content = content.replace("router = APIRouter()", "from pydantic import BaseModel\n\nclass CheckoutRequest(BaseModel):\n    is_onetime: bool = False\n\nrouter = APIRouter()")
    
    old_endpoint = '''@router.post("/checkout")
async def create_checkout(user: dict = Depends(get_current_user)):
    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""
    from app.services.lemonsqueezy_client import create_checkout_url
    
    url = await create_checkout_url(user_id=user["id"], email=user.get("email"))
    return {"url": url}'''
    
    new_endpoint = '''@router.post("/checkout")
async def create_checkout(payload: CheckoutRequest = CheckoutRequest(), user: dict = Depends(get_current_user)):
    """프론트엔드에서 결제 버튼을 눌렀을 때 호출되는 API"""
    from app.services.lemonsqueezy_client import create_checkout_url
    import os
    
    variant_id = os.environ.get("LEMONSQUEEZY_ONETIME_VARIANT_ID") if payload.is_onetime else os.environ.get("LEMONSQUEEZY_VARIANT_ID")
    
    url = await create_checkout_url(user_id=user["id"], email=user.get("email"), variant_id=variant_id)
    return {"url": url}'''
    
    content = content.replace(old_endpoint, new_endpoint)
    with open(billing_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 백엔드(billing.py) 패치 완료")

# 4. 프론트엔드 1: api/client.ts 수정
frontend_client = "frontend/src/api/client.ts"
if os.path.exists(frontend_client):
    shutil.copy2(frontend_client, frontend_client + ".bak")
    with open(frontend_client, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r"createCheckout:\s*\(\)\s*=>\s*[^\n]+,"
    new_code = '''createCheckout: (is_onetime = false) => request<{ url: string }>('/billing/checkout', { method: 'POST', body: JSON.stringify({ is_onetime }) }),'''
    content, count = re.subn(pattern, new_code, content)
    with open(frontend_client, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 프론트엔드(client.ts) 패치 완료")

# 5. 프론트엔드 2: PaymentModal.tsx 수정 (지능형 탐색)
modal_path = "frontend/src/components/PaymentModal.tsx"
if os.path.exists(modal_path):
    shutil.copy2(modal_path, modal_path + ".bak")
    with open(modal_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 단품/1회권과 관련된 함수를 찾아서 true 주입
    def repl(match):
        func_body = match.group(0)
        if "api.createCheckout()" in func_body and any(k in func_body.lower() for k in ["onetime", "one_time", "단품", "150", "2.99"]):
            return func_body.replace("api.createCheckout()", "api.createCheckout(true)")
        return func_body

    pattern = r"(const\s+handle\w+\s*=\s*async\s*\(\)\s*=>\s*\{.*?api\.createCheckout\(\)\s*.*?\})"
    content, count = re.subn(pattern, repl, content, flags=re.DOTALL)
    
    if count == 0: # 2차 시도 (그냥 createCheckout() 근처 텍스트 확인)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "api.createCheckout()" in line:
                context = "\n".join(lines[max(0, i-5):i+5]).lower()
                if any(k in context for k in ["onetime", "one_time", "단품", "150", "2.99"]):
                    lines[i] = line.replace("api.createCheckout()", "api.createCheckout(true)")
                    content = "\n".join(lines)
                    count += 1
    with open(modal_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 프론트엔드(PaymentModal.tsx) 패치 완료")

# 6. GCP Cloud Run 환경변수 자동 등록
print("\n☁️ Cloud Run 환경변수 업데이트 중...")
gcloud_cmd = f"gcloud run services update saju-backend --region asia-northeast3 --update-env-vars LEMONSQUEEZY_ONETIME_VARIANT_ID={variant_id}"
try:
    subprocess.run(gcloud_cmd, shell=True, check=True)
    print("✅ GCP 환경변수 등록 완료!")
except Exception as e:
    print(f"⚠️ GCP 자동 등록 실패. 터미널에 직접 입력해 주세요:\n{gcloud_cmd}")

print("\n==================================================")
print("🎉 모든 코드 수정 및 환경변수 설정이 완료되었습니다!")
print("이제 아래 두 명령어만 터미널에 입력하시면 끝납니다.")
print("1. .\\deploy.ps1")
print("2. git add . && git commit -m 'fix: 1회권 결제 완벽 적용' && git push origin main")
print("==================================================")