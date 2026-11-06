# scripts/remove_lucky_code_button.py
"""
LuckyCodeSection.tsx 의 빈 TouchableOpacity 블록 + 불필요한 import 제거.
"""
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
TSX = Path("frontend/src/components/sections/LuckyCodeSection.tsx")

if not TSX.exists():
    print(f"❌ {TSX} 없음")
    sys.exit(1)

txt = TSX.read_text(encoding="utf-8")
orig = txt

# (1) 빈 TouchableOpacity 블록 통째 제거
old_block = '''      <TouchableOpacity
        onPress={() => /* 시조 모아보기 제거됨 */}
        style={{ marginTop: 16, padding: 12, backgroundColor: colors.surface, borderRadius: 12, borderWidth: 1, borderColor: colors.primary, alignItems: "center" }}
      >
        {/* 시조 모아보기 버튼 제거됨 */}
      </TouchableOpacity>

'''
if old_block in txt:
    txt = txt.replace(old_block, '', 1)
    print("✅ 빈 TouchableOpacity 블록 제거")
else:
    print("⚠️ 예상한 블록 못 찾음 — 유사 패턴 시도")
    # 패턴 fallback
    import re
    pattern = re.compile(
        r'<TouchableOpacity\b[^>]*onPress\s*=\s*\{\(\)\s*=>\s*/\*[^*]*\*/\}[^>]*>.*?</TouchableOpacity>\s*\n',
        re.DOTALL,
    )
    txt, n = pattern.subn('', txt)
    if n == 0:
        print("❌ 제거 실패. 수동 확인 필요")
        sys.exit(1)
    print(f"✅ 패턴 fallback 제거: {n}건")

# (2) router import 제거 (더 이상 안 씀)
old_router = 'import { router } from "expo-router";\n'
if old_router in txt and 'router.' not in txt.replace(old_router, ''):
    txt = txt.replace(old_router, '', 1)
    print("✅ 'router' import 제거")

# (3) TouchableOpacity import 제거
old_import = 'import { TouchableOpacity } from "react-native";\n'
if old_import in txt and '<TouchableOpacity' not in txt:
    txt = txt.replace(old_import, '', 1)
    print("✅ 'TouchableOpacity' import 제거")

# (4) react-native import에서 TouchableOpacity 통합된 경우
old_rn = 'import { View, Text, TouchableOpacity } from "react-native";'
new_rn = 'import { View, Text } from "react-native";'
if old_rn in txt:
    txt = txt.replace(old_rn, new_rn, 1)
    print("✅ react-native import 정리")

# 결과
if txt == orig:
    print("\nℹ️ 변경 사항 없음")
    sys.exit(0)

print("\n🩺 [변경 후 파일 앞부분]")
for line in txt.splitlines()[:15]:
    print("   " + line)

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/remove_lucky_code_button.py --apply")
    sys.exit(0)

TSX.write_text(txt, encoding="utf-8")
print("\n🎉 저장 완료. 다음:")
print("   git add frontend/src/components/sections/LuckyCodeSection.tsx")
print('   git commit -m "remove: empty collection button wrapper"')
print("   git push origin main")