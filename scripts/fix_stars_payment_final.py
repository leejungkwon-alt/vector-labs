# scripts/fix_stars_payment_final.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/src/components/PaymentModal.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 기존 handlePay 함수 전체를 정규식으로 찾아서 교체
pattern = r'const handlePay = async \(productId: string\) => \{[\s\S]*?\n  \};'

new_func = '''const handlePay = async (productId: string) => {
    setLoading(productId);
    try {
      const tg = (window as any).Telegram?.WebApp;
      const isTelegram = !!tg?.initData;

      if (isTelegram) {
        // --- 텔레그램 스타 결제 ---
        try {
          const { invoice_link } = await api.createStarsInvoice();
          tg.openInvoice(invoice_link, (status: string) => {
            if (status === "paid") {
              Alert.alert("결제 완료", "프리미엄이 활성화되었습니다! 앱을 새로고침합니다.");
              window.location.reload();
            } else if (status === "cancelled") {
              // 사용자 취소
            } else if (status === "failed") {
              Alert.alert("결제 실패", "결제를 다시 시도해주세요.");
            }
          });
          return; // ★ 중요: 여기서 함수를 종료하여 Lemon Squeezy로 넘어가지 않도록 함
        } catch (e: any) {
          Alert.alert("결제 오류", e.message || "텔레그램 결제를 시작할 수 없습니다.");
          return;
        }
      }

      // --- 기존 Lemon Squeezy 결제 (일반 웹) ---
      const { url } = await api.checkout();
      if (Platform.OS === "web") {
        window.location.href = url;
      } else {
        await Linking.openURL(url);
        onClose();
      }
    } catch (e: any) {
      Alert.alert("Checkout Failed", e.message || "Please try again.");
    } finally {
      setLoading(null);
    }
  };'''

if re.search(pattern, src, flags=re.DOTALL):
    src = re.sub(pattern, new_func, src, count=1, flags=re.DOTALL)
    PATH.write_text(src, encoding="utf-8")
    print("✅ PaymentModal.tsx 결제 로직 수정 완료 (return; 누락 버그 해결)")
else:
    print("❌ handlePay 함수를 찾지 못했습니다. 수동 확인 필요.")