# scripts/fix_pc_touch_modal.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/src/components/BirthDateWheelPicker.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 이미 패치가 적용되었는지 확인
if "position: 'fixed'" in src:
    print("⚠️ 이미 웹 오버레이 패치가 적용되어 있습니다.")
    sys.exit(0)

# 2. <Modal> 내부의 내용물 추출 (정규식 활용)
pattern = r'<Modal[^>]*>\s*<View style=\{styles\.overlay\}>(.*?)</View>\s*</Modal>'
match = re.search(pattern, src, flags=re.DOTALL)

if not match:
    print("❌ Modal 패턴을 찾지 못했습니다. 수동 확인 필요.")
    sys.exit(1)

inner_content = match.group(1)

# 3. 웹이면 View 오버레이, 네이티브면 기존 Modal을 쓰도록 코드 교체
new_render = f'''{{Platform.OS === 'web' ? (
      <View style={{{{ position: 'fixed' as any, top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999, touchAction: 'manipulation' }}}}> 
        <View style={{styles.overlay}}>
          {inner_content}
        </View>
      </View>
    ) : (
      <Modal visible={{visible}} transparent animationType="slide">
        <View style={{styles.overlay}}>
          {inner_content}
        </View>
      </Modal>
    )}}'''

# 4. 기존 Modal 렌더링 부분을 new_render로 교체
src = src.replace(match.group(0), new_render, 1)

# 5. visible이 false일 때 렌더링되지 않도록 early return 추가
if "if (!visible) return null;" not in src:
    # useEffect 바로 위에 추가
    src = src.replace("  return (", "  if (!visible) return null;\n\n  return (", 1)

# 6. 웹에서 오버레이 배경색이 투명해지지 않도록 배경색 강제 지정 (필요시)
if "backgroundColor: 'rgba(0,0,0,0.5)'" in src and "position: 'fixed'" not in src:
    pass # 이미 스타일이 있을 것이므로 생략

PATH.write_text(src, encoding="utf-8")
print("✅ BirthDateWheelPicker.tsx PC 터치 씹힘 수정 완료 (Modal -> View 오버레이)")