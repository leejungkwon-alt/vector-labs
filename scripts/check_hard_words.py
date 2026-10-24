import json
from pathlib import Path

DATA_DIR = Path("app/services/content/data/ko/core_pillars")
BAD_WORDS = ["편인", "정인", "식신", "상관", "편재", "정재", "비견", "겁재", "편관", "정관", "격국", "용신", "조후", "억부", "지장간", "천간", "지지"]

print("=== 어려운 사주 용어가 포함된 일주 파일 검사 ===")
count = 0
for path in DATA_DIR.glob("*.json"):
    if ".bak" in path.name: continue
    data = json.loads(path.read_text(encoding="utf-8"))
    text = json.dumps(data, ensure_ascii=False)
    
    found = [word for word in BAD_WORDS if word in text]
    if found:
        print(f"⚠️ {path.name}: {', '.join(found)}")
        count += 1

print(f"\n총 {count}개의 파일에 어려운 용어가 포함되어 있습니다.")
