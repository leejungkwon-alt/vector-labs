import json
from pathlib import Path

DATA_DIR = Path("app/services/content/data/ko")
FILES = ["sections.json", "career.json", "love.json", "wealth.json"]

# 한글 (영어) 매핑 딕셔너리
MAPPING = {
    "THE_PIONEER": "거목 (Pioneer)",
    "THE_ADAPTER": "덩굴 (Adapter)",
    "THE_RADIATOR": "태양 (Radiator)",
    "THE_KEEPER": "등불 (Keeper)",
    "THE_ANCHOR": "산 (Anchor)",
    "THE_CULTIVATOR": "정원 (Cultivator)",
    "THE_BLADE": "칼날 (Blade)",
    "THE_GEM": "보석 (Gem)",
    "THE_DEEP": "바다 (Deep)",
    "THE_SPRING": "샘 (Spring)",
    "THE_STEWARD": "관리자 (Steward)",
    "THE_OPERATOR": "운영자 (Operator)",
    "THE_FLOW": "흐름 (Flow)",
    "THE_CREATOR": "창작자 (Creator)",
    "THE_CHALLENGER": "도전자 (Challenger)",
    "THE_OFFICER": "원칙주의자 (Officer)",
    "THE_SURVIVOR": "생존자 (Survivor)",
    "THE_MYSTIC": "탐구자 (Mystic)",
    "THE_MENTOR": "멘토 (Mentor)",
    "THE_GENERALIST": "올라운더 (Generalist)",
    "THE_TWIN": "동반자 (Twin)",
    "THE_RIVAL": "경쟁자 (Rival)",
    "THE_ALLY": "조력자 (Ally)",
    "THE_EMPATH": "공감자 (Empath)"
}

def process_file(filename):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"❌ {filename} 없음")
        return
    
    data = json.loads(path.read_text(encoding="utf-8"))
    orig_data = json.dumps(data, ensure_ascii=False)
    updated = False

    if filename == "sections.json":
        if "MODE_DISPLAY" in data:
            data["MODE_DISPLAY"] = MAPPING
            updated = True
    else:
        # career.json, love.json, wealth.json 처리
        for content_key, content in data.get("CONTENT", {}).items():
            for match_type in ["best_match", "challenging_match"]:
                if match_type in content and isinstance(content[match_type], list):
                    new_matches = [MAPPING.get(m, m) for m in content[match_type]]
                    if content[match_type] != new_matches:
                        content[match_type] = new_matches
                        updated = True

    if updated:
        new_data = json.dumps(data, ensure_ascii=False)
        if new_data != orig_data:
            # 백업 생성
            bak = path.with_suffix(".json.bak.bilingual")
            bak.write_text(orig_data, encoding="utf-8")
            
            # 덮어쓰기
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"✅ {filename} 한글(영어) 병기 업데이트 완료")
        else:
            print(f"⚠️ {filename} 이미 적용됨 (변경 사항 없음)")
    else:
        print(f"⚠️ {filename} 대상 데이터를 찾을 수 없습니다.")

print("=== 매치 데이터 한글(영어) 병기 변환 시작 ===")
for f in FILES:
    process_file(f)
print("🎉 작업 완료! 백엔드 서버를 재시작하거나 재배포해주세요.")
