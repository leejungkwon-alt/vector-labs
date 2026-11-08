# scripts/finalize_timeline_v2.py
"""
1) content_writer.py: _resolve_theme 수정 (branch 우선 → 반복 해소)
2) timeline_themes.json 재작성 (KO + EN, 자연스러운 현대어)
"""
import ast
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ═══════════════════════════════════════════════════════════
# 1. content_writer.py: branch 우선 매칭
# ═══════════════════════════════════════════════════════════
CW = Path("app/services/content_writer.py")
txt = CW.read_text(encoding="utf-8")

OLD = '''    rel = d.get("stem_relation") or d.get("branch_relation")
    elem = d.get("stem_element") or d.get("branch_element")'''

NEW = '''    # 지지(branch) 우선 → 인접 대운이 다른 theme 나옴
    rel = d.get("branch_relation") or d.get("stem_relation")
    elem = d.get("branch_element") or d.get("stem_element")'''

if OLD in txt:
    txt = txt.replace(OLD, NEW, 1)
    print("✅ content_writer.py: branch 우선 매칭")
elif "지지(branch) 우선" in txt:
    print("ℹ️ 이미 branch 우선")
else:
    print("❌ branch 우선 매칭 패턴 못 찾음")
    sys.exit(1)

# 디버그 print 제거
lines = txt.splitlines(keepends=True)
cleaned = [l for l in lines if "[DEBUG-THEME]" not in l]
if len(cleaned) != len(lines):
    txt = "".join(cleaned)
    print(f"✅ 디버그 print {len(lines) - len(cleaned)}줄 제거")

try:
    ast.parse(txt)
except SyntaxError as e:
    print(f"❌ 문법 오류: {e.lineno}: {e.msg}")
    sys.exit(1)

