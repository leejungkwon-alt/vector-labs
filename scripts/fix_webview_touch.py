# scripts/fix_webview_touch.py
from pathlib import Path
import sys

PATH = Path("frontend/src/components/DateTimeField.tsx")
if not PATH.exists():
    print("❌ DateTimeField.tsx 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

old_press = 'onPress={() => setShowWheel(true)}'

new_press = '''onPress={() => {
            if (Platform.OS === "web") {
              // 텔레그램 웹뷰 터치 씹힘 방지: 포커스 해제 후 약간의 지연
              if (typeof document !== "undefined" && document.activeElement instanceof HTMLElement) {
                document.activeElement.blur();
              }
              setTimeout(() => setShowWheel(true), 50);
            } else {
              setShowWheel(true);
            }
          }}'''

if new_press in src:
    print("⚠️ 이미 터치 씹힘 방지 코드가 적용되어 있습니다.")
    sys.exit(0)

if old_press in src:
    src = src.replace(old_press, new_press, 1)
    PATH.write_text(src, encoding="utf-8")
    print("✅ DateTimeField.tsx 터치 씹힘 방지 패치 완료")
else:
    print("❌ 기존 onPress 코드를 찾지 못했습니다. 수동 확인 필요.")