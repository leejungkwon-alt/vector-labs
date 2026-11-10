# scripts/cleanup_telegram_ui.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 디버그 상태 및 useEffect 제거
src = re.sub(r'const \[dbg, setDbg\] = useState\(.*?\);\n', '', src)
src = re.sub(r'useEffect\(\(\) => \{\s*const w = window as any;.*?setDbg\(.*?\}, \[\]\);', '', src, flags=re.DOTALL)

# 2. 노란색 디버그 박스 제거
src = re.sub(r'\{/\* 디버그 박스.*?<Text style=\{\{ fontSize: 12, color: "black" \}\}>\{dbg\}</Text>\s*</View>\s*\}', '', src, flags=re.DOTALL)

# 3. 파란색 박스 내부의 BUILD 1110-C 텍스트 제거
src = src.replace('<Text style={{ fontSize: 10, color: "#aaa", marginBottom: 4 }}>BUILD 1110-C</Text>\n', '')

# 4. 중복된 예전 스위치(텔레그램 데일리 운세) 제거
# 예전 UI 패턴을 정규식으로 찾아서 삭제 (텔레그램 데일리 운세 카드)
old_duplicate = r'\{/\* 텔레그램 데일리 푸시.*?\}\)\}'
src = re.sub(old_duplicate, '', src, flags=re.DOTALL)
# 만약 위 정규식이 안 먹혔다면, 텔레그램 데일리 운세 텍스트가 있는 View 덩어리를 찾아서 삭제
old_duplicate_2 = r'<View[^>]*>\s*<Text[^>]*>\{t\("settings\.telegramPushTitle"\)\}</Text>.*?</View>'
# 조심스럽게 접근: 텍스트가 "텔레그램 데일리 운세"로 하드코딩되어 있을 수도 있음
src = re.sub(r'<View[^>]*>\s*<Text[^>]*>텔레그램 데일리 운세</Text>.*?</View>', '', src, flags=re.DOTALL)

PATH.write_text(src, encoding="utf-8")
print("✅ UI 찌꺼기 청소 완료")