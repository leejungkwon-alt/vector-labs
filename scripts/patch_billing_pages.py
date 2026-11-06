# scripts/patch_billing_pages.py
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
SUCCESS_PATH = Path("frontend/app/billing/success.tsx")
CANCEL_PATH = Path("frontend/app/billing/cancel.tsx")

# 1. success.tsx 다국어 패치
if SUCCESS_PATH.exists():
    txt = SUCCESS_PATH.read_text(encoding="utf-8")
    
    # useT import 추가
    if "useT" not in txt:
        txt = txt.replace('import { router } from "expo-router";', 'import { router } from "expo-router";\nimport { useT } from "@/i18n";')
    
    # 컴포넌트 내부 t 선언
    if "const t = useT();" not in txt:
        txt = txt.replace("export default function BillingSuccessScreen() {", "export default function BillingSuccessScreen() {\n  const t = useT();")
        
    # 하드코딩된 텍스트 교체
    txt = txt.replace('결제가 완료되었습니다!', '{t("billing.successTitle")}')
    txt = txt.replace('프리미엄 기능이 활성화되었습니다.', '{t("billing.successDesc1")}')
    txt = txt.replace('잠시 후 설정 화면에서 확인해 주세요.', '{t("billing.successDesc2")}')
    txt = txt.replace('설정으로 돌아가기', '{t("billing.backToSettings")}')
    
    if APPLY:
        SUCCESS_PATH.write_text(txt, encoding="utf-8")
        print("🎉 success.tsx 다국어 패치 완료")

# 2. cancel.tsx 생성
cancel_content = '''import { router } from "expo-router";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { colors, spacing, radius } from "@/theme";
import { useT } from "@/i18n";

export default function BillingCancelScreen() {
  const t = useT();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t("billing.cancelTitle")}</Text>
      <Text style={styles.desc}>{t("billing.cancelDesc")}</Text>
      <TouchableOpacity style={styles.btn} onPress={() => router.replace("/settings")}>
        <Text style={styles.btnText}>{t("billing.backToSettings")}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, justifyContent: "center", alignItems: "center", padding: spacing.lg },
  title: { fontSize: 24, fontWeight: "700", color: colors.text, marginBottom: spacing.md },
  desc: { fontSize: 16, color: colors.textMuted, textAlign: "center", marginBottom: spacing.xl },
  btn: { backgroundColor: colors.primary, paddingVertical: 14, paddingHorizontal: 24, borderRadius: radius.md },
  btnText: { color: colors.onPrimary, fontSize: 16, fontWeight: "600" },
});
'''
if APPLY:
    CANCEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    CANCEL_PATH.write_text(cancel_content, encoding="utf-8")
    print("🎉 cancel.tsx 신규 생성 완료")

# 3. JSON 번역 파일 업데이트
TRANSLATIONS = {
    "ko": {"successTitle": "결제가 완료되었습니다!", "successDesc1": "프리미엄 기능이 활성화되었습니다.", "successDesc2": "잠시 후 설정 화면에서 확인해 주세요.", "backToSettings": "설정으로 돌아가기", "cancelTitle": "결제가 취소되었습니다", "cancelDesc": "결제가 완료되지 않았습니다. 언제든지 다시 시도하실 수 있습니다."},
    "en": {"successTitle": "Payment Successful!", "successDesc1": "Premium features are now active.", "successDesc2": "Please check the settings screen shortly.", "backToSettings": "Back to Settings", "cancelTitle": "Payment Cancelled", "cancelDesc": "Your payment was not completed. You can try again anytime."},
    "ja": {"successTitle": "お支払いが完了しました！", "successDesc1": "プレミアム機能が有効になりました。", "successDesc2": "しばらくしてから設定画面でご確認ください。", "backToSettings": "設定に戻る", "cancelTitle": "お支払いがキャンセルされました", "cancelDesc": "お支払いは完了していません。いつでも再試行できます。"},
    "zh": {"successTitle": "支付成功！", "successDesc1": "高级功能已激活。", "successDesc2": "请稍后在设置页面查看。", "backToSettings": "返回设置", "cancelTitle": "支付已取消", "cancelDesc": "您的支付未完成。您可以随时重试。"},
    "es": {"successTitle": "¡Pago exitoso!", "successDesc1": "Las funciones premium están activas.", "successDesc2": "Verifique la pantalla de configuración en breve.", "backToSettings": "Volver a Configuración", "cancelTitle": "Pago cancelado", "cancelDesc": "Su pago no se completó. Puede intentarlo de nuevo en cualquier momento."}
}

def get_lang_key(filename):
    stem = filename.stem.lower()
    if stem.startswith("zh"): return "zh"
    if stem.startswith("ja"): return "ja"
    if stem.startswith("es"): return "es"
    if stem.startswith("ko"): return "ko"
    if stem.startswith("en"): return "en"
    return None

json_files = [p for p in Path("frontend").rglob("*.json") if "node_modules" not in str(p) and get_lang_key(p)]

if APPLY:
    for f in json_files:
        lang = get_lang_key(f)
        if lang not in TRANSLATIONS: continue
        try:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception:
            continue
        if not isinstance(data, dict): continue

        if "billing" not in data:
            data["billing"] = {}
        
        changed = False
        for key, value in TRANSLATIONS[lang].items():
            if key not in data["billing"]:
                data["billing"][key] = value
                changed = True

        if changed:
            with open(f, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            print(f"🎉 JSON 패치 완료: {f}")

if not APPLY:
    print("🧪 미리보기 모드입니다. 실제로 적용하려면 --apply 플래그를 추가하세요.")
else:
    print("\n✅ 결제 완료/취소 페이지 패치가 완료되었습니다.")