# scripts/fix_date_picker.py
"""
BirthDateWheelPicker.tsx 다국어 + 레이아웃 통합 패치
1) useT() 훅 추가, 하드코딩된 한국어 → t() 교체
2) 스타일 수정 (웹/native 분기, 불필요한 height 제거)
3) 5개 언어 JSON에 datePicker 키 추가
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ============ 1. TSX 패치 ============
TSX = Path("frontend/src/components/BirthDateWheelPicker.tsx")
if not TSX.exists():
    print(f"❌ {TSX} 없음")
    sys.exit(1)

txt = TSX.read_text(encoding="utf-8")
orig = txt

# (a) useT import
if "useT" not in txt:
    txt = txt.replace(
        "import { Picker } from '@react-native-picker/picker';",
        "import { Picker } from '@react-native-picker/picker';\nimport { useT } from '@/i18n';",
        1,
    )

# (b) const t = useT()
if "const t = useT();" not in txt:
    txt = txt.replace(
        "initialDate }: Props) {  const initDate",
        "initialDate }: Props) {\n  const t = useT();\n  const initDate",
        1,
    )

# (c) 하드코딩 텍스트 교체
repl = [
    ('<Text style={styles.cancelText}>취소</Text>',
     '<Text style={styles.cancelText}>{t("datePicker.cancel")}</Text>'),
    ('<Text style={styles.title}>생년월일 선택</Text>',
     '<Text style={styles.title}>{t("datePicker.title")}</Text>'),
    ('<Text style={styles.confirmText}>확인</Text>',
     '<Text style={styles.confirmText}>{t("datePicker.confirm")}</Text>'),
    ('label={`${y}년`}', 'label={`${y}${t("datePicker.yearSuffix")}`}'),
    ('label={`${m}월`}', 'label={`${m}${t("datePicker.monthSuffix")}`}'),
    ('label={`${d}일`}', 'label={`${d}${t("datePicker.daySuffix")}`}'),
]
for old, new in repl:
    if old in txt:
        txt = txt.replace(old, new, 1)

# (d) 스타일 수정
old_styles = """  pickerContainer: { flexDirection: 'row', height: 200, width: '100%' },
  picker: { flex: 1, color: textColor },
  pickerItem: { color: textColor, fontSize: 18, height: 200 },"""
new_styles = """  pickerContainer: {
    flexDirection: 'row',
    height: isWeb ? 56 : 200,
    width: '100%',
    alignItems: 'center',
    paddingHorizontal: 8,
  },
  picker: { flex: 1, color: textColor, height: isWeb ? 40 : undefined },
  pickerItem: { color: textColor, fontSize: 18 },"""

if old_styles in txt:
    txt = txt.replace(old_styles, new_styles, 1)
    print("✅ 스타일 수정 완료")
else:
    print("⚠️ 스타일 패턴 불일치 — 파일 확인 필요")

if txt != orig:
    print("✅ TSX 변경 완료")
    if APPLY:
        TSX.write_text(txt, encoding="utf-8")
        print(f"🎉 저장: {TSX}")
else:
    print("ℹ️ TSX 변경 사항 없음")

# ============ 2. JSON 번역 키 추가 ============
TRANSLATIONS = {
    "ko": {"cancel": "취소", "title": "생년월일 선택", "confirm": "확인",
           "yearSuffix": "년", "monthSuffix": "월", "daySuffix": "일"},
    "en": {"cancel": "Cancel", "title": "Select Date", "confirm": "OK",
           "yearSuffix": "", "monthSuffix": "", "daySuffix": ""},
    "ja": {"cancel": "キャンセル", "title": "生年月日を選択", "confirm": "確認",
           "yearSuffix": "年", "monthSuffix": "月", "daySuffix": "日"},
    "zh": {"cancel": "取消", "title": "选择出生日期", "confirm": "确认",
           "yearSuffix": "年", "monthSuffix": "月", "daySuffix": "日"},
    "es": {"cancel": "Cancelar", "title": "Seleccionar fecha", "confirm": "Aceptar",
           "yearSuffix": "", "monthSuffix": "", "daySuffix": ""},
}

def lang_key(p):
    s = p.stem.lower()
    return "zh" if s.startswith("zh") else "ja" if s.startswith("ja") else \
           "es" if s.startswith("es") else "ko" if s.startswith("ko") else \
           "en" if s.startswith("en") else None

json_files = [p for p in Path("frontend").rglob("*.json")
              if "node_modules" not in str(p) and lang_key(p)]

print(f"\n📦 번역 파일 {len(json_files)}개")
for f in json_files:
    lang = lang_key(f)
    if lang not in TRANSLATIONS:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, dict):
        continue
    if "datePicker" not in data:
        data["datePicker"] = {}
    changed = False
    for k, v in TRANSLATIONS[lang].items():
        if k not in data["datePicker"]:
            data["datePicker"][k] = v
            changed = True
    if changed:
        if APPLY:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
            print(f"🎉 {f}")
        else:
            print(f"🧪 {f} (예정)")

if not APPLY:
    print("\n🧪 미리보기. 적용: python scripts/fix_date_picker.py --apply")