# scripts/fix_payment_modal_ui_v2.py
from pathlib import Path
import sys

PATH = Path("frontend/src/components/PaymentModal.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# ─────────────────────────────────────────────
# 1. isTelegramEnv 상태 추가 (안전한 위치: bootstrap 선언 바로 다음)
# ─────────────────────────────────────────────
anchor = "  const bootstrap = useAuthStore((s) => s.bootstrap);"
state_code = """
  const tg = typeof window !== "undefined" ? (window as any).Telegram?.WebApp : null;
  const isTelegramEnv = !!tg?.initData;"""

if "const isTelegramEnv" not in src:
    if anchor in src:
        src = src.replace(anchor, anchor + state_code, 1)
        print("✅ isTelegramEnv 상태 추가 완료")
    else:
        print("❌ bootstrap 선언을 찾지 못했습니다.")
        sys.exit(1)
else:
    print("⚠️ isTelegramEnv가 이미 존재합니다.")

# ─────────────────────────────────────────────
# 2. 가격 텍스트 동적 변경
# ─────────────────────────────────────────────
old_price = '<Text style={styles.planPrice}>$6.99 / month (Cancel anytime)</Text>'
new_price = '<Text style={styles.planPrice}>{isTelegramEnv ? "400 Stars / month" : "$6.99 / month (Cancel anytime)"}</Text>'

if old_price in src:
    src = src.replace(old_price, new_price, 1)
    print("✅ 가격 표시 동적 변경 완료")
elif "400 Stars / month" in src:
    print("⚠️ 가격은 이미 변경되어 있습니다.")
else:
    print("❌ 가격 텍스트를 찾지 못했습니다.")

# ─────────────────────────────────────────────
# 3. 하단 결제 안내 문구 동적 변경
# ─────────────────────────────────────────────
old_terms = '<Text style={styles.terms}>Secure checkout powered by Lemon Squeezy.</Text>'
new_terms = '<Text style={styles.terms}>{isTelegramEnv ? "Secure checkout powered by Telegram Stars." : "Secure checkout powered by Lemon Squeezy."}</Text>'

if old_terms in src:
    src = src.replace(old_terms, new_terms, 1)
    print("✅ 결제 안내 문구 동적 변경 완료")
elif "Telegram Stars" in src:
    print("⚠️ 안내 문구는 이미 변경되어 있습니다.")
else:
    print("❌ 안내 문구를 찾지 못했습니다.")

PATH.write_text(src, encoding="utf-8")
print("🎉 PaymentModal UI 동적 변경 완료")