if APPLY:
    CW.write_text(txt, encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 2. 테마 콘텐츠 (KO + EN, 자연스러운 현대어)
# ═══════════════════════════════════════════════════════════
KO_THEMES = {
    "same": {
        "木": {"theme": "성장이 이어지는 10년", "body": "성장의 기운이 10년 내내 이어져요. 같은 방향이라 지루해질 수 있으니, 새로운 방식을 일부러 시도해보세요."},
        "火": {"theme": "열정이 계속 타오르는 10년", "body": "열정의 기운이 10년 내내 이어져요. 과열되지 않게 리듬을 조절하면서 가는 게 핵심이에요."},
        "土": {"theme": "중심이 더 단단해지는 10년", "body": "안정의 기운이 10년 내내 이어져요. 안주하지 않도록 작은 변화를 꾸준히 시도해보세요."},
        "金": {"theme": "판단이 선명해지는 10년", "body": "결단의 기운이 10년 내내 이어져요. 너무 예리해지면 주변과 부딪힐 수 있으니 부드러움도 챙기세요."},
        "水": {"theme": "유연함이 깊어지는 10년", "body": "유연함의 기운이 10년 내내 이어져요. 흐름을 타다 보면 중심을 잃을 수 있으니 가끔은 멈춰 점검하세요."},
    },
    "generates_me": {
        "木": {"theme": "성장이 나를 밀어주는 10년", "body": "성장의 기운이 당신을 밀어주는 10년이에요. 받는 게 많으니 받은 만큼 흘려보내는 연습도 필요해요."},
        "火": {"theme": "열정이 나를 데워주는 10년", "body": "열정의 기운이 당신을 데워주는 10년이에요. 따뜻한 흐름 속에서 마음껏 펼쳐보세요."},
        "土": {"theme": "안정이 나를 받쳐주는 10년", "body": "안정의 기운이 당신을 받쳐주는 10년이에요. 든든한 기반 위에서 마음 놓고 도전해보세요."},
        "金": {"theme": "결단이 나를 다듬어주는 10년", "body": "결단의 기운이 당신을 다듬어주는 10년이에요. 흐릿하던 것들이 서서히 또렷해져요."},
        "水": {"theme": "유연함이 나를 채워주는 10년", "body": "유연함의 기운이 당신을 채워주는 10년이에요. 조용히 도움의 손길이 들어오는 시기예요."},
    },
    "i_generate": {
        "木": {"theme": "내가 성장을 만드는 10년", "body": "당신이 뭔가를 자라게 하는 10년이에요. 베풀수록 더 채워지는 시기예요."},
        "火": {"theme": "내가 열정을 피우는 10년", "body": "당신이 열정을 만들어내는 10년이에요. 창작이나 표현 활동에서 특히 빛을 발해요."},
        "土": {"theme": "내가 안정을 만드는 10년", "body": "당신이 기반을 다지는 10년이에요. 하나씩 결과물이 쌓여가는 시기예요."},
        "金": {"theme": "내가 결단을 만드는 10년", "body": "당신이 방향을 정해가는 10년이에요. 단단한 결과물이 나오기 시작해요."},
        "水": {"theme": "내가 흐름을 트는 10년", "body": "당신이 새로운 길을 여는 10년이에요. 흐름을 만들면서 더 멀리 가는 시기예요."},
    },
    "i_control": {
        "木": {"theme": "내가 성장을 다루는 10년", "body": "성장의 기운이 강한 10년이에요. 당신이 이걸 정리하면서 자기 자리를 세워가요."},
        "火": {"theme": "내가 열정을 다루는 10년", "body": "열정의 기운이 강한 10년이에요. 당신이 이걸 식히면서 한 박자 쉬어가는 시기예요."},
        "土": {"theme": "내가 안정을 다루는 10년", "body": "안정의 기운이 강한 10년이에요. 당신이 이걸 정리하면서 흐름을 다스려요."},
        "金": {"theme": "내가 결단을 다루는 10년", "body": "결단의 기운이 강한 10년이에요. 당신의 열정이 이걸 두드리면서 원하는 모양을 만들어가요."},
        "水": {"theme": "내가 유연함을 다루는 10년", "body": "유연함의 기운이 강한 10년이에요. 당신이 이걸 감싸면서 중심을 잡아줘요."},
    },
    "controls_me": {
        "木": {"theme": "성장이 나를 흔드는 10년", "body": "성장의 기운이 당신을 흔드는 10년이에요. 흔들릴수록 뿌리를 더 깊이 내리세요."},
        "火": {"theme": "열정이 나를 단련하는 10년", "body": "열정의 기운이 당신을 단련하는 10년이에요. 뜨거움 속에서 더 단단해져요."},
        "土": {"theme": "안정이 나를 감싸는 10년", "body": "안정의 기운이 당신을 감싸는 10년이에요. 울타리 안에서 오히려 더 깊어지는 시기예요."},
        "金": {"theme": "결단이 나를 깎는 10년", "body": "결단의 기운이 당신을 깎는 10년이에요. 깎인 자리에서 새로운 게 자라나요."},
        "水": {"theme": "유연함이 나를 덮는 10년", "body": "유연함의 기운이 당신을 덮는 10년이에요. 눌리는 대신 증기처럼 떠오르는 시기예요."},
    },
}

EN_THEMES = {
    "same": {
        "木": {"theme": "A decade of steady growth", "body": "Growth runs through the whole 10 years. Same direction can feel dull — try new ways on purpose."},
        "火": {"theme": "A decade of steady fire", "body": "Passion burns through the whole 10 years. Pacing matters more than intensity."},
        "土": {"theme": "A decade of deeper roots", "body": "Stability runs through the whole 10 years. Keep small changes going so you don't drift."},
        "金": {"theme": "A decade of sharper edges", "body": "Clarity sharpens for 10 years. Sharp can cut — stay soft where it matters."},
        "水": {"theme": "A decade of deeper flow", "body": "Flexibility deepens for 10 years. Flowing too long loses center — pause to check in."},
    },
    "generates_me": {
        "木": {"theme": "Growth lifts you for 10 years", "body": "Growth energy carries you. Take it in — then pass it on."},
        "火": {"theme": "Passion warms you for 10 years", "body": "Passion energy warms you. This is the season to expand."},
        "土": {"theme": "Stability holds you for 10 years", "body": "Stability energy holds you. Bold moves are safe on this ground."},
        "金": {"theme": "Clarity refines you for 10 years", "body": "Clarity energy refines you. Blurry things gradually become clear."},
        "水": {"theme": "Flexibility fills you for 10 years", "body": "Flexibility energy fills you. Quiet help arrives from unexpected places."},
    },
    "i_generate": {
        "木": {"theme": "You grow things for 10 years", "body": "You make things grow. The more you give, the more you get back."},
        "火": {"theme": "You spark things for 10 years", "body": "You create heat. Creative work shines brightest here."},
        "土": {"theme": "You build things for 10 years", "body": "You lay foundations. Small pieces stack up into something real."},
        "金": {"theme": "You shape things for 10 years", "body": "You set direction. Solid outcomes start landing."},
        "水": {"theme": "You open paths for 10 years", "body": "You open new roads. Making flow lets you go further."},
    },
    "i_control": {
        "木": {"theme": "You handle growth for 10 years", "body": "Growth energy is strong. You tidy it and set your own footing."},
        "火": {"theme": "You handle fire for 10 years", "body": "Passion energy is strong. You cool it and take a step back."},
        "土": {"theme": "You handle stability for 10 years", "body": "Stability energy is strong. You shape it and steady the flow."},
        "金": {"theme": "You handle clarity for 10 years", "body": "Clarity energy is strong. Your fire beats it into the shape you want."},
        "水": {"theme": "You handle flexibility for 10 years", "body": "Flexibility energy is strong. You hold it and center yourself."},
    },
    "controls_me": {
        "木": {"theme": "Growth shakes you for 10 years", "body": "Growth energy shakes you. The more you're tested, the deeper you root."},
        "火": {"theme": "Fire tempers you for 10 years", "body": "Fire energy tempers you. Heat makes you harder, in a good way."},
        "土": {"theme": "Stability contains you for 10 years", "body": "Stability energy contains you. Walls make you go deeper."},
        "金": {"theme": "Clarity cuts you for 10 years", "body": "Clarity energy cuts you. What grows back is stronger."},
        "水": {"theme": "Flexibility covers you for 10 years", "body": "Flexibility energy covers you. You don't sink — you rise like steam."},
    },
}

KO_CAUTIONS = {
    "same": "같은 방향이라 지루해질 수 있어요. 작은 변화를 의식적으로 만들어보세요.",
    "generates_me": "받기만 하면 무뎌져요. 받은 만큼 흘려보내는 연습이 필요해요.",
    "i_generate": "베풀다 지칠 수 있어요. 자신을 먼저 채우는 시간을 확보하세요.",
    "i_control": "통제하려는 마음이 강해지면 관계가 상해요. 놓아줄 건 놓아주세요.",
    "controls_me": "압박이 클수록 조급해져요. 남의 속도와 비교하지 마세요.",
}
KO_PRACTICES = {
    "same": "매년 한 가지, 새로운 방식을 시도해보세요.",
    "generates_me": "받은 것들을 기록하고, 감사로 돌려주세요.",
    "i_generate": "매주 하루는 온전히 자신을 위해 비워두세요.",
    "i_control": "결정 전에 '이걸 꼭 통제해야 하나?' 물어보세요.",
    "controls_me": "매년 한 가지, 10년 후에도 남을 기술을 쌓으세요.",
}
EN_CAUTIONS = {
    "same": "Same direction can get dull. Make small changes on purpose.",
    "generates_me": "Only receiving makes you numb. Pass on what you get.",
    "i_generate": "Giving drains you. Protect time to refill yourself first.",
    "i_control": "Control hurts relationships. Let go of what you can't hold.",
    "controls_me": "Pressure feeds urgency. Don't race against others' speed.",
}
EN_PRACTICES = {
    "same": "Try one new approach each year.",
    "generates_me": "Journal what you receive. Return it as gratitude.",
    "i_generate": "Keep one full day a week just for you.",
    "i_control": "Before deciding, ask: 'Do I really need to control this?'",
    "controls_me": "Build one skill a year that lasts the next decade.",
}
KO_ELEM = {"木": "성장", "火": "열정", "土": "안정", "金": "결단", "水": "유연함"}
EN_ELEM = {"木": "growth", "火": "passion", "土": "stability", "金": "clarity", "水": "flexibility"}

# ═══════════════════════════════════════════════════════════
# 3. 언어별 JSON 저장
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("2) timeline_themes.json 재작성 (KO + EN)")
print("=" * 55)

LANG_DATA = {
    "ko": {"THEMES": KO_THEMES, "CAUTIONS": KO_CAUTIONS, "PRACTICES": KO_PRACTICES, "ELEM_LABEL": KO_ELEM},
    "en": {"THEMES": EN_THEMES, "CAUTIONS": EN_CAUTIONS, "PRACTICES": EN_PRACTICES, "ELEM_LABEL": EN_ELEM},
}

for lang, data in LANG_DATA.items():
    out = Path(f"app/services/content/data/{lang}/timeline_themes.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    if APPLY:
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✅ {lang}: {out}")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/finalize_timeline_v2.py --apply")
else:
    print("🎉 완료. 다음:")
    print("   .\\deploy.ps1")