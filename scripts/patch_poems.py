# scripts/patch_poems.py
"""
data/poems.json (25개 시조 × 5개 언어) interpretation 필드의
전문용어(한자 오행, 월건, 기릅니다 등)를 일상어로 치환.
- sijo_ko, commentary, practice는 그대로 유지 (문학성/시적 표현 보존)
- interpretation만 대상
"""
import json
import re
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
POEMS_PATH = Path("data/poems.json")

if not POEMS_PATH.exists():
    print(f"❌ {POEMS_PATH} 없음")
    sys.exit(1)

with open(POEMS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# ═══════════════════════════════════════════════════════
# 치환 사전
# ═══════════════════════════════════════════════════════
REPLACEMENTS = {
    "ko": [
        # 괄호형 먼저
        (r"수\(水\)", "유연함"),
        (r"목\(木\)", "성장"),
        (r"화\(火\)", "열정"),
        (r"토\(土\)", "안정"),
        (r"금\(金\)", "결단"),
        # 맨 한자 (한국어는 컴파운드 없음)
        (r"水", "유연함"),
        (r"木", "성장"),
        (r"火", "열정"),
        (r"土", "안정"),
        (r"金", "결단"),
        # 전문용어
        (r"월건의", "이번 달의"),
        (r"월건", "이번 달"),
        (r"일간", "본질"),
        (r"용신", "필요한 기운"),
        # 동사
        (r"기릅니다", "북돋웁니다"),
        (r"극합니다", "억누릅니다"),
        (r"공명합니다", "어우러집니다"),
        (r"상생", "서로 도움"),
        (r"상극", "부딪힘"),
    ],
    "en": [
        (r"\bWood\b", "growth"),
        (r"\bFire\b", "passion"),
        (r"\bEarth\b", "stability"),
        (r"\bMetal\b", "clarity"),
        (r"\bWater\b", "flexibility"),
        (r"month pillar", "this month's energy"),
        (r"resonates with", "harmonizes with"),
        (r"nourishes", "supports"),
        (r"challenges", "restrains"),
    ],
    "ja": [
        # 일본어는 어절 경계 없어서 구체적 phrase만
        (r"月建の木", "今月の成長"),
        (r"月建の火", "今月の情熱"),
        (r"月建の土", "今月の安定"),
        (r"月建の金", "今月の決断"),
        (r"月建の水", "今月の柔軟性"),
        (r"あなたの木", "あなたの成長"),
        (r"あなたの火", "あなたの情熱"),
        (r"あなたの土", "あなたの安定"),
        (r"あなたの金", "あなたの決断"),
        (r"あなたの水", "あなたの柔軟性"),
        (r"月建", "今月"),
        (r"共鳴", "調和"),
        (r"生み出", "引き出"),
    ],
    "zh_cn": [
        (r"月建之木", "本月的成长"),
        (r"月建之火", "本月的热情"),
        (r"月建之土", "本月的稳定"),
        (r"月建之金", "本月的决断"),
        (r"月建之水", "本月的柔韧"),
        (r"你的木", "你的成长"),
        (r"你的火", "你的热情"),
        (r"你的土", "你的稳定"),
        (r"你的金", "你的决断"),
        (r"你的水", "你的柔韧"),
        (r"月建", "本月"),
        (r"共鸣", "和谐"),
    ],
    "es": [
        (r"\bMadera\b", "crecimiento"),
        (r"\bFuego\b", "pasión"),
        (r"\bTierra\b", "estabilidad"),
        (r"\bMetal\b", "claridad"),
        (r"\bAgua\b", "flexibilidad"),
        (r"resuena con", "armoniza con"),
    ],
}

def apply_repl(text, pairs):
    result = text
    for pat, repl in pairs:
        result = re.sub(pat, repl, result)
    return result

# ═══════════════════════════════════════════════════════
# 변경 수집 + 미리보기
# ═══════════════════════════════════════════════════════
poems = data.get("poems", [])
print(f"📖 {POEMS_PATH}  ({len(poems)}개 시조)\n")

changes = []
for p in poems:
    pid = p.get("id", "?")
    tr = p.get("translations", {})
    for lang, pairs in REPLACEMENTS.items():
        if lang not in tr:
            continue
        old = tr[lang].get("interpretation", "")
        if not old:
            continue
        new = apply_repl(old, pairs)
        if old != new:
            changes.append((pid, lang, old, new))

print(f"🔄 총 변경 예정: {len(changes)}건\n")
print("=" * 60)
print("📋 샘플 (처음 8건)")
print("=" * 60)
for pid, lang, old, new in changes[:8]:
    print(f"\n[{pid}] [{lang}]")
    print(f"  ❌ OLD: {old[:200]}")
    print(f"  ✅ NEW: {new[:200]}")

if not APPLY:
    print(f"\n🧪 미리보기 모드. 실제 적용: python scripts/patch_poems.py --apply")
    sys.exit(0)

# ═══════════════════════════════════════════════════════
# 적용
# ═══════════════════════════════════════════════════════
for p in poems:
    tr = p.get("translations", {})
    for lang, pairs in REPLACEMENTS.items():
        if lang not in tr:
            continue
        tr[lang]["interpretation"] = apply_repl(tr[lang].get("interpretation", ""), pairs)

with open(POEMS_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n🎉 저장 완료: {POEMS_PATH}")
print("   다음: .\\deploy.ps1")