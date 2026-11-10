# scripts/fix_daily_free_paywall.py
from pathlib import Path
import sys

PATH = Path("frontend/app/(tabs)/daily.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

if "Daily Paywall" in src:
    print("⚠️ 이미 프리미엄 안내 화면이 적용되어 있습니다.")
    sys.exit(0)

# 1. 무료 회원 구분 로직 삽입 (기존 렌더링 return 문 앞)
# (user가 free이면, 데이터를 기다리지 않고 즉시 업그레이드 화면을 렌더링하도록 함)
anchor = "  if (!profileReady || !ready) {"
paywall_logic = '''
  // Daily Paywall: 무료 회원은 API 호출을 막았으므로, 예쁜 업그레이드 유도 화면을 보여줌
  if (user?.tier === "free") {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24, backgroundColor: colors.bg }}>
        <Text style={{ fontSize: 48, marginBottom: 16 }}>🔒</Text>
        <Text style={{ fontSize: 22, fontWeight: "700", color: colors.text, marginBottom: 12, textAlign: "center" }}>
          프리미엄 전용 메뉴입니다
        </Text>
        <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", marginBottom: 32, lineHeight: 22 }}>
          매일 아침, 당신만을 위한 깊이 있는 데일리 운세를 확인하려면 프리미엄으로 업그레이드하세요.
        </Text>
        <TouchableOpacity 
          style={{ backgroundColor: colors.primary, paddingHorizontal: 32, paddingVertical: 16, borderRadius: 12, width: "100%", alignItems: "center" }}
          onPress={() => router.push("/settings")}
        >
          <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>
            프리미엄 구독하러 가기
          </Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (!profileReady || !ready) {'''

if anchor in src:
    src = src.replace(anchor, paywall_logic, 1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ daily.tsx에 무료 회원용 프리미엄 안내 화면 추가 완료")
else:
    print("❌ 대상 위치를 찾지 못했습니다. 수동 확인 필요.")