import json, re
from pathlib import Path

DATA_DIR = Path("app/services/content/data/ko/core_pillars")
# 60갑자 패턴 (천간 + 지지)
HANJA_PATTERN = re.compile(r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]')

def clean_text(text):
    if not isinstance(text, str):
        return text
    # 1. 특수 패턴 처리: "성숙한 丙寅은" -> "성숙한 당신은"
    text = re.sub(r'성숙한\s*[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥](은|는)', '성숙한 당신은', text)
    
    # 2. 나머지 한자 기둥명을 '당신'으로 변경
    text = HANJA_PATTERN.sub('당신', text)
    
    # 3. 조사 교정 (당신는 -> 당신은, 당신가 -> 당신이 등)
    text = text.replace("당신는", "당신은")
    text = text.replace("당신가", "당신이")
    text = text.replace("당신를", "당신을")
    text = text.replace("당신와", "당신과")
    
    return text

print("=== JSON 본문 내 한자 기둥명 -> '당신'으로 평이화 교체 ===")
count = 0
for path in DATA_DIR.glob("*.json"):
    if ".bak" in path.name: continue
    data = json.loads(path.read_text(encoding="utf-8"))
    orig_data = json.dumps(data, ensure_ascii=False)
    
    # 문자열 변환 처리
    for key in ["hero", "narrative", "shadows", "advice", "keywords"]:
        if key in data:
            if isinstance(data[key], str):
                data[key] = clean_text(data[key])
            elif isinstance(data[key], list):
                data[key] = [clean_text(item) for item in data[key]]
                
    new_data = json.dumps(data, ensure_ascii=False)
    if new_data != orig_data:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"✅ {path.name}: 평이화 완료")
        count += 1

print(f"\n🎉 총 {count}개의 파일 본문에서 한자를 완벽하게 제거했습니다!")
