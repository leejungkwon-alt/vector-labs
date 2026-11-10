# scripts/patch_telegram_switch.py
from pathlib import Path
import sys

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

if "handleTelegramToggle" in src:
    print("⚠️ 이미 스위치로 패치되어 있습니다."); sys.exit(0)

# 1) Switch import 추가
old_import = 'from "react-native";'
new_import = 'from "react-native";\nimport { Switch } from "react-native";'
# 중복 import 방지: 이미 Switch가 있는지 확인
if "Switch" not in src.split("from \"react-native\"")[0][-100:]:
    if old_import in src:
        src = src.replace(old_import, new_import, 1)

# 2) 기존 카드형 UI 블록을 스위치 UI로 교체
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

if old_card not in src:
    print("❌ 기존 텔레그램 카드 UI를 찾을 수 없습니다. 수동 확인 필요."); sys.exit(1)
src = src.replace(old_card, new_card, 1)

# 3) 기존 handleTelegramRegister 함수를 스위치 상태 + 핸들러로 교체
old_handler = '''const handleTelegramRegister = async () => {
    try {
      const tg = (window as any).Telegram?.WebApp;
      if (!tg || !tg.initData) {
        alert("텔레그램 앱에서만 이용할 수 있습니다.");
        return;
      }
      const { storage } = await import("@/store/secureStore");
      const token = await storage.getItem("saju.access_token");
      
      const res = await fetch("https://saju-backend-787049663118.asia-northeast3.run.app/api/v1/telegram/register", {
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
      alert(t("settings.telegramPushSuccess"));
    } catch (e: any) {
      alert(e.message);
    }
  };'''

new_handler = '''const [isTgSubscribed, setIsTgSubscribed] = useState(false);
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

if old_handler not in src:
    print("❌ 기존 handleTelegramRegister 함수를 찾을 수 없습니다. 수동 확인 필요."); sys.exit(1)
src = src.replace(old_handler, new_handler, 1)

PATH.write_text(src, encoding="utf-8")
print("✅ settings.tsx 텔레그램 스위치 UI로 교체 완료")