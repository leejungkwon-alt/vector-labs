# scripts/fix_payment_modal_ui.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/src/components/PaymentModal.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. isTelegram 상태 감지 로직 추가 (컴포넌트 내부)
if "const isTelegramEnv = " not in src:
    # 컴포넌트 시작 부분 찾기
    match = re.search(r'(export function PaymentModal[^\{]+\{)', src)
    if match:
        state_code = '''
  const tg = typeof window !== "undefined" ? (window as any).Telegram?.WebApp : null;
  const isTelegramEnv = !!tg?.initData;
'''
        src = src[:match.end()] + state_code + src[match.end():]

# 2. 가격 표시 텍스트 동적 변경 ($6.99 -> 400 Stars)
old_price = '<Text style={styles.planPrice}>$6.99 / month (Cancel anytime)</Text>'
new_price = '''<Text style={styles.planPrice}>
                {isTelegramEnv ? "400 Stars / month" : "$6.99 / month (Cancel anytime)"}
              </Text>'''
if old_price in src:
    src = src.replace(old_price, new_price, 1)
    print("✅ 가격 표시 동적 변경 완료")

# 3. 하단 결제 안내 문구 동적 변경 (Lemon Squeezy -> Telegram Stars)
old_terms = '<Text style={styles.terms}>Secure checkout powered by Lemon Squeezy.</Text>'
new_terms = '''<Text style={styles.terms}>
              {isTelegramEnv 
                ? "Secure checkout powered by Telegram Stars." 
                : "Secure checkout powered by Lemon Squeezy."}
            </Text>'''
if old_terms in src:
    src = src.replace(old_terms, new_terms, 1)
    print("✅ 결제 안내 문구 동적 변경 완료")

# 4. 깨진 아이콘(네모 박스) 제거 (상단 X 버튼이나 플랜 옆 아이콘)
src = re.sub(r'<Ionicons name="[^"]+" size=\{24\} color=\{colors\.textMuted\} />', '<Text style={{ fontSize: 20 }}>✕</Text>', src)

PATH.write_text(src, encoding="utf-8")
print("🎉 PaymentModal UI 동적 변경 완료")