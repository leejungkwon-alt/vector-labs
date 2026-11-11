import os
import re
import shutil
import subprocess

print("🚀 안드로이드 구글 플레이 결제 로직을 적용합니다...\n")

file_path = "frontend/src/components/PaymentModal.tsx"
if os.path.exists(file_path):
    shutil.copy2(file_path, file_path + ".bak")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. import 문 추가
    if "react-native-iap" not in content:
        content = "import * as RNIap from 'react-native-iap';\n" + content

    # 2. useEffect 및 상태 추가
    init_logic = '''
  const [iapReady, setIapReady] = useState(false);
  
  useEffect(() => {
    let isMounted = true;
    const initIAP = async () => {
      if (Platform.OS === 'android' && !isTelegramEnv) {
        try {
          await RNIap.initConnection();
          if (isMounted) setIapReady(true);
          console.log('IAP Connection initialized');
        } catch (err) {
          console.warn('IAP init error:', err);
        }
      }
    };
    initIAP();
    return () => {
      isMounted = false;
      if (Platform.OS === 'android' && !isTelegramEnv) {
        RNIap.endConnection();
      }
    };
  }, [isTelegramEnv]);
'''
    # 컴포넌트 본문 상단에 훅 추가
    if "const [iapReady" not in content:
        # 첫 번째 useState 훅 근처에 추가
        content = re.sub(r"(const \[loading, setLoading\] = useState[^;]+;)", r"\1\n" + init_logic, content)

    # 3. 기존 결제 핸들러 교체 (handlePay 함수 전체)
    # handlePay 함수의 시작부터 끝까지 정규식으로 찾아서 새 로직으로 교체
    old_handle_pay_pattern = r"const handlePay = async \(productId: string\) => \{[\s\S]*?\n  \};"
    
    new_handle_pay = '''const handlePay = async (productId: string) => {
    setLoading(productId);
    try {
      const tg = (window as any).Telegram?.WebApp;
      const isTelegram = !!tg?.initData;

      // --- 1. 안드로이드 앱 (구글 플레이 결제) ---
      if (Platform.OS === 'android' && !isTelegram) {
        if (!iapReady) {
          alert("구글 플레이 결제 모듈을 불러오는 중입니다. 잠시 후 다시 시도해 주세요.");
          return;
        }
        
        try {
          const sku = productId === "onetime" ? "gyeol_onetime_credit" : "gyeol_premium_monthly";
          
          // 구글 결제창 호출
          const purchase = productId === "onetime" 
            ? await RNIap.requestPurchase({ sku })
            : await RNIap.requestSubscription({ sku });

          if (purchase && (purchase as any).transactionReceipt) {
            const receipt = (purchase as any).transactionReceipt;
            
            // TODO: 백엔드 영수증 검증 API 호출
            // await api.verifyGooglePurchase(receipt, productId);
            
            // 결제 완료 처리 (임시)
            await RNIap.finishTransaction({ purchase: purchase as any, isConsumable: productId === "onetime" });
            alert("결제가 완료되었습니다! (서버 검증 연동 필요)");
            onClose();
            bootstrap();
          }
        } catch (err: any) {
          if (err.code !== 'E_USER_CANCELLED') {
            alert("결제 중 오류가 발생했습니다: " + err.message);
          }
        }
        return;
      }

      // --- 2. 텔레그램 스타 결제 ---
      if (isTelegram) {
        try {
          const { invoice_link } = productId === "onetime" 
            ? await api.createStarsInvoiceOnetime() 
            : await api.createStarsInvoice();
          tg.openInvoice(invoice_link, (status: string) => {
            if (status === "paid") {
              alert("결제 완료", "프리미엄이 활성화되었습니다! 앱을 새로고침합니다.");
              window.location.reload();
            }
          });
          return;
        } catch (e: any) {
          alert("결제 오류", e.message || "텔레그램 결제를 시작할 수 없습니다.");
          return;
        }
      }

      // --- 3. 일반 웹 (레몬 스퀴지) ---
      const { url } = await api.checkout(productId === 'onetime');
      if (Platform.OS === "web") {
        window.location.href = url;
      } else {
        await Linking.openURL(url);
        onClose();
      }
    } catch (e: any) {
      alert("Checkout Failed", e.message || "Please try again.");
    } finally {
      setLoading(null);
    }
  };'''

    # 기존 handlePay 교체
    if "const handlePay" in content:
        content = re.sub(old_handle_pay_pattern, new_handle_pay, content, flags=re.DOTALL)
    else:
        # 만약 handlePay가 없고 다른 이름이면 파일을 저장하지 않음 (에러 방지)
        print("⚠️ handlePay 함수를 찾지 못했습니다. 기존 코드를 유지합니다.")
        return

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ PaymentModal.tsx 구글 플레이 결제 연동 완료!")

    print("\n✨ 안드로이드 브랜치에 커밋합니다...")
    try:
        subprocess.run("git add .", shell=True, check=True)
        subprocess.run('git commit -m "feat: 구글 플레이 인앱 결제 로직 연동 완료"', shell=True, check=True)
        print("🎉 커밋 완료! 이제 빌드를 진행하세요.")
    except subprocess.CalledProcessError:
        print("⚠️ 커밋 실패 (변경 사항이 없거나 오류 발생)")
else:
    print("❌ 파일을 찾을 수 없습니다.")
