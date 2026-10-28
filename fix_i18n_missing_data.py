import json
from pathlib import Path

DATA_DIR = Path("app/services/content/data")

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# 1. zh_cn compatibility.json - family 키 이식
en_comp = load(DATA_DIR / "en/compatibility.json")
zh_comp_path = DATA_DIR / "zh_cn/compatibility.json"
zh_comp = load(zh_comp_path)

if "family" not in zh_comp.get("ELEMENT_CONTENT", {}):
    # 영문 family 데이터를 복사 (임시 폴백)
    for key in ["ELEMENT_CONTENT", "DAY_MASTER_CONTENT", "TEN_GODS_CONTENT", "SINSAL_CONTENT"]:
        if "family" not in zh_comp[key]:
            zh_comp[key]["family"] = en_comp[key]["family"]
    save(zh_comp_path, zh_comp)
    print("✅ zh_cn compatibility family 복구 완료")

# 2. ja, zh_cn daily/monthly/year - 3변형 리스트 강제 적용
for lang in ["ja", "zh_cn"]:
    for section, key_name in [("daily", "DAILY_THEME_CONTENT"), ("monthly", "MONTHLY_THEME_CONTENT"), ("year", "YEAR_THEME_CONTENT")]:
        file_path = DATA_DIR / lang / f"{section}.json"
        en_file_path = DATA_DIR / "en" / f"{section}.json"
        if not file_path.exists(): continue
        
        lang_data = load(file_path)
        en_data = load(en_file_path)
        
        changed = False
        for tg, content in lang_data.get(key_name, {}).items():
            if isinstance(content, dict):
                # 단일 dict인 경우 -> en 데이터에서 3개 리스트 복사
                if tg in en_data[key_name] and isinstance(en_data[key_name][tg], list):
                    # 임시로 영문 텍스트 이식 (추후 번역 필요)
                    lang_data[key_name][tg] = en_data[key_name][tg]
                    changed = True
        
        if changed:
            save(file_path, lang_data)
            print(f"✅ {lang}/{section}.json 변형 리스트 구조 복구 완료")

# 3. ko personalization.json - seven_killings 누락
ko_p_path = DATA_DIR / "ko/personalization.json"
ko_p = load(ko_p_path)
if "seven_killings" not in ko_p.get("SPECIAL_CONDITIONS", {}):
    ko_p["SPECIAL_CONDITIONS"]["seven_killings"] = "당신은 강한 '보스' 기운을 가지고 있습니다. 주도권을 잡고 전략을 짜며 무리를 이끄는 데 탁월합니다. 압박과 위기 상황에서 오히려 더 강해집니다."
    save(ko_p_path, ko_p)
    print("✅ ko personalization seven_killings 복구 완료")