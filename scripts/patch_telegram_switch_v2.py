# scripts/patch_telegram_switch_v2.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. Switch import 확인 및 추가
if 'import { Switch }' not in src and 'Switch,' not in src and ', Switch' not in src:
    src = src.replace('from "react-native";', 'from "react-native";\nimport { Switch } from "react-native";', 1)

# 2. UI 카드 교체 (이전 스크립트와 동일한 로직)
old_card = '''      {/* 텔레그램 데일리 푸시 (TMA 환경일 때만 노출) */}
      {typeof window !== "undefined" && !!(window as any).Telegram?.WebApp?.initData && (
        <View style={[styles.profileBox, { backgroundColor: "#0088cc10", borderColor: "#0088cc" }]}>
          <Text style={[styles.sectionTitle, { color: "#0088cc" }]}>{t("settings.telegramPushTitle")}</Text>
          <Text style={{ fontSize: 14, color: colors.text, marginBottom: 12, lineHeight: 20 }}>
            {t("settings.telegramPushDesc")}
          </Text>
          <TouchableOpacity style={[styles.upgradeBtn, { backgroundColor: "#0088cc" }]} onPress={handleTelegramRegister}>
            <Text style={styles.upgradeBtnText}>{t("settings.telegramPushCta")}</Text>
          </TouchableOpacity>
        </View>
      )}'''

new_card = '''      {/* 텔레그램 알림 스위치 (TMA 환경일 때만 노출) */}
      {typeof window !== "undefined" && !!(window as any).Telegram?.WebApp?.initData && (
        <View style={styles.profileBox}>
          <View style={[styles.row, { borderBottomWidth: 0 }]}>
            <View style={{ flex: 1 }}>
              <Text style={styles.label}>{t("settings.telegramPushTitle")}</Text>
              <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4, lineHeight: 18 }}>
                {t("settings.telegramPushDesc")}
              </Text>
            </View>
            <Switch 
              value={isTgSubscribed} 
              onValueChange={handleTelegramToggle} 
              disabled={isTgLoading} 
            />
          </View>
        </View>
      )}'''

if old_card in src:
    src = src.replace(old_card, new_card, 1)
    print("✅ UI 카드를 스위치로 교체 완료")
elif new_card not in src:
    print("⚠️ UI 카드 교체 실패 (이미 교체되었거나 형식이 다름)")

# 3. 핸들러 함수 정규식으로 교체 (내부 코드가 달라도 통째로 교체)
# handleTelegramRegister 함수의 시작부터 끝(닫는 괄호)까지 찾는 정규식
pattern = r'(const handleTelegramRegister = async \(\) => \{.*?\n  \};)'
replacement = '''const [isTgSubscribed, setIsTgSubscribed] = useState(false);
  const [isTgLoading, setIsTgLoading] = useState(false);

  const handleTelegramToggle = async () => {
    const tg = (window as any).Telegram?.WebApp;
    if (!tg || !tg.initData) return;
    setIsTgLoading(true);
    try {
      const { storage } = await import("@/store/secureStore");
      const token = await storage.getItem("saju.access_token");
      const endpoint = isTgSubscribed ? "unregister" : "register";
      const res = await fetch(`https://saju-backend-787049663118.asia-northeast3.run.app/api/v1/telegram/${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token || ""}`,
        },
        body: JSON.stringify({ init_data: tg.initData, lang }),
      });
      if (!res.ok) {
        if (res.status === 409) throw new Error(t("settings.telegramPushNoProfile"));
        if (res.status === 403) throw new Error(t("settings.telegramPushAgeLimit"));
        throw new Error(t("settings.telegramPushError"));
      }
      setIsTgSubscribed(!isTgSubscribed);
    } catch (e: any) {
      alert(e.message);
    } finally {
      setIsTgLoading(false);
    }
  };'''

if re.search(pattern, src, flags=re.DOTALL):
    src = re.sub(pattern, replacement, src, count=1, flags=re.DOTALL)
    print("✅ 핸들러 함수를 스위치 토글로 교체 완료")
else:
    print("❌ 핸들러 함수를 찾지 못했습니다.")

PATH.write_text(src, encoding="utf-8")
print("🎉 settings.tsx 최종 패치 완료")