import os
import re
import shutil

filepath = "frontend/src/components/PaymentModal.tsx"

if os.path.exists(filepath):
    shutil.copy2(filepath, filepath + ".bak")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1회권 결제 함수(또는 버튼)를 찾아서 true 전달하도록 변경
    # 패턴: handleOneTimeCheckout, onetime, 단품, $2.99 등이 포함된 함수 내부의 api.createCheckout()
    
    def repl(match):
        # 매칭된 함수 전체 문자열
        func_body = match.group(0)
        if "api.createCheckout()" in func_body:
            # 만약 "onetime" 이나 "단품" 이라는 단어가 근처에 있으면 true 주입
            if any(k in func_body.lower() for k in ["onetime", "one_time", "단품", "150", "2.99"]):
                func_body = func_body.replace("api.createCheckout()", "api.createCheckout(true)")
                return func_body
        return func_body

    # 대략적인 함수 블록 추출 정규식
    # const handle... = async () => { ... api.createCheckout() ... }
    pattern = r"(const\s+handle\w+\s*=\s*async\s*\(\)\s*=>\s*\{.*?api\.createCheckout\(\)\s*.*?\})"
    
    new_content, count = re.subn(pattern, repl, content, flags=re.DOTALL)
    
    # 만약 함수 블록 추출에 실패했다면, 그냥 화면 전체에서 첫 번째 createCheckout() 찾기
    if count == 0:
        # 그냥 api.createCheckout() 을 찾아서 근처 텍스트 확인 후 치환
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "api.createCheckout()" in line:
                context = "\n".join(lines[max(0, i-5):i+5]).lower()
                if any(k in context for k in ["onetime", "one_time", "단품", "150", "2.99"]):
                    lines[i] = line.replace("api.createCheckout()", "api.createCheckout(true)")
                    new_content = "\n".join(lines)
                    count += 1

    if count > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ PaymentModal.tsx 자동 수정 완료! (1회권 버튼에 true 주입됨)")
    else:
        print("⚠️ 1회권 버튼을 자동으로 찾지 못했습니다. (파일 구조가 특이할 수 있습니다.)")
        print("👇 PaymentModal.tsx의 45~75번째 줄을 캡처해서 보여주시면, 그것만 딱 고쳐드리겠습니다.")
else:
    print(f"❌ 파일을 찾을 수 없습니다: {filepath}")