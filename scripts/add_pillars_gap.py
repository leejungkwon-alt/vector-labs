#!/usr/bin/env python3
"""
甲 일간 6일주 추가 (甲子, 甲寅, 甲辰, 甲午, 甲申, 甲戌).
甲은 양목(陽木)의 기운으로, 거목처럼 곧게 뻗는 개척자 성향입니다.
"""
from __future__ import annotations
import argparse, json, shutil, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app" / "services" / "content" / "data"


def _ts() -> str: return datetime.now().strftime("%Y%m%d_%H%M%S")

def _backup(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + f".bak.{_ts()}")
    shutil.copy2(path, bak)
    return bak

def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


HANJA_TO_HANGUL = {
    "甲": "갑", "乙": "을", "丙": "병", "丁": "정", "戊": "무",
    "己": "기", "庚": "경", "辛": "신", "壬": "임", "癸": "계",
    "子": "자", "丑": "축", "寅": "인", "卯": "묘", "辰": "진", "巳": "사",
    "午": "오", "未": "미", "申": "신", "酉": "유", "戌": "술", "亥": "해",
}

def _reading(pillar: str) -> str:
    return "".join(HANJA_TO_HANGUL.get(c, c) for c in pillar)


PILLARS = {
    "ko": {
        "甲子": {
            "name": "나무 위의 달빛", "pillar": "甲子",
            "hero": "당신은 달빛 아래 자라는 나무입니다. 어두운 밤에도 방향을 잃지 않고, 조용히 위로 자라는 사람이죠.",
            "narrative": [
                "당신은 지혜가 성장을 이끄는 사람입니다. 甲子(갑자)는 큰 나무가 깊은 물 위에 뿌리내린 기둥이에요. 물이 나무를 키우듯, 당신의 성장은 깊은 생각과 지혜에서 나옵니다. 그래서 당신은 무작정 앞으로 나아가는 개척자가 아니라, 방향을 정확히 아는 개척자입니다.",
                "당신의 강점은 '정확한 방향 감각'입니다. 남들이 망설일 때 당신은 이미 어디로 가야 하는지 알고 있습니다. 하지만 그것을 소리치지 않고, 조용히 자기 길을 걷습니다. 그래서 당신이 지나간 자리에는 길이 남아 있고, 뒤따라오는 사람들이 그 길을 따라옵니다.",
                "당신의 그림자는 '생각이 행동보다 앞서는 것'입니다. 물이 깊으면 나무가 키우기 좋지만, 물이 너무 깊으면 나무가 어디로 뻗어야 할지 헷갈립니다. 당신은 생각을 너무 많이 해서, 정작 움직여야 할 순간에 망설입니다. 그리고 그 사이에 기회가 지나가죠.",
                "성숙한 甲子는 '지혜와 실행의 균형을 아는 사람'입니다. 깊은 생각을 유지하되, 필요한 순간에는 망설이지 않고 움직일 줄 아는 사람. 그때 당신의 지혜는 생각에 머무는 게 아니라, 실제로 세상을 바꾸는 힘이 됩니다."
            ],
            "shadows": [
                "생각이 너무 많아 결정을 미루고, 그 사이에 기회를 놓칩니다.",
                "정확한 방향 감각이 있어도, 그것을 다른 사람에게 설명하지 않아 오해를 삽니다.",
                "조용히 걷는 습관 때문에, 정작 당신의 기여가 잘 보이지 않습니다."
            ],
            "advice": [
                "이번 주에 한 번, 결론이 완벽하지 않아도 말로 꺼내보세요.",
                "당신이 조용히 판단한 것을 하나 골라, 왜 그렇게 생각했는지 누군가에게 설명해 보세요.",
                "결정해야 할 것 하나를 골라, 정해진 기한 안에 반드시 결정하세요.",
                "당신이 걸어온 길을 한 번 돌아보세요. 그 길에 이미 사람들이 따라오고 있다는 걸 알아채야 합니다."
            ],
            "keywords": ["달빛 개척", "깊은 지혜", "정확한 방향", "조용한 성장"]
        },
        "甲寅": {
            "name": "거대한 거목", "pillar": "甲寅",
            "hero": "당신은 숲의 거대한 거목입니다. 그 어떤 바람에도 흔들리지 않고, 자신만의 방향으로 하늘을 향해 뻗는 사람이죠.",
            "narrative": [
                "당신은 甲 중에서도 가장 순수한 甲입니다. 甲寅(갑인)은 甲의 록(祿) 자리에 甲이 앉은, 목 기운이 두 겹으로 겹친 기둥이에요. 그래서 당신의 신념은 흔들리지 않고, 당신의 추진력은 압도적이며, 당신의 태도는 흔들림이 없습니다. 사람들은 당신 앞에서 이상하게 '이 사람은 다르다'는 인상을 받습니다.",
                "당신의 강점은 '확고한 신념'입니다. 한 번 마음먹으면 반드시 해냅니다. 그리고 그 과정에서 당신은 사람들을 이끄는 힘을 발휘합니다. 당신이 이끄는 팀은 방향이 명확하고, 당신이 시작한 프로젝트는 중간에 흐트러지지 않습니다. 이건 노력이 아니라, 두 겹의 木이 만들어내는 자연스러운 결과예요.",
                "당신의 그림자는 '너무 곧아서 부러지는 것'입니다. 거목은 그 어떤 바람에도 흔들리지 않지만, 너무 곧으면 강한 바람에 부러집니다. 당신의 신념이 지나치면 유연성을 잃고, 다른 사람의 다름을 인정하지 못합니다. 그리고 그 곧음이 자신에게도 향해서, 완벽하지 않은 자신을 용서하지 못합니다.",
                "성숙한 甲寅은 '곧되 부러지지 않는 사람'입니다. 신념을 유지하되, 필요할 때는 유연하게 휘어질 줄 아는 사람. 그때 당신의 거목은 바람에 부러지지 않고, 오히려 뿌리를 더 깊이 내립니다."
            ],
            "shadows": [
                "신념이 너무 곧아서, 다른 사람의 다름을 '틀림'으로 판단합니다.",
                "유연성을 잃어, 방향을 바꿔야 할 때도 계속 밀어붙입니다.",
                "완벽하지 않은 자신을 오래 용서하지 못해, 스스로가 갈립니다."
            ],
            "advice": [
                "이번 주에 한 번, 당신의 신념과 다른 의견을 끝까지 들어보세요.",
                "결정을 내리기 전에 '이건 신념인가, 고집인가' 스스로에게 물어보세요.",
                "당신이 자주 던지는 '왜 이것밖에' 를 '무엇을 해냈지'로 한 번 바꿔보세요.",
                "자신에게 '이 정도면 충분해'라고 말할 순간을 하나 만들어 두세요."
            ],
            "keywords": ["순수 甲", "거대한 거목", "확고한 신념", "곧은 리더십"]
        },
        "甲辰": {
            "name": "용의 숲", "pillar": "甲辰",
            "hero": "당신은 용이 사는 숲입니다. 겉은 평범해 보이지만, 그 아래에는 세상을 움직일 만한 큰 그림이 자라고 있는 사람이죠.",
            "narrative": [
                "당신은 쉽게 드러나지 않는 큰 그릇의 사람입니다. 甲辰(갑진)은 거대한 나무가 습한 땅 위에 뿌리내린 기둥이에요. 辰은 용의 땅이고 물을 저장합니다. 그래서 당신은 평소엔 무던해 보이는데, 결정적인 순간에 성장의 무게가 드러납니다. 사람들은 나중에 '그 사람이 그런 사람이었어?'라며 놀라죠.",
                "당신의 강점은 '큰 그림을 보는 힘'입니다. 작은 전술보다 큰 구도를 먼저 그리고, 그 안에서 사람과 자원을 배치합니다. 그리고 당신은 서두르지 않습니다. 충분히 시간을 두고, 묵직하게 성장합니다. 이게 甲辰의 진짜 힘이에요. 평소엔 조용하지만, 필요할 때는 세상을 움직이는 사람입니다.",
                "당신의 그림자는 '잠재력만 간직하는 것'입니다. 辰의 물을 甲이 다 쓰지 않으면, 그 물은 그냥 땅속에 고여 있습니다. 당신도 마찬가지예요. 큰 그림을 그리고 있지만 정작 꺼내 보여주지 않으면, 주변 사람들은 당신의 잠재력을 모릅니다. 그리고 시간이 지나면 '그 사람은 뭘 하는 사람이지?'라는 평가가 붙습니다.",
                "성숙한 甲辰은 '큰 그림을 작은 시작으로 꺼내는 사람'입니다. 큰 구도를 유지하되, 작은 행동을 통해 그것을 세상에 드러내는 사람. 그때 당신의 존재감은 위압이 아니라, 사람들이 믿고 기댈 수 있는 힘이 됩니다."
            ],
            "shadows": [
                "큰 그림만 그리다가, 정작 작은 실행을 놓칩니다.",
                "잠재력만 간직하고, 정작 꺼내 보여주지 않아 과소평가받습니다.",
                "결정적인 순간을 계속 기다리다가, 그 순간이 오지 않습니다."
            ],
            "advice": [
                "이번 주에 당신이 품고 있는 큰 그림 하나를, 구체적인 행동으로 꺼내 보세요.",
                "큰 그림 안에서 지금 당장 할 수 있는 '작은 시작' 하나를 정하세요.",
                "당신의 계획을 누군가에게 설명해 보세요. 머릿속에만 두면 사람들은 모릅니다.",
                "결정적인 순간을 기다리지 말고, 이번 주에 스스로 결정적인 순간을 하나 만드세요."
            ],
            "keywords": ["큰 그림", "묵직한 성장", "용의 숲", "잠재력 실현"]
        },
        "甲午": {
            "name": "불을 뿜는 나무", "pillar": "甲午",
            "hero": "당신은 불을 뿜는 나무입니다. 뜨거운 열정으로 주변을 밝히는, 카리스마의 사람이죠.",
            "narrative": [
                "당신은 열정과 표현의 사람입니다. 甲午(갑오)는 큰 나무가 뜨거운 불기운 위에 앉은 기둥이에요. 나무가 불을 만나면 타오릅니다. 당신의 열정이 그래요. 뜨거운 열기로 주변을 밝히고, 사람들을 끌어당깁니다. 당신 곁에 있으면 사람들은 이상하게 활력을 얻습니다.",
                "당신의 강점은 '뜨거운 표현력'입니다. 당신은 자신의 생각과 감정을 숨기지 않고, 열정적으로 표현합니다. 그래서 당신은 사람들을 움직이는 힘이 있어요. 당신이 좋아하는 것, 원하는 것, 믿는 것을 말할 때, 사람들은 그 열기에 끌려갑니다. 이건 흔한 재능이 아닙니다.",
                "당신의 그림자는 '너무 뜨겁게 타오르는 것'입니다. 나무가 불을 만나면 타오르지만, 그 불이 너무 뜨거우면 나무 자신도 다 타버립니다. 당신은 열정에 사로잡혀, 정작 자신의 체력을 잊습니다. 쉬지 않고 달리다가, 어느 순간 완전히 꺼져버리죠. 그리고 그때 주변 사람들은 당신의 갑작스러운 침묵에 당황합니다.",
                "성숙한 甲午는 '열정을 조율하는 사람'입니다. 뜨거운 열정을 유지하되, 그것이 자신을 태우지 않도록 조절할 줄 아는 사람. 그때 당신의 열정은 한 번 타오르고 마는 불꽃이 아니라, 오래 사람들을 밝히는 등대가 됩니다."
            ],
            "shadows": [
                "열정이 너무 뜨거워서, 정작 자신의 체력을 잊고 달립니다.",
                "쉬지 않고 달리다가, 어느 순간 완전히 꺼져버립니다.",
                "열정이 지나쳐, 다른 사람을 압도하거나 지치게 만듭니다."
            ],
            "advice": [
                "이번 주에 '아무것도 하지 않는' 시간을 하루 30분 이상 확보하세요.",
                "당신의 열정을 건강하게 발산할 수 있는 취미나 운동을 하나 만드세요.",
                "쉬는 순간 '이 시간에 뭘 해야 하지'가 떠오르면, '지금은 쉬는 중이야'라고 스스로에게 답해주세요.",
                "당신의 열정을 사람들에게 쏟기 전에, 스스로에게 먼저 쓰세요. 그래야 오래갑니다."
            ],
            "keywords": ["뜨거운 열정", "카리스마", "표현력", "열정의 조율"]
        },
        "甲申": {
            "name": "바위에 뿌리내린 나무", "pillar": "甲申",
            "hero": "당신은 바위에 뿌리내린 나무입니다. 척박한 환경에서도 뿌리를 깊이 내려, 더 단단해지는 사람이죠.",
            "narrative": [
                "당신은 압박 속에서 단단해지는 사람입니다. 甲申(갑신)은 큰 나무가 단단한 금속 위에 앉은 기둥이에요. 金은 木을 벱니다. 그래서 당신의 환경은 늘 만만치 않습니다. 그런데 놀랍게도 당신은 그 압박 속에서 더 단단해지고, 뿌리를 더 깊이 내립니다. 이건 흔한 재능이 아니에요.",
                "당신의 강점은 '지혜로운 돌파'입니다. 당신은 무작정 부딪히지 않습니다. 환경을 정확히 읽고, 어디로 뿌리를 내려야 하는지, 어디로 가지를 뻗어야 하는지 계산합니다. 그래서 당신은 어려운 상황에서 오히려 더 좋은 결과를 만들어냅니다. 조직에서 '이 사람이 맡으면 어떻게든 된다'는 평가가 붙는 이유입니다.",
                "당신의 그림자는 '상처를 억누르는 것'입니다. 바위에 뿌리내린 나무는 단단하지만, 그 뿌리는 상처투성이입니다. 당신은 어려움을 잘 견디지만, 그 상처를 잘 꺼내지 않습니다. 그리고 그 상처가 쌓이면, 어느 순간 당신의 열정이 완전히 식어버립니다. '이제 지쳤다'는 말조차 하지 못한 채로요.",
                "성숙한 甲申은 '상처를 인정하는 사람'입니다. 단단함을 유지하되, 정작 자신의 상처와 피로를 인정하고 돌볼 줄 아는 사람. 그때 당신의 뿌리는 더 이상 상처투성이가 아니라, 깊고 단단한 생명력이 됩니다."
            ],
            "shadows": [
                "상처와 피로를 억누르다가, 어느 순간 열정이 완전히 식어버립니다.",
                "단단함이 지나쳐서, 주변 사람들이 당신의 힘듦을 알아채지 못합니다.",
                "환경을 이겨내려는 집념이 지나쳐, 정작 자신을 돌보지 못합니다."
            ],
            "advice": [
                "이번 주에 한 번, 자신의 피로나 상처를 인정하고 누군가에게 꺼내 보세요.",
                "당신이 오래 견뎌온 것 하나를 스스로에게 인정해 주세요. 그게 뿌리입니다.",
                "규칙적으로 회복 시간을 확보하세요. 뿌리도 쉬어야 다시 자랍니다.",
                "당신의 단단함을 자랑이 아니라 나눔의 도구로 쓰세요. 그것이 진짜 힘입니다."
            ],
            "keywords": ["바위 위 나무", "압박 속 성장", "지혜로운 돌파", "뿌리의 단단함"]
        },
        "甲戌": {
            "name": "마른 땅의 나무", "pillar": "甲戌",
            "hero": "당신은 마른 땅에 뿌리내린 나무입니다. 원칙과 결단으로 자신의 영역을 지키는, 책임의 사람이죠.",
            "narrative": [
                "당신은 원칙과 결단의 사람입니다. 甲戌(갑술)은 큰 나무가 건조한 흙 위에 앉은 기둥이에요. 木은 土를 이깁니다. 그래서 당신은 자신의 자리에서 확고하게 서 있습니다. 흔들리지 않고, 쉽게 물러서지 않습니다. 사람들은 당신의 이런 단단함에 신뢰를 보냅니다.",
                "당신의 강점은 '책임의 무게'입니다. 당신은 맡은 일을 끝까지 책임지고, 원칙에 따라 판단합니다. 이 태도는 조직에서 큰 신뢰를 만들어요. 다들 흔들릴 때 당신은 흔들리지 않으니까요. 그리고 당신의 결단은 빠르고 정확합니다. 그것이 당신이 리더의 자리에 서는 이유입니다.",
                "당신의 그림자는 '원칙이 융통성을 잃는 것'입니다. 나무가 땅을 이기지만, 그 땅이 너무 건조하면 나무도 자라기 어렵습니다. 당신의 원칙이 지나치면, 다른 사람의 다름을 '틀림'으로 판단하게 됩니다. 그리고 그 원칙이 스스로에게도 향해서, 완벽하지 않은 자신을 용서하지 못합니다.",
                "성숙한 甲戌은 '원칙에 물기를 더하는 사람'입니다. 확고한 원칙을 유지하되, 그 원칙에 이르지 못하는 사람을 이해할 줄 아는 사람. 그때 당신의 원칙은 압박이 아니라, 사람들이 배우고 싶어 하는 기준이 됩니다."
            ],
            "shadows": [
                "원칙이 너무 확고해서, 다른 사람의 다름을 '틀림'으로 판단합니다.",
                "융통성이 부족해서, 변화가 필요한 순간에도 고집을 부립니다.",
                "완벽하지 않은 자신을 오래 용서하지 못해, 스스로에게 가혹합니다."
            ],
            "advice": [
                "이번 주에 한 번, 자신의 원칙과 다른 의견을 끝까지 들어보세요.",
                "당신의 원칙 중 하나를 이번 주에는 조금 느슨하게 풀어보세요. 세상이 무너지지 않는다는 걸 확인하는 겁니다.",
                "결정을 내리기 전에 '이건 원칙의 문제인가, 내가 지금 지친 것인가'를 한 번 구분해 보세요.",
                "자신에게 '이 정도면 충분해'라고 말할 순간을 하나 만들어 두세요."
            ],
            "keywords": ["원칙의 무게", "마른 땅 나무", "책임의 결단", "원칙과 유연"]
        }
    },
    "en": {
        "甲子": {
            "name": "Moonlight on the Tree", "pillar": "甲子",
            "hero": "You're a tree growing under moonlight. Even in darkness, you don't lose the direction — you grow upward, quietly.",
            "narrative": [
                "Wisdom leads your growth. 甲子 is a great tree rooted in deep water. Water feeds the tree — and your growth comes from deep thought and quiet understanding. So you're not a pioneer who just charges forward. You're the kind who knows exactly where forward is.",
                "Your strength is precise sense of direction. While others hesitate, you already know the way. But you don't shout it — you walk it quietly. The places you've passed through carry a trail, and the people behind you follow it.",
                "Your shadow is thinking ahead of action. Deep water is good for a tree, but if the water runs too deep, the tree forgets where to reach. You think so much that you hesitate at the moment you should move, and the opening passes.",
                "A mature Jia-Zi knows the balance between wisdom and action. Keeping the depth of thought, and moving without hesitation when the moment arrives. Then your wisdom stops living only in your head and becomes something that actually changes the world."
            ],
            "shadows": [
                "Thinking so much that decisions get delayed and the opening closes.",
                "Having the direction without explaining it, which creates misunderstanding.",
                "Walking quietly, so your contribution doesn't show up as much as it should."
            ],
            "advice": [
                "Once this week, say the conclusion out loud even if it isn't fully formed.",
                "Pick one judgment you've kept silent and explain why you see it that way.",
                "Pick one decision and make it by a fixed deadline.",
                "Look back at the path you've walked. People are already following it."
            ],
            "keywords": ["moonlit pioneer", "deep wisdom", "precise direction", "quiet growth"]
        },
        "甲寅": {
            "name": "Giant Oak", "pillar": "甲寅",
            "hero": "You're the great oak of the forest. Unshaken by any wind, reaching toward the sky in your own direction.",
            "narrative": [
                "You're the purest form of 甲. 甲寅 is 甲 sitting in its own 祿 (Lu) — double wood, layered on itself. Your conviction doesn't shake, your drive is overwhelming, your stance is firm. People feel in your presence that this person is different.",
                "Your strength is unwavering conviction. Once you set your mind, you finish it. And in the process, you lead people. The teams you lead have clear direction, and the projects you start don't fall apart midway. It isn't effort — it's the natural output of double wood.",
                "Your shadow is being so straight that you break. A great tree doesn't shake in the wind, but a tree that's too straight breaks in a strong gust. Your conviction taken too far loses flexibility, and you can't accept other people's differences. And that straightness also turns inward — you can't forgive your own imperfection.",
                "A mature Jia-In is straight but unbreakable. Keeping the conviction, and knowing how to bend when it's needed. Then your oak doesn't break in the wind — it drives its roots deeper."
            ],
            "shadows": [
                "A conviction so straight that other people's differences register as errors.",
                "Losing flexibility, pushing the same direction when a turn was needed.",
                "Unable to forgive your own imperfection, so you slowly grind yourself down."
            ],
            "advice": [
                "Once this week, listen all the way through to a view that isn't yours.",
                "Before deciding, ask: is this conviction, or is this stubbornness?",
                "Turn one 'why only this much' into 'what did I actually make?'",
                "Say 'this is enough' to yourself once this week."
            ],
            "keywords": ["pure 甲", "giant oak", "unwavering conviction", "straight leadership"]
        },
        "甲辰": {
            "name": "Forest of Dragons", "pillar": "甲辰",
            "hero": "You're a forest where dragons live. Ordinary on the surface, growing a big picture beneath that could move the world.",
            "narrative": [
                "You're the kind of large vessel that doesn't reveal itself easily. 甲辰 is a giant tree rooted in damp earth. 辰 is the dragon's earth, and it stores water. You look unremarkable most of the time — and then at a decisive moment, your growth shows. People say later, 'Wait — that person was that person?'",
                "Your strength is seeing the big picture. You sketch the large frame first and arrange people and resources inside it. And you don't rush. You grow heavily, slowly. That's the real strength of 甲辰 — quiet most of the time, moving the world when it counts.",
                "Your shadow is holding the potential without releasing it. If 甲 doesn't use the water in 辰, it just stays pooled in the ground. Same for you. If you sketch a big picture but never bring it out, people don't know your potential. And over time the label 'what does that person actually do?' starts to attach.",
                "A mature Jia-Jin brings the big picture out through small starts. Keeping the large frame, and revealing it through small actions. Then your presence stops being intimidating and becomes the thing people trust and lean on."
            ],
            "shadows": [
                "Sketching the big picture and missing the small execution.",
                "Holding the potential and never revealing it, so people underestimate you.",
                "Waiting for the decisive moment until it never arrives."
            ],
            "advice": [
                "Bring one big picture you're holding into concrete action this week.",
                "Pick one small start inside the big picture that you can do right now.",
                "Explain your plan to someone. Kept only in your head, people don't know.",
                "Stop waiting for the decisive moment — create one this week."
            ],
            "keywords": ["big picture", "heavy growth", "dragon forest", "potential made real"]
        },
        "甲午": {
            "name": "Tree Ablaze", "pillar": "甲午",
            "hero": "You're a tree on fire. You light the room with your heat — a person of real charisma.",
            "narrative": [
                "You're the person of passion and expression. 甲午 is a great tree sitting on hot fire. Wood meeting fire burns. Your heat is like that — it lights the room and pulls people in. People feel strange vitality when they're near you.",
                "Your strength is fiery expression. You don't hide what you think or feel — you express it with heat. That gives you the power to move people. When you say what you love, what you want, what you believe, people are drawn to that fire. It's a rare gift.",
                "Your shadow is burning too hot. Wood meeting fire burns — but if the fire is too hot, the wood itself burns up. You get caught up in the passion and forget your own stamina. You run without stopping, and then one day you go out completely. And the people around you are startled by your sudden silence.",
                "A mature Jia-O tunes the fire. Keeping the heat, and controlling it so it doesn't consume you. Then your passion isn't a single flare — it becomes a lighthouse that lights people for a long time."
            ],
            "shadows": [
                "Burning so hot that you forget your own stamina.",
                "Running without rest until you go out completely.",
                "Passion that overwhelms or exhausts other people."
            ],
            "advice": [
                "Set aside at least 30 minutes a day this week with nothing productive in it.",
                "Find one hobby or exercise that lets you discharge the heat healthily.",
                "When 'what should I be doing' comes up while resting, tell yourself: I'm resting now.",
                "Spend your passion on yourself before you spend it on others. That's what keeps it burning."
            ],
            "keywords": ["hot passion", "charisma", "expression", "tuning the fire"]
        },
        "甲申": {
            "name": "Tree Rooted in Stone", "pillar": "甲申",
            "hero": "You're a tree rooted in stone. In hostile conditions, you drive your roots deeper and become harder.",
            "narrative": [
                "You harden under pressure. 甲申 is a great tree sitting on hard metal. Metal cuts wood — and so your environment is never easy. But remarkably, you become harder under the pressure and drive your roots deeper. That's rare.",
                "Your strength is wise breakthrough. You don't charge blindly. You read the environment carefully, and you calculate where to root and where to branch. So you often get better results under difficulty. That's why organizations say, 'If this person takes it, it somehow gets done.'",
                "Your shadow is burying the wounds. A tree rooted in stone is solid — but the roots are covered in scars. You endure difficulty well, but you don't bring the wounds out. And when the wounds accumulate, one day your passion goes out completely. Without even saying 'I'm exhausted.'",
                "A mature Jia-Shin acknowledges the wound. Keeping the firmness, and admitting your own scars and fatigue. Then your roots stop being scar tissue and become deep, hard strength."
            ],
            "shadows": [
                "Holding the wounds and fatigue inside until your passion goes out completely.",
                "So firm that the people around you don't see how hard it is for you.",
                "Persevering so hard that you stop looking after yourself."
            ],
            "advice": [
                "Once this week, acknowledge your fatigue or wound, and share it with someone.",
                "Acknowledge one thing you've endured for a long time. That's your root.",
                "Protect recovery time consistently. Roots also need rest to grow.",
                "Use your firmness as a tool for sharing, not a badge. That's real strength."
            ],
            "keywords": ["tree on stone", "growth under pressure", "wise breakthrough", "root strength"]
        },
        "甲戌": {
            "name": "Tree on Dry Earth", "pillar": "甲戌",
            "hero": "You're a tree rooted in dry earth. A person of responsibility, holding your ground through principle and decision.",
            "narrative": [
                "You're a person of principle and decisiveness. 甲戌 is a great tree sitting on dry earth. Wood overcomes earth. So you stand firmly in your place. You don't shake easily and you don't step back easily. People put real trust in that firmness.",
                "Your strength is the weight of responsibility. You carry what you take on to the end, and you judge by principle. This builds enormous trust in organizations — when everyone else is wavering, you aren't. Your decisions come fast and clean. That's why you end up in leadership.",
                "Your shadow is principle losing flexibility. Wood overcomes earth, but if the earth is too dry, the tree can't grow well either. Your principle taken too far makes differences look like errors. And that same principle turns on you — you can't forgive your own imperfection.",
                "A mature Jia-Xu adds moisture to the principle. Keeping the firm principle, and understanding the people who can't reach it yet. Then your principle stops being pressure and becomes the kind of standard people want to learn."
            ],
            "shadows": [
                "Principle so firm that other people's differences register as errors.",
                "Lacking flexibility, holding on when a change was actually needed.",
                "Unable to forgive your own imperfection, being very harsh with yourself."
            ],
            "advice": [
                "Once this week, listen all the way through to a view that isn't yours.",
                "Loosen one of your principles this week on purpose. Confirm nothing breaks.",
                "Before deciding, ask: is this principle, or am I just tired?",
                "Say 'this is enough' to yourself once this week."
            ],
            "keywords": ["weight of principle", "tree on dry earth", "responsible decision", "principle and flexibility"]
        }
    }
}


