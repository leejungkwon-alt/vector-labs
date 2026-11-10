# scripts/fix_telegram_clean_final.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 디버그 상태(dbg) 및 useEffect 제거
src = src.replace('  const [dbg, setDbg] = useState("로딩 중");\n', '')
debug_effect = '''  useEffect(() => {
    if (typeof window === "undefined") return;
    const w = window as any;
    setDbg(
      `BUILD 1110-D | Telegram: ${!!w.Telegram} | WebApp: ${!!w.Telegram?.WebApp} | initData: ${w.Telegram?.WebApp?.initData?.length ?? 0} | hash: ${window.location.hash.slice(0, 10)}`
    );
  }, []);\n\n'''
src = src.replace(debug_effect, '')

# 2. 노란색 디버그 박스 제거
debug_box = '''        {/* DEBUG BOX */}
        <View style={{ backgroundColor: "yellow", padding: 12, zIndex: 9999 }}>
          <Text style={{ fontSize: 12, color: "black", fontWeight: "bold" }}>{dbg}</Text>
        </View>\n\n'''
src = src.replace(debug_box, '')

# 3. 위쪽에 있는 중복 텔레그램 스위치 블록 제거
upper_switch = '''      {/* 텔레그램 알림 스위치 (TMA 환경일 때만 노출) */}
      {isTgEnv && (
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
      )}\n\n'''
src = src.replace(upper_switch, '')

# 4. 아래쪽 스위치 블록에서 'BUILD 1110-C' 텍스트 제거 및 다국어 적용
lower_switch_old = '''            {/* 텔레그램 알림 스위치 */}
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
      )}'''

lower_switch_new = '''      {/* 텔레그램 알림 스위치 */}
      {isTgEnv && (
        <View style={{ marginTop: 24, padding: 16, borderRadius: 12, borderWidth: 1, borderColor: "#0088cc", backgroundColor: "#f0f8ff" }}>
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
            <View style={{ flex: 1, marginRight: 10 }}>
              <Text style={{ fontSize: 16, fontWeight: "600", color: "#0088cc" }}>{t("settings.telegramPushTitle") || "텔레그램 알림 받기"}</Text>
              <Text style={{ fontSize: 12, color: colors.textMuted, marginTop: 4, lineHeight: 18 }}>
                {t("settings.telegramPushDesc") || "매일 아침 텔레그램으로 오늘의 운세를 보내드립니다."}
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

if lower_switch_old in src:
    src = src.replace(lower_switch_old, lower_switch_new)
    print("✅ 아래쪽 중복 스위치 정리 및 다국어 적용 완료")
else:
    print("⚠️ 아래쪽 스위치 패턴을 찾지 못했습니다. 수동 확인 필요.")

PATH.write_text(src, encoding="utf-8")
print("🎉 settings.tsx 청소 완료")