# scripts/kill_repetition.py
"""
1) theme variant: index%3 → (index + index//3) % 3 (충돌 해소)
2) caution/practice: severity × 2-variant (인접 대운 다른 문구)
"""
import ast
import json
import shutil
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv
BASE = Path("app/services/content/data")

# ═══════════════════════════════════════════════════════════
# KO CAUTIONS: severity × 2 variant
# ═══════════════════════════════════════════════════════════
KO_CAUTIONS = {
    "same": {
        "danger": [
            "같은 방향이라 지루해지기 쉬워요. 의식적으로 새로운 자극을 만들어보세요.",
            "정체될 수 있어요. 일부러라도 새로운 시도를 넣으세요.",
        ],
        "warning": [
            "매너리즘이 올 수 있어요. 한 가지씩 새로 시도해보세요.",
            "지루함이 스며들 수 있어요. 의식적으로 자극을 만들어보세요.",
        ],
        "neutral": [
            "흐름을 유지하되, 작은 변화를 준비해두세요.",
            "지금 페이스는 좋아요. 다만 매너리즘을 조심하세요.",
        ],
        "positive": [
            "지금의 결을 즐기세요. 같은 방향의 힘이 서로를 밀어줍니다.",
            "이 흐름을 만끽하세요. 비슷한 에너지가 서로를 강화해요.",
        ],
    },
    "generates_me": {
        "danger": [
            "받기만 하면 무뎌져요. 받은 만큼 꼭 돌려주세요.",
            "일방적으로 받기만 하면 병이 돼요. 반드시 흘려보내세요.",
        ],
        "warning": [
            "채워지는 만큼, 흘려보내는 것도 잊지 마세요.",
            "받기만 하면 무뎌져요. 주는 연습도 필요해요.",
        ],
        "neutral": [
            "받는 것에 감사하고, 적당히 흘려보내세요.",
            "받은 만큼 흘려보내는 균형을 잡으세요.",
        ],
        "positive": [
            "받은 기운을 잘 활용하면 큰 도약이 됩니다.",
            "이 지원을 최대한 누리세요. 지금이 도약 타이밍이에요.",
        ],
    },
    "i_generate": {
        "danger": [
            "베풀다 지칠 수 있어요. 자신을 먼저 채우세요.",
            "주기만 하다간 텅 비어요. 자신을 먼저 돌보세요.",
        ],
        "warning": [
            "주는 것과 받는 것의 균형을 확인하세요.",
            "베풀되, 자신을 잃지 마세요.",
        ],
        "neutral": [
            "베풀되, 무리하지 마세요.",
            "적당히 나누는 게 오래 갑니다.",
        ],
        "positive": [
            "베풀수록 채워지는 시기예요. 마음껏 나누세요.",
            "지금의 넉넉함을 나눠보세요. 더 커집니다.",
        ],
    },
    "i_control": {
        "danger": [
            "통제하려는 마음이 강해지면 관계가 상해요. 놓아줄 건 놓아주세요.",
            "붙잡을수록 흘러가요. 지금은 힘을 빼야 할 때예요.",
        ],
        "warning": [
            "다루되, 다스리려 하지 마세요. 힘을 빼는 연습이 필요해요.",
            "통제욕이 올라올 수 있어요. 한 박자 쉬어가세요.",
        ],
        "neutral": [
            "적당히 다루면서 균형을 잡으세요.",
            "지금 페이스는 괜찮아요. 유연함을 잃지 마세요.",
        ],
        "positive": [
            "다루는 감각이 좋아요. 지금 페이스를 유지하세요.",
            "지금의 조율이 딱 맞아요. 이 감각을 기억하세요.",
        ],
    },
    "controls_me": {
        "danger": [
            "압박이 클수록 조급해져요. 남의 속도와 비교하지 마세요.",
            "지금은 저항할 때가 아니에요. 흐름에 몸을 맡기세요.",
        ],
        "warning": [
            "지금은 저항보다 흐름에 맡기는 게 나아요.",
            "버티기보다 받아들이는 게 지금의 지혜예요.",
        ],
        "neutral": [
            "압박을 인정하고, 자신의 페이스를 지키세요.",
            "흐름에 맡기되, 중심을 잃지 마세요.",
        ],
        "positive": [
            "약간의 압박은 오히려 성장의 원동력이에요.",
            "이 압박을 연료로 쓰면 큰 도약이 됩니다.",
        ],
    },
}

