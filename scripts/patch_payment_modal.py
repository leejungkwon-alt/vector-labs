import shutil
from pathlib import Path
from datetime import datetime

FILE = Path("frontend/src/components/PaymentModal.tsx")

def main():
    if not FILE.exists():
        print(f"❌ {FILE} 파일이 없습니다.")
        return

    src = FILE.read_text(encoding="utf-8")
    
    # 1. 구독 설명 명확화
    src = src.replace(
        '<Text style={styles.planPrice}>$2.99 / month</Text>',
        '<Text style={styles.planPrice}>$2.99 / month (Cancel anytime)</Text>'
    )
    
    # 2. 심화 리포트 (One-time -> Lifetime Unlock)
    src = src.replace(
        '<Text style={styles.planPrice}>$0.99 (one-time)</Text>',
        '<Text style={styles.planPrice}>$0.99 (Lifetime Unlock)</Text>'
    )
    src = src.replace(
        '<Text style={styles.planDetail}>Love, Career & Wealth patterns</Text>',
        '<Text style={styles.planDetail}>Love, Career & Wealth patterns (Keep forever)</Text>'
    )

    # 3. 궁합 (One-time -> Lifetime Unlock)
    src = src.replace(
        '<Text style={styles.planPrice}>$1.99 (one-time)</Text>',
        '<Text style={styles.planPrice}>$1.99 (Lifetime Unlock)</Text>'
    )
    src = src.replace(
        '<Text style={styles.planDetail}>4-axis chemistry with your partner</Text>',
        '<Text style={styles.planDetail}>4-axis chemistry (Keep forever)</Text>'
    )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = FILE.with_suffix(f".tsx.bak.{ts}")
    shutil.copy2(FILE, bak)
    
    FILE.write_text(src, encoding="utf-8")
    print("✅ 결제 모달 문구 수정 완료! (백업 생성됨)")
    print("   - one-time -> Lifetime Unlock 으로 변경")
    print("   - 평생 소장 혜택임을 명시")

if __name__ == "__main__":
    main()
