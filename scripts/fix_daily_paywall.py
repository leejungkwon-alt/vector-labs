import shutil
from pathlib import Path
from datetime import datetime

FILE = Path("frontend/app/(tabs)/daily.tsx")

def main():
    if not FILE.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {FILE}")
        return

    src = FILE.read_text(encoding="utf-8")

    # 1. 에러 판별 로직 강화 (403 에러를 확실하게 잡아냄)
    src = src.replace(
        "const isForbidden = error instanceof ApiError && error.status === 403;",
        "const isForbidden = (error as any)?.status === 403;"
    )

    # 2. 로그인 필요 방어 코드 제거 (유저님 지적 반영)
    login_check_code = """  if (!user) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>로그인이 필요합니다.</Text>
        <Text style={styles.errorDetail}>네트워크 상태를 확인하거나 앱을 재시작해 주세요.</Text>
      </View>
    );
  }

"""
    if login_check_code in src:
        src = src.replace(login_check_code, "")

    # 3. 데이터가 없을 때 빈 화면(null) 대신 결제 유도 화면 띄우기
    old_data_check = """  const dailyData = data?.daily as DailyResponse["daily"];
  if (!dailyData || !dailyData.items) return null;"""
    
    new_data_check = """  const dailyData = data?.daily as DailyResponse["daily"];
  if (!dailyData || !dailyData.items) {
    return (
      <View style={styles.center}>
        <View style={{ backgroundColor: colors.surface, padding: 24, borderRadius: radius.lg, alignItems: "center", borderWidth: 1, borderColor: colors.border }}>
          <Ionicons name="lock-closed" size={48} color={colors.primary} style={{ marginBottom: 16 }} />
          <Text style={{ fontSize: 20, fontWeight: "700", color: colors.text, marginBottom: 8 }}>구독자 전용 기능입니다</Text>
          <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", lineHeight: 22, marginBottom: 24 }}>
            매일 아침 당신의 기운을 읽어주는\\n데일리 에너지 서비스입니다.\\n프리미엄으로 업그레이드하고\\n7일치 흐름을 미리 확인하세요.
          </Text>
          <TouchableOpacity style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 14, borderRadius: radius.md, width: "100%", alignItems: "center" }} onPress={() => router.push("/(tabs)/settings")}>
            <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>프리미엄 업그레이드</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }"""
    src = src.replace(old_data_check, new_data_check)

    # 저장
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = FILE.with_suffix(f".tsx.bak.{ts}")
    shutil.copy2(FILE, bak)
    FILE.write_text(src, encoding="utf-8")
    print("✅ daily.tsx 결제 유도 패치 완료!")
    print("   - 로그인 에러 문구 제거")
    print("   - 데이터 없음(403) 상황 시 '구독자 전용 기능입니다' 카드 강제 표시")
    print(f"📦 백업 파일: {bak.name}")

if __name__ == "__main__":
    main()
