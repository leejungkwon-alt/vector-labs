import json
from pathlib import Path

DATA_DIR = Path("app/services/content/data/ko/core_pillars")

def refine_natural_language(text):
    if not isinstance(text, str):
        return text
    
    # 1. "성숙한 당신은 ~" -> "당신이 한 단계 더 성숙해지면 ~"
    # (예: 성숙한 당신은 ~ 사람입니다 -> 당신이 한 단계 더 성숙해지면 ~ 사람이 됩니다)
    text = text.replace("성숙한 당신은", "당신이 한 단계 더 성숙해지면")
    text = text.replace("성숙한 당신의", "한 단계 성숙해진 당신의")
    text = text.replace("한 당신은", "당신은") # 혹시 남아있을 경우 대비
    
    # 2. "대화재" -> "오래 타오르는 불씨" 또는 "장작불" (불(火)의 긍정적 의미 강조)
    text = text.replace("몇 년에 걸친 대화재", "몇 년에 걸쳐 오래 타오르는 불")
    text = text.replace("대화재", "오래 타오르는 불씨")
    
    # 3. 기타 기계적 표현 교정
    text = text.replace("사람입니다. 처음의 뜨거움을", "사람이 됩니다. 처음의 뜨거움을")
    
    return text

print("=== 콘텐츠 본문 어색한 번역투 자연어 교정 시작 ===")
count = 0
for path in DATA_DIR.glob("*.json"):
    if ".bak" in path.name: continue
    data = json.loads(path.read_text(encoding="utf-8"))
    orig_data = json.dumps(data, ensure_ascii=False)
    
    for key in ["hero", "narrative", "shadows", "advice"]:
        if key in data:
            if isinstance(data[key], str):
                data[key] = refine_natural_language(data[key])
            elif isinstance(data[key], list):
                data[key] = [refine_natural_language(item) for item in data[key]]
                
    new_data = json.dumps(data, ensure_ascii=False)
    if new_data != orig_data:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"✅ {path.name}: 자연어 교정 완료")
        count += 1

print(f"\n🎉 총 {count}개의 파일에서 기계적인 문장을 자연스러운 대화체로 교정했습니다!")
