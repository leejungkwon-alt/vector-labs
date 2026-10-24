#!/usr/bin/env python3
"""
壬 일간 6일주 추가 (壬子, 壬寅, 壬辰, 壬午, 壬申, 壬戌).
壬은 양수(陽水)의 기운으로, 큰물처럼 광활하고 지혜로운 성향입니다.
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
        "壬子": {
            "name": "겨울의 깊은 바다", "pillar": "壬子",
            "hero": "당신은 겨울의 깊은 바다입니다. 겉은 얼음처럼 단단하지만, 그 아래에서는 멈추지 않는 물결이 흐르는 사람이죠.",
            "narrative": [
                "당신은 壬 중에서도 가장 순수한 壬입니다. 壬子(임자)는 壬의 록(祿) 자리에 壬이 앉은, 물 기운이 두 겹으로 겹친 기둥이에요. 그래서 당신의 지혜는 흔들리지 않고, 당신의 시야는 광활하며, 당신의 생각은 깊습니다. 사람들은 당신 앞에서 이상하게 '이 사람은 뭔가 다르다'는 인상을 받습니다.",
                "당신의 강점은 '깊이 생각하는 힘'입니다. 표면만 보는 사람들과 달리 당신은 사건 아래의 구조를 봅니다. 결정을 서두르지 않고, 충분히 가라앉힌 뒤에 내리는 결론은 대체로 맞습니다. 그래서 당신은 조직에서 '큰 판단을 맡길 수 있는 사람'으로 통합니다.",
                "당신의 그림자는 '얼음 아래 갇힌 감정'입니다. 겨울 바다의 표면은 얼음이지만 그 아래는 흐르고 있어요. 당신도 겉으로는 차분하지만, 안에는 깊은 감정의 물결이 있습니다. 문제는 그 감정이 얼음 아래에 갇혀 있어서, 주변 사람들이 당신의 온도를 잘 느끼지 못한다는 거예요. '차갑다'거나 '속을 모르겠다'는 말을 들은 적 있다면, 그건 당신이 무심해서가 아니라 너무 깊이 담아두기 때문입니다.",
                "성숙한 壬子는 '얼음을 스스로 녹일 줄 아는 사람'입니다. 깊은 지혜를 유지하되, 그 아래 흐르는 감정을 조금씩 꺼내 보여줄 줄 아는 사람. 그때 당신의 깊이는 거리감이 아니라, 사람들이 의지하고 싶은 지혜가 됩니다."
            ],
            "shadows": [
                "얼음 아래 감정을 너무 오래 담아두어, 주변 사람들이 당신의 온도를 오해합니다.",
                "결정을 너무 오래 미루다가, 그 사이에 기회가 지나갑니다.",
                "당신의 깊이가 거리감으로 읽혀, 친밀감을 쌓기까지 오래 걸립니다."
            ],
            "advice": [
                "이번 주에 한 번, 평소 담아두던 감정을 조금 꺼내 보여주세요. 작은 것도 괜찮습니다.",
                "결정해야 할 것 하나를 골라, 정해진 기한 안에 반드시 결정하세요. 완벽하지 않아도 됩니다.",
                "당신의 지혜를 하나 골라, 누군가에게 설명해 주세요. 지혜는 나눌 때 더 선명해집니다.",
                "바다도 땅이 필요합니다. 하루에 하나, 흔들리지 않는 작은 의식을 만드세요."
            ],
            "keywords": ["깊은 지혜", "얼음 아래 흐름", "광활한 시야", "멀리 보는 눈"]
        },
        "壬寅": {
            "name": "봄을 만난 바다", "pillar": "壬寅",
            "hero": "당신은 봄을 만난 바다입니다. 얼었던 물이 풀리며 나무를 키우듯, 당신의 지혜는 사람을 자라게 하는 사람이죠.",
            "narrative": [
                "당신은 지혜로 사람을 키우는 사람입니다. 壬寅(임인)은 水가 木을 낳는 기둥이에요. 물이 나무를 키우듯, 당신은 넓은 안목으로 사람의 잠재력을 알아보고 그것이 자라도록 조용히 공급합니다. 화려한 리더십이 아니라, 뿌리에 물을 대는 사람이에요.",
                "당신의 강점은 '넓은 안목'입니다. 사람을 볼 때 지금의 모습이 아니라 앞으로의 가능성을 봅니다. 그리고 그 가능성이 실제로 자라도록 환경을 만들어 줍니다. 당신이 키운 사람들은 시간이 지나면 '그때 그 사람이 없었으면'이라고 말합니다. 당신의 기여는 늘 사후에 인정됩니다.",
                "당신의 그림자는 '너무 많이 흘려보내는 것'입니다. 물이 흐르듯, 당신은 자신의 것을 남에게 아낌없이 흘려보냅니다. 그런데 흐르는 물은 결국 자신의 물줄기를 잃기 쉬워요. 다른 사람의 성장을 돕다가, 정작 자신의 성장은 계속 미룹니다. 그리고 결정해야 할 순간에도 '물처럼 흘러가면 되지' 하며 회피합니다.",
                "성숙한 壬寅은 '자신도 물의 일부임을 아는 사람'입니다. 다른 사람을 키우는 동시에 자신도 자라는 사람. 그때 당신의 흐름은 한 번 지나가고 마는 계절이 아니라, 몇 년 동안 계속 사람을 살리는 강물이 됩니다."
            ],
            "shadows": [
                "다른 사람의 성장만 챙기고, 자신의 성장은 계속 미룹니다.",
                "결정해야 할 순간에 '흘러가면 되지' 하며 회피합니다.",
                "자신의 기여를 너무 낮게 봐서, 스스로에게 인색해집니다."
            ],
            "advice": [
                "이번 주에 자신의 성장을 위해 쓸 시간을 먼저 달력에 넣어두세요.",
                "결정해야 할 것 하나는 '흘려보내지 말고' 기한 안에 정하세요.",
                "당신의 지혜를 구체적인 말이나 글로 남겨두세요. 흐르는 것만으로는 남지 않습니다.",
                "당신이 키우는 사람들 사이에, 당신을 위한 자리를 하나 만들어 두세요."
            ],
            "keywords": ["봄의 바다", "사람을 키우는 지혜", "넓은 안목", "함께 자람"]
        },
        "壬辰": {
            "name": "용이 사는 바다", "pillar": "壬辰",
            "hero": "당신은 용이 사는 바다입니다. 겉은 평범해 보이지만, 그 아래에는 세상을 움직일 만한 잠재력이 잠들어 있는 사람이죠.",
            "narrative": [
                "당신은 쉽게 드러나지 않는 큰 그릇의 사람입니다. 壬辰(임진)은 魁罡(괴강)에 속하는 강한 기둥이에요. 辰은 용의 땅이고, 물을 저장합니다. 그래서 당신은 평소엔 무던해 보이는데, 결정적인 순간에 무게가 드러납니다. 사람들은 나중에 '그 사람이 그런 사람이었어?'라며 놀라죠.",
                "당신의 강점은 '큰 그림을 보는 힘'입니다. 작은 전술보다 큰 구도를 먼저 그리고, 그 안에서 사람과 자원을 배치합니다. 결정적인 순간, 남들이 흔들릴 때 당신은 조용히 중심을 잡습니다. 이게 壬辰의 진짜 힘이에요. 평소엔 조용하지만, 필요할 때는 세상을 움직이는 사람입니다.",
                "당신의 그림자는 '잠재력만 간직하는 것'입니다. 용은 계속 동굴에 있으면 그냥 전설이 됩니다. 당신도 마찬가지예요. 큰 그림을 그리고 있지만 정작 꺼내 보여주지 않으면, 주변 사람들은 당신의 잠재력을 모릅니다. 그리고 시간이 지나면 '그 사람은 뭘 하는 사람이지?'라는 평가가 붙습니다.",
                "성숙한 壬辰은 '용을 깨울 줄 아는 사람'입니다. 큰 그림을 유지하되, 작은 시작을 통해 그것을 세상에 꺼내는 사람. 그때 당신의 존재감은 위압이 아니라, 사람들이 믿고 기댈 수 있는 힘이 됩니다."
            ],
            "shadows": [
                "잠재력만 간직하고, 정작 꺼내 보여주지 않아 과소평가받습니다.",
                "큰 그림만 그리다가, 정작 작은 실행을 놓칩니다.",
                "결정적인 순간을 계속 기다리다가, 그 순간이 오지 않습니다."
            ],
            "advice": [
                "이번 주에 당신이 품고 있는 잠재력 하나를 구체적인 행동으로 꺼내 보세요.",
                "큰 그림 안에서 지금 당장 할 수 있는 '작은 시작' 하나를 정하세요.",
                "당신의 계획을 누군가에게 설명해 보세요. 머릿속에만 두면 용은 계속 잠들어 있습니다.",
                "결정적인 순간을 기다리지 말고, 이번 주에 스스로 결정적인 순간을 하나 만드세요."
            ],
            "keywords": ["魁罡", "큰 그릇", "숨은 용", "결정적 무게"]
        },
        "壬午": {
            "name": "불을 품은 바다", "pillar": "壬午",
            "hero": "당신은 불을 품은 바다입니다. 겉은 깊고 차갑지만, 안에는 뜨거운 열정이 흐르는 사람이죠.",
            "narrative": [
                "당신은 냉정함과 열정을 동시에 지닌 사람입니다. 壬午(임오)는 깊은 물 위에 뜨거운 불기운이 앉은 기둥이에요. 물과 불은 서로를 이기지만, 한 사람 안에 있으면 아주 독특한 온도가 만들어집니다. 겉으로 보면 당신은 차분하고 이성적이지만, 안에서는 뜨거운 열정이 끓고 있어요.",
                "당신의 강점은 '두 가지를 동시에 쓸 수 있는 힘'입니다. 냉정한 판단과 뜨거운 열정, 이 두 가지를 함께 쓸 수 있는 사람은 드물어요. 그래서 당신은 중요한 순간에 감정에 휘둘리지 않으면서도, 사람들을 감동시키는 결정을 내립니다. 이중성이 당신의 무기예요.",
                "당신의 그림자는 '겉과 속의 온도차로 인한 오해'입니다. 당신이 뜨거운 마음을 품고 있는데도 겉으로는 차갑게 보이면, 주변 사람들은 당신이 무관심하다고 느낍니다. 그리고 당신이 어느 순간 뜨거운 감정을 터뜨리면, 사람들은 당신의 갑작스러운 변화에 당황합니다. 당신의 이중성을 모르는 사람들에게 당신은 '알 수 없는 사람'이 됩니다.",
                "성숙한 壬午는 '두 면을 통합하는 사람'입니다. 뜨거운 열정과 냉정한 판단을 하나의 목소리로 엮는 사람. 그때 당신의 이중성은 흔들림이 아니라, 사람들이 의지하고 싶은 깊은 열정이 됩니다."
            ],
            "shadows": [
                "겉과 속의 온도차로 인해, 사람들이 당신의 진심을 오해합니다.",
                "감정이 갑자기 폭발하면, 평소의 차분함과 대비되어 주변이 크게 당황합니다.",
                "뜨거운 열정을 계속 감추다가, 어느 순간 완전히 지쳐버립니다."
            ],
            "advice": [
                "이번 주에 한 번, 당신의 뜨거운 열정을 말로 꺼내 보여주세요. 좋아하는 것, 원하는 것.",
                "감정이 올라올 때, '이건 지금 표현할 때인가, 조금 더 다듬을 때인가' 스스로에게 물어보세요.",
                "가까운 사람에게 '나는 겉으로는 차분해 보여도 속으로는 뜨거워'라고 한 번 설명해 주세요.",
                "당신의 열정을 건강하게 발산할 수 있는 취미나 운동을 하나 만드세요."
            ],
            "keywords": ["냉정한 열정", "이중성", "깊은 불", "두 얼굴의 지혜"]
        },
        "壬申": {
            "name": "바위를 뚫는 물", "pillar": "壬申",
            "hero": "당신은 바위를 뚫는 물입니다. 부드러워 보이지만, 시간이 지나면 어떤 것도 통과하는 사람이죠.",
            "narrative": [
                "당신은 예리함과 지혜를 동시에 지닌 사람입니다. 壬申(임신)은 金이 水를 낳는 기둥이에요. 예리한 금속이 깊은 물을 만나면, 그 물은 아주 정확하고 끈질깁니다. 당신의 지혜는 그래요. 부드러워 보이지만, 시간이 지나면 어떤 것도 통과해 버립니다.",
                "당신의 강점은 '끈질긴 추진력'입니다. 다른 사람들이 포기하는 지점에서도 당신은 계속 흐릅니다. 그런데 물처럼 미는 게 아니라, 정확한 지점을 골라 계속 흘러 들어가요. 그래서 당신은 어려운 과제를 결국 완수합니다. 조직에서 '이 사람이 맡으면 어떻게든 끝난다'는 평가가 붙는 이유입니다.",
                "당신의 그림자는 '너무 오래 밀어붙이는 것'입니다. 물은 부드럽지만, 계속 한 곳으로 흐르면 그곳을 뚫습니다. 당신의 끈질김은 무기가 되지만, 때로는 고집이 됩니다. 유연성을 잃고, 자신이 지친 것을 인정하지 못하고, 끝나야 할 것을 계속 붙들고 있죠. 그리고 주변 사람들은 그런 당신을 보면서 말리지 못합니다.",
                "성숙한 壬申은 '흐를 때와 뚫을 때를 구분하는 사람'입니다. 계속 밀어붙이는 대신, 때로는 방향을 바꾸고, 때로는 잠시 멈추는 사람. 그때 당신의 끈질김은 소모가 아니라, 오래 유지되는 추진력이 됩니다."
            ],
            "shadows": [
                "집요함이 지나쳐서, 이미 끝난 일을 계속 붙들고 있습니다.",
                "유연성을 잃어, 방향을 바꿔야 할 때도 계속 밀어붙입니다.",
                "자신이 지친 것을 인정하지 못해, 결국 몸이 강제로 멈추게 합니다."
            ],
            "advice": [
                "이번 주에 '내가 계속 붙들고 있는 것' 세 가지를 적어보세요. 그중 하나는 놓아도 됩니다.",
                "밀어붙이기 전에, '이 방향이 지금도 맞나'를 한 번 확인하세요.",
                "회복 시간을 규칙적으로 확보하세요. 물이 쉬지 않고 흐르면 말라버립니다.",
                "당신이 오래 붙들어 온 지혜를 하나 골라, 누군가에게 나눠주세요. 그게 새로운 흐름을 만듭니다."
            ],
            "keywords": ["바위를 뚫는 인내", "예리한 지혜", "끈질긴 추진", "흐름의 강도"]
        },
        "壬戌": {
            "name": "마른 땅에 스며드는 물", "pillar": "壬戌",
            "hero": "당신은 마른 땅에 스며드는 물입니다. 겉으로는 보이지 않아도, 당신이 지나간 자리에는 생명이 자라나는 사람이죠.",
            "narrative": [
                "당신은 조용한 영향력의 사람입니다. 壬戌(임술)은 魁罡(괴강)에 속하면서, 마른 흙 위에 깊은 물이 앉은 기둥이에요. 물이 마른 땅에 스며들면 표면에는 안 보이지만, 그 아래에서 생명이 자라납니다. 당신의 강함이 딱 그렇습니다. 눈에 띄지 않지만, 당신이 지나간 자리는 조금씩 달라져 있어요.",
                "당신의 강점은 '원칙과 유연함의 결합'입니다. 魁罡은 원칙의 기둥이지만, 水는 유연함의 기운이에요. 그래서 당신은 자신의 원칙을 지키면서도, 그것을 관철하는 방식에서는 아주 부드럽습니다. 사람들은 당신의 원칙에 압도되지 않으면서도, 결국 당신의 뜻대로 흘러가게 됩니다.",
                "당신의 그림자는 '너무 스며들어 자신을 잃는 것'입니다. 마른 땅에 스며드는 물은 결국 땅의 일부가 됩니다. 당신도 다른 사람의 삶에 너무 깊이 스며들어서, 정작 자신이 무엇을 원하는지 잊어버릴 때가 있어요. 그리고 당신의 영향력을 스스로 인정하지 않아, 자신이 얼마나 중요한 사람인지 모릅니다.",
                "성숙한 壬戌은 '스며들되 중심을 잃지 않는 사람'입니다. 다른 사람의 삶에 스며들어 영향을 주면서도, 자신의 물줄기는 유지하는 사람. 그때 당신의 조용한 영향력은 사람들이 뒤늦게 알아차리는, 아주 깊은 힘이 됩니다."
            ],
            "shadows": [
                "다른 사람의 삶에 너무 스며들어, 자신의 물줄기를 잃습니다.",
                "자신의 영향력을 인정하지 않아, 과소평가받고도 모릅니다.",
                "원칙을 지키다가, 정작 자신의 필요를 계속 뒤로 미룹니다."
            ],
            "advice": [
                "이번 주에 당신이 영향을 준 사람이나 상황을 하나 떠올려 보세요. 그게 당신의 힘입니다.",
                "다른 사람의 삶에 스며들기 전에, '이건 그 사람이 스스로 할 수 있는 일인가'를 물어보세요.",
                "당신의 원칙 중 하나를 이번 주에는 당신 자신을 위해 써보세요.",
                "당신의 물줄기를 유지할 수 있는 작은 루틴을 하루에 하나 만드세요."
            ],
            "keywords": ["魁罡", "스며드는 지혜", "조용한 영향력", "마른 땅의 생명"]
        }
    },
    "en": {
        "壬子": {
            "name": "Frozen Deep Sea", "pillar": "壬子",
            "hero": "You're a winter sea. Hard as ice on the surface, and beneath it, a current that never stops moving.",
            "narrative": [
                "You're the purest form of 壬. 壬子 is 壬 sitting in its own 祿 (Lu) — double water, layered on itself. Your wisdom doesn't shake, your field of vision is wide, your thinking is deep. People get a strange sense in your presence: this person is different.",
                "Your strength is depth of thought. Where others see only the surface, you see the machinery under a situation. You don't rush to conclusions, and the conclusions you arrive at after letting things settle tend to be right. So organizations end up trusting you with the biggest judgments.",
                "Your shadow is emotion locked under the ice. The surface of a winter sea is ice, but underneath it's still moving — and so are you. You look calm, but you carry deep currents. The problem is the ice keeps them from reaching the people around you. If you've been called cold or hard to read, it's not because you don't care — it's because you carry too much too deep.",
                "A mature Im-Ja knows how to melt their own ice. Keeping the deep wisdom, and letting some of that inner water come up. Then your depth stops being distance and becomes wisdom people want to lean on."
            ],
            "shadows": [
                "Holding feelings under the ice so long that people misread your temperature.",
                "Delaying decisions long enough that the opening closes.",
                "Your depth reads as distance, so intimacy takes a long time to build."
            ],
            "advice": [
                "Once this week, bring one kept feeling up. Small is fine.",
                "Pick one decision to make by a fixed deadline. It doesn't have to be perfect.",
                "Explain one piece of your wisdom to someone. Wisdom sharpens when shared.",
                "Even the sea needs earth. Give your day one small ritual that doesn't move."
            ],
            "keywords": ["deep wisdom", "currents under ice", "wide field of vision", "long sight"]
        },
        "壬寅": {
            "name": "Sea Meeting Spring", "pillar": "壬寅",
            "hero": "You're a sea meeting spring. Thawed water feeding trees — your wisdom is the kind that makes people grow.",
            "narrative": [
                "You grow people with your wisdom. 壬寅 is water giving birth to wood. Water feeds the tree — and that's you, quietly supplying what helps a person's potential rise. Not a flashy kind of leadership. The kind that pours water on a root.",
                "Your strength is wide perspective. When you look at a person, you see not who they are now but the possibility ahead, and you build the conditions for that possibility to actually grow. People you cultivate end up saying later, 'If not for that person back then.' Your contribution gets recognized after the fact.",
                "Your shadow is giving too much of your flow away. Water flows, and you give without asking much in return. But water that only flows loses its own channel. You help other people's growth and keep postponing your own. And at the moment a decision is needed, you tell yourself, 'It'll just flow somewhere' — and let it pass.",
                "A mature Im-In knows they're part of the water too. Growing yourself in the same season you grow others. Then your flow isn't a one-season current — it becomes a river that keeps people alive for years."
            ],
            "shadows": [
                "Tending other people's growth while postponing your own indefinitely.",
                "Avoiding decisions with 'it'll just flow somewhere' when a choice is actually needed.",
                "Valuing your contribution so low that you're stingy with yourself."
            ],
            "advice": [
                "Put your own growth on the calendar first this week.",
                "Pick one decision and make it by the deadline. Don't let it flow past you.",
                "Give your wisdom a concrete form — words or written text. Flowing alone doesn't leave a trace.",
                "Set aside a place among the people you cultivate for yourself."
            ],
            "keywords": ["spring sea", "wisdom that grows people", "wide perspective", "growing together"]
        },
        "壬辰": {
            "name": "Sea Where Dragons Live", "pillar": "壬辰",
            "hero": "You're a sea where dragons live. Ordinary on the surface, with the kind of potential beneath that could move the world.",
            "narrative": [
                "You're the kind of large vessel that doesn't reveal itself easily. 壬辰 belongs to the 魁罡 (Commander) set of pillars. 辰 is the dragon's earth, and it stores water. You look unremarkable most of the time — and then at a decisive moment, your weight shows. People say later, 'Wait — that person was that person?'",
                "Your strength is seeing the big picture. You sketch the large frame before the small tactics, and inside it you arrange people and resources. In the decisive moment, while everyone else is shaking, you quietly hold the center. That's the real power of 壬辰 — quiet most of the time, moving the world when it counts.",
                "Your shadow is holding the potential without releasing it. A dragon that stays in the cave forever becomes a legend. Same for you. You're sketching the big picture but not bringing it out, so people never find out what you carry. And over time, the label 'what does that person actually do?' starts to attach.",
                "A mature Im-Jin knows how to wake the dragon. Keeping the big picture, and bringing it into the world through small beginnings. Then your presence stops being intimidating and becomes the thing people rely on."
            ],
            "shadows": [
                "Holding the potential and never releasing it, so people underestimate you.",
                "Sketching the big picture and missing the small execution.",
                "Waiting so long for the decisive moment that it never arrives."
            ],
            "advice": [
                "Bring one piece of your potential out this week as a concrete action.",
                "Pick one 'small start' inside the big picture that you can do right now.",
                "Explain your plan to someone. Kept only in your head, the dragon stays asleep.",
                "Stop waiting for the decisive moment. Make one this week."
            ],
            "keywords": ["魁罡", "large vessel", "sleeping dragon", "decisive weight"]
        },
        "壬午": {
            "name": "Sea Holding Fire", "pillar": "壬午",
            "hero": "You're a sea holding fire. Cool and deep on the surface, with heat running through you underneath.",
            "narrative": [
                "You hold cool judgment and hot passion at once. 壬午 is deep water with fire resting on it. Water and fire fight each other — but in one person, they create a very particular temperature. You look calm and rational from outside, while a hot current runs inside.",
                "Your strength is using both at the same time. Cool judgment paired with hot passion is rare. That's why, at important moments, you don't get swept up emotionally and yet still make decisions that move people. The duality is your weapon.",
                "Your shadow is the misreading that comes from the temperature gap. If you carry hot feelings but look cold, people around you take your distance as indifference. And when the heat comes out suddenly, it catches them off guard. To someone who doesn't know about your duality, you become 'the person I can't quite read.'",
                "A mature Im-O integrates both sides. Weaving hot passion and cool judgment into one voice. Then your duality stops being a shake and becomes the kind of deep passion people want to rely on."
            ],
            "shadows": [
                "The gap between surface and interior makes people misread your sincerity.",
                "Sudden emotional outbursts surprise people who read you as steady.",
                "Hiding the heat so long that you exhaust yourself."
            ],
            "advice": [
                "Once this week, say one of your hot feelings out loud. What you love, what you want.",
                "When emotion rises, ask: is this the moment to express it, or to give it more shape?",
                "Tell someone close, 'I look calm but I run hot inside.' It clears years of misreading.",
                "Find one hobby or exercise that lets you discharge the heat healthily."
            ],
            "keywords": ["cool passion", "duality", "deep fire", "two-faced wisdom"]
        },
        "壬申": {
            "name": "Water Piercing Stone", "pillar": "壬申",
            "hero": "You're water that pierces stone. Gentle to look at, and, given time, impossible to stop.",
            "narrative": [
                "You hold sharpness and wisdom together. 壬申 is metal giving birth to water. Sharp metal meeting deep water makes water extremely precise and persistent. Your wisdom is like that. It looks soft, but give it time and it gets through anything.",
                "Your strength is persistent drive. Where other people quit, you keep flowing. But not by pushing like a hammer — by finding the exact spot and continuing to flow into it. So difficult projects do get finished by you. That's why organizations say, 'If this person takes it, it somehow gets done.'",
                "Your shadow is pushing too long. Water is gentle, but if it keeps flowing in one spot, it cuts through. Your persistence is a weapon that sometimes becomes stubbornness. You lose flexibility, can't admit you're tired, and keep holding something that should have ended. And the people around you can't stop you.",
                "A mature Im-Shin knows the difference between flowing and piercing. Sometimes changing direction, sometimes stopping, instead of always pushing. Then your persistence becomes sustained drive instead of exhaustion."
            ],
            "shadows": [
                "Persistence taken so far that you keep holding onto something already finished.",
                "Losing flexibility, pushing the same direction when a turn was needed.",
                "Unable to admit exhaustion until your body forces you to stop."
            ],
            "advice": [
                "List three things you're holding this week. One of them can be put down.",
                "Before pushing, ask once: is this direction still right?",
                "Give yourself regular recovery. Water that never rests runs dry.",
                "Share one piece of wisdom you've been carrying for a long time. It opens a new channel."
            ],
            "keywords": ["piercing persistence", "sharp wisdom", "relentless drive", "strength of flow"]
        },
        "壬戌": {
            "name": "Water Seeping into Dry Earth", "pillar": "壬戌",
            "hero": "You're water seeping into dry earth. Invisible from the surface — and life grows where you've passed.",
            "narrative": [
                "You're the quiet kind of influence. 壬戌 belongs to the 魁罡 (Commander) set, and it's deep water resting on dry earth. Water seeping into dry earth is invisible at the surface, but underneath, life grows. That's exactly your strength. You don't stand out, and yet the places you've passed through are quietly different.",
                "Your strength is principle combined with flexibility. 魁罡 is a principled pillar, but water is fluid. So you keep your principle while being very soft in how you carry it through. People don't feel run over by your values, and yet they end up moving in the direction you were flowing toward.",
                "Your shadow is seeping so far in that you lose yourself. Water that seeps into dry earth becomes part of the earth. You get so deeply into other people's lives that you forget what you actually want. And because you don't recognize your own influence, you don't realize how significant you are.",
                "A mature Im-Xu seeps in without losing the center. Influencing other people's lives while keeping your own channel. Then your quiet influence becomes the kind of power people only realize later, and deeply."
            ],
            "shadows": [
                "Seeping so far into other people's lives that you lose your own channel.",
                "Not recognizing your own influence, and so underestimating yourself.",
                "Keeping principles while continuously pushing your own needs to the back."
            ],
            "advice": [
                "Recall one person or situation you've influenced this week. That's your power.",
                "Before seeping in, ask: can this person do this on their own?",
                "Use one of your principles for yourself this week.",
                "Build one small daily ritual that keeps your own channel intact."
            ],
            "keywords": ["魁罡", "seeping wisdom", "quiet influence", "life in dry earth"]
        }
    }
}


def main() -> int:
    ap = argparse.ArgumentParser(description="壬 일간 6일주 추가")
    ap.add_argument("--force", action="store_true", help="스텁 덮어쓰기")
    args = ap.parse_args()

    print("=== 壬 일간 6일주 추가 (壬子, 壬寅, 壬辰, 壬午, 壬申, 壬戌) ===")
    
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