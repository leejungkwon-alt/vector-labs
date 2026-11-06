# scripts/force_age_limit_json.py
"""5개 언어 JSON에 ageLimit 키를 강제로 주입합니다."""
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

TRANS = {
    "ko": {
        "ageLimitTitle": "🔞 만 14세 미만은 이용할 수 없습니다",
        "ageLimitDesc": "Gyeol은 만 14세 이상만 이용 가능한 서비스입니다.\n상대방의 생년월일을 다시 확인해 주세요.",
        "ageLimitRetry": "다시 입력하기",
    },
    "en": {
        "ageLimitTitle": "🔞 Users under 14 cannot use this service",
        "ageLimitDesc": "Gyeol is available only to users aged 14 and over.\nPlease check the birthdate again.",
        "ageLimitRetry": "Try again",
    },
    "ja": {
        "ageLimitTitle": "🔞 14歳未満の方はご利用いただけません",
        "ageLimitDesc": "Gyeolは14歳以上の方のみご利用いただけます。\nお相手の生年月日をご確認ください。",
        "ageLimitRetry": "再入力する",
    },
    "zh": {
        "ageLimitTitle": "🔞 14岁以下用户无法使用此服务",
        "ageLimitDesc": "Gyeol仅限14岁及以上用户使用。\n请重新确认对方的出生日期。",
        "ageLimitRetry": "重新输入",
    },
    "es": {
        "ageLimitTitle": "🔞 Los menores de 14 años no pueden usar este servicio",
        "ageLimitDesc": "Gyeol solo está disponible para usuarios de 14 años o más.\nVerifique la fecha de nacimiento nuevamente.",
        "ageLimitRetry": "Intentar de nuevo",
    },
}

def lang_key(p):
    s = p.stem.lower()
    return ("zh" if s.startswith("zh") else "ja" if s.startswith("ja") else
            "es" if s.startswith("es") else "ko" if s.startswith("ko") else
            "en" if s.startswith("en") else None)

print("=" * 50)
print("5개 언어 JSON에 ageLimit 키 강제 주입")
print("=" * 50)

for f in Path("frontend/src/locales").glob("*.json"):
    lang = lang_key(f)
    if lang not in TRANS:
        continue
    
    with open(f, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    
    if "compatibility" not in data:
        data["compatibility"] = {}
        
    changed = False
    for k, v in TRANS[lang].items():
        if data["compatibility"].get(k) != v:
            data["compatibility"][k] = v
            changed = True
            
    if changed:
        print(f"  ✅ {f.name}: ageLimit 3개 키 추가/업데이트")
        if APPLY:
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
    else:
        print(f"  ℹ️ {f.name}: 이미 존재함")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/force_age_limit_json.py --apply")
else:
    print("🎉 패치 완료. 다음:")
    print("   git add frontend/")
    print('   git commit -m "fix(i18n): force add ageLimit keys"')
    print("   git push origin main   ← 반드시 실행!")