# scripts/patch_frontend_checkout.py
"""
프론트엔드(Lemon Squeezy 결제 연동) 패치 스크립트
1. client.ts: billing/checkout API 호출 메서드 추가
2. PaymentModal.tsx: 기존 mock 결제 로직을 Lemon Squeezy 결제창 호출로 교체
"""
import re
import shutil
import sys
from pathlib import Path

# 파일 경로 (프로젝트 구조에 맞게 수정 필요)
CLIENT_PATH = Path("frontend/src/api/client.ts")
MODAL_PATH = Path("frontend/src/components/PaymentModal.tsx")

def patch_client():
    if not CLIENT_PATH.exists():
        print(f"⚠️ {CLIENT_PATH} 파일을 찾을 수 없습니다. 경로를 확인해 주세요.")
        return

    src = CLIENT_PATH.read_text(encoding="utf-8")
    if "checkout:" in src:
        print("✅ client.ts 는 이미 패치되어 있습니다.")
        return

    backup = CLIENT_PATH.with_suffix(".ts.bak")
    shutil.copy2(CLIENT_PATH, backup)
    print(f"백업 생성: {backup}")

    # 기존 purchase 메서드 근처에 checkout 메서드 삽입
    # (만약 purchase 메서드가 없다면 파일 하단에 추가해야 할 수도 있습니다)
    checkout_code = '    checkout: () => request<{ url: string }>("/billing/checkout", { method: "POST" }),\n'
    
    if "purchase:" in src:
        src = re.sub(r'(\s*)purchase:\s*\(', f'{checkout_code}\\1purchase: (', src, count=1)
    else:
        # purchase가 없으면 request 함수 내부나 객체 끝에 추가
        print("⚠️ purchase 메서드를 찾지 못했습니다. 수동으로 checkout 메서드를 추가해 주세요.")
        return

    CLIENT_PATH.write_text(src, encoding="utf-8")
    print("✅ client.ts 패치 완료 (checkout API 추가)")

def patch_modal():
    if not MODAL_PATH.exists():
        print(f"⚠️ {MODAL_PATH} 파일을 찾을 수 없습니다. 경로를 확인해 주세요.")
        return

    src = MODAL_PATH.read_text(encoding="utf-8")
    if "window.location.href = url" in src:
        print("✅ PaymentModal.tsx 는 이미 패치되어 있습니다.")
        return

    backup = MODAL_PATH.with_suffix(".tsx.bak")
    shutil.copy2(MODAL_PATH, backup)
    print(f"백업 생성: {backup}")

    # 1) react-native import에 Platform, Linking 추가
    def add_import(match):
        imports = match.group(1).split(',')
        imports = [i.strip() for i in imports]
        if 'Platform' not in imports: imports.append('Platform')
        if 'Linking' not in imports: imports.append('Linking')
        return f"import {{ {', '.join(imports)} }} from 'react-native';"

    src = re.sub(r"import\s*{([^}]*)}\s*from\s*'react-native';", add_import, src)

    # 2) 결제 로직 교체 (기존 api.purchase 호출을 찾아서 교체)
    # 정규식으로 기존 purchase 호출 블록을 찾습니다. (프로젝트 코드에 맞게 수정이 필요할 수 있음)
    # 예: const receipt = await api.purchase({...});
    purchase_pattern = r"(const\s+\w+\s*=\s*await\s+api\.purchase\([\s\S]*?\);)"
    
    lemon_logic = """try {
      const { url } = await api.checkout();
      if (Platform.OS === "web") {
        window.location.href = url;
      } else {
        await Linking.openURL(url);
      }
    } catch (err) {
      console.error("Checkout failed", err);
    }"""

    if re.search(purchase_pattern, src):
        src = re.sub(purchase_pattern, lemon_logic, src)
        print("→ mock purchase 로직을 Lemon Squeezy checkout으로 교체했습니다.")
    else:
        print("⚠️ 기존 api.purchase 호출 패턴을 찾지 못했습니다. 수동으로 수정이 필요할 수 있습니다.")

    MODAL_PATH.write_text(src, encoding="utf-8")
    print("✅ PaymentModal.tsx 패치 완료")

if __name__ == "__main__":
    print("🚀 프론트엔드 Lemon Squeezy 결제 연동 패치를 시작합니다...\n")
    patch_client()
    patch_modal()
    print("\n🎉 프론트엔드 패치가 완료되었습니다. Vercel에 재배포하세요!")