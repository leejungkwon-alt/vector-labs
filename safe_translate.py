# 파일명: safe_translate.py
import os
import json
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(ROOT, "app", "services", "content", "data", "ko", "cross_insight.json")
WRITER_FILE = os.path.join(ROOT, "app", "services", "content_writer.py")
FRONT_FILE = os.path.join(ROOT, "frontend", "src", "components", "sections", "PremiumSection.tsx")

# 바꿀 단어 사전
REPLACE_DICT = {
    "당신의 숨겨진 세 가지 얼굴": "당신의 숨겨진 세 가지 얼굴",
    "내 안의 세 가지 얼굴": "당신의 숨겨진 세 가지 얼굴",
    "지금 이 시기": "지금 내 인생의 흐름",
    "새로운 도전의 시기": "새로운 도전의 시기", "甲子": "새로운 시작의 시기", "乙丑": "안정과 내실의 시기",
    "丙寅": "열정과 성장의 시기", "丁卯": "관계와 소통의 시기", "戊辰": "기반 다지기의 시기",
    "己巳": "지혜와 변화의 시기", "庚午": "성취와 명예의 시기", "辛未": "섬세한 조율의 시기",
    "壬申": "유연한 적응의 시기", "癸酉": "내면의 성숙의 시기", "甲戌": "굳건한 의지의 시기",
    "乙亥": "따뜻한 포용의 시기", "丙子": "빛나는 지혜의 시기", "丁丑": "꾸준한 노력의 시기",
    "丙辰": "용기와 도약의 시기", "戊午": "열정과 성취의 시기", "庚申": "결단과 실행의 시기"
}

def replace_text_in_file(filepath):
    if not os.path.exists(filepath):
        print(f"[SKIP] 파일 없음: {os.path.basename(filepath)}")
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    for old, new in REPLACE_DICT.items():
        content = content.replace(old, new)
        # 한자 뒤에 붙은 괄호 제거 (예: 새로운 도전의 시기(무인) -> 새로운 도전의 시기)
        content = re.sub(r'[\(\[]' + old + r'[\)\]]', new, content)
        
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] 수정 완료: {os.path.basename(filepath)}")
    else:
        print(f"[PASS] 변경할 단어가 없습니다: {os.path.basename(filepath)}")

def replace_text_in_json(filepath):
    if not os.path.exists(filepath):
        print(f"[SKIP] JSON 파일 없음: {os.path.basename(filepath)}")
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    def recursive_replace(obj):
        if isinstance(obj, str):
            for old, new in REPLACE_DICT.items():
                obj = obj.replace(old, new)
            return obj
        elif isinstance(obj, dict):
            return {k: recursive_replace(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [recursive_replace(v) for v in obj]
        return obj

    new_data = recursive_replace(data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] 수정 완료: {os.path.basename(filepath)}")

print("=== 안전한 텍스트 변환 시작 ===")
replace_text_in_json(JSON_FILE)
replace_text_in_file(WRITER_FILE)
replace_text_in_file(FRONT_FILE)
print("=== 작업 완료 ===")