EN_CAUTIONS = {
    "same": {
        "danger": [
            "Same direction gets dull fast. Build in new stimulation on purpose.",
            "You could stall. Add something new on purpose.",
        ],
        "warning": [
            "Complacency is coming. Try one new thing at a time.",
            "Boredom creeps in. Make small changes.",
        ],
        "neutral": [
            "Keep the flow, but prep a small change.",
            "Your pace is good. Just watch for routine.",
        ],
        "positive": [
            "Enjoy this grain. Same-direction forces push each other.",
            "Soak it in. Similar energy strengthens you.",
        ],
    },
    "generates_me": {
        "danger": [
            "Only receiving makes you numb. Give back what you get.",
            "One-way receiving sours. Pass it on.",
        ],
        "warning": [
            "As you fill up, don't forget to pass it on.",
            "Receiving only dulls you. Practice giving.",
        ],
        "neutral": [
            "Be grateful, and let it flow.",
            "Balance receiving with giving.",
        ],
        "positive": [
            "Use this support well — it becomes a big leap.",
            "Make the most of this lift. It's a launch window.",
        ],
    },
    "i_generate": {
        "danger": [
            "Giving drains you. Fill yourself first.",
            "Give-only empties you. Care for yourself first.",
        ],
        "warning": [
            "Check the balance of giving and receiving.",
            "Give — but don't lose yourself.",
        ],
        "neutral": [
            "Give — but not past your limit.",
            "Share moderately. It lasts longer.",
        ],
        "positive": [
            "The more you give, the more you're filled. Share freely.",
            "Share your abundance. It grows.",
        ],
    },
    "i_control": {
        "danger": [
            "Holding too tight hurts the bond. Let go of what you can't hold.",
            "Grip too hard and it slips. Time to loosen.",
        ],
        "warning": [
            "Handle it — don't control it. Practice loosening your grip.",
            "Control impulse rises. Pause a beat.",
        ],
        "neutral": [
            "Manage it gently, and find balance.",
            "Your pace is fine. Keep flexibility.",
        ],
        "positive": [
            "Your handling is good right now. Keep this pace.",
            "This tuning is spot on. Remember this feel.",
        ],
    },
    "controls_me": {
        "danger": [
            "Pressure feeds urgency. Don't race against others' pace.",
            "Not the time to push back. Let the current carry you.",
        ],
        "warning": [
            "Don't resist now — let the current carry you.",
            "Acceptance works better than resistance here.",
        ],
        "neutral": [
            "Acknowledge the pressure, keep your pace.",
            "Let it flow — but don't lose center.",
        ],
        "positive": [
            "A bit of pressure is fuel for growth.",
            "Use this pressure as fuel. Big leaps come from it.",
        ],
    },
}

