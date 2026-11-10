import os
import shutil
import subprocess
import re

print("🚀 레몬 스퀴지 1회권 웹 결제 최종 수정 스크립트를 시작합니다...\n")

# 1. 프론트엔드: api/client.ts 수정 (checkout 함수가 is_onetime을 받도록)
client_path = "frontend/src/api/client.ts"
if os.path.exists(client_path):
    shutil.copy2(client_path, client_path + ".bak")
    with open(client_path, "r", encoding="utf-8") as f:
        content = f.read()

    # checkout 함수 찾아서 파라미터 추가
    pattern = r"checkout:\s*\(\)\s*=>\s*[^\n]+,"
    replacement = '''checkout: (is_onetime = false) => request<{ url: string }>('/billing/checkout', { method: 'POST', body: JSON.stringify({ is_onetime }) }),'''
    content, count = re.subn(pattern, replacement, content)
    
    # 만약 위 패턴이 없다면(혹은 이전 스크립트로 createCheckout으로 변경했다면)
    if count == 0:
        pattern2 = r"createCheckout:\s*\(\)\s*=>\s*[^\n]+,"
        content, count = re.subn(pattern2, replacement.replace("checkout:", "createCheckout:"), content)

    with open(client_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 프론트엔드 client.ts 수정 완료 (is_onetime 파라미터 수신 준비)")

# 2. 프론트엔드: PaymentModal.tsx 수정
modal_path = "frontend/src/components/PaymentModal.tsx"
if os.path.exists(modal_path):
    shutil.copy2(modal_path, modal_path + ".bak")
    with open(modal_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 하드코딩된 api.checkout() 호출 부분을 productId에 따라 분기하도록 수정
    old_code = "const { url } = await api.checkout();"
    new_code = "const { url } = await api.checkout(productId === 'onetime');"
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(modal_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 프론트엔드 PaymentModal.tsx 수정 완료 (1회권 결제 분기 적용)")
    else:
        print("⚠️ PaymentModal.tsx에서 api.checkout() 호출 부분을 찾지 못했습니다. 코드가 이미 수정되었을 수 있습니다.")

# 3. 자동으로 깃 커밋 및 푸시 (프론트엔드 배포)
print("\n📦 프론트엔드 배포를 위해 Git에 푸시합니다...")
try:
    subprocess.run("git add .", shell=True, check=True)
    subprocess.run('git commit -m "fix: 레몬 스퀴지 1회권 결제 링크 분기 적용"', shell=True, check=True)
    subprocess.run("git push origin main", shell=True, check=True)
    print("✅ Git 푸시 완료! Vercel이 자동으로 배포를 시작합니다.")
except subprocess.CalledProcessError:
    print("⚠️ Git 푸시에 실패했습니다. 변경 사항이 없거나, 원격 저장소에 문제가 있을 수 있습니다.")

print("\n==================================================")
print("🎉 프론트엔드 수정 및 배포 완료!")
print("이제 백엔드만 배포하면 끝납니다. 아래 명령어를 실행하세요:")
print("👉 .\\deploy.ps1")
print("==================================================")