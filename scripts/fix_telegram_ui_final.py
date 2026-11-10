# scripts/fix_telegram_ui_final.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 남아있는 찌꺼기(BUILD 1110-B 등) 모두 청소
src = re.sub(r'\{/\* 텔레그램 알림 스위치 \*/\}.*?\{isTgEnv && \(.*?\}\)\}', '', src, flags=re.DOTALL)
src = re.sub(r'\{/\* 디버그용 빌드 마커.*?\}\)\}', '', src, flags=re.DOTALL)
src = re.sub(r'<Text style=\{\{ fontSize: 10, color: "#aaa", marginBottom: 4 \}\}>BUILD 1110-B.*?</Text>', '', src, flags=re.DOTALL)

# 2. 핸들러 및 상태(isTgEnv)가 없으면 안전하게 추가
if 'handleTelegramToggle' not in src:
    old_handler = 'const handleLinkAccount = () => {'
    new_handler = '''const [isTgSubscribed, setIsTgSubscribed] = useState(false);
  const [isTgLoading, setIsTgLoading] = useState(false);
  const [isTgEnv, setIsTgEnv] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if ((window as any).Telegram?.WebApp?.initData) {
      setIsTgEnv(true);
      return;
    }
    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-web-app.js";
    script.async = true;
    script.onload = () => {
      if ((window as any).Telegram?.WebApp?.initData) {
        setIsTgEnv(true);
      }
    };
    document.head.appendChild(script);
  }, []);

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
  };

  const handleLinkAccount = () => {'''
    if old_handler in src:
        src = src.replace(old_handler, new_handler, 1)

# 3. UI 삽입: '{/* 5. 언어 설정 */}' 바로 위
anchor = '{/* 5. 언어 설정 */}'
telegram_ui = '''      {/* 텔레그램 알림 스위치 */}
      {isTgEnv && (
        <View style={{ marginTop: 24, padding: 16, borderRadius: 12, borderWidth: 1, borderColor: "#0088cc", backgroundColor: "#f0f8ff" }}>
          <Text style={{ fontSize: 10, color: "#aaa", marginBottom: 4 }}>BUILD 1110-C</Text>
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
            <View style={{ flex: 1, marginRight: 10 }}>
              <Text style={{ fontSize: 16, fontWeight: "600", color: "#0088cc" }}>텔레그램 알림 받기</Text>
              <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4, lineHeight: 18 }}>
                매일 아침 텔레그램으로 오늘의 운세를 보내드립니다.
              </Text>
            </View>
            <Switch 
              value={isTgSubscribed} 
              onValueChange={handleTelegramToggle} 
              disabled={isTgLoading} 
            />
          </View>
        </View>
      )}

'''

if anchor in src:
    src = src.replace(anchor, telegram_ui + anchor, 1)
    print("✅ 텔레그램 스위치 UI를 언어 설정 위에 삽입했습니다.")
else:
    print("❌ '{/* 5. 언어 설정 */}' 위치를 찾지 못했습니다.")

PATH.write_text(src, encoding="utf-8")
print("✅ 최종 패치 완료")