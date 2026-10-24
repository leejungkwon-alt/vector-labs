import shutil
from pathlib import Path
from datetime import datetime

FILE = Path("frontend/app/(tabs)/settings.tsx")

def main():
    if not FILE.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {FILE}")
        return

    src = FILE.read_text(encoding="utf-8")

    # 1. formatBirthInfo 헬퍼 함수 추가 (컴포넌트 내부에 삽입)
    helper_code = """
  const formatBirthInfo = () => {
    if (!profile?.birth_date) return "미등록 (입력 필요)";
    let info = profile.birth_date;
    
    if (profile.birth_time_mode === "exact" && profile.birth_time) {
      // HH:MM:SS 중 앞의 5자리(HH:MM)만 표시
      info += ` ${profile.birth_time.substring(0, 5)}`;
    } else if (profile.birth_time_mode === "noon") {
      info += " (시간 모름 - 정오 기준)";
    } else if (profile.birth_time_mode === "day_only") {
      info += " (시간 모름 - 일주만)";
    }
    
    if (profile.birth_location) {
      // 도시 키값(seoul, new_york)을 보기 좋게 표시
      info += ` · ${profile.birth_location}`;
    }
    return info;
  };

  const getLoginProvider = () => {"""
    
    # getLoginProvider 함수 바로 위에 헬퍼 함수 삽입
    if "const formatBirthInfo = () =>" not in src:
        src = src.replace("  const getLoginProvider = () => {", helper_code)

    # 2. 기존 생년월일 표시 부분을 formatBirthInfo() 호출로 교체
    old_birth_row = """        <View style={styles.row}>
          <Text style={styles.label}>등록된 생년월일</Text>
          <Text style={styles.value}>
            {profile?.birth_date ? profile.birth_date : "미등록 (입력 필요)"}
          </Text>
        </View>"""
        
    new_birth_row = """        <View style={styles.row}>
          <Text style={styles.label}>출생 정보 (생년월일시)</Text>
          <Text style={[styles.value, { flexShrink: 1, textAlign: "right" }]}>
            {formatBirthInfo()}
          </Text>
        </View>"""

    if old_birth_row in src:
        src = src.replace(old_birth_row, new_birth_row)

    # 백업 생성 및 저장
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = FILE.with_suffix(f".tsx.bak.{ts}")
    shutil.copy2(FILE, bak)
    
    FILE.write_text(src, encoding="utf-8")
    print(f"✅ 출생 정보(생년월일시 + 출생지) 표시 완료!")
    print(f"📦 백업: {bak.name}")

if __name__ == "__main__":
    main()
