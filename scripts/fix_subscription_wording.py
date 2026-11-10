# scripts/fix_subscription_wording.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/src/components/PaymentModal.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 프리미엄 구독 가격 텍스트 변경
old_text = '{isTelegramEnv ? "400 Stars / month" : "$6.99 / month (Cancel anytime)"}'
new_text = '{isTelegramEnv ? "400 Stars / month (Auto-renews)" : "$6.99 / month (Auto-renews. Cancel anytime.)"}'

if old_text in src:
    src = src.replace(old_text, new_text, 1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ 프리미엄 구독 가격 문구 수정 완료")
else:
    # 만약 이전 패치에서 약간 다르게 들어갔다면 정규식으로 찾아서 교체
    pattern = r'\{isTelegramEnv \? "[^"]*" : "[^"]*"\}'
    if re.search(pattern, src):
        src = re.sub(pattern, new_text, src, count=1)
        PATH.write_text(src, encoding="utf-8")
        print("✅ 프리미엄 구독 가격 문구 수정 완료 (정규식 적용)")
    else:
        print("❌ 가격 텍스트를 찾지 못했습니다. 수동 확인 필요.")

# 2. 하단 안내 문구도 조금 더 명확하게 변경 (선택)
# "Secure checkout powered by Telegram Stars." -> "Subscription auto-renews. Secure checkout powered by Telegram Stars."
old_terms = '{isTelegramEnv ? "Secure checkout powered by Telegram Stars." : "Secure checkout powered by Lemon Squeezy."}'
new_terms = '{isTelegramEnv ? "Auto-renews. Secure checkout powered by Telegram Stars." : "Auto-renews. Secure checkout powered by Lemon Squeezy."}'

if old_terms in src:
    src = src.replace(old_terms, new_terms, 1)
    print("✅ 하단 안내 문구 수정 완료")