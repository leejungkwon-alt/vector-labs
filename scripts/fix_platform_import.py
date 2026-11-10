# scripts/fix_platform_import.py
from pathlib import Path
import sys

PATH = Path("frontend/app/_layout.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 이미 Platform이 import 되어 있는지 확인
if "import { Platform" in src or ", Platform" in src or "Platform," in src:
    print("⚠️ Platform이 이미 import 되어 있습니다.")
else:
    # react-native에서 import 하는 구문 찾기
    import re
    match = re.search(r'import\s+\{([^}]+)\}\s+from\s+["\']react-native["\'];', src)
    if match:
        # 기존 import 목록에 Platform 추가
        imports = match.group(1)
        new_imports = imports + ", Platform"
        src = src.replace(match.group(0), f'import {{{new_imports}}} from "react-native";', 1)
        print("✅ 기존 react-native import에 Platform 추가 완료")
    else:
        # react-native import 문이 아예 없다면 새로 추가
        src = 'import { Platform } from "react-native";\n' + src
        print("✅ react-native Platform import 새로 추가 완료")

PATH.write_text(src, encoding="utf-8")
print("🎉 수정 완료")