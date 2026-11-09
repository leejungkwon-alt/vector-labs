# scripts/update_compat_labels.py
import json
from pathlib import Path

LABELS = {
    "ko": {
        "elements": "에너지 흐름",
        "dayMaster": "타고난 성정",
        "tenGods": "관계의 방식",
        "sinsal_romance": "두 사람의 인연",
        "sinsal_business": "업무 궁합",
        "sinsal_friend": "우정 케미",
        "sinsal_family": "가족의 결",
    },
    "en": {
        "elements": "Energy Flow",
        "dayMaster": "Innate Temperament",
        "tenGods": "Relationship Style",
        "sinsal_romance": "Destined Connection",
        "sinsal_business": "Work Synergy",
        "sinsal_friend": "Friendship Vibes",
        "sinsal_family": "Family Bond",
    },
    "ja": {
        "elements": "エネルギーの流れ",
        "dayMaster": "生まれ持った気質",
        "tenGods": "関係のスタイル",
        "sinsal_romance": "二人の縁",
        "sinsal_business": "仕事の相性",
        "sinsal_friend": "友情のケミ",
        "sinsal_family": "家族の絆",
    },
    "zh_cn": {
        "elements": "能量流动",
        "dayMaster": "天生性情",
        "tenGods": "相处方式",
        "sinsal_romance": "两人的缘分",
        "sinsal_business": "工作契合度",
        "sinsal_friend": "友情默契",
        "sinsal_family": "家人的羁绊",
    },
    "es": {
        "elements": "Flujo de Energía",
        "dayMaster": "Temperamento Innato",
        "tenGods": "Estilo de Relación",
        "sinsal_romance": "Conexión Destinada",
        "sinsal_business": "Sinergia Laboral",
        "sinsal_friend": "Vibra Amistosa",
        "sinsal_family": "Vínculo Familiar",
    },
}

for lang, L in LABELS.items():
    path = Path(f"frontend/src/locales/{lang}.json")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    comp = data.setdefault("compatibility", {})
    comp["axisElements"]      = L["elements"]
    comp["axisDayMaster"]     = L["dayMaster"]
    comp["axisTenGods"]       = L["tenGods"]
    comp["axisSinsal_romance"]  = L["sinsal_romance"]
    comp["axisSinsal_business"] = L["sinsal_business"]
    comp["axisSinsal_friend"]   = L["sinsal_friend"]
    comp["axisSinsal_family"]   = L["sinsal_family"]
    # 기존 axisSinsal은 그대로 둠 (다른 곳 참조 가능성 대비, 안전)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"✅ {lang}.json updated")