#!/usr/bin/env python3
"""
己 일간 6일주 추가 (己丑, 己卯, 己巳, 己未, 己酉, 己亥).
己는 음토(陰土)의 기운으로, 정원의 흙처럼 기르고 돌보는 성향입니다.
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
        "己丑": {
            "name": "얼어붙은 밭", "pillar": "己丑",
            "hero": "당신은 얼어붙은 땅 아래 봄을 저장한 밭입니다. 겉은 차갑고 단단하지만, 그 아래에는 아직 꺼내지 않은 생명력이 잠들어 있죠.",
            "narrative": [
                "당신은 쉽게 드러내지 않는 사람입니다. 己丑(기축)은 겨울의 축축한 흙이 두 겹으로 겹친 기둥이에요. 그래서 당신의 정서는 늘 안쪽에 머물고, 겉으로 보이는 온도는 실제 온도보다 훨씬 낮습니다. 사람들은 당신을 '차분하다'거나 '무던하다'고 기억하는데, 그건 당신이 느끼지 않아서가 아니라 느낌을 안에 저장하기 때문입니다.",
                "당신의 강점은 '저축'의 감각입니다. 己丑은 씨앗을 땅속에 묻어두는 흙이에요. 당신은 돈을, 감정을, 신뢰를, 시간을 함부로 쓰지 않습니다. 지금 이 순간에는 아껴두고, 정말 필요한 때에 꺼내는 재주가 있습니다. 그래서 당신은 위기에서 오히려 강해요. 다른 사람들이 텅 비었을 때, 당신의 저장고에는 아직 남아 있는 게 있습니다.",
                "당신의 그림자는 '너무 오래 얼어 있는 것'입니다. 己丑은 봄을 저장하지만, 그 봄을 계속 꺼내지 않으면 결국 흙 자체가 굳어버립니다. 당신이 안에 담아둔 것들을 충분히 꺼내지 않으면, 사람들은 당신 곁에 있어도 당신의 진심을 알 수 없어요. '이 사람은 늘 괜찮다'는 평가 뒤에, 당신 혼자만 아는 피로가 쌓여 갑니다.",
                "성숙한 己丑은 '저장한 봄을 꺼낼 줄 아는 사람'입니다. 아껴둔 감정, 쌓아둔 신뢰, 묻어둔 재능을 적절한 순간에 꺼내는 사람. 그때 당신의 차가움은 냉정이 아니라 깊은 안정이 되고, 사람들은 당신 곁에서 진짜 봄을 경험합니다."
            ],
            "shadows": [
                "안에 담아둔 감정을 너무 오래 꺼내지 않아, 주변 사람들이 당신의 온도를 오해합니다.",
                "신뢰를 아끼다가, 정작 필요한 순간에 도움을 청하지 못하고 혼자 짊어집니다.",
                "저축의 감각이 지나쳐서, 스스로에게도 너무 인색해질 때가 있습니다."
            ],
            "advice": [
                "이번 주에 한 번, 평소 아껴두던 감정 한 가지를 꺼내보세요. 작은 것도 괜찮습니다.",
                "당신이 혼자 해결하려는 일 하나를 골라, 누군가에게 먼저 도움을 청해보세요.",
                "지금 이 순간 '내가 왜 이걸 참고 있지?' 스스로에게 물어보세요. 답이 나오면 그중 하나는 꺼내도 됩니다.",
                "당신의 저장고가 넘치지 않도록, 규칙적으로 자신을 위한 지출을 하나 만들어 두세요. 돈이든 시간이든."
            ],
            "keywords": ["겨울 흙", "깊은 저장", "인내의 힘", "꺼내지 않은 봄"]
        },
        "己卯": {
            "name": "봄을 여는 밭", "pillar": "己卯",
            "hero": "당신은 봄기운이 스며드는 밭입니다. 나무의 뿌리가 땅을 뚫고 올라오듯, 당신은 사람들 사이에서 성장의 통로가 됩니다.",
            "narrative": [
                "당신은 성장을 촉진하는 사람입니다. 己卯(기묘)는 부드러운 흙 위에 봄나무의 기운이 앉은 기둥이에요. 나무는 흙을 뚫고 자라지만, 동시에 흙이 나무에게 자리를 내주죠. 당신은 그래서 사람들 곁에서 '나도 뭔가 해볼 수 있을 것 같다'는 감각을 자연스럽게 만들어냅니다.",
                "당신의 강점은 유연한 리더십입니다. 강하게 밀어붙이지 않고, 상대가 스스로 자라도록 공간을 내주는 방식이에요. 그래서 당신이 이끄는 팀은 당신이 없을 때도 스스로 움직입니다. 당신은 지시하는 사람이 아니라, 뿌리내리게 하는 사람입니다.",
                "당신의 그림자는 '너무 많이 내주는 것'입니다. 봄나무가 흙을 다 써버리면 흙은 척박해집니다. 당신은 다른 사람의 성장을 돕다가 정작 자신의 성장을 늘 뒤로 미룹니다. 그리고 그렇게 자란 사람이 떠나면, 이유를 알 수 없는 상실감이 밀려옵니다. 당신은 그걸 배신이라고 느끼지만, 사실은 당신이 붙잡을 것을 하나도 남겨두지 않았기 때문이에요.",
                "성숙한 己卯는 '자신도 밭의 일부임을 아는 사람'입니다. 다른 사람을 키우는 동시에 자신도 자라는 사람. 그때 당신의 봄은 한 번 오고 마는 계절이 아니라, 몇 년 동안 계속 피어나는 정원이 됩니다."
            ],
            "shadows": [
                "다른 사람의 성장을 돕다가, 자신의 성장은 계속 뒤로 미룹니다.",
                "경계를 세우지 못해, 아무에게나 흙을 내어주고 척박해집니다.",
                "당신이 키운 사람이 떠나면, 이유를 알 수 없는 배신감에 오래 시달립니다."
            ],
            "advice": [
                "이번 주에 자신의 성장을 위해 쓸 시간을 먼저 달력에 넣어두세요. 남는 시간에 하지 말고요.",
                "누군가를 돕고 싶을 때, '이건 이 사람이 스스로 할 수 있는 일인가'를 한 번 물어보세요.",
                "당신이 키운 사람이 떠나면, '이건 성장의 증거다'라고 스스로에게 말해주세요. 붙잡는 게 사랑이 아닙니다.",
                "당신의 봄을 나눌 사람과 당신의 봄을 함께 키울 사람을 구분해 보세요. 후자가 진짜 인연입니다."
            ],
            "keywords": ["성장의 통로", "유연한 리더", "봄나무", "함께 자람"]
        },
        "己巳": {
            "name": "온기를 품은 정원", "pillar": "己巳",
            "hero": "당신은 온기가 스민 정원입니다. 해가 내리쬐는 흙에서 꽃이 피어나듯, 당신 곁에서는 사람과 일이 저절로 익어갑니다.",
            "narrative": [
                "당신은 따뜻함이 자연스럽게 배어 있는 사람입니다. 己巳(기사)는 火가 土를 낳는 기둥이에요. 그래서 당신의 돌봄은 애쓰지 않아도 흘러나옵니다. 다른 사람들은 당신 곁에 있으면 '이 사람이 나를 좋아하는구나'를 굳이 확인하지 않아도 느낍니다.",
                "당신의 강점은 '생산적 돌봄'입니다. 그냥 따뜻한 게 아니라, 실제로 뭔가 자라게 하는 온기예요. 당신이 관심을 기울이는 프로젝트는 이상하게 잘 익어가고, 당신이 챙기는 사람은 조금씩 건강해집니다. 당신은 말없이 밭을 갈고 물을 주는 사람입니다.",
                "당신의 그림자는 '자신을 태우는 온기'입니다. 火生土는 아름다운 구조지만, 火는 土를 낳으면서 스스로를 소모합니다. 당신은 사람들을 돌보다가 어느 순간 완전히 비어버린 자신을 발견합니다. 그리고 그때 사람들은 당신이 왜 갑자기 멀어졌는지 이해하지 못해요. 당신은 설명할 힘조차 없이 조용히 사라지죠.",
                "성숙한 己巳는 '받는 온기도 아는 사람'입니다. 주는 온기와 받는 온기가 균형을 이룰 때, 당신의 정원은 계속 꽃을 피울 수 있습니다. 그때 당신의 돌봄은 소모가 아니라 나눔이 되고, 사람들은 당신 곁에서 오래 머물고 싶어 합니다."
            ],
            "shadows": [
                "돌봄이 지나쳐서, 어느 순간 완전히 비어버린 자신을 발견합니다.",
                "받는 것에 서툴러서, 도움을 주려는 사람을 오히려 불편하게 만듭니다.",
                "자신을 돌보는 일을 늘 뒤로 미루고, 결국 몸이 강제로 멈추게 합니다."
            ],
            "advice": [
                "이번 주에 한 번, 누군가가 당신을 위해 뭔가 해주게 두세요. 거절하지 말고 그냥 받아보세요.",
                "당신이 돌보는 사람 중 한 명에게, 이번에는 당신을 돌봐달라고 부탁해 보세요.",
                "돌보기 전에 스스로에게 물어보세요. '내가 지금 이걸 할 여력이 있나?' 없다면 미뤄도 됩니다.",
                "'내가 없으면 안 돼'라는 감각이 들 때, 정말 그런지 한 번 확인해 보세요. 대부분은 그렇지 않습니다."
            ],
            "keywords": ["따뜻한 정원", "생산적 돌봄", "자연스러운 치유", "주고받는 온기"]
        },
        "己未": {
            "name": "마른 초원", "pillar": "己未",
            "hero": "당신은 여름의 마른 초원입니다. 강한 햇볕을 견디며 스스로 단단해진 땅이죠.",
            "narrative": [
                "당신은 인내로 만들어진 사람입니다. 己未(기미)는 여름의 건조한 흙이 두 겹으로 겹친 기둥이에요. 그래서 당신은 쉽게 흔들리지 않고, 쉽게 지치지도 않습니다. 어려운 상황에서 오히려 더 단단해지는 타입이죠.",
                "당신의 강점은 '관철력'입니다. 한 번 마음먹은 것을 끝까지 밀고 나가는 힘이 있어요. 남들이 중간에 포기하는 일도 당신은 완수합니다. 그래서 당신은 조직에서 '이 사람이 맡으면 끝난다'는 신뢰를 얻습니다. 화려하지 않지만, 결과물로 증명하는 사람입니다.",
                "당신의 그림자는 '너무 건조해지는 것'입니다. 여름 흙은 물을 머금지 못합니다. 당신은 오래 견디는 대신, 유연함을 잃기 쉽습니다. 변화가 필요한 순간에도 고집을 부리거나, 자신의 방식을 끝까지 밀어붙여서 주변 사람들이 지쳐버리기도 합니다. 그리고 무엇보다, 스스로에게 너무 건조합니다. 쉬어야 할 때도 '아직 괜찮다'고 스스로를 설득하죠.",
                "성숙한 己未는 '단단함에 물기를 더한 사람'입니다. 인내와 관철력을 유지하되, 필요할 때 유연하게 물러설 줄 아는 사람. 그때 당신의 초원은 마른 땅이 아니라, 계절마다 다른 꽃이 피는 초원이 됩니다."
            ],
            "shadows": [
                "인내가 지나쳐서, 이미 끝난 일을 계속 붙들고 있습니다.",
                "변화가 필요한 순간에도 고집을 부려, 더 나은 길을 놓칩니다.",
                "자신에게 너무 건조해서, 쉬어야 할 때도 '아직 괜찮다'고 스스로를 속입니다."
            ],
            "advice": [
                "이번 주에 '내가 지금 붙들고 있는 것' 세 가지를 적어보세요. 그중 하나는 놓아도 됩니다.",
                "결정을 내리기 전에 '이건 인내인가, 고집인가' 스스로에게 물어보세요. 둘은 다릅니다.",
                "규칙적으로 물을 주세요. 산책이든, 낮잠이든, 아무것도 안 하는 시간이든. 그게 당신의 물기입니다.",
                "당신이 끝까지 밀어붙이는 일 하나에, 이번 주에는 '중간 점검'을 넣어보세요. 방향이 맞는지 확인하는 겁니다."
            ],
            "keywords": ["여름 흙", "강한 인내", "관철력", "단단한 초원"]
        },
        "己酉": {
            "name": "정교한 화단", "pillar": "己酉",
            "hero": "당신은 정교하게 가꾼 화단입니다. 아름다움과 실용을 동시에 추구하는, 섬세한 손길의 사람이죠.",
            "narrative": [
                "당신은 정밀함과 실용을 함께 지닌 사람입니다. 己酉(기유)는 부드러운 흙 위에 예리한 금속이 앉은 기둥이에요. 그래서 당신은 아름다움을 추구하면서도, 그 아름다움이 실제로 쓸모 있어야 한다고 느낍니다. 화려하지만 비어 있는 것보다, 소박해도 완성도 있는 것을 선호합니다.",
                "당신의 강점은 '완성도'입니다. 당신이 손대는 것에는 이상하게 정성이 배어 있습니다. 디테일 하나하나를 정확하게 다듬고, 전체가 흐트러지지 않게 조율합니다. 그래서 당신이 만든 것, 당신이 고른 것에는 늘 '이 사람 손을 거쳤구나' 싶은 결이 남습니다.",
                "당신의 그림자는 '완벽주의'입니다. 己酉의 정밀함은 아름답지만, 지나치면 스스로를 옥죕니다. 아무도 알아채지 못할 디테일에 몇 시간을 쏟고, 완벽하지 않은 결과물에 오래 실망합니다. 그리고 다른 사람의 결과물에도 같은 잣대를 들이대서, 의도치 않게 상처를 줍니다. 당신의 기준은 당신에게는 자연스럽지만, 다른 사람에게는 벽이 될 수 있어요.",
                "성숙한 己酉는 '기준을 관대함과 함께 쓰는 사람'입니다. 완성도를 유지하되, 그 완성도에 이르지 못하는 사람을 이해할 줄 아는 사람. 그때 당신의 정교함은 압박이 아니라, 사람들이 배우고 싶어 하는 아름다움이 됩니다."
            ],
            "shadows": [
                "완벽하지 않은 결과물에 오래 마음이 붙잡혀, 다음 일로 넘어가기 어렵습니다.",
                "다른 사람에게도 같은 기준을 적용해서, 의도치 않게 상처를 줍니다.",
                "아무도 못 볼 디테일에 에너지를 너무 많이 쏟아, 정작 중요한 일을 놓칩니다."
            ],
            "advice": [
                "이번 주에 일부러 80%에서 멈추는 연습을 한 번 해보세요. 어떤 결과물이든요.",
                "다른 사람의 결과물을 볼 때, '이건 내 기준이 아니라 이 사람의 기준이다'를 먼저 떠올려 보세요.",
                "당신이 자주 던지는 '왜 이 정도밖에 안 됐지'를 '무엇을 해냈지'로 한 번 바꿔보세요.",
                "당신의 완벽주의가 가장 심해지는 순간은 언제인지 관찰해 보세요. 대부분 피로할 때입니다."
            ],
            "keywords": ["정교한 손길", "미감", "실용적 아름다움", "완성도"]
        },
        "己亥": {
            "name": "물 머금은 땅", "pillar": "己亥",
            "hero": "당신은 물을 머금은 비옥한 땅입니다. 풍요로움을 품고도 티를 내지 않는, 깊은 사람이죠.",
            "narrative": [
                "당신은 풍요로움을 품은 사람입니다. 己亥(기해)는 부드러운 흙 위에 깊은 물이 앉은 기둥이에요. 흙이 물을 머금으면 아주 비옥해지듯, 당신은 지혜와 감정과 경험을 안에 품고 있습니다. 그리고 그 풍요로움을 겉으로 자랑하지 않아요. 사람들은 시간이 지나서야 당신이 얼마나 많은 것을 담고 있는지 알게 됩니다.",
                "당신의 강점은 '유연한 실무 능력'입니다. 己亥는 땅의 안정과 물의 유연함을 동시에 지녔습니다. 그래서 당신은 계획적이면서도 즉흥적일 수 있고, 원칙을 지키면서도 필요할 때 방향을 바꿀 줄 압니다. 어떤 환경에서도 살아남는 사람이에요.",
                "당신의 그림자는 '물에 잠기는 것'입니다. 물이 너무 많으면 흙이 흙의 역할을 못합니다. 당신은 감정이 깊고 사고가 많아서, 때때로 그 물결에 휩쓸립니다. 결정을 미루고, 생각이 꼬리를 물고, 정작 필요한 순간에 움직이지 못하죠. 그리고 그 사이에 기회는 지나갑니다.",
                "성숙한 己亥는 '물을 품되 땅의 중심을 지키는 사람'입니다. 깊은 감정과 지혜를 유지하되, 결정할 때는 단호해지는 사람. 그때 당신의 풍요로움은 사람들이 기대고 싶은 지혜가 되고, 당신의 유연함은 방향 상실이 아니라 지혜로운 적응이 됩니다."
            ],
            "shadows": [
                "생각이 너무 많아 결정을 미루고, 그 사이에 기회를 놓칩니다.",
                "감정의 물결에 휩쓸려, 정작 필요한 순간에 움직이지 못합니다.",
                "자신의 풍요로움을 너무 감춰서, 주변 사람들이 당신의 진가를 모릅니다."
            ],
            "advice": [
                "이번 주에 결정해야 할 것을 하나 골라, 정해진 기한 안에 반드시 결정하세요. 완벽하지 않아도 됩니다.",
                "감정이 올라올 때, '이건 정보인가, 아니면 나를 잠기게 하는 파도인가' 스스로에게 물어보세요.",
                "당신이 아는 것 하나를 누군가에게 알려주세요. 당신의 풍요로움은 나눌 때 더 커집니다.",
                "물에는 땅이 필요합니다. 당신의 하루에 '고정된 땅' 하나를 만드세요. 같은 시간에 하는 작은 의식 같은 것."
            ],
            "keywords": ["비옥함", "깊은 지혜", "유연한 실무", "품위 있는 풍요"]
        }
    },
    "en": {
        "己丑": {
            "name": "Frozen Field", "pillar": "己丑",
            "hero": "You're a field holding spring underground. Cold and solid on the surface, with an unfreed life force still asleep beneath.",
            "narrative": [
                "You don't show yourself easily. 己丑 is damp winter earth layered on itself. Your emotions stay inside, and the temperature people see is much cooler than the temperature you actually feel. People remember you as composed, or even bland. It's not because you don't feel — it's because you store what you feel rather than spending it.",
                "Your strength is the instinct to save. 己丑 is soil that buries seeds. You don't spend money, emotion, trust, or time carelessly. You hold them for the right moment and then release them with precision. That's why you're stronger in a crisis than most people. When everyone else is empty, your storehouse still has something in it.",
                "Your shadow is staying frozen too long. 己丑 stores spring, but if you never open the storehouse, the soil itself hardens. If you don't let out what you've been holding, people can't read your heart even when they're standing next to you. 'Always fine' gets written on you, and beneath that label your private fatigue quietly stacks up.",
                "A mature Ji-Chou knows how to release the stored spring. Opening the kept emotion, the banked trust, the buried gift at the right moment. Then your coolness stops being distance and becomes deep stability, and the people around you get to experience actual spring."
            ],
            "shadows": [
                "Keeping feelings inside so long that people misread your temperature entirely.",
                "Conserving trust so tightly that you don't ask for help when you need it.",
                "The saving instinct taken so far it makes you stingy with yourself."
            ],
            "advice": [
                "Once this week, take out one feeling you've been keeping. Small is fine.",
                "Pick one thing you're solving alone and ask for help before you need it.",
                "Ask yourself, 'Why am I holding this in right now?' Of the answers, one can be let out.",
                "Set up a regular spend on yourself — money or time — so the storehouse doesn't overflow."
            ],
            "keywords": ["winter earth", "deep storage", "patient strength", "stored spring"]
        },
        "己卯": {
            "name": "Field Opening Spring", "pillar": "己卯",
            "hero": "You're a field spring is already seeping into. Roots push through the soil, and you are the passage where growth happens.",
            "narrative": [
                "You're the person who makes growth possible. 己卯 is soft earth with spring wood sitting on top. Wood breaks through earth, but earth also has to yield a place for the tree. That's the dynamic you carry — people feel 'maybe I could try too' when they're near you.",
                "Your strength is flexible leadership. You don't push hard. You make room for someone else to grow on their own, and the team you lead keeps moving even when you step away. You're not the one who gives instructions — you're the one who lets things take root.",
                "Your shadow is giving away too much. If the spring tree uses all the soil, the earth goes barren. You help other people grow and postpone your own growth indefinitely. And when someone you cultivated leaves, a loss you can't quite explain arrives. You read it as betrayal, but it's usually because you left nothing behind for yourself to hold.",
                "A mature Ji-Mao knows they're part of the field too. Growing yourself in the same season you grow others. Then your spring isn't a season that passes — it becomes a garden that keeps blooming year after year."
            ],
            "shadows": [
                "Helping others grow while postponing your own growth indefinitely.",
                "Unable to hold a boundary, you give your soil to anyone and end up barren.",
                "When someone you cultivated leaves, you carry a betrayal you can't name for a long time."
            ],
            "advice": [
                "Put your own growth on the calendar first this week. Don't fit it in afterwards.",
                "Before you help someone, ask: can this person do this themselves?",
                "When someone leaves, tell yourself, 'This is proof of growth.' Holding on isn't love.",
                "Separate the people you share your spring with from the people you grow spring with. The second kind is the real connection."
            ],
            "keywords": ["passage of growth", "flexible leader", "spring tree", "growing together"]
        },
        "己巳": {
            "name": "Garden Filled with Warmth", "pillar": "己巳",
            "hero": "You're a garden warmed by the sun. Fruit ripens without effort around you — people, projects, and small living things.",
            "narrative": [
                "Warmth comes naturally to you. 己巳 is fire giving birth to earth. So your care flows without you having to force it. People don't have to check whether you like them — they can feel it just by being near you.",
                "Your strength is productive care. It's not just tenderness for its own sake — it actually makes things grow. Projects you pay attention to ripen in unusual ways, and people you look after get a little healthier. You're the one quietly tilling the field and watering the beds.",
                "Your shadow is warmth that consumes you. 火生土 is beautiful as a structure — but fire feeds earth and uses itself up in the process. You look after people until one day you find yourself completely empty, and the people around you don't understand why you suddenly went distant. You don't even have the energy to explain.",
                "A mature Ji-Si knows how to receive warmth too. When giving and receiving balance, your garden keeps blooming. Then your care becomes sharing rather than depletion, and the people around you want to stay for a long time."
            ],
            "shadows": [
                "Caring so much that you suddenly find yourself completely empty.",
                "So unpracticed at receiving that you make it awkward for people who want to help you.",
                "Putting your own care last until your body forces you to stop."
            ],
            "advice": [
                "Once this week, let someone do something for you. Don't decline — just receive it.",
                "Ask one of the people you care for to care for you this time.",
                "Before you give care, ask: 'Do I have the capacity for this right now?' If not, you can defer.",
                "When you feel 'they can't manage without me,' check. Most of the time, they can."
            ],
            "keywords": ["warm garden", "productive care", "natural healing", "exchanged warmth"]
        },
        "己未": {
            "name": "Dry Meadow", "pillar": "己未",
            "hero": "You're a summer meadow. Baked hard under the sun, and made more solid by it.",
            "narrative": [
                "You've been shaped by endurance. 己未 is dry summer earth layered on itself. You don't shake easily, and you don't wear out easily. You get harder, not softer, under difficulty.",
                "Your strength is follow-through. Once you set your mind, you push it through to the end. What other people abandon halfway, you finish. So organizations end up saying, 'If this person takes it, it's done.' You don't perform — you prove yourself through the result.",
                "Your shadow is drying out. Summer earth can't hold water. You endure for a long time, but you lose flexibility. When a change is needed, you may hold your ground anyway, or insist on your way until the people around you run out. And you're dry with yourself too — even when you should rest, you convince yourself you're still fine.",
                "A mature Ji-Wei brings moisture to the firmness. Keeping the patience and the follow-through, and adding flexibility where it's needed. Then your meadow isn't dry ground — it's a meadow that flowers in a different color each season."
            ],
            "shadows": [
                "So much endurance that you keep holding onto something that's already over.",
                "Holding your ground when a change is what the moment actually needed.",
                "So dry with yourself that you convince yourself you're fine when you should rest."
            ],
            "advice": [
                "List three things you're holding onto this week. One of them can be put down.",
                "Before deciding, ask yourself: is this patience, or is this stubbornness? They're not the same.",
                "Water yourself regularly. A walk, a nap, an hour of nothing. That's your moisture.",
                "Add a midpoint check-in to the thing you're pushing through. Confirm the direction is still right."
            ],
            "keywords": ["summer earth", "strong endurance", "follow-through", "solid meadow"]
        },
        "己酉": {
            "name": "Precise Flowerbed", "pillar": "己酉",
            "hero": "You're a carefully tended flowerbed. A person with a delicate hand, always looking for beauty that actually serves.",
            "narrative": [
                "You hold precision and practicality at the same time. 己酉 is soft earth with a sharp metal edge on top. So you want beauty, but you want that beauty to do something useful. You prefer the modest and finished over the showy and empty.",
                "Your strength is craftsmanship. Whatever you touch has visible care in it. You work every detail into place and keep the whole thing from falling out of tune. What you make and what you choose carries a signature — 'this passed through that person's hands.'",
                "Your shadow is perfectionism. The precision of 己酉 is beautiful, but pushed too far it starts to close in on you. Hours on a detail no one will notice. Long disappointment over results that weren't quite right. And you apply the same standard to other people, which can hurt them without meaning to. Your bar is natural to you — but to others it can be a wall.",
                "A mature Ji-You uses the standard with generosity. Keeping the quality bar, and understanding people who can't reach it yet. Then your precision stops being pressure and becomes the kind of beauty people want to learn."
            ],
            "shadows": [
                "Stuck on imperfect results long enough that you can't move on to the next thing.",
                "Applying your bar to other people and hurting them without meaning to.",
                "Burning energy on details no one will see, and missing the thing that mattered."
            ],
            "advice": [
                "Once this week, practice stopping at 80%. Any result.",
                "When you look at someone else's work, remind yourself first: this is their bar, not mine.",
                "Turn one 'why is it only this good?' into 'what did I actually make?'",
                "Notice when the perfectionism peaks. It's usually when you're tired."
            ],
            "keywords": ["delicate hand", "aesthetic sense", "useful beauty", "craftsmanship"]
        },
        "己亥": {
            "name": "Water-Filled Earth", "pillar": "己亥",
            "hero": "You're fertile ground soaked through with water. Deep, quiet, carrying richness you never show off.",
            "narrative": [
                "You carry abundance. 己亥 is soft earth with deep water resting on it. Earth soaked with water becomes very fertile — and that's you. You hold wisdom, emotion, and experience inside, and you don't advertise any of it. People find out later how much you were carrying.",
                "Your strength is flexible execution. 己亥 has the stability of earth and the fluidity of water at once. You can be planned and improvisational, principled and able to change direction when the situation calls for it. You survive in almost any environment.",
                "Your shadow is getting waterlogged. If there's too much water, earth stops behaving like earth. Your feelings run deep and your thoughts move fast, and sometimes that current sweeps you up. You delay decisions, your thoughts spiral, and the moment that needed movement passes you by.",
                "A mature Ji-Hai holds the water while keeping the earth's center. Keeping the depth and the wisdom, and becoming decisive when a decision is actually required. Then your abundance becomes wisdom people lean on, and your flexibility becomes wise adaptation instead of lost direction."
            ],
            "shadows": [
                "Thinking so much that you miss the moment to act.",
                "Swept up by your own emotional current just when you needed to move.",
                "Hiding your abundance so well that people never learn what you carry."
            ],
            "advice": [
                "Pick one decision to make this week and make it within a fixed deadline. It doesn't have to be perfect.",
                "When emotion rises, ask: is this information, or is this a wave pulling me under?",
                "Teach someone one thing you know. Your abundance grows when you share it.",
                "Water needs earth. Give your day one fixed piece of ground — a small ritual at the same time."
            ],
            "keywords": ["fertility", "deep wisdom", "flexible execution", "quiet abundance"]
        }
    }
}


def main() -> int:
    ap = argparse.ArgumentParser(description="己 일간 6일주 추가")
    ap.add_argument("--force", action="store_true", help="스텁 덮어쓰기")
    args = ap.parse_args()

    print("=== 己 일간 6일주 추가 (己丑, 己卯, 己巳, 己未, 己酉, 己亥) ===")
    
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