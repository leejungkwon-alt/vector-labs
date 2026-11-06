# scripts/add_axis_signatures.py
"""
4축 카드에 짧은 시그니처 문장 추가 (body 앞에 prepend).
- 전문 용어 없음 (오행·십신 등 한자 X)
- 일상어, 문학적 톤 유지
- 5개 언어
- 기존 body는 손대지 않음
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# 축별 시그니처 (관계 유형 무관, 한 언어당 축별 1개)
SIGNATURES = {
    "ko": {
        "ELEMENT_CONTENT":   "자연스러운 흐름에서 보면,",
        "DAY_MASTER_CONTENT":"타고난 성정에서 보면,",
        "TEN_GODS_CONTENT":  "관계의 방식에서 보면,",
        "SINSAL_CONTENT":    "두 사람의 인연에서 보면,",
    },
    "en": {
        "ELEMENT_CONTENT":   "In your shared flow,",
        "DAY_MASTER_CONTENT":"In your innate natures,",
        "TEN_GODS_CONTENT":  "In how you relate,",
        "SINSAL_CONTENT":    "In the thread between you,",
    },
    "ja": {
        "ELEMENT_CONTENT":   "自然な流れで見ると、",
        "DAY_MASTER_CONTENT":"生まれ持った気質で見ると、",
        "TEN_GODS_CONTENT":  "関係のパターンで見ると、",
        "SINSAL_CONTENT":    "二人の縁で見ると、",
    },
    "zh_cn": {
        "ELEMENT_CONTENT":   "从自然的流动来看，",
        "DAY_MASTER_CONTENT":"从先天气质来看，",
        "TEN_GODS_CONTENT":  "从相处方式来看，",
        "SINSAL_CONTENT":    "从两人的缘分来看，",
    },
    "es": {
        "ELEMENT_CONTENT":   "En su flujo natural,",
        "DAY_MASTER_CONTENT":"En sus naturalezas innatas,",
        "TEN_GODS_CONTENT":  "En cómo se relacionan,",
        "SINSAL_CONTENT":    "En el hilo entre ustedes,",
    },
}

def lang_key(p: Path) -> str:
    raw = p.parent.name.lower()
    return "zh_cn" if raw.startswith("zh") else raw

# ========== 1. JSON 패치 ==========
print("=" * 55)
print("1) JSON: 4축 콘텐츠 루트에 __signature__ 추가")
print("=" * 55)

for f in Path("app/services/content/data").rglob("compatibility.json"):
    lang = lang_key(f)
    if lang not in SIGNATURES:
        print(f"⚠️ {f}: lang '{lang}' 인식 실패")
        continue
    
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    
    changed = False
    for content_key, sig_text in SIGNATURES[lang].items():
        content = data.get(content_key)
        if not isinstance(content, dict):
            print(f"  ⚠️ {lang}: '{content_key}' 없음")
            continue
        if "__signature__" not in content:
            content["__signature__"] = sig_text
            changed = True
            print(f"  ✅ {lang} · {content_key}: \"{sig_text}\"")
        else:
            print(f"  ℹ️ {lang} · {content_key}: 이미 있음")
    
    if changed and APPLY:
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

# ========== 2. writer.py 패치 ==========
print("\n" + "=" * 55)
print("2) writer.py: _write_axis 에 시그니처 prepend")
print("=" * 55)

WRITER = Path("app/services/compatibility_writer.py")
if not WRITER.exists():
    print(f"❌ {WRITER} 없음")
    sys.exit(1)

txt = WRITER.read_text(encoding="utf-8")
orig = txt

# _write_axis 함수 내 body 처리 부분 교체
old_body = '''    content = rel_map.get(tag) or rel_map.get("DEFAULT", {})
    
    out = {
        "score": axis_data["score"],
        "grade": axis_data["grade"],
        "tag": tag,
        "headline": content.get("headline", ""),
        "body": content.get("body", ""),
    }'''

new_body = '''    content = rel_map.get(tag) or rel_map.get("DEFAULT", {})
    signature = content_map.get("__signature__", "")
    
    body = content.get("body", "")
    if signature and body:
        body = f"{signature} {body}"
    
    out = {
        "score": axis_data["score"],
        "grade": axis_data["grade"],
        "tag": tag,
        "headline": content.get("headline", ""),
        "body": body,
    }'''

if old_body in txt:
    txt = txt.replace(old_body, new_body, 1)
    print("  ✅ _write_axis: 시그니처 prepend 로직 추가")
elif 'signature = content_map.get("__signature__"' in txt:
    print("  ℹ️ 이미 패치됨")
else:
    print("  ❌ 패턴 불일치 — writer.py 수동 확인 필요")
    sys.exit(1)

if APPLY:
    WRITER.write_text(txt, encoding="utf-8")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/add_axis_signatures.py --apply")
else:
    print("🎉 패치 완료. 다음:")
    print("   .\\deploy.ps1")