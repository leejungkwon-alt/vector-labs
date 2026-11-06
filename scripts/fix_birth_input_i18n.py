# scripts/fix_birth_input_i18n.py
"""
1) birth-input.tsx의 하드코딩 한국어 3개 + tf() fallback 4개를 영어/중립으로 변경
2) i18n JSON에 birthInput 키 추가 (5개 언어)
3) "출생 정보 입력" 하드코딩된 네비게이션 파일 탐색
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ============ 1) birth-input.tsx 패치 ============
BIRTH = Path("frontend/app/birth-input.tsx")
txt = BIRTH.read_text(encoding="utf-8")
orig = txt

# 하드코딩 → t() 교체
hardcoded = [
    ('>도시 이름 (City Name)<', '>{t("birthInput.cityNameLabel")}<'),
    ('>경도 (Longitude)<', '>{t("birthInput.longitudeLabel")}<'),
    (
        '* 사주 계산 시 태양시 보정에 사용됩니다. 모르시면 비워두셔도 됩니다.',
        '{t("birthInput.longitudeHint")}',
    ),
]
for old, new in hardcoded:
    if old in txt:
        txt = txt.replace(old, new, 1)
        print(f"✅ 교체: {old[:30]}...")

# tf() fallback을 한국어 → 영어 (언어별 i18n 키가 없을 때만 뜨는 fallback이므로 영어 기본)
fallbacks = [
    ('tf("birthInput.cityLookupLoading", "도시를 찾는 중…")',
     'tf("birthInput.cityLookupLoading", "Searching city...")'),
    ('tf("birthInput.cityLookupNotFound", "도시를 찾지 못했어요. 철자를 확인하거나 경도와 타임존을 직접 입력해 주세요.")',
     'tf("birthInput.cityLookupNotFound", "City not found. Check spelling or enter manually.")'),
    ('tf("birthInput.cityLookupError", "도시 검색에 실패했어요. 경도와 타임존을 직접 입력해 주세요.")',
     'tf("birthInput.cityLookupError", "City search failed. Please enter manually.")'),
    ('tf("birthInput.tzOffsetAtBirth", "출생일 기준 UTC 오프셋")',
     'tf("birthInput.tzOffsetAtBirth", "UTC offset at birth")'),
]
for old, new in fallbacks:
    if old in txt:
        txt = txt.replace(old, new, 1)
        print(f"✅ fallback 변경: {old[:40]}...")

# ============ 2) JSON 번역 키 추가 ============
TRANS = {
    "ko": {
        "cityNameLabel": "도시 이름",
        "longitudeLabel": "경도",
        "longitudeHint": "* 사주 계산 시 태양시 보정에 사용됩니다. 모르시면 비워두셔도 됩니다.",
    },
    "en": {
        "cityNameLabel": "City Name",
        "longitudeLabel": "Longitude",
        "longitudeHint": "* Used for solar time correction. Leave blank if unknown.",
    },
    "ja": {
        "cityNameLabel": "都市名",
        "longitudeLabel": "経度",
        "longitudeHint": "* 四柱推命計算の太陽時補正に使用。不明な場合は空欄で構いません。",
    },
    "zh": {
        "cityNameLabel": "城市名称",
        "longitudeLabel": "经度",
        "longitudeHint": "* 用于四柱计算中的太阳时校正。不清楚可留空。",
    },
    "es": {
        "cityNameLabel": "Nombre de la ciudad",
        "longitudeLabel": "Longitud",
        "longitudeHint": "* Se usa para la corrección de hora solar. Deje en blanco si no lo sabe.",
    },
}

def lang_key(p):
    s = p.stem.lower()
    return ("zh" if s.startswith("zh") else "ja" if s.startswith("ja") else
            "es" if s.startswith("es") else "ko" if s.startswith("ko") else
            "en" if s.startswith("en") else None)

for f in Path("frontend/src/locales").glob("*.json"):
    lang = lang_key(f)
    if lang not in TRANS:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    if "birthInput" not in data:
        data["birthInput"] = {}
    changed = False
    for k, v in TRANS[lang].items():
        if k not in data["birthInput"]:
            data["birthInput"][k] = v
            changed = True
    if changed:
        if APPLY:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
            print(f"🎉 {f}")
        else:
            print(f"🧪 {f} (예정)")

# ============ 3) 네비게이션 헤더 하드코딩 탐색 ============
print("\n🔎 '출생 정보 입력' 하드코딩 탐색 (네비게이션 헤더)...")
header_hits = []
for p in Path("frontend/app").rglob("*.tsx"):
    try:
        t = p.read_text(encoding="utf-8")
    except Exception:
        continue
    if "출생 정보 입력" in t:
        header_hits.append(p)
        print(f"  📂 {p}")
        for i, line in enumerate(t.splitlines(), 1):
            if "출생 정보 입력" in line:
                print(f"     L{i}: {line.strip()}")

if not header_hits:
    print("  ✅ 하드코딩 없음 (이미 i18n 처리? 또는 다른 곳)")

# ============ 결과 ============
if txt != orig and APPLY:
    BIRTH.write_text(txt, encoding="utf-8")
    print(f"\n🎉 {BIRTH} 저장 완료")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/fix_birth_input_i18n.py --apply")