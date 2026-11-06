# scripts/find_datepicker.py
from pathlib import Path

print("🔎 DatePicker 관련 파일 및 하드코딩된 한국어 문자열을 찾습니다...\n")

hits = []
for p in Path("frontend").rglob("*.tsx"):
    if any(x in str(p) for x in ["node_modules", "dist", ".expo", "_expo"]):
        continue
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        continue

    # DatePicker 또는 한국어 문자열 포함 여부 확인
    has_dp = any(k in txt for k in ["DatePicker", "WheelPicker", "ScrollPicker", "Picker"])
    has_kr = any(k in txt for k in ["생년월일", "년", "월", "일", "취소", "확인"])
    
    if has_dp or (has_kr and ("picker" in p.name.lower() or "date" in p.name.lower())):
        hits.append((p, txt))

if not hits:
    print("❌ DatePicker 관련 .tsx 파일을 찾지 못했습니다.")
    print("   더 넓은 검색이 필요합니다.")
else:
    for p, txt in hits:
        print(f"📂 {p}")
        for i, line in enumerate(txt.splitlines(), 1):
            stripped = line.strip()
            if any(k in line for k in ["생년월일", "년\"", "년'", "월\"", "일\"", "취소", "확인", "setYear", "Pickers"]):
                print(f"  L{i}: {stripped[:130]}")
        print()

# package.json에서 picker 라이브러리 확인
pkg = Path("frontend/package.json")
if pkg.exists():
    print("\n📦 [관련 패키지]")
    for line in pkg.read_text(encoding="utf-8").splitlines():
        if any(k in line.lower() for k in ["picker", "wheel", "scroll"]):
            print(f"  {line.strip()}")