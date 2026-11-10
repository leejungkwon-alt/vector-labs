# scripts/grade_based_practices.py
"""
PRACTICES를 grade 심각도별로 분기 (KO + EN)
- CHALLENGING → danger (생존/자기 보호)
- CAUTION     → warning (예방적, 작은 조정)
- NEUTRAL     → neutral (유지/꾸준함)
- FAVORABLE/PEAK → positive (확장/활용)
"""
import ast
import json
import shutil
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
BASE = Path("app/services/content/data")

KO_PRACTICES = {
    "same": {
        "danger": "지금 하는 방식을 유지하되, 한 가지만 일부러 바꿔보세요.",
        "warning": "한 분기에 한 번은 새로운 시도를 넣어보세요.",
        "neutral": "매년 한 가지, 새로운 방식을 시도해보세요.",
        "positive": "지금의 리듬을 즐기면서, 그 강점을 더 확장해보세요.",
    },
    "generates_me": {
        "danger": "받은 것을 반드시 흘려보내세요. 안 그러면 무뎌져요.",
        "warning": "받은 것에 감사 표시를 해보세요. 말이든 행동이든.",
        "neutral": "받은 것들을 기록하고, 감사로 돌려주세요.",
        "positive": "받은 기운을 크게 활용해보세요. 지금이 확장 타이밍이에요.",
    },
    "i_generate": {
        "danger": "자신을 먼저 채우세요. 지금은 베풀 때가 아니라 채울 때예요.",
        "warning": "주는 것과 받는 것의 균형을 한 번 점검해보세요.",
        "neutral": "매주 하루는 온전히 자신을 위해 비워두세요.",
        "positive": "마음껏 나누세요. 베풀수록 더 채워지는 시기예요.",
    },
    "i_control": {
        "danger": "통제를 내려놓는 연습을 해보세요. 하루에 하나씩.",
        "warning": "힘을 빼는 연습이 필요해요. 다스리려 하지 말고 다뤄보세요.",
        "neutral": "결정 전에 '이걸 꼭 통제해야 하나?' 물어보세요.",
        "positive": "지금의 감각을 유지하세요. 이 페이스가 좋아요.",
    },
    "controls_me": {
        "danger": "자신의 페이스를 지키세요. 남의 속도와 비교하지 마세요.",
        "warning": "저항을 줄이고, 흐름에 맡겨보세요.",
        "neutral": "매년 한 가지, 10년 후에도 남을 기술을 쌓으세요.",
        "positive": "약간의 압박을 연료로 활용해보세요. 성장의 원동력이에요.",
    },
}

EN_PRACTICES = {
    "same": {
        "danger": "Keep the current way — but change one thing on purpose.",
        "warning": "Try one new thing per quarter.",
        "neutral": "Try one new approach each year.",
        "positive": "Enjoy the rhythm and stretch that strength further.",
    },
    "generates_me": {
        "danger": "Pass it on. If you don't, you'll go numb.",
        "warning": "Show gratitude for what you receive — words or actions.",
        "neutral": "Journal what you receive. Return it as gratitude.",
        "positive": "Use this support well. This is your expansion window.",
    },
    "i_generate": {
        "danger": "Fill yourself first. This isn't the giving season — it's refill time.",
        "warning": "Check the balance of giving and receiving once.",
        "neutral": "Keep one full day a week just for you.",
        "positive": "Give freely. The more you give, the more you fill.",
    },
    "i_control": {
        "danger": "Practice letting go — one thing a day.",
        "warning": "Loosen your grip. Handle it, don't control it.",
        "neutral": "Before deciding, ask: 'Do I really need to control this?'",
        "positive": "Keep this feel. You're in a good groove.",
    },
    "controls_me": {
        "danger": "Protect your pace. Don't race against others' speed.",
        "warning": "Reduce resistance. Let the current carry you.",
        "neutral": "Build one skill a year that lasts the next decade.",
        "positive": "Turn the pressure into fuel. It's your growth engine.",
    },
}

# ═══════════════════════════════════════════════════════════
# 1. JSON 갱신
# ═══════════════════════════════════════════════════════════
for lang, practices in [("ko", KO_PRACTICES), ("en", EN_PRACTICES)]:
    path = BASE / lang / "timeline_themes.json"
    if not path.exists():
        print(f"❌ {path} 없음")
        sys.exit(1)
    data = json.load(path.open(encoding="utf-8"))
    data["PRACTICES"] = practices
    if APPLY:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ {lang}: PRACTICES grade별 4단계 재작성")

# ja/zh/es EN 복사
for lang in ["ja", "zh_cn", "es"]:
    src = BASE / "en" / "timeline_themes.json"
    dst = BASE / lang / "timeline_themes.json"
    if APPLY:
        shutil.copy(src, dst)
        print(f"✅ {lang}: EN 복사")

# ═══════════════════════════════════════════════════════════
# 2. content_writer.py: practice에도 severity 매핑
# ═══════════════════════════════════════════════════════════
CW = Path("app/services/content_writer.py")
txt = CW.read_text(encoding="utf-8")

OLD = '''    # cautions[rel]이 dict(severity별) 또는 str(하위 호환)
    rel_caution = cautions.get(rel, "")
    if isinstance(rel_caution, dict):
        caution_text = rel_caution.get(severity, rel_caution.get("neutral", ""))
    else:
        caution_text = rel_caution

    return {
        "theme": t.get("theme", ""),
        "body": t.get("body", ""),
        "caution": caution_text,
        "practice": practices.get(rel, ""),
    }'''

NEW = '''    # cautions/practices[rel]이 dict(severity별) 또는 str(하위 호환)
    rel_caution = cautions.get(rel, "")
    if isinstance(rel_caution, dict):
        caution_text = rel_caution.get(severity, rel_caution.get("neutral", ""))
    else:
        caution_text = rel_caution

    rel_practice = practices.get(rel, "")
    if isinstance(rel_practice, dict):
        practice_text = rel_practice.get(severity, rel_practice.get("neutral", ""))
    else:
        practice_text = rel_practice

    return {
        "theme": t.get("theme", ""),
        "body": t.get("body", ""),
        "caution": caution_text,
        "practice": practice_text,
    }'''

if OLD not in txt:
    print("❌ caution/practice return 패턴 못 찾음")
    print("   다음 명령으로 확인:")
    print("   Get-Content 'app/services/content_writer.py' | Select-String 'practice' -Context 2,2")
    sys.exit(1)

txt = txt.replace(OLD, NEW, 1)
print("✅ grade → practice severity 매핑 로직 추가")

try:
    ast.parse(txt)
    print("✅ 문법 검증 통과")
except SyntaxError as e:
    print(f"❌ 문법 오류: {e.lineno}: {e.msg}")
    sys.exit(1)

if APPLY:
    CW.write_text(txt, encoding="utf-8")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/grade_based_practices.py --apply")
else:
    print("🎉 완료. 다음:")
    print("   .\\deploy.ps1")