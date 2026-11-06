# scripts/fix_age_icon.py
"""
5개 언어 JSON에서 🔞 이모지를 🚫 로 교체합니다.
"""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
NEW_ICON = "🚫"  # 원하시면 ⚠️, 👦, 🔒 등으로 변경 가능

def lang_key(p):
    s = p.stem.lower()
    return ("zh" if s.startswith("zh") else "ja" if s.startswith("ja") else
            "es" if s.startswith("es") else "ko" if s.startswith("ko") else
            "en" if s.startswith("en") else None)

print("=" * 50)
print(f"🔞 → {NEW_ICON} 로 교체")
print("=" * 50)

for f in Path("frontend/src/locales").glob("*.json"):
    lang = lang_key(f)
    if not lang:
        continue
    
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    
    compat = data.get("compatibility", {})
    if not isinstance(compat, dict):
        continue
    
    changed = False
    old_title = compat.get("ageLimitTitle", "")
    if "🔞" in old_title:
        compat["ageLimitTitle"] = old_title.replace("🔞", NEW_ICON).strip()
        changed = True
        print(f"  ✅ {f.name}: {compat['ageLimitTitle']}")
    
    if changed and APPLY:
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

print()
if not APPLY:
    print(f"🧪 미리보기. 적용: python scripts/fix_age_icon.py --apply")
else:
    print("🎉 패치 완료. 다음:")
    print("   git add frontend/")
    print('   git commit -m "fix(i18n): replace 18+ icon with forbidden icon"')
    print("   git push origin main")