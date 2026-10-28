#!/usr/bin/env python3
"""
fix_labels.py
- ja, zh_cn, es 의 sections.json 에서 MODE_DISPLAY 내 영어 괄호 (ex: (Flow)) 제거
- frontend/src/components/sections/shared.tsx 의 다국어 라벨 업데이트
"""
import json
import re
import sys
from pathlib import Path

# 경로 설정 (이 스크립트가 루트에 있다고 가정)
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "app" / "services" / "content" / "data"
SHARED_TSX = ROOT / "frontend" / "src" / "components" / "sections" / "shared.tsx"

PAREN_REGEX = re.compile(r'\s*\([a-zA-Z\s]+\)')

def fix_backend_json(lang: str):
    path = DATA_DIR / lang / "sections.json"
    if not path.exists():
        print(f"[SKIP] {lang}/sections.json 파일 없음")
        return

    data = json.loads(path.read_text(encoding="utf-8"))
    mode_display = data.get("MODE_DISPLAY", {})
    changed = False

    for key, val in mode_display.items():
        if isinstance(val, str):
            new_val = PAREN_REGEX.sub('', val).strip()
            if new_val != val:
                mode_display[key] = new_val
                changed = True
                print(f"  [{lang}] {key}: '{val}' -> '{new_val}'")

    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"✅ {lang}/sections.json 저장 완료")
    else:
        print(f"✔️ {lang}/sections.json 이미 깨끗함")

def fix_frontend_tsx():
    if not SHARED_TSX.exists():
        print(f"[SKIP] {SHARED_TSX} 파일 없음")
        return

    text = SHARED_TSX.read_text(encoding="utf-8")
    
    # 이미 ja 언어가 추가되어 있다면 패스 (중복 실행 방지)
    if "ja:" in text and "zh_cn:" in text and "es:" in text:
        print("✔️ shared.tsx 이미 다국어 라벨로 업데이트됨")
        return

    new_block = '''const useFormatMode = () => {
  const lang = useLanguageStore((s) => s.lang);
  return (m: string) => {
    if (!m || !m.startsWith("THE_")) return m;
    const entry = MODE_LABELS[m];
    if (!entry) return m;
    // 현재 언어에 맞는 라벨 반환 (없으면 en 폴백)
    return entry[lang as keyof typeof entry] || entry.en;
  };
};

const MODE_LABELS: Record<string, { ko: string, en: string, ja: string, zh_cn: string, es: string }> = {
  THE_PIONEER:    { ko: "거목",       en: "Pioneer",    ja: "大木",         zh_cn: "先锋",     es: "Pionero" },
  THE_ADAPTER:    { ko: "덩굴",       en: "Adapter",    ja: "蔦",           zh_cn: "适应者",   es: "Adaptador" },
  THE_RADIATOR:   { ko: "태양",       en: "Radiator",   ja: "太陽",         zh_cn: "太阳",     es: "Radiador" },
  THE_KEEPER:     { ko: "등불",       en: "Keeper",     ja: "灯火",         zh_cn: "守灯人",   es: "Linterna" },
  THE_ANCHOR:     { ko: "산",         en: "Anchor",     ja: "山",           zh_cn: "锚",       es: "Ancla" },
  THE_CULTIVATOR: { ko: "정원",       en: "Cultivator", ja: "庭",           zh_cn: "耕耘者",   es: "Cultivador" },
  THE_BLADE:      { ko: "칼날",       en: "Blade",      ja: "刃",           zh_cn: "刀刃",     es: "Filo" },
  THE_GEM:        { ko: "보석",       en: "Gem",        ja: "宝石",         zh_cn: "宝石",     es: "Gema" },
  THE_DEEP:       { ko: "바다",       en: "Deep",       ja: "海",           zh_cn: "深海",     es: "Profundo" },
  THE_SPRING:     { ko: "샘",         en: "Spring",     ja: "泉",           zh_cn: "泉水",     es: "Manantial" },
  THE_STEWARD:    { ko: "관리자",     en: "Steward",    ja: "管理人",       zh_cn: "管家",     es: "Administrador" },
  THE_OPERATOR:   { ko: "운영자",     en: "Operator",   ja: "運営者",       zh_cn: "运营者",   es: "Operador" },
  THE_FLOW:       { ko: "흐름",       en: "Flow",       ja: "流れ",         zh_cn: "流动型",   es: "Flujo" },
  THE_CREATOR:    { ko: "창작자",     en: "Creator",    ja: "創造者",       zh_cn: "创作者",   es: "Creador" },
  THE_CHALLENGER: { ko: "도전자",     en: "Challenger", ja: "挑戦者",       zh_cn: "挑战者",   es: "Desafiante" },
  THE_OFFICER:    { ko: "원칙주의자", en: "Officer",    ja: "原理主義者",   zh_cn: "管理者",   es: "Guardián" },
  THE_SURVIVOR:   { ko: "생존자",     en: "Survivor",   ja: "生存者",       zh_cn: "幸存者",   es: "Superviviente" },
  THE_MYSTIC:     { ko: "탐구자",     en: "Mystic",     ja: "探究者",       zh_cn: "神秘主义者", es: "Místico" },
  THE_MENTOR:     { ko: "멘토",       en: "Mentor",     ja: "メンター",     zh_cn: "导师",     es: "Mentor" },
  THE_GENERALIST: { ko: "올라운더",   en: "Generalist", ja: "オールラウンダー", zh_cn: "通才",   es: "Generalista" },
  THE_TWIN:       { ko: "동반자",     en: "Twin",       ja: "相棒",         zh_cn: "同伴者",   es: "Compañero" },
  THE_RIVAL:      { ko: "경쟁자",     en: "Rival",      ja: "ライバル",     zh_cn: "竞争对手", es: "Rival" },
  THE_ALLY:       { ko: "조력자",     en: "Ally",       ja: "味方",         zh_cn: "盟友",     es: "Aliado" },
  THE_EMPATH:     { ko: "공감자",     en: "Empath",     ja: "共感者",       zh_cn: "共情者",   es: "Empático" },
};
'''

    # 정규식으로 useFormatMode ~ MODE_LABELS 끝부분까지 싹 교체
    pattern = r"const useFormatMode = \(\) => \{.*?const MODE_LABELS: Record<string, \{ ko: string, en: string \}> = \{.*?\n\};"
    
    if not re.search(pattern, text, flags=re.DOTALL):
        print("❌ [ERROR] shared.tsx에서 교체할 MODE_LABELS 블록을 찾지 못했습니다. 수동으로 확인해주세요.")
        return

    text = re.sub(pattern, new_block, text, flags=re.DOTALL)
    SHARED_TSX.write_text(text, encoding="utf-8")
    print("✅ shared.tsx 업데이트 완료")

if __name__ == "__main__":
    print("=== 백엔드 JSON 수정 (ja, zh_cn, es) ===")
    for lang in ["ja", "zh_cn", "es"]:
        fix_backend_json(lang)
    
    print("\n=== 프론트엔드 TSX 수정 ===")
    fix_frontend_tsx()
    
    print("\n🎉 모든 작업 완료!")
    print("※ 주의: 화면에 반영하려면 백엔드(uvicorn)와 프론트엔드(expo)를 재시작해야 합니다.")