KO_PRACTICES = {
    "same": {
        "danger": [
            "지금 하는 방식을 유지하되, 한 가지만 일부러 바꿔보세요.",
            "작은 변화부터 시작하세요. 하루에 한 가지.",
        ],
        "warning": [
            "한 분기에 한 번은 새로운 시도를 넣어보세요.",
            "월 1회, 평소와 다른 선택을 해보세요.",
        ],
        "neutral": [
            "매년 한 가지, 새로운 방식을 시도해보세요.",
            "분기마다 한 번씩 새로운 자극을 넣으세요.",
        ],
        "positive": [
            "지금의 리듬을 즐기면서, 그 강점을 더 확장해보세요.",
            "이 흐름을 다음 단계로 끌어올려 보세요.",
        ],
    },
    "generates_me": {
        "danger": [
            "받은 것을 반드시 흘려보내세요. 안 그러면 무뎌져요.",
            "받은 것을 기록하고, 반드시 돌려주세요.",
        ],
        "warning": [
            "받은 것에 감사 표시를 해보세요. 말이든 행동이든.",
            "받은 만큼 작게라도 나눠보세요.",
        ],
        "neutral": [
            "받은 것들을 기록하고, 감사로 돌려주세요.",
            "받은 기운을 일상에서 작게 나눠보세요.",
        ],
        "positive": [
            "받은 기운을 크게 활용해보세요. 지금이 확장 타이밍이에요.",
            "이 지원을 큰 그림에 써보세요. 도약의 씨앗이에요.",
        ],
    },
    "i_generate": {
        "danger": [
            "자신을 먼저 채우세요. 지금은 베풀 때가 아니라 채울 때예요.",
            "일주일에 하루는 온전히 자신만을 위해 쓰세요.",
        ],
        "warning": [
            "주는 것과 받는 것의 균형을 한 번 점검해보세요.",
            "베풀기 전에, 먼저 자신의 그릇을 확인하세요.",
        ],
        "neutral": [
            "매주 하루는 온전히 자신을 위해 비워두세요.",
            "주는 만큼 채우는 시간도 확보하세요.",
        ],
        "positive": [
            "마음껏 나누세요. 베풀수록 더 채워지는 시기예요.",
            "지금의 넉넉함을 흘려보내세요. 선순환이 옵니다.",
        ],
    },
    "i_control": {
        "danger": [
            "통제를 내려놓는 연습을 해보세요. 하루에 하나씩.",
            "오늘 하루, 결정 하나를 그냥 흘려보내세요.",
        ],
        "warning": [
            "힘을 빼는 연습이 필요해요. 다스리려 하지 말고 다뤄보세요.",
            "결정 전에 '이걸 꼭 붙잡아야 하나?' 물어보세요.",
        ],
        "neutral": [
            "결정 전에 '이걸 꼭 통제해야 하나?' 물어보세요.",
            "하루에 한 번, 통제 충동을 관찰해보세요.",
        ],
        "positive": [
            "지금의 감각을 유지하세요. 이 페이스가 좋아요.",
            "지금의 조율을 기록해두세요. 다음에 활용하세요.",
        ],
    },
    "controls_me": {
        "danger": [
            "자신의 페이스를 지키세요. 남의 속도와 비교하지 마세요.",
            "매일 5분, 호흡에 집중하며 흐름을 느껴보세요.",
        ],
        "warning": [
            "저항을 줄이고, 흐름에 맡겨보세요.",
            "하루 한 번, 통제할 수 없는 것을 인정해보세요.",
        ],
        "neutral": [
            "매년 한 가지, 시간이 흘러도 남을 기술을 쌓으세요.",
            "매주 하루는 아무 계획 없이 보내보세요.",
        ],
        "positive": [
            "약간의 압박을 연료로 활용해보세요. 성장의 원동력이에요.",
            "이 압박을 다음 단계로 가는 발판으로 쓰세요.",
        ],
    },
}

EN_PRACTICES = {
    "same": {
        "danger": [
            "Keep the current way — but change one thing on purpose.",
            "Start small: one change a day.",
        ],
        "warning": [
            "Try one new thing per quarter.",
            "Once a month, choose differently.",
        ],
        "neutral": [
            "Try one new approach each year.",
            "Add new stimulus each quarter.",
        ],
        "positive": [
            "Enjoy the rhythm and stretch that strength further.",
            "Lift this flow to the next level.",
        ],
    },
    "generates_me": {
        "danger": [
            "Pass it on. If you don't, you'll go numb.",
            "Journal what you get — and return it.",
        ],
        "warning": [
            "Show gratitude for what you receive — words or actions.",
            "Share a little of what you've received.",
        ],
        "neutral": [
            "Journal what you receive. Return it as gratitude.",
            "Share your gains in small ways.",
        ],
        "positive": [
            "Use this support well. This is your expansion window.",
            "Apply this lift to a big goal. A seed for a leap.",
        ],
    },
    "i_generate": {
        "danger": [
            "Fill yourself first. This isn't the giving season — it's refill time.",
            "One day a week, fully for you.",
        ],
        "warning": [
            "Check the balance of giving and receiving once.",
            "Before giving, check your own cup.",
        ],
        "neutral": [
            "Keep one full day a week just for you.",
            "Protect time to refill as much as you give.",
        ],
        "positive": [
            "Give freely. The more you give, the more you fill.",
            "Pass on this abundance. It multiplies.",
        ],
    },
    "i_control": {
        "danger": [
            "Practice letting go — one thing a day.",
            "Today, let one decision flow.",
        ],
        "warning": [
            "Loosen your grip. Handle it, don't control it.",
            "Before deciding, ask: 'Do I really need to hold this?'",
        ],
        "neutral": [
            "Before deciding, ask: 'Do I really need to control this?'",
            "Once a day, notice the urge to control.",
        ],
        "positive": [
            "Keep this feel. You're in a good groove.",
            "Note this rhythm — reuse it later.",
        ],
    },
    "controls_me": {
        "danger": [
            "Protect your pace. Don't race against others' speed.",
            "5 minutes a day: breathe and follow the current.",
        ],
        "warning": [
            "Reduce resistance. Let the current carry you.",
            "Once a day, accept what you can't control.",
        ],
        "neutral": [
            "Build one skill a year that lasts the next decade.",
            "One day a week, go without plans.",
        ],
        "positive": [
            "Turn the pressure into fuel. It's your growth engine.",
            "Use this pressure as a step to the next level.",
        ],
    },
}

