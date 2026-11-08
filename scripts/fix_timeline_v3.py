# scripts/fix_timeline_v3.py
"""
1) KO "10년" → "시기" (테마명/본문)
2) EN "decade" → "season", "10 years" → "season"
3) ja/zh_cn/es: EN 복사 (fallback, 테스트 통과)
"""
import json
import shutil
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
BASE = Path("app/services/content/data")

# ═══════════════════════════════════════════════════════════
# 1. KO: "10년" → "시기" (문맥별 정밀 치환)
# ═══════════════════════════════════════════════════════════
KO_REPLACEMENTS = [
    # 가장 긴 것 먼저
    ("10년 내내", "이 시기 내내"),
    ("10년의", "이 시기의"),
    ("10년 동안", "이 시기 동안"),
    ("10년 후에도", "시간이 흘러도"),
    ("하는 10년", "하는 시기"),
    ("되는 10년", "되는 시기"),
    ("는 10년이에요", "는 시기예요"),
    ("하는 10년이에요", "하는 시기예요"),
    ("10년이에요", "시기예요"),
]

def ko_fix(text: str) -> str:
    for old, new in KO_REPLACEMENTS:
        text = text.replace(old, new)
    return text

ko_path = BASE / "ko" / "timeline_themes.json"
ko_data = json.load(ko_path.open(encoding="utf-8"))

ko_changes = 0
for rel, themes in ko_data.get("THEMES", {}).items():
    for elem, info in themes.items():
        for key in ("theme", "body"):
            old = info.get(key, "")
            new = ko_fix(old)
            if new != old:
                info[key] = new
                ko_changes += 1
print(f"✅ KO: {ko_changes}개 문장 수정")

if APPLY:
    ko_path.write_text(json.dumps(ko_data, ensure_ascii=False, indent=2), encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 2. EN: "decade" → "season", "10 years" → "season"
# ═══════════════════════════════════════════════════════════
EN_REPLACEMENTS = [
    ("A decade of", "A season of"),
    ("the whole 10 years", "the whole season"),
    ("for 10 years", "this season"),
    ("10 years", "season"),
]

def en_fix(text: str) -> str:
    for old, new in EN_REPLACEMENTS:
        text = text.replace(old, new)
    return text

en_path = BASE / "en" / "timeline_themes.json"
en_data = json.load(en_path.open(encoding="utf-8"))

en_changes = 0
for rel, themes in en_data.get("THEMES", {}).items():
    for elem, info in themes.items():
        for key in ("theme", "body"):
            old = info.get(key, "")
            new = en_fix(old)
            if new != old:
                info[key] = new
                en_changes += 1
print(f"✅ EN: {en_changes}개 문장 수정")

if APPLY:
    en_path.write_text(json.dumps(en_data, ensure_ascii=False, indent=2), encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 3. ja/zh_cn/es: EN 복사 (fallback)
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("3) ja/zh_cn/es: EN 복사 (fallback)")
print("=" * 55)

for lang in ["ja", "zh_cn", "es"]:
    target_dir = BASE / lang
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "timeline_themes.json"
    if APPLY:
        shutil.copy(en_path, target)
        print(f"  ✅ {lang}: {target}")
    else:
        print(f"  🧪 {lang}: 복사 예정")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/fix_timeline_v3.py --apply")
else:
    print("🎉 완료. 다음:")
    print("   .\\deploy.ps1")