import shutil
from pathlib import Path
from datetime import datetime

FILE = Path("frontend/app/(tabs)/compatibility.tsx")

def main():
    if not FILE.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {FILE}")
        return

    src = FILE.read_text(encoding="utf-8")
    
    # 1. router import 추가 (기존 코드에 없다면 추가)
    if 'import { router } from "expo-router";' not in src:
        src = src.replace(
            'import { useSafeAreaInsets } from "react-native-safe-area-context";',
            'import { useSafeAreaInsets } from "react-native-safe-area-context";\nimport { router } from "expo-router";'
        )

    # 2. 기존 에러 렌더링 블록을 예쁜 유료화 안내 카드로 교체
    old_error_block = """    if (error) {
      const msg = error instanceof ApiError ? error.detail : (error as Error).message;
      return <Text style={{ color: colors.danger, marginTop: 20, textAlign: "center" }}>{msg}</Text>;
    }"""
    
    new_error_block = """    if (error) {
      const msg = error instanceof ApiError ? error.detail : (error as Error).message;
      
      // 👇 403 에러(궁합 결제 필요)일 때 예쁜 결제 유도 화면 노출
      if (error instanceof ApiError && error.status === 403) {
        return (
          <View style={{ marginTop: 30, padding: 24, backgroundColor: colors.primary + "10", borderRadius: radius.lg, alignItems: "center", borderWidth: 1, borderColor: colors.primary + "30" }}>
            <Text style={{ fontSize: 40, marginBottom: 12 }}>💎</Text>
            <Text style={{ fontSize: 20, fontWeight: "800", color: colors.text, marginBottom: 8 }}>궁합 분석은 유료 기능입니다</Text>
            <Text style={{ fontSize: 15, color: colors.textMuted, textAlign: "center", marginBottom: 24, lineHeight: 22 }}>
              상대방과의 4가지 케미(오행, 일간, 가치관, 신살)를 확인하려면{"\\n"}
              궁합 애드온을 구매하거나 프리미엄으로 업그레이드하세요.
            </Text>
            <TouchableOpacity 
              style={{ backgroundColor: colors.primary, paddingHorizontal: 24, paddingVertical: 16, borderRadius: radius.md, width: "100%", alignItems: "center" }} 
              onPress={() => router.push("/(tabs)/settings")}
            >
              <Text style={{ color: "#FFF", fontSize: 16, fontWeight: "700" }}>프리미엄 / 애드온 구매하러 가기</Text>
            </TouchableOpacity>
          </View>
        );
      }
      
      // 그 외 일반 에러
      return <Text style={{ color: colors.danger, marginTop: 20, textAlign: "center" }}>{msg}</Text>;
    }"""

    if old_error_block in src:
        src = src.replace(old_error_block, new_error_block)
        
        # 백업 생성 및 저장
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = FILE.with_suffix(f".tsx.bak.{ts}")
        shutil.copy2(FILE, bak)
        
        FILE.write_text(src, encoding="utf-8")
        print("✅ compatibility.tsx 패치 완료!")
        print("   - 궁합 탭에서 403 에러 발생 시 '유료 기능 안내 카드'가 예쁘게 표시됩니다.")
        print(f"📦 백업 파일: {bak.name}")
    else:
        print("⚠️ 교체할 에러 코드 패턴을 찾지 못했습니다. 파일을 직접 확인해주세요.")

if __name__ == "__main__":
    main()
