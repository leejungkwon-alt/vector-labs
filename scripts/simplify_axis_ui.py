# scripts/simplify_axis_ui.py
"""
1) 5개 언어 JSON: 축 제목(axisElements 등)을 일상어로 교체
2) 프론트엔드: 본문 텍스트가 너무 길면 3줄까지만 보여주고 '더보기' 없이 말줄임표 처리 (선택)
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ==========================================
# 1) JSON: 축 제목 변경
# ==========================================
TITLE_MAP = {
    "ko": {
        "axisElements": "자연스러운 흐름",
        "axisDayMaster": "타고난 성정",
        "axisTenGods": "관계의 방식",
        "axisSinsal": "두 사람의 인연",
    },
    "en": {
        "axisElements": "Natural Flow",
        "axisDayMaster": "Innate Natures",
        "axisTenGods": "Relating Style",
        "axisSinsal": "Your Connection",
    },
    "ja": {
        "axisElements": "自然な流れ",
        "axisDayMaster": "生まれ持った気質",
        "axisTenGods": "関係のパターン",
        "axisSinsal": "二人の縁",
    },
    "zh_cn": {
        "axisElements": "自然流动",
        "axisDayMaster": "先天气质",
        "axisTenGods": "相处方式",
        "axisSinsal": "两人的缘分",
    },
    "es": {
        "axisElements": "Flujo natural",
        "axisDayMaster": "Naturalezas",
        "axisTenGods": "Estilo de relación",
        "axisSinsal": "Su conexión",
    },
}

def lang_key(p: Path) -> str:
    raw = p.parent.name.lower()
    return "zh_cn" if raw.startswith("zh") else raw

print("=" * 50)
print("1) 프론트엔드 JSON: 축 제목 일상어로 교체")
print("=" * 50)
for f in Path("frontend/src/locales").glob("*.json"):
    lang = lang_key(f)
    if lang not in TITLE_MAP:
        continue
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    
    compat = data.get("compatibility", {})
    if not isinstance(compat, dict):
        continue
    
    changed = False
    for key, new_title in TITLE_MAP[lang].items():
        if compat.get(key) != new_title:
            compat[key] = new_title
            changed = True
            print(f"  ✅ {lang} · {key} → \"{new_title}\"")
            
    if changed and APPLY:
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

# ==========================================
# 2) 프론트엔드: 긴 본문 3줄까지만 표시 (UI 다듬기)
# ==========================================
print("\n" + "=" * 50)
print("2) 프론트엔드: 축 카드 본문 4줄 제한 (시각적 피로 감소)")
print("=" * 50)
TSX = Path("frontend/app/(tabs)/compatibility.tsx")
if TSX.exists():
    txt = TSX.read_text(encoding="utf-8")
    # 축 카드의 <Text>{axis.body}</Text> 부분을 찾아 numberOfLines={4} 추가
    old_body = '<Text style={{ fontSize: 14, color: colors.textMuted, lineHeight: 20 }}>{axis.body}</Text>'
    new_body = '<Text style={{ fontSize: 14, color: colors.textMuted, lineHeight: 20 }} numberOfLines={4}>{axis.body}</Text>'
    
    if old_body in txt:
        txt = txt.replace(old_body, new_body, 1)
        print("  ✅ 본문 numberOfLines={4} 적용 (4줄 초과 시 말줄임표)")
        if APPLY:
            TSX.write_text(txt, encoding="utf-8")
    elif 'numberOfLines={4}' in txt:
        print("  ℹ️ 이미 적용됨")
    else:
        print("  ⚠️ 본문 렌더링 패턴 불일치 — 수동 확인 필요")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/simplify_axis_ui.py --apply")
else:
    print("🎉 패치 완료. 다음:")
    print("   git add frontend/")
    print('   git commit -m "fix(compat): simplify axis titles and limit body lines"')
    print("   git push origin main")