def main() -> int:
    ap = argparse.ArgumentParser(description="甲 일간 6일주 추가")
    ap.add_argument("--force", action="store_true", help="스텁 덮어쓰기")
    args = ap.parse_args()

    print("=== 甲 일간 6일주 추가 (甲子, 甲寅, 甲辰, 甲午, 甲申, 甲戌) ===")
    
    created = skipped = 0
    for lang in ("ko", "en"):
        for pillar, data in PILLARS[lang].items():
            path = DATA / lang / "core_pillars" / f"{pillar}.json"
            if path.exists() and not args.force:
                skipped += 1
                continue
            if path.exists(): _backup(path)
            _write_json(path, data)
            created += 1
    print(f"  - 일주 파일: 생성 {created}개 / 건너뜀 {skipped}개")

    for lang in ("ko", "en"):
        names_path = DATA / lang / "pillar_names.json"
        if names_path.exists():
            names_data = json.loads(names_path.read_text(encoding="utf-8"))
            for pillar, p_data in PILLARS[lang].items():
                names_data[pillar] = {
                    "name": p_data["name"],
                    "traditional": f"{_reading(pillar)}({pillar})"
                }
            _write_json(names_path, names_data)
            print(f"  - [{lang}] pillar_names.json 업데이트 완료")

    print("\n✅ 완료. 검증:")
    print("  pytest -q")
    return 0

if __name__ == "__main__":
    sys.exit(main())