#!/usr/bin/env python3
"""
辛 일간 6일주 추가 (辛丑, 辛卯, 辛巳, 辛未, 辛酉, 辛亥).
辛은 음금(陰金)의 기운으로, 세공된 보석처럼 정교하고 미감이 뛰어난 성향입니다.
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
        "辛丑": {
            "name": "겨울 화원의 보석", "pillar": "辛丑",
            "hero": "당신은 겨울 화원에 놓인 보석입니다. 추운 땅 아래 묻혀 있지만, 빛이 닿는 순간 누구보다 정교하게 빛나는 사람이죠.",
            "narrative": [
                "당신은 절제된 아름다움을 지닌 사람입니다. 辛丑(신축)은 차갑고 축축한 흙 위에 세공된 금속이 앉은 기둥이에요. 그래서 당신은 감정을 크게 드러내지 않지만, 그 안에 담긴 것은 유난히 정교합니다. 사람들은 당신을 '조용한 사람'으로 기억하다가, 어느 순간 당신이 만든 것, 당신이 고른 것에서 이상하게 '정성'을 느낍니다.",
                "당신의 강점은 '감춰진 완성도'입니다. 남들이 알아채지 않아도 당신은 기준을 지킵니다. 화려하게 티 내지 않지만, 당신의 손을 거친 것에는 대체로 흐트러짐이 없어요. 이건 노력이라기보다 몸에 밴 감각입니다. 당신은 '이 정도면 됐다'와 '이건 아니다' 사이의 아주 미세한 선을 본능적으로 알아챕니다.",
                "당신의 그림자는 '알아봐주지 않는 것에 지치는 것'입니다. 겨울 화원의 보석은 누가 보러 오지 않으면 그냥 차가운 돌이에요. 당신은 자신의 정성을 스스로 인정하지 않고, 남이 알아봐주길 조용히 기다립니다. 그 기다림이 길어지면 서운함이 되고, 서운함이 길어지면 스스로의 기준을 의심하게 됩니다.",
                "성숙한 辛丑은 '자신의 빛을 스스로 아는 사람'입니다. 누가 봐주지 않아도 자신의 완성도를 스스로 인정하고, 필요할 때는 스스로 빛을 꺼내 보여줄 줄 아는 사람. 그때 당신의 정교함은 더 이상 감춰진 보석이 아니라, 사람들이 찾아와 머무는 화원이 됩니다."
            ],
            "shadows": [
                "정성을 쏟았는데 알아봐주지 않으면, 조용히 서운함을 쌓아둡니다.",
                "자신의 완성도를 스스로 인정하지 않아, 늘 부족한 느낌에 시달립니다.",
                "감정을 잘 드러내지 않다 보니, 가까운 사람들조차 당신의 진심을 오해합니다."
            ],
            "advice": [
                "이번 주에 당신이 이룬 작은 것 하나를, 누가 알아봐주지 않아도 스스로에게 소리 내어 칭찬해 주세요.",
                "서운함이 쌓이기 전에, 가까운 사람에게 '이거 봐줘서 고마워' 대신 '이거 나 좀 봐줬으면 좋겠어'라고 말해보세요.",
                "당신의 결과물 중 하나를 다른 사람에게 보여주세요. 완벽하지 않아도 괜찮습니다.",
                "겨울 화원에도 봄은 옵니다. 지금이 덜 빛나는 시기라면, 그건 당신의 실패가 아니라 계절입니다."
            ],
            "keywords": ["감춰진 완성도", "절제된 미감", "겨울의 정성", "스스로 인정하기"]
        },
        "辛卯": {
            "name": "봄 정원의 옥", "pillar": "辛卯",
            "hero": "당신은 봄 정원에 놓인 옥입니다. 자라나는 것들 사이에서 조용히 빛나며, 그 성장을 섬세하게 돕는 사람이죠.",
            "narrative": [
                "당신은 정교함과 성장을 함께 지닌 사람입니다. 辛卯(신묘)는 세공된 금속 위에 봄나무의 기운이 앉은 기둥이에요. 그래서 당신은 아름다움을 추구하면서도, 그 아름다움이 실제로 자라나야 한다고 느낍니다. 화려하게 피어나는 것보다, 시간을 두고 정성스럽게 가꾸는 쪽을 선호하죠.",
                "당신의 강점은 '섬세한 정원사'의 감각입니다. 사람이든 프로젝트든, 자라나는 데 필요한 것을 정확히 알아채고 조용히 공급합니다. 화려한 리더십이 아니라, 뒤에서 물과 빛을 조율하는 사람이에요. 그래서 당신이 키운 것들은 시간이 지나면 유난히 단단하게 자리 잡습니다.",
                "당신의 그림자는 '완벽한 조건을 기다리는 것'입니다. 봄 정원의 옥은 흙이 준비되고, 빛이 맞고, 물이 적당해야 빛납니다. 당신은 그 조건이 갖춰지지 않으면 스스로를 꺼내지 않습니다. 그런데 그 조건은 생각보다 오래 오지 않아요. 기다리는 사이에 봄은 지나가고, 당신의 옥은 여전히 흙 속에 있습니다.",
                "성숙한 辛卯는 '조건이 아니라 타이밍을 아는 사람'입니다. 완벽하지 않아도 지금 꺼내 보여줄 줄 아는 사람. 그때 당신의 정교함은 기다림이 아니라 성장이 되고, 당신이 가꾼 것들이 당신과 함께 자라납니다."
            ],
            "shadows": [
                "완벽한 조건을 기다리다가, 정작 시작할 수 있는 봄을 놓칩니다.",
                "자라나는 것을 돕다가, 자신의 성장은 계속 미룹니다.",
                "섬세함이 지나쳐서, 조금 흐트러진 것에도 오래 마음이 걸립니다."
            ],
            "advice": [
                "이번 주에 '조건이 다 갖춰지지 않아도' 시작할 수 있는 일 하나를 골라 시작해 보세요.",
                "당신이 키우는 것들 사이에, 당신 자신을 위한 자리를 하나 만들어 두세요.",
                "완벽한 결과물이 아니어도 누군가에게 보여주세요. 세상은 생각보다 너그럽습니다.",
                "지금 이 봄이 언제까지 갈지 스스로에게 물어보세요. 그게 당신의 타이밍입니다."
            ],
            "keywords": ["섬세한 정원사", "세련된 성장", "유연한 기준", "봄의 옥"]
        },
        "辛巳": {
            "name": "열기 속의 보석", "pillar": "辛巳",
            "hero": "당신은 열기 속에서 벼려진 보석입니다. 뜨거운 압박이 오히려 당신을 더 정교하게 만드는 사람이죠.",
            "narrative": [
                "당신은 압박 속에서 더 선명해지는 사람입니다. 辛巳(신사)는 세공된 금속 위에 뜨거운 불기운이 앉은 기둥이에요. 금속이 불을 만나면 강해지거나 녹아내리는데, 당신은 강해지는 쪽입니다. 어려운 상황에서 오히려 집중력이 올라가고, 정밀함이 살아나죠.",
                "당신의 강점은 '압박 속의 예리함'입니다. 남들이 흐트러질 때 당신은 더 정확해집니다. 중요한 발표, 결정적인 순간, 마감이 다가올 때 당신의 진가가 드러납니다. 이건 재능이에요. 많은 사람들이 압박을 견디지 못하지만, 당신은 압박을 연료로 씁니다.",
                "당신의 그림자는 '너무 오래 뜨거운 것'입니다. 火는 金을 벼리지만, 계속 가열하면 결국 녹입니다. 당신은 스스로를 계속 압박 속에 두는 경향이 있습니다. 쉬는 것에 죄책감을 느끼고, 쉬는 순간에도 '이 시간에 뭘 해야 하지'를 생각합니다. 그러다 어느 순간 완전히 꺼져버리죠.",
                "성숙한 辛巳는 '열기를 다스릴 줄 아는 사람'입니다. 뜨거운 압박을 유지하되, 그 사이에 회복의 시간을 넣을 줄 아는 사람. 그때 당신의 예리함은 소진이 아니라, 오래 유지되는 정밀함이 됩니다."
            ],
            "shadows": [
                "쉬는 것에 죄책감을 느껴, 결국 완전히 꺼져버립니다.",
                "압박이 없으면 오히려 무기력해져서, 스스로 압박을 만듭니다.",
                "예민함이 압박과 만나면, 사소한 것에도 크게 반응합니다."
            ],
            "advice": [
                "이번 주에 '아무것도 하지 않는' 시간을 하루 30분 이상 확보하세요. 생산성 없는 시간이 당신을 회복시킵니다.",
                "쉬는 순간 '이 시간에 뭘 해야 하지'가 떠오르면, 그 생각을 스스로에게 '지금은 쉬는 중이야'라고 답해주세요.",
                "지금 압박이 없는데 무기력하다면, 그건 실패가 아니라 회복 신호입니다. 몸이 먼저 알았어요.",
                "당신의 예민함이 사소한 것에 반응할 때, '이건 압박인가, 아니면 내가 지친 건가' 물어보세요."
            ],
            "keywords": ["압박 속 예리함", "열기의 벼림", "정밀한 집중", "회복의 리듬"]
        },
        "辛未": {
            "name": "마른 화분 속 보석", "pillar": "辛未",
            "hero": "당신은 마른 화분에 놓인 보석입니다. 주변은 건조해도, 당신의 결은 흐트러지지 않는 사람이죠.",
            "narrative": [
                "당신은 건조함 속에서도 기준을 유지하는 사람입니다. 辛未(신미)는 여름의 마른 흙 위에 세공된 금속이 앉은 기둥이에요. 화분의 흙이 말라도 보석은 스스로 녹슬지 않습니다. 당신도 그렇습니다. 환경이 척박해도, 당신의 기준과 태도는 쉽게 무너지지 않아요.",
                "당신의 강점은 '환경에 흔들리지 않는 완성도'입니다. 다른 사람들이 상황을 탓하며 흐트러질 때, 당신은 묵묵히 자신의 기준을 지킵니다. 그래서 당신이 만든 것에는 늘 일정한 품질이 있습니다. 좋은 날에도 나쁜 날에도 같은 퀄리티가 나오는 사람이에요. 이건 아주 드문 능력입니다.",
                "당신의 그림자는 '건조함이 경직이 되는 것'입니다. 마른 흙은 부드러움을 잃기 쉽습니다. 당신의 기준이 너무 단단해지면, 다른 사람의 다름을 '틀림'으로 판단하게 됩니다. 그리고 그 기준을 스스로에게도 똑같이 적용해서, 완벽하지 않은 자신을 용서하지 못합니다. 화분이 말라가면 결국 보석도 빛을 잃어요.",
                "성숙한 辛未는 '기준에 물기를 더한 사람'입니다. 완성도를 유지하되, 그 완성도에 이르지 못하는 자신과 타인을 이해할 줄 아는 사람. 그때 당신의 기준은 압박이 아니라, 사람들이 배우고 싶어 하는 아름다움이 됩니다."
            ],
            "shadows": [
                "기준이 너무 단단해져서, 다른 사람의 다름을 '틀림'으로 판단합니다.",
                "완벽하지 않은 자신을 오래 용서하지 못해, 스스로가 갈립니다.",
                "주변의 건조함에 오래 노출되면, 결국 자신의 빛도 잃게 됩니다."
            ],
            "advice": [
                "이번 주에 자신에게 '이 정도면 충분해'라고 말할 순간을 하나 만들어 두세요.",
                "다른 사람의 결과물을 볼 때, '이건 틀린 게 아니라 다른 것'이라고 한 번 되뇌어 보세요.",
                "환경이 너무 건조하다고 느껴지면, 그 환경에 오래 머무르지 마세요. 화분은 바꿔도 됩니다.",
                "당신의 기준 중 하나를 이번 주에는 조금 느슨하게 풀어보세요. 세상이 무너지지 않는다는 걸 확인하는 겁니다."
            ],
            "keywords": ["일정한 완성도", "마른 흙의 인내", "기준의 강철", "물기 더하기"]
        },
        "辛酉": {
            "name": "완전한 보석", "pillar": "辛酉",
            "hero": "당신은 완전히 세공된 보석입니다. 辛의 기운이 가장 순수하게 응축된, 흔들리지 않는 아름다움의 사람이죠.",
            "narrative": [
                "당신은 辛 중에서도 가장 순수한 辛입니다. 辛酉(신유)는 辛의 록(祿) 자리에 辛이 앉은, 금속 기운이 두 겹으로 겹친 기둥이에요. 그래서 당신의 기준은 흔들리지 않고, 당신의 미감은 정확하며, 당신의 태도는 완성되어 있습니다. 사람들은 당신 앞에서 이상하게 '이 사람은 흐트러지지 않는다'는 인상을 받습니다.",
                "당신의 강점은 '압도적 정밀함'입니다. 당신이 손대는 것은 아무리 작아도 완성도가 다릅니다. 디테일을 하나하나 정확하게 다듬고, 전체가 흐트러지지 않도록 조율합니다. 어떤 분야에서든 '이 사람이 만든 것'이라는 표시가 남습니다. 그것이 당신의 서명입니다.",
                "당신의 그림자는 '완벽이 사람을 밀어내는 것'입니다. 완전한 보석은 흠이 없어서, 흠이 있는 사람이 곁에 있기 어렵습니다. 당신의 기준은 당신에게는 자연스럽지만, 다른 사람에게는 벽입니다. 그리고 그 기준은 당신 자신에게도 벽이 됩니다. 완벽하지 않은 자신을 볼 때마다, 당신은 스스로를 가장 혹독하게 심판합니다.",
                "성숙한 辛酉는 '완벽을 나누는 사람'입니다. 완성도를 유지하되, 그 완성도에 이르는 길에 있는 사람을 이해하고 기다릴 줄 아는 사람. 그때 당신의 완벽은 압박이 아니라, 사람들이 배우고 싶어 하는 아름다움이 됩니다."
            ],
            "shadows": [
                "자신의 기준이 너무 높아, 완벽하지 않은 자신을 계속 심판합니다.",
                "다른 사람이 당신 앞에서 긴장하거나 실수를 감추려 합니다.",
                "완벽을 추구하다가, 정작 완성하지 못하고 오래 붙들고 있습니다."
            ],
            "advice": [
                "이번 주에 80%에서 내보내는 연습을 한 번 하세요. 아무도 죽지 않는다는 걸 확인하는 겁니다.",
                "다른 사람이 실수했을 때, 먼저 '나도 그런 적 있어'라고 말해주세요. 그게 벽을 허뭅니다.",
                "당신이 자주 던지는 '왜 이것밖에' 를 '무엇을 해냈지'로 한 번 바꿔보세요.",
                "완벽하지 않은 자신에게 이번 주에 한 번, 소리 내어 '이 정도면 충분히 잘했어'라고 말해주세요."
            ],
            "keywords": ["순수 辛", "최고 정밀", "완성의 서명", "완벽 나누기"]
        },
        "辛亥": {
            "name": "물빛 속 보석", "pillar": "辛亥",
            "hero": "당신은 물빛에 비친 보석입니다. 깊은 물 위에서 조용히 빛나며, 그 빛으로 주변의 진실을 비추는 사람이죠.",
            "narrative": [
                "당신은 지혜와 정밀함을 함께 지닌 사람입니다. 辛亥(신해)는 세공된 금속 위에 깊은 물기운이 앉은 기둥이에요. 금속이 물 위에 있으면 그 빛이 반사되어 주변을 비춥니다. 당신의 지혜도 그렇습니다. 조용하지만, 당신이 보는 것은 남들보다 정확합니다.",
                "당신의 강점은 '감정의 정밀함'입니다. 당신은 사람의 마음을 아주 세밀하게 읽습니다. 말하지 않은 것, 표정에 스친 것, 목소리에 배어 있는 것을 당신은 알아챕니다. 그래서 당신과 대화하면 사람들은 이상하게 '이 사람은 나를 이해한다'는 느낌을 받습니다.",
                "당신의 그림자는 '생각이 물결처럼 꼬리를 무는 것'입니다. 물이 깊으면 반사가 선명하지만, 물결이 일면 모든 것이 흐트러집니다. 당신은 감정이 올라올 때 그 물결에 휩쓸려, 정작 필요한 판단을 미룹니다. 그리고 결정을 미루는 사이에 기회가 지나갑니다.",
                "성숙한 辛亥는 '물결을 다스리는 사람'입니다. 감정과 지혜를 유지하되, 결정할 때는 물결을 잠재우고 선명하게 볼 줄 아는 사람. 그때 당신의 지혜는 흔들림이 아니라 깊은 통찰이 되고, 당신의 빛은 사람들이 의지하고 싶은 등대가 됩니다."
            ],
            "shadows": [
                "생각이 너무 많아 결정을 미루고, 그 사이에 기회를 놓칩니다.",
                "감정의 물결에 휩쓸려, 정작 필요한 순간에 움직이지 못합니다.",
                "자신의 지혜를 너무 감춰서, 주변 사람들이 당신의 진가를 모릅니다."
            ],
            "advice": [
                "이번 주에 결정해야 할 것 하나를 골라, 정해진 기한 안에 반드시 결정하세요. 완벽하지 않아도 됩니다.",
                "감정이 올라올 때, '이건 정보인가, 아니면 나를 잠기게 하는 파도인가' 스스로에게 물어보세요.",
                "당신이 아는 것 하나를 누군가에게 나눠주세요. 당신의 지혜는 나눌 때 더 선명해집니다.",
                "물에는 땅이 필요합니다. 하루에 하나, 흔들리지 않는 작은 의식을 만드세요."
            ],
            "keywords": ["물빛 지혜", "감정의 정밀함", "깊은 통찰", "선명한 판단"]
        }
    },
    "en": {
        "辛丑": {
            "name": "Jewel in Winter Garden", "pillar": "辛丑",
            "hero": "You're a jewel set in a winter garden. Buried in cold ground, but the moment light reaches you, no one shines with more precision.",
            "narrative": [
                "You carry a restrained kind of beauty. 辛丑 is crafted metal resting on cold, damp earth. You don't show your feelings loudly, but what's inside you is unusually fine. People remember you as quiet — and then one day they notice a strange care in the things you make and the things you choose.",
                "Your strength is hidden completeness. You hold your standard even when no one is watching. You don't make a show of it, but the things that pass through your hands don't come out messy. It's less effort than instinct — you can feel the tiny line between 'this is fine' and 'this is not', and you hold it.",
                "Your shadow is getting tired of not being seen. A jewel in a winter garden is just a cold stone to anyone who doesn't come to look. You don't give yourself credit for your own care, and you quietly wait for someone else to notice. That waiting turns into hurt, and hurt turns into doubting your own standard.",
                "A mature Xin-Chou knows their own light. Recognizing your own completeness even when nobody's looking, and bringing it out into view when the moment calls. Then your precision stops being a hidden jewel and becomes a garden people come to sit in."
            ],
            "shadows": [
                "Quietly storing hurt when your care goes unseen.",
                "Not giving yourself credit for your own completeness, always feeling insufficient.",
                "Not showing feelings clearly enough that even those close to you misread you."
            ],
            "advice": [
                "Once this week, praise yourself out loud for one small thing you finished. No one else needs to hear it.",
                "Before hurt stacks up, tell someone close: 'I'd like you to see this.'",
                "Show one thing you've made to someone else. It doesn't have to be perfect.",
                "Winter gardens have springs too. If you're in a dim season, that's a season, not a failure."
            ],
            "keywords": ["hidden completeness", "restrained beauty", "winter care", "self-recognition"]
        },
        "辛卯": {
            "name": "Jade in the Spring Garden", "pillar": "辛卯",
            "hero": "You're jade set in a spring garden. Quietly shining among things that are growing, and delicately helping them grow.",
            "narrative": [
                "You hold precision and growth together. 辛卯 is crafted metal sitting on spring wood. You want beauty, but you want it to actually grow. You prefer the carefully cultivated over the instantly spectacular.",
                "Your strength is the instinct of a delicate gardener. You notice exactly what a person or a project needs to grow and quietly supply it. Not a flashy kind of leadership — the kind that adjusts water and light from behind the scenes. What you cultivate tends to take root and hold.",
                "Your shadow is waiting for perfect conditions. Jade in a spring garden needs prepared soil, the right light, the right water. When those conditions aren't there, you don't bring yourself out. And those conditions take longer to arrive than you think. Spring passes while your jade is still in the dirt.",
                "A mature Xin-Mao knows timing more than conditions. Bringing yourself out before it's perfect. Then your precision becomes growth rather than waiting, and what you tend grows alongside you."
            ],
            "shadows": [
                "Waiting for perfect conditions and missing the spring you could have started in.",
                "Helping things grow while continuing to postpone your own growth.",
                "Finer sensitivity than most people can meet, so small imperfections stick with you."
            ],
            "advice": [
                "Start one thing this week that doesn't need perfect conditions.",
                "Set aside a place among the things you cultivate for yourself.",
                "Show your work before it's finished. The world is more forgiving than you expect.",
                "Ask yourself how long this spring is going to last. That's your timing."
            ],
            "keywords": ["delicate gardener", "refined growth", "flexible standards", "spring jade"]
        },
        "辛巳": {
            "name": "Jewel in Heat", "pillar": "辛巳",
            "hero": "You're a jewel forged in heat. Pressure makes you more precise, not weaker.",
            "narrative": [
                "You sharpen under pressure. 辛巳 is crafted metal resting on hot fire. Metal meeting fire either hardens or melts — you harden. Under difficulty, your focus actually improves and your precision comes alive.",
                "Your strength is edge under pressure. When other people scatter, you get clearer. Important presentations, decisive moments, tight deadlines — that's where you're most yourself. This is a gift. Most people can't carry pressure. You burn it as fuel.",
                "Your shadow is staying hot too long. Fire tempers metal, but kept hot indefinitely it melts it. You keep yourself under pressure out of habit. You feel guilty resting, and even when you rest you wonder what you should be doing. And then one day you go out completely.",
                "A mature Xin-Si governs the heat. Keeping the pressure but putting recovery in between. Then your edge becomes sustained precision instead of exhaustion."
            ],
            "shadows": [
                "Feeling guilty about rest until you burn out completely.",
                "Getting listless without pressure, so you manufacture your own.",
                "When sensitivity meets pressure, small things land very hard."
            ],
            "advice": [
                "Set aside at least 30 minutes a day this week with nothing productive in it. That's what restores you.",
                "When 'what should I be doing' comes up while resting, tell yourself: 'I'm resting now.'",
                "If there's no pressure and you feel flat, that's a recovery signal, not a failure.",
                "When sensitivity spikes, ask: is this pressure, or am I tired?"
            ],
            "keywords": ["edge under pressure", "forged in heat", "precise focus", "recovery rhythm"]
        },
        "辛未": {
            "name": "Jewel in Dry Soil", "pillar": "辛未",
            "hero": "You're a jewel set in dry soil. The surroundings go barren, and your lines don't blur.",
            "narrative": [
                "You hold your standard in dry conditions. 辛未 is crafted metal resting on dry summer earth. Dry soil doesn't rust the jewel. You're like that — your standard and your way of moving don't crumble just because the environment is difficult.",
                "Your strength is consistent quality. When other people blame circumstances and let things go, you quietly hold your line. So what you produce has a steady quality. Good days, bad days, same output. That's a rare ability.",
                "Your shadow is dryness becoming rigidity. Dry earth loses its softness. If your standard gets too hard, other people's differences start to look like errors. And you apply that same standard to yourself, so you can't forgive yourself for not being perfect. If the pot dries out too long, even the jewel loses its light.",
                "A mature Xin-Wei adds moisture to the standard. Keeping the quality, and understanding the people — including yourself — who can't reach it yet. Then the standard stops being pressure and becomes the kind of beauty people want to learn."
            ],
            "shadows": [
                "A standard so firm that other people's differences register as errors.",
                "Unable to forgive yourself for not being perfect, so you slowly grind yourself down.",
                "Staying in dry environments until even your own light dims."
            ],
            "advice": [
                "Say to yourself this week, 'This is enough.' Once is enough.",
                "When you see someone else's work, remind yourself: not wrong, just different.",
                "If the environment feels too dry, don't stay in it for long. A pot can be changed.",
                "Loosen one of your standards this week on purpose. Confirm the world doesn't fall apart."
            ],
            "keywords": ["steady quality", "dry earth patience", "standard of steel", "adding moisture"]
        },
        "辛酉": {
            "name": "Perfect Gem", "pillar": "辛酉",
            "hero": "You're a fully cut gem. 辛's energy condensed to its purest form — beauty that doesn't shake.",
            "narrative": [
                "You're the purest form of 辛. 辛酉 is 辛 sitting in its own 祿 (Lu) — double metal, layered on itself. Your standard doesn't shift, your aesthetic is exact, your stance is complete. People get a strange sense in your presence: this person doesn't come undone.",
                "Your strength is overwhelming precision. Whatever you touch is finished to a different level, however small. You work the details into place and keep the whole thing from drifting. Anywhere you go, 'this person made that' shows up as a signature.",
                "Your shadow is perfection pushing people away. A flawless gem makes it hard for people with flaws to stand next to it. Your standard is natural to you, but it's a wall to others. And it's a wall to you too — every time you see your own imperfection, you judge yourself harder than anyone else would.",
                "A mature Xin-You shares the perfection. Keeping the standard while understanding the people on the road toward it. Then your perfection stops being pressure and becomes the kind of beauty people want to learn."
            ],
            "shadows": [
                "A standard so high that your own imperfection is always being judged.",
                "People around you tense up, or start hiding their mistakes, near you.",
                "Chasing perfection so far that you never actually finish."
            ],
            "advice": [
                "Ship something at 80% this week. Confirm nothing breaks.",
                "When someone makes a mistake, say first, 'I've done that too.' It opens the wall.",
                "Turn one 'why only this much' into 'what did I actually make?'",
                "Say out loud to yourself once this week: 'This is well done.'"
            ],
            "keywords": ["pure 辛", "highest precision", "signature of finish", "shared perfection"]
        },
        "辛亥": {
            "name": "Jewel in Water's Light", "pillar": "辛亥",
            "hero": "You're a jewel reflected in water. Quietly shining on deep water, illuminating the truth around you.",
            "narrative": [
                "You hold wisdom and precision together. 辛亥 is crafted metal resting on deep water. Metal over water reflects — and so does your mind. You see things more exactly than most people, even when you say nothing.",
                "Your strength is precision in feeling. You read people with unusual accuracy — what they don't say, what flickers across their face, what sits underneath their voice. When people talk to you, they end up feeling strangely understood.",
                "Your shadow is thinking like water rippling. Deep water reflects clearly, but ripples blur everything. When emotion rises, you get caught in the ripples and delay the decision that needed to be made. Opportunities pass in that delay.",
                "A mature Xin-Hai governs the ripples. Keeping the emotion and the wisdom, but settling the water when a decision is actually needed. Then your wisdom is deep insight rather than wavering, and your light becomes a lighthouse people steer by."
            ],
            "shadows": [
                "Thinking so much that a decision gets delayed until the moment has passed.",
                "Swept up by emotional ripples when you need to move.",
                "Hiding your wisdom so well that people don't learn what you carry."
            ],
            "advice": [
                "Pick one decision to make this week and make it by a fixed deadline. It doesn't have to be perfect.",
                "When emotion rises, ask: is this information, or is this a wave pulling me under?",
                "Share one thing you know with someone. Your wisdom gets clearer when you share it.",
                "Water needs earth. Give your day one small ritual that doesn't move."
            ],
            "keywords": ["wisdom in water", "precision in feeling", "deep insight", "clear judgment"]
        }
    }
}


def main() -> int:
    ap = argparse.ArgumentParser(description="辛 일간 6일주 추가")
    ap.add_argument("--force", action="store_true", help="스텁 덮어쓰기")
    args = ap.parse_args()

    print("=== 辛 일간 6일주 추가 (辛丑, 辛卯, 辛巳, 辛未, 辛酉, 辛亥) ===")
    
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