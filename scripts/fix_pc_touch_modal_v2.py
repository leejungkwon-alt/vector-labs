# scripts/fix_pc_touch_modal_v2.py
from pathlib import Path
import sys

PATH = Path("frontend/src/components/BirthDateWheelPicker.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 이미 패치가 적용되었는지 확인
if "position: 'fixed'" in src:
    print("⚠️ 이미 패치되어 있습니다."); sys.exit(0)

# ─────────────────────────────────────────────
# 1. 렌더링 시작 부분 찾기 (return 바로 뒤)
# ─────────────────────────────────────────────
old_start = "  return (\n    <Modal visible={visible} transparent animationType=\"slide\">"

new_start = """  if (!visible) return null;

  // 웹(텔레그램 데스크톱 포함)에서는 Modal의 포커스 트랩 때문에 첫 터치가 씹힘 → View 오버레이 사용
  const isWeb = Platform.OS === 'web';
  const Container: any = isWeb ? View : Modal;
  const containerProps = isWeb
    ? { style: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999, touchAction: 'manipulation' } }
    : { visible, transparent: true, animationType: 'slide' };

  return (
    <Container {...containerProps}>"""

if old_start not in src:
    print("❌ 기존 Modal 시작 패턴을 찾지 못했습니다. 파일을 직접 확인해주세요.")
    sys.exit(1)

src = src.replace(old_start, new_start, 1)

# ─────────────────────────────────────────────
# 2. 렌더링 닫는 부분 찾기 (</Modal>)
# ─────────────────────────────────────────────
src = src.replace("    </Modal>\n  );\n}", "    </Container>\n  );\n}", 1)

# ─────────────────────────────────────────────
# 3. Platform import 확인 (이미 있음)
# ─────────────────────────────────────────────
if "Platform" not in src.split("\n")[0:5][0] and "Platform," not in src:
    # 첫 번째 import 문에 Platform 추가
    import re
    m = re.search(r"import \{[^}]*\} from 'react-native'", src)
    if m:
        old_import = m.group(0)
        new_import = old_import.replace("}", ", Platform }")
        src = src.replace(old_import, new_import, 1)

PATH.write_text(src, encoding="utf-8")
print("✅ BirthDateWheelPicker.tsx 안전하게 패치 완료 (Modal/View 동적 전환)")