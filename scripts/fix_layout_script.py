# scripts/fix_layout_script.py
from pathlib import Path
import sys

PATH = Path("frontend/app/_layout.tsx")
if not PATH.exists():
    print("❌ _layout.tsx 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 기존에 혹시 모를 텔레그램 스크립트 로드 코드 제거 (중복 방지)
import re
src = re.sub(r'// \[TMA\] 텔레그램 SDK 로드.*?document\.head\.appendChild\(script\);\s*\}', '', src, flags=re.DOTALL)

# 2. 최상단 import 바로 아래에 스크립트 로드 코드 삽입
injection = '''
// [TMA] 텔레그램 SDK 로드 (앱 실행 최우선)
if (typeof window !== "undefined") {
  const script = document.createElement("script");
  script.src = "https://telegram.org/js/telegram-web-app.js";
  script.async = false; // 동기적으로 로드하여 해시 파싱 보장
  document.head.appendChild(script);
}
'''

# 파일의 첫 번째 import 문 뒤에 삽입
if "[TMA] 텔레그램 SDK 로드" not in src:
    match = re.search(r'(import.*?;\n)', src)
    if match:
        src = src[:match.end()] + injection + src[match.end():]
        PATH.write_text(src, encoding="utf-8")
        print("✅ _layout.tsx에 텔레그램 SDK 로드 코드 삽입 완료")
    else:
        print("⚠️ import 문을 찾지 못했습니다.")
else:
    print("⚠️ 이미 코드가 존재합니다.")