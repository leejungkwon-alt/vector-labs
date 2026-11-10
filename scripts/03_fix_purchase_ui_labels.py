import os
import re
import shutil

settings_path = "frontend/app/(tabs)/settings.tsx"

if os.path.exists(settings_path):
    shutil.copy2(settings_path, settings_path + ".bak")
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 기존 텍스트 매핑 로직을 찾아서 레몬 스퀴지(lemon_sub) 추가
    old_ui = '''{item.product_id === "stars_onetime" ? "1회 이용권 (150 Stars)" : 
                 item.product_id === "stars_sub" ? "프리미엄 구독 (400 Stars)" : 
                 item.product_id}'''
    
    new_ui = '''{item.product_id === "stars_onetime" ? "1회 이용권 (텔레그램 150 Stars)" : 
                 item.product_id === "stars_sub" ? "프리미엄 구독 (텔레그램 400 Stars)" : 
                 item.product_id === "lemon_sub" ? "프리미엄 구독 (웹 결제)" :
                 item.product_id}'''

    if old_ui in content:
        content = content.replace(old_ui, new_ui)
        with open(settings_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 프론트엔드 구매 내역 UI에 '웹 결제(레몬 스퀴지)' 텍스트 매핑 추가 완료!")
    else:
        # 정규식으로 재시도 (줄바꿈이나 띄어쓰기가 다를 경우 대비)
        pattern = r"\{item\.product_id === \"stars_onetime\".*?item\.product_id\}"
        def repl(m):
            return '''{item.product_id === "stars_onetime" ? "1회 이용권 (텔레그램 150 Stars)" : 
                 item.product_id === "stars_sub" ? "프리미엄 구독 (텔레그램 400 Stars)" : 
                 item.product_id === "lemon_sub" ? "프리미엄 구독 (웹 결제)" :
                 item.product_id}'''
        content, count = re.subn(pattern, repl, content, flags=re.DOTALL)
        if count > 0:
            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(content)
            print("✅ (정규식) 프론트엔드 구매 내역 UI 업데이트 완료!")
        else:
            print("⚠️ UI 매핑 코드를 찾지 못했습니다. 직접 수정이 필요할 수 있습니다.")
else:
    print("❌ 파일을 찾을 수 없습니다.")