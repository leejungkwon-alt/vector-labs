import json
import re
from pathlib import Path

ROOT = Path(".")
DATA_DIR = ROOT / "app" / "services" / "content" / "data"

def fix_backend_json(lang):
    path = DATA_DIR / lang / "sections.json"
    if not path.exists(): return
    data = json.loads(path.read_text(encoding="utf-8"))
    mode = data.get("MODE_DISPLAY", {})
    changed = False
    for k, v in mode.items():
        new_v = re.sub(r'\s*\([a-zA-Z\s]+\)', '', v).strip()
        if new_v != v:
            mode[k] = new_v
            changed = True
    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"✅ {lang}/sections.json MODE_DISPLAY 정리 완료")

def fix_zh_core_pillars():
    pillar_dir = DATA_DIR / "zh_cn" / "core_pillars"
    if not pillar_dir.exists(): return
    
    # 기계번역으로 깨진 음역 오류 목록
    wrong_map = {
        "冰阴": "丙寅", "丁周": "丁丑", "丁海": "丁亥", "丁茂": "丁卯", "丁思": "丁巳", "丁伟": "丁未", "丁游": "丁酉",
        "吴武": "戊午", "吴子": "戊子", "吴寅": "戊寅", "吴辰": "戊辰", "吴旭": "戊戌", "吴申": "戊申",
        "吉周": "己丑", "吉海": "己亥", "吉茂": "己卯", "吉思": "己巳", "吉伟": "己未", "吉游": "己酉",
        "耿武": "庚午", "耿子": "庚子", "耿寅": "庚寅", "耿辰": "庚辰", "耿旭": "庚戌", "耿申": "庚申",
        "辛周": "辛丑", "辛海": "辛亥", "辛茂": "辛卯", "辛思": "辛巳", "辛伟": "辛未", "辛游": "辛酉",
        "壬武": "壬午", "壬旭": "壬戌", 
        "癸周": "癸丑", "癸海": "癸亥", "癸茂": "癸卯", "癸思": "癸巳", "癸伟": "癸未", "癸游": "癸酉",
        "甲武": "甲午", "甲旭": "甲戌",
        "乙周": "乙丑", "乙海": "乙亥", "乙茂": "乙卯", "乙思": "乙巳", "乙伟": "乙未", "乙游": "乙酉",
    }
    
    for fp in pillar_dir.glob("*.json"):
        correct_hanja = fp.stem
        text = fp.read_text(encoding="utf-8")
        original_text = text
        
        for wrong, right in wrong_map.items():
            if wrong in text:
                text = text.replace(wrong, right)
        
        # "成熟的丁丑은" 처럼 남아있는 한국어 조사 제거
        text = re.sub(r'成熟的(甲|乙|丙|丁|戊|己|庚|辛|壬|癸)(子|丑|寅|卯|辰|巳|午|未|申|酉|戌|亥)[은는]', r'成熟的\1\2', text)
        
        if text != original_text:
            fp.write_text(text, encoding="utf-8")
            print(f"✅ zh_cn/core_pillars/{fp.name} 오역 수정 완료")

def fix_frontend_tsx():
    # 1. shared.tsx 다국어 업데이트 (이전 실패한 로직 안전하게 교체)
    shared_path = ROOT / "frontend" / "src" / "components" / "sections" / "shared.tsx"
    if shared_path.exists():
        text = shared_path.read_text(encoding="utf-8")
        if "ja:" not in text or "zh_cn:" not in text:
            start_marker = "const useFormatMode = () => {"
            end_marker = "export function CompatBox"
            
            start_idx = text.find(start_marker)
            end_idx = text.find(end_marker)
            
            if start_idx != -1 and end_idx != -1:
                new_block = '''const useFormatMode = () => {
  const lang = useLanguageStore((s) => s.lang);
  return (m: string) => {
    if (!m || !m.startsWith("THE_")) return m;
    const entry = MODE_LABELS[m];
    if (!entry) return m;
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
                text = text[:start_idx] + new_block + text[end_idx:]
                shared_path.write_text(text, encoding="utf-8")
                print("✅ shared.tsx 다국어 라벨 업데이트 완료")

    # 2. ChartSection.tsx 하드코딩된 "(본질)" 제거 및 i18n 적용
    chart_path = ROOT / "frontend" / "src" / "components" / "sections" / "ChartSection.tsx"
    if chart_path.exists():
        text = chart_path.read_text(encoding="utf-8")
        if '&& "(본질)"' in text:
            text = text.replace('{layer.is_self && "(본질)"}', '{layer.is_self && t("sections.coreEssence")}')
            if 'import { useT }' not in text:
                text = 'import { useT } from "@/i18n";\n' + text
            if 'const t = useT();' not in text:
                text = text.replace('export function ChartSectionView({ section }: { section: ChartSection }) {', 'export function ChartSectionView({ section }: { section: ChartSection }) {\n  const t = useT();')
            chart_path.write_text(text, encoding="utf-8")
            print("✅ ChartSection.tsx (본질) -> 다국어(i18n) 교체 완료")

if __name__ == "__main__":
    print("=== 1. 백엔드 MODE_DISPLAY 영어 괄호 제거 (ja, zh_cn, es) ===")
    for lang in ["ja", "zh_cn", "es"]:
        fix_backend_json(lang)
    
    print("\n=== 2. 중국어 core_pillars 기계번역 오류 수정 (冰阴 -> 丙寅 등) ===")
    fix_zh_core_pillars()
    
    print("\n=== 3. 프론트엔드 다국어 및 하드코딩 수정 ===")
    fix_frontend_tsx()
    
    print("\n🎉 모든 수정이 완료되었습니다. 서버와 앱을 재시작해주세요.")