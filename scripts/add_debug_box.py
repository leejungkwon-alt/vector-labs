# scripts/add_debug_box.py
from pathlib import Path
import sys
import re

PATH = Path("frontend/app/(tabs)/settings.tsx")
if not PATH.exists():
    print("❌ 파일 없음"); sys.exit(1)

src = PATH.read_text(encoding="utf-8")

# 1. 상태(state) 추가
if "const [dbg, setDbg]" not in src:
    anchor_state = "const t = useT();"
    if anchor_state in src:
        src = src.replace(anchor_state, 'const [dbg, setDbg] = useState("로딩 중");\n  ' + anchor_state, 1)
    else:
        src = src.replace("const [isTgEnv", 'const [dbg, setDbg] = useState("로딩 중");\n  const [isTgEnv', 1)

# 2. useEffect 추가 (SSR 에러 방지 가드 포함)
if "setDbg(" not in src:
    effect = '''
  useEffect(() => {
    if (typeof window === "undefined") return;
    const w = window as any;
    setDbg(
      `BUILD 1110-D | Telegram: ${!!w.Telegram} | WebApp: ${!!w.Telegram?.WebApp} | initData: ${w.Telegram?.WebApp?.initData?.length ?? 0} | hash: ${window.location.hash.slice(0, 10)}`
    );
  }, []);
'''
    src = src.replace("return (", effect + "\n  return (", 1)

# 3. 화면 최상단(return 바로 다음)에 노란색 박스 삽입
if "DEBUG BOX" not in src:
    match = re.search(r'return\s*\(\s*(<[a-zA-Z]+[^>]*>)', src)
    if match:
        open_tag = match.group(1)
        debug_jsx = open_tag + '''
        {/* DEBUG BOX */}
        <View style={{ backgroundColor: "yellow", padding: 12, zIndex: 9999 }}>
          <Text style={{ fontSize: 12, color: "black", fontWeight: "bold" }}>{dbg}</Text>
        </View>
'''
        src = src.replace(open_tag, debug_jsx, 1)
        print("✅ 화면 최상단에 노란색 디버그 박스를 추가했습니다.")
    else:
        print("⚠️ return ( 구문을 찾지 못했습니다.")

PATH.write_text(src, encoding="utf-8")
print("✅ 패치 완료")