# ═══════════════════════════════════════════════════════════
# 1. JSON 저장
# ═══════════════════════════════════════════════════════════
print("=" * 55)
print("1) caution/practice severity × 2-variant 적용")
print("=" * 55)

for lang, cautions, practices in [("ko", KO_CAUTIONS, KO_PRACTICES), ("en", EN_CAUTIONS, EN_PRACTICES)]:
    path = BASE / lang / "timeline_themes.json"
    data = json.load(path.open(encoding="utf-8"))
    data["CAUTIONS"] = cautions
    data["PRACTICES"] = practices
    if APPLY:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✅ {lang}: CAUTIONS/PRACTICES 2-variant")

for lang in ["ja", "zh_cn", "es"]:
    src = BASE / "en" / "timeline_themes.json"
    dst = BASE / lang / "timeline_themes.json"
    if APPLY:
        shutil.copy(src, dst)
        print(f"  ✅ {lang}: EN 복사")

# ═══════════════════════════════════════════════════════════
# 2. content_writer.py 수정
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("2) content_writer.py 수정")
print("=" * 55)

CW = Path("app/services/content_writer.py")
txt = CW.read_text(encoding="utf-8")

# ── theme variant formula 변경 ──
OLD_THEME = '''    # 3-variant list면 index 기반 선택 (인접 대운 자동 다름)
    if isinstance(raw, list):
        idx = int(d.get("index", 0))
        t = raw[idx % len(raw)]'''

NEW_THEME = '''    # 3-variant list면 (index + index//3) % 3 (인접·5차이 모두 다름)
    if isinstance(raw, list):
        idx = int(d.get("index", 0))
        variant_idx = (idx + idx // 3) % len(raw)
        t = raw[variant_idx]'''

if OLD_THEME in txt:
    txt = txt.replace(OLD_THEME, NEW_THEME, 1)
    print("  ✅ theme variant: (index + index//3) % 3")
else:
    print("  ⚠️ theme variant 패턴 불일치 (수동 확인 필요)")

# ── caution/practice에 variant 적용 ──
OLD_CAUTION = '''    # cautions/practices[rel]이 dict(severity별) 또는 str(하위 호환)
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

NEW_CAUTION = '''    # cautions/practices[rel]이 dict(severity별) 또는 str(하위 호환)
    idx = int(d.get("index", 0))

    def _pick(container, rel, severity):
        rel_val = container.get(rel, "")
        if not isinstance(rel_val, dict):
            return rel_val
        sev_val = rel_val.get(severity, rel_val.get("neutral", ""))
        # severity 내부가 list면 index%len으로 선택
        if isinstance(sev_val, list) and sev_val:
            return sev_val[idx % len(sev_val)]
        return sev_val if isinstance(sev_val, str) else ""

    return {
        "theme": t.get("theme", ""),
        "body": t.get("body", ""),
        "caution": _pick(cautions, rel, severity),
        "practice": _pick(practices, rel, severity),
    }'''

if OLD_CAUTION in txt:
    txt = txt.replace(OLD_CAUTION, NEW_CAUTION, 1)
    print("  ✅ caution/practice: severity × variant 적용")
else:
    print("  ⚠️ caution/practice 패턴 불일치 (수동 확인 필요)")

try:
    ast.parse(txt)
    print("  ✅ 문법 검증 통과")
except SyntaxError as e:
    print(f"  ❌ 문법 오류: {e.lineno}: {e.msg}")
    sys.exit(1)

if APPLY:
    CW.write_text(txt, encoding="utf-8")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/kill_repetition.py --apply")
else:
    print("🎉 완료. 다음:")
    print("   .\\deploy.ps1")