import shutil
from pathlib import Path
from datetime import datetime

FILE = Path("frontend/app/(tabs)/daily.tsx")

def main():
    if not FILE.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {FILE}")
        return

    src = FILE.read_text(encoding="utf-8")
    orig_src = src

    # 1. 에러 판별 로직 강화 (instanceof 오류 방지)
    src = src.replace(
        "const isForbidden = error instanceof ApiError && error.status === 403;",
        "const isForbidden = (error as any)?.status === 403;"
    )

    # 2. 유저 정보가 없을 때 (로그인 실패) 방어 코드 추가
    if "로그인이 필요합니다" not in src:
        old_profile_check = """  if (!profile) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>사주 정보가 없습니다.</Text>
        <Text style={styles.errorDetail}>홈 탭에서 사주 정보를 먼저 입력해 주세요.</Text>
      </View>
    );
  }"""
        new_profile_check = """  if (!user) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>로그인이 필요합니다.</Text>
        <Text style={styles.errorDetail}>네트워크 상태를 확인하거나 앱을 재시작해 주세요.</Text>
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>사주 정보가 없습니다.</Text>
        <Text style={styles.errorDetail}>홈 탭에서 사주 정보를 먼저 입력해 주세요.</Text>
      </View>
    );
  }"""
        src = src.replace(old_profile_check, new_profile_check)

    # 3. 데이터가 누락되었을 때 빈 화면(null) 대신 에러 안내창 띄우기
    old_data_check = """  const dailyData = data?.daily as DailyResponse["daily"];
  if (!dailyData || !dailyData.items) return null;"""
    
    new_data_check = """  const dailyData = data?.daily as DailyResponse["daily"];
  if (!dailyData || !dailyData.items) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>데이터를 불러오지 못했습니다.</Text>
        <Text style={styles.errorDetail}>잠시 후 다시 시도해 주세요.</Text>
      </View>
    );
  }"""
    src = src.replace(old_data_check, new_data_check)

    # 변경 사항이 있으면 저장
    if src != orig_src:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = FILE.with_suffix(f".tsx.bak.{ts}")
        shutil.copy2(FILE, bak)
        FILE.write_text(src, encoding="utf-8")
        print("✅ daily.tsx 방어 코드 패치 완료!")
        print("   - 유저 정보 없음, 데이터 없음 상황에서 빈 화면 대신 안내 문구 표시")
        print(f"📦 백업 파일: {bak.name}")
    else:
        print("⚠️ 이미 패치되었거나 코드를 찾지 못했습니다.")

if __name__ == "__main__":
    main()
