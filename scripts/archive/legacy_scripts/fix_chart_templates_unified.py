#!/usr/bin/env python3
"""
차트 템플릿(CHART_NOTE_TEMPLATE, CHART_POSITION_TEMPLATES) 다국어 통일화.
- EN/ES: 한국어와 동일한 깊이와 뉘앙스로 번역 보강
- KO: 조사 오류('이' -> '가') 수정
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app" / "services" / "content" / "data"

TEMPLATES = {
    "ko": {
        "CHART_NOTE_TEMPLATE": "당신의 {a}와 {b}가 모두 '{archetype}'입니다. 이는 일할 때나 혼자 있을 때나 당신의 모습이 똑같다는 뜻입니다. '직장에서의 나'와 '진짜 나'가 분리되지 않아 늘 진솔하고 일관적이지만, 일과 일상의 경계가 모호해져 쉽게 지칠 수 있습니다.",
        "CHART_POSITION_TEMPLATES": {
            "year_pillar": "어린 시절과 가족의 영향으로, 당신은 '{archetype}'의 성향을 타고났습니다.",
            "month_pillar": "사회생활과 직장에서 당신은 '{archetype}'처럼 행동하며 두각을 나타냅니다.",
            "day_pillar": "당신의 가장 깊은 내면이자 본질은 '{archetype}'입니다.",
            "hour_pillar": "앞으로 나이 들수록, 그리고 내면 깊은 곳에서는 '{archetype}'의 모습이 드러납니다."
        }
    },
    "en": {
        "CHART_NOTE_TEMPLATE": "Your {a} and {b} both share the same '{archetype}' energy. This means that whether you're working or alone, your presence remains exactly the same. Because 'who you are at work' and 'the real you' are not separated, you are always sincere and consistent. However, the boundary between work and daily life can blur, making it easy for you to burn out.",
        "CHART_POSITION_TEMPLATES": {
            "year_pillar": "Influenced by your childhood and family, you were born with the traits of '{archetype}'.",
            "month_pillar": "In your social life and career, you stand out by acting like '{archetype}'.",
            "day_pillar": "Your deepest inner self and core essence is '{archetype}'.",
            "hour_pillar": "As you grow older and look within, the energy of '{archetype}' emerges."
        }
    },
    "es": {
        "CHART_NOTE_TEMPLATE": "Tu {a} y tu {b} comparten la misma energía '{archetype}'. Esto significa que, ya sea trabajando o a solas, tu presencia es exactamente la misma. Como 'quién eres en el trabajo' y 'el verdadero tú' no están separados, siempre eres sincero y consistente. Sin embargo, el límite entre el trabajo y la vida diaria puede difuminarse, haciendo que sea fácil que te agotes.",
        "CHART_POSITION_TEMPLATES": {
            "year_pillar": "Influenciado por tu infancia y familia, naciste con los rasgos de '{archetype}'.",
            "month_pillar": "En tu vida social y carrera, destacas actuando como '{archetype}'.",
            "day_pillar": "Tu ser interior más profundo y esencia central es '{archetype}'.",
            "hour_pillar": "A medida que envejeces y miras hacia adentro, emerge la energía de '{archetype}'."
        }
    }
}

def main() -> int:
    print("[Fix] 차트 템플릿 다국어 통일화")
    
    for lang, keys in TEMPLATES.items():
        path = DATA / lang / "sections.json"
        if not path.exists():
            print(f"  [ERR] {path} 없음")
            continue
            
        data = json.loads(path.read_text(encoding="utf-8"))
        
        # 템플릿 업데이트
        data["CHART_NOTE_TEMPLATE"] = keys["CHART_NOTE_TEMPLATE"]
        if "CHART_POSITION_TEMPLATES" not in data:
            data["CHART_POSITION_TEMPLATES"] = {}
        data["CHART_POSITION_TEMPLATES"].update(keys["CHART_POSITION_TEMPLATES"])
        
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8"
        )
        print(f"  [OK] {path.name} 업데이트")
        
    print("\n✅ 템플릿 통일 완료. 백엔드 서버를 재시작하거나 새로고침하세요.")
    return 0

if __name__ == "__main__":
    sys.exit(main())