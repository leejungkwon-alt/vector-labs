from pathlib import Path

SHARED_TSX = Path("frontend/src/components/sections/shared.tsx")

if not SHARED_TSX.exists():
    print("❌ 파일 없음:", SHARED_TSX)
    exit()

text = SHARED_TSX.read_text(encoding="utf-8")

# 이미 다국어로 변경되었는지 확인
if "ja:" in text and "zh_cn:" in text and "es:" in text:
    print("✔️ 이미 다국어 라벨로 업데이트되어 있습니다.")
    exit()

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

# 시작 지점과 끝 지점 찾기
start_marker = "const useFormatMode = () => {"
end_marker = "export function CompatBox"

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx != -1 and end_idx != -1:
    # 기존 코드를 새 코드로 교체
    new_text = text[:start_idx] + new_block + text[end_idx:]
    SHARED_TSX.write_text(new_text, encoding="utf-8")
    print("✅ shared.tsx 업데이트 완료")
else:
    print("❌ 시작 또는 끝 마커를 찾을 수 없습니다. 수동으로 확인해주세요.")