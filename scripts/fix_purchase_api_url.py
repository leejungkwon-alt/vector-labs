import os
import shutil

print("🚀 프론트엔드 API 주소 오류 수정을 시작합니다...\n")

# 1. client.ts 에서 잘못된 주소 수정
client_path = "frontend/src/api/client.ts"
if os.path.exists(client_path):
    shutil.copy2(client_path, client_path + ".bak")
    with open(client_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "/auth/me/purchases" in content:
        content = content.replace("/auth/me/purchases", "/billing/purchases")
        with open(client_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ client.ts 주소 수정 완료 (/auth/me/purchases -> /billing/purchases)")
    else:
        print("ℹ️ client.ts 에서 '/auth/me/purchases' 를 찾지 못했습니다. (이미 수정되었거나 코드가 다름)")

    # 2. getPurchases 함수가 없다면 추가
    if "getPurchases" not in content:
        import re
        pattern = r"(getPortalUrl:\s*\(\)\s*=>[^\n]+,)"
        replacement = r"\1\n  getPurchases: () => request<{ purchases: any[] }>('/billing/purchases'),"
        content, count = re.subn(pattern, replacement, content)
        if count > 0:
            with open(client_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ client.ts getPurchases 함수 추가 완료")

print("\n✨ 수정 완료! 이제 아래 순서대로 실행해 주세요.")
print("1. 백엔드 배포 (새 API 주소 적용): .\\deploy.ps1")
print("2. 프론트엔드 배포 (Git): git add . && git commit -m 'fix: 구매 내역 API 주소 수정' && git push")