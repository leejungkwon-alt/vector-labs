# scripts/patch_settings_telegram.py
from pathlib import Path
import sys

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

if "handleTelegramRegister" in src:
    print("⚠️ 이미 패치되어 있습니다."); sys.exit(0)

# 1. 핸들러 함수 추가 (handleLinkAccount 근처에 삽입)
old_handler = "const handleLinkAccount = () => {"
new_handler = '''const handleTelegramRegister = async () => {
    try {
      const tg = (window as any).Telegram?.WebApp;
      if (!tg || !tg.initData) {
        alert("텔레그램 앱에서만 이용할 수 있습니다.");
        return;
      }
      const res = await fetch("https://saju-backend-787049663118.asia-northeast3.run.app/api/v1/telegram/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${(useAuthStore.getState() as any).token || ""}`,
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
  };

  const handleLinkAccount = () => {'''

if old_handler in src and new_handler not in src:
    src = src.replace(old_handler, new_handler, 1)
else:
    print("❌ handleLinkAccount 위치를 찾을 수 없습니다. 수동 확인 필요."); sys.exit(1)


# 2. UI 삽입 (익명 로그인 박스 바로 위)
old_ui = '''      {/* ⭐️ 추가된 부분: 익명 로그인 상태일 때 계정 연결 유도 */}'''
new_ui = '''      {/* 텔레그램 데일리 푸시 (TMA 환경일 때만 노출) */}
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
      )}

      {/* ⭐️ 추가된 부분: 익명 로그인 상태일 때 계정 연결 유도 */}'''

if old_ui in src:
    src = src.replace(old_ui, new_ui, 1)
else:
    print("❌ UI 삽입 위치를 찾을 수 없습니다. 수동 확인 필요."); sys.exit(1)

PATH.write_text(src, encoding="utf-8")
print("✅ settings.tsx 패치 완료")