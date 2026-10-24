#!/usr/bin/env python3
"""
丁 일간 6일주 추가 (丁丑, 丁卯, 丁巳, 丁未, 丁酉, 丁亥).
이 스크립트를 실행하면 火 일간(丙 + 丁) 전원이 고유 콘텐츠를 받습니다.

사용:
    python scripts/add_pillars_ding.py
    python scripts/add_pillars_ding.py --force   # 빈 스텁 덮어쓰기 (권장)
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app" / "services" / "content" / "data"


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _backup(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + f".bak.{_ts()}")
    shutil.copy2(path, bak)
    return bak


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


PILLARS = {
    "ko": {
        "丁丑": {
            "pillar": "丁丑",
            "hero": "당신은 비옥한 흙 위에 놓인 촛불입니다. 아래에서 조용히 영양분을 받으며 위로는 꾸준히 빛을 내죠.",
            "narrative": [
                "당신의 온기는 요란하지 않습니다. 누군가를 압도하는 뜨거움이 아니라, 오래 곁에 있어도 부담스럽지 않은 빛이에요. 처음 만나는 사람들은 당신을 조용하고 차분한 사람으로 기억합니다. 그런데 시간이 지나면, 이 조용함이 사실은 아주 정교하게 유지되는 온도라는 걸 알아차립니다.",
                "당신은 안정과 돌봄을 함께 하는 사람입니다. 가까운 사람들이 기대는 자리가 되고, 조직에서는 없어서는 안 될 조용한 중심이 되죠. 이 역할이 당신에게 자연스러운 만큼, 주변 사람들은 당신이 '괜찮은 사람'이라는 걸 너무 쉽게 가정합니다. 당신이 힘들어도 다들 모르고 지나갈 수 있어요.",
                "당신의 그림자는 '꾸준함이 당연해지는 것'입니다. 계속 빛을 내면, 그 빛이 공기처럼 여겨집니다. 그때 필요한 건 밝기를 높이는 게 아니라, 가끔은 스스로를 위해 빛을 잠시 꺼두는 용기예요. 꺼진 촛불이 실패가 아니듯, 잠시 쉬는 당신도 실패가 아닙니다.",
                "성숙한 丁丑은 '자신도 돌봄의 대상임을 인정하는 사람'입니다. 다른 사람에게 베푸는 그 정성의 10분의 1이라도 자기 자신에게 돌릴 때, 당신의 빛은 오래갑니다. 그게 당신이 오래 빛날 수 있는 유일한 방법이에요.",
            ],
            "shadows": [
                "당신이 꾸준해서, 주변 사람들이 당신의 피로를 알아채지 못합니다.",
                "돌봄의 대상이 항상 다른 사람이고, 자신은 늘 뒷순위로 밀립니다.",
                "쉬는 순간 죄책감을 느껴서, 결국 몸이 강제로 멈추게 만듭니다.",
            ],
            "advice": [
                "이번 주에 당신을 돌봐줄 사람 한 명을 정해, 작은 부탁을 하나 해보세요.",
                "당신이 꾸준히 해온 일 중 하나를 이번 주엔 하지 말고, 그 여백을 스스로에게 주세요.",
                "당신의 컨디션을 한 번은 소리 내어 말해보세요. '요즘 좀 지쳐 있어.'",
                "당신의 빛이 꺼지는 게 두렵다면, 꺼졌다 켜지는 것도 하나의 리듬임을 기억하세요.",
            ],
            "keywords": ["따뜻한 안정", "조용한 돌봄", "비옥한 온기", "자기 돌봄"],
        },
        "丁卯": {
            "pillar": "丁卯",
            "hero": "당신은 봄나무 위의 촛불입니다. 타오르는 불꽃이 아니라, 자라나는 걸 돕는 빛이에요.",
            "narrative": [
                "당신은 성장과 온기가 함께 있는 사람입니다. 촛불이 나무를 태우는 대신, 당신의 빛은 자라나는 것들을 비춥니다. 사람들은 당신 곁에서 이상하게 '더 나아질 수 있을 것 같다'는 감각을 얻습니다. 당신이 뭘 특별히 해주지 않아도요.",
                "당신의 창조성은 조용한 편입니다. 큰 폭발보다는 꾸준한 빛으로, 아이디어를 키우고 사람을 북돋우고 관계를 자라게 하죠. 그래서 당신과 함께 일한 사람들은 시간이 지나서야 '그때 그 사람 덕분이었구나' 하고 알아차립니다. 당신의 기여는 늘 사후에 인정됩니다.",
                "당신의 그림자는 자기 빛을 남의 성장에 다 써버리는 것입니다. 다른 사람의 잠재력을 키우다가, 정작 자기 자신의 잠재력은 방치해둘 때가 있어요. 타인의 성장은 당신에게 자연스러운 일이지만, 당신의 성장도 그만큼 중요합니다.",
                "성숙한 丁卯는 '자기 성장을 타인과 나란히 놓는 사람'입니다. 누군가를 키우는 일과 자신이 자라는 일을 동시에 할 때, 당신의 빛은 더 이상 남을 위한 도구가 아니라 당신 자신의 삶이 됩니다.",
            ],
            "shadows": [
                "남의 성장은 잘 돕지만, 정작 자신의 성장은 자꾸 뒤로 미룹니다.",
                "당신의 조용한 기여가 자주 과소평가되고, 그게 서운함으로 쌓입니다.",
                "당신이 키운 사람이 성장해서 떠나면, 배신감에 가까운 상실을 느낍니다.",
            ],
            "advice": [
                "이번 주에 당신 자신을 위해 시작할 작은 것 하나를 정해보세요.",
                "당신의 기여를 한 번은 소리 내어 말해보세요. 자랑이 아니라 사실 확인입니다.",
                "당신이 키우는 사람이 떠나는 건 성장의 증거이지, 배신이 아닙니다. 그 감각을 스스로에게 설명해보세요.",
                "자신의 성장을 위해 시간을 쓰는 것을 죄책감 없이 허락하세요. 그게 당신의 빛을 지키는 길입니다.",
            ],
            "keywords": ["자라나는 빛", "조용한 창조", "성장의 온기", "자기 성장"],
        },
        "丁巳": {
            "pillar": "丁巳",
            "hero": "당신은 두 겹의 불꽃입니다. 안쪽의 촛불이 바깥의 열기를 지나 더 깊게 타오르죠.",
            "narrative": [
                "당신은 조용하지만 강렬한 사람입니다. 밖으로 뿜어내는 열기보다 안쪽으로 모으는 열기가 강해서, 처음 만나는 사람들은 당신을 차분하다고 느낍니다. 그런데 함께 시간을 보내면, 당신의 시선이 얼마나 정확하고 집요한지 알아차립니다.",
                "당신의 강점은 '집중된 시선'입니다. 남들이 놓치는 디테일을 붙잡고, 흐릿한 것을 선명하게 만들고, 표면 아래를 읽습니다. 그래서 당신이 하는 일은 대체로 밀도가 높습니다. 양은 적어도 질이 다릅니다. 이건 당신이 노력해서 얻은 게 아니라, 두 겹의 불꽃이 만들어내는 자연스러운 결과예요.",
                "당신의 그림자는 '스스로에게 너무 엄격한 것'입니다. 두 겹의 불꽃은 스스로를 태우기 쉽습니다. 다른 사람에게는 관대한데, 자기 자신에게는 놀랄 만큼 가혹한 기준을 들이대죠. 그 기준이 당신을 성장시킨 것도 사실이지만, 동시에 당신을 갉아먹고 있습니다.",
                "성숙한 丁巳는 '자신에게도 정확한 온기를 주는 사람'입니다. 남을 정확하게 보는 그 눈으로 자기 자신도 정확하게 보고, 지친 부분에는 지친 만큼의 온기를 허락하는 사람. 그때 당신의 밀도 높은 시선은 더 이상 압박이 아니라, 깊은 이해가 됩니다.",
            ],
            "shadows": [
                "남에게는 관대하지만, 자신에게는 놀랄 만큼 가혹합니다.",
                "완벽한 결과를 만들지 못하면 스스로를 오래 괴롭힙니다.",
                "집중이 강한 만큼, 한번 지치면 회복이 오래 걸립니다.",
            ],
            "advice": [
                "이번 주에 '이 정도면 충분하다'를 한 번 실천해보세요. 자기 자신에게 하는 겁니다.",
                "당신이 남에게 허락하는 관대함을 하나 골라, 자신에게도 똑같이 적용해보세요.",
                "집중하고 나면 반드시 회복 시간을 붙이세요. 두 겹의 불꽃은 그게 없으면 꺼집니다.",
                "당신이 자주 자신에게 던지는 '왜 이것밖에 못했지'를, '무엇을 해냈지'로 한 번 바꿔보세요.",
            ],
            "keywords": ["집중된 열기", "정확한 시선", "두 겹의 불꽃", "자기 관대함"],
        },
        "丁未": {
            "pillar": "丁未",
            "hero": "당신은 메마른 땅 위의 촛불입니다. 흔들려도 꺼지지 않는, 단단하게 타오르는 사람이죠.",
            "narrative": [
                "당신은 쉽게 꺼지지 않는 사람입니다. 조건이 좋지 않아도, 주변이 흔들려도, 당신의 불은 계속 타오릅니다. 처음에는 조용해 보이지만, 시간이 지나면 '이 사람은 쉽게 무너지지 않는다'는 인상을 남기죠. 그 인상은 정확합니다.",
                "당신은 저항력의 사람입니다. 힘든 상황에서 오히려 집중력이 올라가고, 문제를 정면으로 마주할 수 있는 힘이 있습니다. 이건 흔한 재능이 아니에요. 많은 사람들이 어려운 상황에서 흐트러지지만, 당신은 어려울수록 더 선명해집니다.",
                "당신의 그림자는 '버티는 것이 미덕이 되는 것'입니다. 오래 버티다 보면, 버티지 않아도 되는 상황에서도 계속 버티게 됩니다. 안 좋은 환경, 맞지 않는 관계, 이미 끝난 프로젝트를 '여기서 포기하면 지는 것 같아서' 계속 붙들고 있을 때가 있어요. 그건 인내가 아니라 집착입니다.",
                "성숙한 丁未는 '버틸 것과 내려놓을 것을 구분하는 사람'입니다. 당신의 저항력은 무기가 맞습니다. 다만 그 무기를 어디에 쓸지 스스로 선택할 수 있어야 해요. 버티는 것도, 놓아주는 것도, 둘 다 당신의 힘입니다.",
            ],
            "shadows": [
                "안 좋은 상황에서도 계속 버티다가, 결국 자신을 소진시킵니다.",
                "포기가 '지는 것'처럼 느껴져서, 이미 끝난 것을 붙들고 있습니다.",
                "당신의 저항력이 주변 사람들에게 '이 사람은 괜찮을 거야'라는 오해를 만듭니다.",
            ],
            "advice": [
                "이번 주에 '내가 지금 버티고 있는 것' 세 가지를 적어보세요. 그중 하나는 놓아도 됩니다.",
                "포기는 실패가 아니라 '다음으로 넘어가는 선택'이라는 걸 스스로에게 상기시켜 보세요.",
                "당신이 괜찮은 척하는 순간을 하나 붙잡아, 그 순간엔 괜찮지 않다고 말해보세요.",
                "당신의 저항력은 무기지만, 무기는 쓸 곳을 골라야 진짜 힘이 됩니다.",
            ],
            "keywords": ["단단한 불씨", "저항의 힘", "쉽게 꺼지지 않음", "내려놓는 용기"],
        },
        "丁酉": {
            "pillar": "丁酉",
            "hero": "당신은 정교한 금속 위에 놓인 촛불입니다. 반사된 빛이 당신의 것을 몇 배로 만들어내죠.",
            "narrative": [
                "당신은 정밀함과 온기가 함께 있는 사람입니다. 촛불이 금속 위에서 반사되면, 원래의 빛보다 훨씬 밝고 정교한 빛이 됩니다. 당신의 온기도 그렇습니다. 그냥 따뜻한 게 아니라, 정확하게 필요한 곳에 정확한 만큼의 온기를 주는 사람이에요.",
                "당신의 미적 감각과 기준은 아주 높습니다. 좋은 것과 그럭저럭인 것의 차이를 알아채고, 그 차이를 중요하게 여기죠. 이 감각은 당신이 손대는 모든 것에 스며듭니다. 사람들은 당신이 만든 것, 당신이 고른 것에서 이상하게 '정교함'을 느낍니다. 설명은 못 하지만요.",
                "당신의 그림자는 '완벽주의가 관계를 가로막는 것'입니다. 기준이 높은 만큼, 사람에게도 같은 기준을 적용할 때가 있습니다. 그 기준은 당신에게는 자연스럽지만, 상대에게는 부담입니다. 그리고 당신 자신에게도요. 완벽하지 않은 나를 용서하는 게, 완벽하지 않은 타인을 받아들이는 것보다 먼저입니다.",
                "성숙한 丁酉는 '기준을 관대함과 함께 쓰는 사람'입니다. 당신의 기준은 선물입니다. 다만 그 선물을 상대가 받을 준비가 되어 있는지 확인할 필요가 있어요. 기준은 지키되, 그 기준에 이르는 길에서 넘어지는 사람을 밀어내지 마세요. 그게 당신의 온기가 진짜로 빛나는 방식입니다.",
            ],
            "shadows": [
                "자신의 기준을 타인에게 그대로 적용해서, 상대를 지치게 만듭니다.",
                "완벽하지 않은 결과물에 오래 마음이 붙잡혀 있습니다.",
                "높은 기준이 '이 정도면 충분하다'를 못 느끼게 만듭니다.",
            ],
            "advice": [
                "이번 주에 80%에서 멈추는 연습을 한 번 해보세요. 어떤 결과물이든요.",
                "당신의 기준을 사람에게 적용하기 전에, '이 사람이 지금 그걸 감당할 수 있나?'를 한 번 물어보세요.",
                "당신이 '이 정도면 됐다'고 느끼는 순간을 하루 한 번은 만들어보세요.",
                "완벽하지 않은 자신을 먼저 용서하세요. 그게 다른 사람을 받아들이는 시작입니다.",
            ],
            "keywords": ["정교한 온기", "반사되는 빛", "높은 기준", "관대한 정밀"],
        },
        "丁亥": {
            "pillar": "丁亥",
            "hero": "당신은 수면 위에 뜬 촛불입니다. 흔들리지만 꺼지지 않는, 섬세한 균형의 사람이죠.",
            "narrative": [
                "당신은 예민함과 지혜가 함께 있는 사람입니다. 수면 위의 촛불은 늘 흔들리지만, 그 흔들림 속에서도 꺼지지 않는 빛이 있습니다. 당신의 감수성도 그렇습니다. 쉽게 흔들리지만, 그 흔들림 자체가 당신의 깊이입니다.",
                "당신은 다른 사람의 감정을 자기 것처럼 느낍니다. 말하지 않아도 그 사람의 상태를 알아채고, 방의 분위기가 바뀌면 당신이 먼저 알아차립니다. 이 예민함은 흔한 재능이 아니에요. 하지만 동시에 아주 피곤한 재능이기도 하죠. 모든 파동을 다 받아내면, 당신 자신의 잔잔함이 사라집니다.",
                "당신의 그림자는 '남의 물결에 휩쓸리는 것'입니다. 다른 사람의 감정이 거세면, 당신도 함께 휩쓸립니다. 그 감정이 내 것인지 남의 것인지 구분이 안 될 때가 있어요. 그 감정의 파도 위에 서서 '이게 내 파도인가, 저 사람의 파도인가?'라고 스스로에게 물어보세요.",
                "성숙한 丁亥는 '자기 파도를 지키는 사람'입니다. 예민함을 유지하되, 그 예민함이 남의 바다로 다 흘러가지 않도록 경계를 만드는 사람. 그때 당신의 빛은 흔들리면서도 꺼지지 않는, 아주 특별한 종류의 빛이 됩니다.",
            ],
            "shadows": [
                "남의 감정과 내 감정을 구분하지 못하고, 둘 다 짊어집니다.",
                "예민함이 피로로 쌓여서, 결국 아무 감정도 못 느끼게 됩니다.",
                "혼자 있는 시간이 부족하면, 자기 색을 잃습니다.",
            ],
            "advice": [
                "감정이 흔들릴 때, '이게 내 파도인가, 남의 파도인가?'를 스스로에게 한 번 물어보세요.",
                "이번 주에 완전히 혼자인 시간을 한 시간 이상 확보하세요. 그게 당신의 회복입니다.",
                "남의 감정을 다 받아내지 않아도 괜찮다는 걸, 스스로에게 허락하세요.",
                "당신의 예민함은 재능입니다. 그 재능을 지키려면, 정기적으로 스스로를 '비우는' 시간이 필요합니다.",
            ],
            "keywords": ["섬세한 균형", "수면의 빛", "예민한 지혜", "자기 파도"],
        },
    },
    "en": {
        "丁丑": {
            "pillar": "丁丑",
            "hero": "You're a candle set on fertile soil. Nourished quietly from below, shining steadily above.",
            "narrative": [
                "Your warmth isn't loud. It's not a heat that overwhelms — it's a light that doesn't burden people even after hours by your side. New people remember you as quiet and composed. Over time, they realize that composure is actually a very precisely held temperature.",
                "You carry stability and care together. You become the one people lean on, the quiet center an organization can't do without. That role comes naturally to you — and because it does, the people around you too easily assume you're fine. Even when you're exhausted, most of them won't notice.",
                "Your shadow is 'being taken for granted.' When you keep shining, that shine becomes air. What you need then isn't more brightness — it's the courage to dim yourself, just for a moment, for your own sake. A candle that goes out isn't failing. Neither are you, when you rest.",
                "A mature Ding-Chou is someone who accepts being cared for too. When you turn even a tenth of the care you give others back on yourself, your light lasts. That's the only way you last.",
            ],
            "shadows": [
                "Because you're steady, people don't notice your fatigue.",
                "The one being cared for is always someone else. You keep landing last.",
                "Rest makes you feel guilty, so you force your body to stop instead.",
            ],
            "advice": [
                "This week, pick one person who could care for you and make one small request.",
                "Skip one thing you'd normally do this week. Give the space to yourself.",
                "Say your state out loud once. 'I'm kind of worn down lately.'",
                "If you fear going out, remember: going out and relighting is also a rhythm.",
            ],
            "keywords": ["warm stability", "quiet care", "fertile warmth", "self-care"],
        },
        "丁卯": {
            "pillar": "丁卯",
            "hero": "You're a candle on a spring branch. Not a flame that consumes — a light that helps things grow.",
            "narrative": [
                "You carry growth and warmth together. Where a candle would normally consume wood, your light instead illuminates what's growing. People around you get a strange sense that they could become better versions of themselves. And you didn't do anything special to produce it.",
                "Your creativity is quiet. Not explosions — steady light that develops ideas, encourages people, and grows relationships. That's why people who've worked with you often realize, months later, 'that was because of them.' Your contribution is always recognized after the fact.",
                "Your shadow is spending your light entirely on other people's growth. You cultivate others' potential while leaving your own neglected. Growing others is natural to you — but your own growth matters just as much.",
                "A mature Ding-Mao is someone who puts their own growth side by side with others'. When you cultivate someone and grow yourself in the same season, your light stops being a tool for others and becomes your own life.",
            ],
            "shadows": [
                "You grow others well and postpone your own growth indefinitely.",
                "Your quiet contribution is often undervalued, and that quietly accumulates into resentment.",
                "When someone you cultivated grows and leaves, it feels almost like betrayal.",
            ],
            "advice": [
                "This week, pick one small thing you'll start for yourself.",
                "Say your contribution out loud once. Not bragging — confirming a fact.",
                "Someone leaving is proof of growth, not betrayal. Explain that to yourself.",
                "Allow time for your own growth without guilt. That's how you keep your light.",
            ],
            "keywords": ["growing light", "quiet creation", "warmth of growth", "own growth"],
        },
        "丁巳": {
            "pillar": "丁巳",
            "hero": "You're a double flame. The inner candle burns deeper for passing through the outer heat.",
            "narrative": [
                "You're quiet but intense. You gather heat inward more than you radiate outward, so new people read you as calm. Spend more time with you, though, and they discover how exact and persistent your gaze is.",
                "Your strength is 'focused attention.' You catch details others miss, sharpen what's blurred, and read beneath surfaces. That's why your work tends to be dense — small in quantity, but a different quality. Not something you trained. A natural result of two flames in one body.",
                "Your shadow is 'being too hard on yourself.' A double flame burns itself easily. You're generous with others and astonishingly severe with yourself. That standard has grown you — and it's also eating you.",
                "A mature Ding-Si gives themselves the same accurate warmth they give others. Seeing oneself with the same precision you use on others — and allowing the tired parts the warmth they're owed. Then your dense gaze stops being pressure and becomes deep understanding.",
            ],
            "shadows": [
                "Generous with others, astonishingly harsh with yourself.",
                "When the result isn't perfect, you torment yourself for a long time.",
                "The intensity of your focus means recovery takes longer when you're depleted.",
            ],
            "advice": [
                "This week, do 'this is enough' once — to yourself.",
                "Take one act of generosity you'd give others and give it to yourself.",
                "After focusing, always attach recovery. A double flame dies without it.",
                "Change one 'why is this all I did' into 'what did I actually do.'",
            ],
            "keywords": ["focused heat", "precise gaze", "double flame", "self-gentleness"],
        },
        "丁未": {
            "pillar": "丁未",
            "hero": "You're a candle on dry earth. Swaying but not going out — a fire that burns firm.",
            "narrative": [
                "You don't go out easily. Bad conditions, restless surroundings — your flame keeps burning. At first you look quiet, but over time you leave the impression: this person doesn't break easily. That impression is accurate.",
                "You're a person of endurance. Under difficulty your focus actually increases, and you can face the problem directly. That's rare. Most people scatter under pressure. You get sharper as things get harder.",
                "Your shadow is making endurance into a virtue. Keep enduring long enough, and you start enduring where endurance isn't needed. Bad environments, wrong relationships, projects already finished — you hold on because 'letting go feels like losing.' That's not endurance. That's clinging.",
                "A mature Ding-Wei can tell what to endure from what to release. Your resistance is a weapon — but you have to choose where to use it. Enduring and releasing are both your powers.",
            ],
            "shadows": [
                "You keep enduring bad situations until you've burned out.",
                "Giving up feels like losing, so you keep holding on to things already over.",
                "Your resilience makes others assume you're always fine.",
            ],
            "advice": [
                "This week, list three things you're enduring. One of them you can put down.",
                "Remind yourself: letting go isn't failure, it's the choice to move on.",
                "Catch one moment you're pretending to be fine — and say you're not.",
                "Your resistance is a weapon — but weapons only work when you choose where to swing.",
            ],
            "keywords": ["firm ember", "power to resist", "not easily extinguished", "courage to release"],
        },
        "丁酉": {
            "pillar": "丁酉",
            "hero": "You're a candle on fine metal. Reflected light makes yours many times over.",
            "narrative": [
                "You carry precision and warmth together. A candle reflected in metal becomes brighter, more refined. Your warmth is like that — not just warm, but exactly the right amount in exactly the right place.",
                "Your aesthetic sense and standards are high. You notice the difference between good and fine, and you take it seriously. That sense seeps into everything you touch. People feel a strange 'precision' in what you make and what you choose. They can't explain it.",
                "Your shadow is perfectionism that blocks relationships. With high standards, you sometimes apply those standards to people too. To you they're natural — to them, they're a burden. And to you, also. Forgiving your imperfect self has to come before accepting the imperfect other.",
                "A mature Ding-You uses standards with generosity. Your standards are a gift — but check whether the other person is ready to receive it. Keep the standard, don't push away the people who stumble on the way to it. That's when your warmth truly shines.",
            ],
            "shadows": [
                "You apply your standards to others as if they were theirs, and wear people out.",
                "Imperfect results take up your mind for a long time.",
                "The high bar makes it hard for you to feel 'this is enough.'",
            ],
            "advice": [
                "This week, practice stopping at 80% once. Any result.",
                "Before applying your standard to someone, ask: can they carry it right now?",
                "Create one moment a day where 'this is enough' actually feels true.",
                "Forgive your imperfect self first. That's how accepting others begins.",
            ],
            "keywords": ["precise warmth", "reflected light", "high standards", "generous precision"],
        },
        "丁亥": {
            "pillar": "丁亥",
            "hero": "You're a candle floating on water. Swaying but never going out — a person of delicate balance.",
            "narrative": [
                "You carry sensitivity and wisdom together. A candle on water always sways, but even in that swaying, it doesn't go out. Your sensitivity works the same way. You're easily moved, and that very movement is your depth.",
                "You feel other people's emotions as if they were your own. You read someone's state without being told, notice the moment a room changes. That's rare. It's also exhausting. If you absorb every wave, your own stillness disappears.",
                "Your shadow is being swept up by other people's tides. When their emotion is strong, you go with it — and sometimes you can't tell whether the feeling is yours or theirs. Standing on that wave, ask yourself once: 'Is this my wave, or theirs?'",
                "A mature Ding-Hai keeps their own wave intact. Retain the sensitivity — but build a boundary so it doesn't all flow into someone else's sea. Then your light becomes a very particular kind: swaying, and never out.",
            ],
            "shadows": [
                "You can't tell other people's emotions from your own, so you carry both.",
                "Sensitivity accumulates as fatigue until you stop feeling anything.",
                "Without enough solitude, you lose your own color.",
            ],
            "advice": [
                "When emotions sway, ask once: 'Is this my wave, or theirs?'",
                "This week, secure at least one full hour of complete solitude. That's your recovery.",
                "Give yourself permission not to absorb every emotion around you.",
                "Sensitivity is a gift — and keeping it means regularly emptying yourself.",
            ],
            "keywords": ["delicate balance", "light on water", "sensitive wisdom", "own wave"],
        },
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="丁 일간 6일주 추가")
    ap.add_argument("--force", action="store_true", help="이미 있어도 덮어쓰기 (스텁 덮어쓰기 권장)")
    args = ap.parse_args()

    print("=== 丁 일간 6일주 추가 (丁丑·丁卯·丁巳·丁未·丁酉·丁亥) ===")
    created = skipped = 0
    for lang in ("ko", "en"):
        for pillar, data in PILLARS[lang].items():
            path = DATA / lang / "core_pillars" / f"{pillar}.json"
            if path.exists() and not args.force:
                print(f"  ⏭️  [{lang}] {pillar}.json 이미 존재 (건너뜀, --force 권장)")
                skipped += 1
                continue
            if path.exists():
                bak = _backup(path)
                print(f"  📦 [{lang}] {pillar}.json 백업: {bak.name}")
            _write_json(path, data)
            print(f"  ✅ [{lang}] {pillar}.json 생성")
            created += 1

    print(f"\n완료: 생성 {created}개 / 건너뜀 {skipped}개")

    # 진척도 계산
    filled = 0
    for lang in ("ko",):
        d = DATA / lang / "core_pillars"
        for path in d.glob("*.json"):
            if ".bak." in path.name:
                continue
            try:
                if json.loads(path.read_text(encoding="utf-8")).get("hero"):
                    filled += 1
            except Exception:
                pass
    print(f"진척도: {filled}/60 ({filled * 100 // 60}%)")

    print("\n검증:")
    print("  pytest tests/test_core_pillar_content.py -v")
    print("  pytest -q")
    print("\n서버가 실행 중이라면 재시작 필수(캐시 무효화).")
    return 0


if __name__ == "__main__":
    sys.exit(main())