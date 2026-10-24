#!/usr/bin/env python3
"""
丙 일간 5일주 추가 (丙子, 丙寅, 丙辰, 丙午, 丙戌).
丙申은 이미 있음. 60일주 중 6개(丙 계열 전부)가 완성됩니다.

사용:
    python scripts/add_pillars_pro.py
    python scripts/add_pillars_pro.py --force   # 이미 있어도 덮어쓰기
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
        "丙子": {
            "pillar": "丙子",
            "hero": "당신은 어두운 호수 위에 떠 있는 등불입니다. 수면 위는 따뜻하게 빛나지만, 그 아래로는 깊고 서늘한 물결이 흐르죠.",
            "narrative": [
                "당신을 처음 만나는 사람들은 당신을 밝고 표현력 좋은 사람으로 기억합니다. 대화를 리드하고, 분위기를 밝히고, 사람들 사이에서 자연스럽게 중심이 되죠. 그런데 조금 더 가까이 다가가면, 그 밝음 아래에 생각보다 깊은 물결이 흐르고 있다는 걸 눈치챕니다. 당신은 겉으로 보이는 것보다 훨씬 복잡한 내면을 가진 사람이에요.",
                "당신의 강점은 이중성입니다. 표면의 열정으로 사람을 끌어들이고, 밑의 깊이로 그 사람을 붙듭니다. 이 두 결이 함께 있어서, 당신은 가볍지 않으면서도 무겁지 않은 사람이 됩니다. 문제는 이 두 결이 스스로 균형을 잃을 때예요. 표면만 앞서면 얕아 보이고, 밑만 앞서면 어두워집니다.",
                "감정의 파도가 오르내리는 것도 그래서일 겁니다. 어떤 날은 세상 모든 것을 사랑할 수 있을 것 같고, 어떤 날은 이유 없이 가라앉습니다. 그 물결을 스스로에게 설명하지 않아도, 그냥 '지금 내가 깊은 쪽에 있다'는 걸 알아채기만 해도 충분합니다. 억지로 물 위로 끌어올리려 하지 마세요.",
                "당신의 성숙은 열정과 깊이를 동시에 인정하는 데서 옵니다. 밝은 면만 사랑하고 어두운 면을 숨기려 하면, 두 면이 서로를 갉아먹기 시작합니다. 두 면이 함께 있을 때, 당신은 사람들이 진짜로 머물고 싶어 하는 자리가 됩니다. 그게 당신이 지닌 가장 단단한 매력이에요.",
            ],
            "shadows": [
                "기분이 가라앉을 때, 주변에 이유를 설명하지 못해 사람들이 당신을 오해합니다.",
                "표면의 밝음에 익숙해진 사람들이, 당신의 깊은 고민을 알아채지 못할 때가 있습니다.",
                "감정이 깊을수록 판단이 흐려집니다. 중요한 결정은 물결이 잦아들 때 내리세요.",
            ],
            "advice": [
                "이번 주에 이유 없이 가라앉는 순간을 하나 붙잡아 보세요. 그게 어떤 종류의 물결인지 알아채기만 해도 좋습니다.",
                "가까운 사람에게 '요즘 좀 깊은 쪽에 있어'라고 말해보세요. 설명이 필요 없습니다.",
                "큰 결정은 감정의 파도가 지나간 뒤에 내리세요. 파도 위에서 내린 결단은 오래가지 않습니다.",
                "당신의 밝음이 진짜인 순간과, 그 밝음이 사람들을 위한 연기인 순간을 구분해 보세요.",
            ],
            "keywords": ["따뜻한 깊이", "빛과 물결", "표면과 심연", "조용한 열정"],
        },
        "丙寅": {
            "pillar": "丙寅",
            "hero": "당신은 소나무 숲 한가운데 피어오르는 불꽃입니다. 땔감이 끝없이 공급되는, 유난히 뜨거운 사람이죠.",
            "narrative": [
                "당신은 자기 안에 연료를 가진 사람입니다. 누가 시키지 않아도 스스로 타오르고, 타오르는 것 자체가 당신의 존재 방식이에요. 처음 만나는 사람들은 당신의 에너지에 압도되거나, 혹은 완전히 매료됩니다. 그 사이는 거의 없죠.",
                "당신의 창조력은 폭발적입니다. 아이디어가 끊이지 않고, 무엇이든 시작하는 순간에 가장 강렬한 에너지가 나옵니다. 그래서 창업, 개척, 새로운 무언가를 여는 일에서 당신은 남들보다 훨씬 앞서갑니다. 이 불꽃은 진짜입니다. 연기나 과장이 아니에요.",
                "문제는 이 불꽃이 지속 가능한가입니다. 소나무 숲은 언젠가 다 탑니다. 당신이 스스로를 태우는 속도를 조절하지 않으면, 어떤 프로젝트에서든 중반에 힘이 빠지고, 관계에서도 갑자기 식어버리는 순간이 옵니다. 이건 당신의 열정이 가짜라는 뜻이 아니라, 열정에 '쉼'이라는 산소를 넣어야 한다는 뜻이에요.",
                "성숙한 丙寅은 '천천히 타는 법'을 배운 사람입니다. 처음의 뜨거움을 오래 끌고 가는 지혜를 익히면, 당신은 한순간의 폭발이 아니라 몇 년에 걸친 대화재가 됩니다. 그게 당신의 진짜 모습이에요.",
            ],
            "shadows": [
                "초반에 모든 에너지를 쏟고, 중반에 힘이 빠지면 스스로를 자책합니다.",
                "빠른 시작에 익숙해진 주변 사람들이, 당신의 느린 마무리를 못 견뎌합니다.",
                "쉬는 시간을 '낭비'라고 느낍니다. 그 감각이 번아웃의 시작입니다.",
            ],
            "advice": [
                "새 프로젝트를 시작할 때 '이걸 몇 년에 걸쳐 할 것인가'를 함께 정해보세요.",
                "이번 주에 하루는 완전히 아무것도 시작하지 마세요. 시작하지 않는 것도 연습입니다.",
                "당신이 타오르는 것과, 당신이 타오르도록 강요받는 것을 구분해 보세요.",
                "오래 타는 불은 산소가 필요합니다. '쉬는 시간'을 연료의 일부로 재정의하세요.",
            ],
            "keywords": ["끊임없는 연료", "폭발적 시작", "뜨거운 창조", "긴 호흡"],
        },
        "丙辰": {
            "pillar": "丙辰",
            "hero": "당신은 안개 낀 들판 위의 햇살입니다. 따뜻함이 수증기로 변해, 주변을 부드럽게 감싸죠.",
            "narrative": [
                "당신은 따뜻하지만 흐릿한 사람입니다. 온기는 진짜인데, 그 온기가 어디로 향하는지, 무엇을 만들고 있는지 스스로도 선명하지 않을 때가 많아요. 그 흐릿함은 당신의 결점이 아니라 결이에요. 어떤 사람은 당신을 '따뜻한 사람'으로 기억하고, 어떤 사람은 '알 수 없는 사람'으로 기억합니다.",
                "당신은 변화와 변형의 사람입니다. 불이 흙을 만나 수증기가 되듯, 당신은 상황에 따라 모습이 달라집니다. 한 자리에서 고정되어 있기보다 관계와 환경에 따라 형태를 바꾸는 쪽이 자연스러워요. 그래서 당신은 사람을 이해하고 분위기를 감지하는 능력이 뛰어납니다. 눈치가 아니라, 그냥 그게 당신의 언어예요.",
                "문제는 이 흐릿함이 판단을 흐릴 때입니다. 감정과 사실이 뒤섞여, 내가 지금 무엇을 느끼는지, 무엇을 원하는지 스스로도 헷갈리는 순간이 옵니다. 그때 무리하게 '선명해지려' 하지 마세요. 안개는 걷히라고 기다리는 게 아니라, 걷힐 때까지 조용히 있는 거예요.",
                "당신의 강점은 이 흐릿함이 만들어내는 부드러움과 포용입니다. 세상을 선명한 경계로 자르지 않고, 흐릿하게 감싸 안을 수 있는 사람. 그게 당신이 사람들 곁에 머물 수 있는 이유입니다. 다만 자기 자신에게는 가끔 선명한 질문을 던져야 해요. '지금 나는 어디에 있고, 어디로 가고 싶은가?'",
            ],
            "shadows": [
                "감정과 사실이 뒤섞여, 내가 무엇을 원하는지 스스로도 모를 때가 있습니다.",
                "흐릿함을 핑계로 중요한 결정을 계속 미루게 됩니다.",
                "주변 사람들이 당신을 '생각이 많은 사람'과 '우유부단한 사람' 사이에서 헷갈려 합니다.",
            ],
            "advice": [
                "하루에 한 번, 스스로에게 선명한 질문을 하나 던지세요. '지금 나는 무엇을 원하는가?'",
                "감정이 흐릴 때는 사실만 종이에 적어보세요. 감정은 그 다음입니다.",
                "선명해지려 애쓰지 말고, 안개가 걷힐 시간을 주세요. 판단은 그 다음에.",
                "당신이 지금 어디에 있는지, 한 달에 한 번은 명확하게 말해보세요. 가족이든, 친구든, 일이든.",
            ],
            "keywords": ["따뜻한 흐림", "변형의 힘", "부드러운 감지", "안개의 지혜"],
        },
        "丙午": {
            "pillar": "丙午",
            "hero": "당신은 정오의 태양입니다. 그림자 없이 모든 것을 비추고, 모든 것을 뜨겁게 만드는 사람이죠.",
            "narrative": [
                "당신은 강렬함 그 자체입니다. 방에 들어서면 온도가 바뀌고, 말을 꺼내면 대화의 방향이 바뀝니다. 이건 당신이 노력해서 만드는 게 아니라, 그냥 그렇게 되는 거예요. 사람들은 당신 앞에서 크게 웃거나, 혹은 조용히 물러섭니다. 중간이 별로 없죠.",
                "당신은 자신을 숨기지 못합니다. 기분이 좋으면 다 보이고, 화가 나면 다 보입니다. 이 투명함은 사람들에게 신뢰를 줍니다 — 당신이 거짓말을 못 하는 사람이라는 걸 알기 때문이죠. 대신 이 투명함은 당신의 피로이기도 합니다. 항상 다 보여야 한다는 압박이 되거든요.",
                "정오의 태양에는 그림자가 없습니다. 하지만 그건 오래 지속될 수 없다는 뜻이기도 해요. 해는 반드시 기울고, 그림자는 다시 길어집니다. 당신의 과제는 정오의 상태를 유지하는 게 아니라, 기울어지는 자신을 받아들이는 것입니다. 해가 진다고 해가 실패한 건 아니에요.",
                "성숙한 丙午는 '빛의 강도를 조절할 줄 아는 사람'입니다. 항상 최대치로 타지 않고, 때로는 흐린 날의 햇살처럼 부드럽게 존재할 줄 아는 사람. 그때 당신은 사람들을 태우는 존재에서, 사람들이 머물고 싶은 온도가 됩니다.",
            ],
            "shadows": [
                "지속적인 최대 출력이 몸과 마음을 갉아먹습니다. 번아웃이 가장 가까운 그림자예요.",
                "당신의 강렬함이 주변 사람들을 압도해, 정작 깊은 이야기를 못 나누게 만듭니다.",
                "'요즘 좀 가라앉았다'는 말을 스스로에게 허락하지 않습니다.",
            ],
            "advice": [
                "이번 주에 한 번, 스스로에게 '지금 최대 출력인가, 적당한 출력인가?' 물어보세요.",
                "당신이 없을 때도 잘 돌아가는 상황을 일부러 한 번 만들어 보세요.",
                "흐린 날의 햇살을 연습하세요. 오늘 하루는 조용히 있는 것도 하나의 방식입니다.",
                "당신의 강렬함을 부정하지 말되, 강렬함 뒤에 오는 회복 시간도 똑같이 중요하게 다루세요.",
            ],
            "keywords": ["정오의 빛", "강렬한 존재감", "투명한 열정", "빛의 조절"],
        },
        "丙戌": {
            "pillar": "丙戌",
            "hero": "당신은 언덕 위의 화톳불입니다. 오래 타도록 설계된, 누구나 몸을 녹일 수 있는 자리죠.",
            "narrative": [
                "당신은 따뜻함과 안정이 함께 있는 사람입니다. 다른 丙일간들이 각자 다른 방식으로 타오르는 반면, 당신의 불은 흙 위에 단단히 자리 잡고 있어요. 그래서 당신은 뜨겁기만 한 사람이 아니라, 오래 머물 수 있는 온기를 가진 사람입니다.",
                "당신은 사람들을 돌보는 데 자연스러운 재능이 있습니다. 화톳불이 주변 사람들을 모으듯, 당신의 곁에는 자연스럽게 사람들이 모입니다. 당신이 특별히 뭘 하는 게 아니라, 그냥 거기 있다는 것만으로도 사람들은 위로를 받습니다. 이건 흔한 능력이 아니에요.",
                "문제는 이 '모두의 온기'가 당신을 소진시킬 수 있다는 것입니다. 당신이 쉬지 않고 모든 사람에게 온기를 주면, 정작 당신 자신의 불은 언젠가 꺼집니다. 화톳불도 땔감이 필요하죠. 당신의 땔감은 무엇인지, 마지막으로 언제 스스로를 채웠는지 스스로에게 물어보세요.",
                "성숙한 丙戌은 '경계를 지키는 온기'를 아는 사람입니다. 누구에게나 열려 있되, 자신을 태우지 않는 방식으로 열려 있는 사람. 당신의 불은 오래 타도록 만들어진 만큼, 얼마나 오래 타느냐가 당신의 진짜 가치입니다.",
            ],
            "shadows": [
                "다른 사람들을 돌보느라 정작 자신의 땔감을 잊습니다.",
                "당신의 온기가 '온기'를 넘어 '통제'가 될 때가 있습니다.",
                "쉬지 않고 모두를 챙기다가 갑자기 완전히 꺼져버리는 패턴이 있습니다.",
            ],
            "advice": [
                "이번 주에 당신의 땔감이 무엇인지 세 가지 적어보세요. 그게 없다면 당신은 오래 못 탑니다.",
                "당신이 챙기는 사람 중 한 명에게, 이번에는 당신을 챙겨달라고 부탁해 보세요.",
                "당신의 온기가 상대가 원해서 주는 것인지, 당신이 주고 싶어서 주는 것인지 구분해 보세요.",
                "완전히 꺼지기 전에, 작은 불씨 하나 정도는 스스로에게 남겨두세요.",
            ],
            "keywords": ["오래 타는 불", "단단한 온기", "돌봄의 힘", "지키는 경계"],
        },
    },
    "en": {
        "丙子": {
            "pillar": "丙子",
            "hero": "You're a lantern floating on a dark lake. Warm light above the surface — cold, deep currents below.",
            "narrative": [
                "People who meet you first remember a bright, expressive person. You lead conversations, warm up rooms, and naturally become the center of things. But step closer, and they notice — there's something deeper moving under the brightness. You are more complex inside than you look from across the room.",
                "Your strength is this duality. The heat on the surface draws people in; the depth underneath keeps them there. Having both makes you someone who isn't light, and isn't heavy either. The trouble comes when these two halves lose their balance. When only the surface leads, you seem shallow. When only the depth leads, you go dark.",
                "This is probably why your emotional tides rise and fall as they do. Some days you could love everything in the world. Other days you sink for no clear reason. You don't have to explain the wave to yourself — just notice, 'I'm on the deep side right now.' Don't force yourself back up.",
                "Your maturity comes from letting both the fire and the depth exist at once. If you only love the bright side and hide the dark one, they start eating each other. When both are present, you become the place people actually want to stay. That's your most solid charm.",
            ],
            "shadows": [
                "When you sink, you can't explain why, and people misread you.",
                "People used to the surface don't notice your deeper worries.",
                "The deeper your feeling, the blurrier your judgment. Make big decisions when the tide is low.",
            ],
            "advice": [
                "This week, catch one moment of sinking without a reason. Just notice what kind of wave it is.",
                "Tell someone close, 'I'm on the deep side right now.' No explanation needed.",
                "Make big decisions after the emotional wave has passed. Calls made on the wave don't last.",
                "Separate the moments when your brightness is real from when it's a performance for others.",
            ],
            "keywords": ["warm depth", "light and tide", "surface and abyss", "quiet fire"],
        },
        "丙寅": {
            "pillar": "丙寅",
            "hero": "You're a flame at the heart of a pine forest. Fuel that never runs out — and a fire that burns hotter than most.",
            "narrative": [
                "You carry your own fuel. You burn without being lit by anyone, and burning is simply how you exist. New people either feel overpowered by your energy or completely drawn to it. There's rarely a middle.",
                "Your creativity is explosive. Ideas don't stop, and your strongest energy comes at the very start of any endeavor. That's why you outrun most people in founding, opening, and starting things. The fire is real — not smoke, not hype.",
                "The question is whether the fire is sustainable. Pine forests burn out eventually. If you don't pace yourself, you run out of steam mid-project, and in relationships you suddenly go cold. This isn't proof that your passion is fake — it means your passion needs oxygen in the form of rest.",
                "A mature Bing-Yin is someone who learns to burn slowly. Once you can carry the initial heat over a long stretch, you stop being a single flare and become a slow, years-long fire. That's your real form.",
            ],
            "shadows": [
                "You pour everything into the start, then blame yourself when you run out mid-way.",
                "People used to your fast starts can't keep up with your slower finishes.",
                "You feel like rest is waste. That feeling is the beginning of burnout.",
            ],
            "advice": [
                "When you start something new, also decide 'how many years is this meant to run?'",
                "Take one full day this week doing nothing new. Not-starting is also a practice.",
                "Separate the moments you're burning on your own from the moments you're being pushed to burn.",
                "A long fire needs oxygen. Redefine rest as part of your fuel.",
            ],
            "keywords": ["relentless fuel", "explosive start", "hot creation", "long breath"],
        },
        "丙辰": {
            "pillar": "丙辰",
            "hero": "You're sunlight over a misty marsh. Warmth that turns to vapor and quietly wraps around everything.",
            "narrative": [
                "You're warm but blurry. The heat is real, but where it points and what it's building is often not clear — even to you. That blur isn't a flaw; it's a texture. Some people remember you as 'the warm one.' Others remember you as 'the one I couldn't quite read.'",
                "You're a person of transformation. Just as fire meets earth and becomes vapor, you take shape according to what's around you. You're more natural changing form with relationships and settings than staying fixed in one place. That's why you read people and rooms so well. Not because you're perceptive as a strategy — because that's simply your language.",
                "The trouble is when the blur blurs your judgment. Feeling and fact get tangled, and you can't tell what you actually feel or want. When that happens, don't force yourself to 'become clear.' Fog doesn't clear by being pushed. It clears by being given time.",
                "Your strength is the softness and acceptance this blur produces. You don't slice the world into clean lines; you can hold it with a blurred kindness. That's why people stay near you. But you need to ask yourself a sharp question sometimes: 'Where am I, and where do I want to go?'",
            ],
            "shadows": [
                "Feeling and fact get tangled, and you don't know what you want.",
                "You use the blur as an excuse to delay important decisions.",
                "People around you are unsure whether you're 'deep' or 'indecisive.'",
            ],
            "advice": [
                "Once a day, ask one sharp question of yourself: 'What do I actually want right now?'",
                "When feelings are unclear, write down the facts first. Feelings come next.",
                "Don't strain to become clear. Give the fog time. Judgment comes after.",
                "Once a month, say clearly where you are — to family, friends, work, whoever.",
            ],
            "keywords": ["warm blur", "power of form", "soft perception", "wisdom of fog"],
        },
        "丙午": {
            "pillar": "丙午",
            "hero": "You're the sun at noon. No shadow, everything lit, everything hot.",
            "narrative": [
                "You are intensity itself. Walk into a room and the temperature changes. Speak, and the conversation turns. This isn't something you work at — it just happens. People either laugh loud around you or quietly step back. There's rarely a middle.",
                "You can't hide. When you're happy, everyone sees it. When you're angry, everyone sees it too. That transparency earns trust — people know you're not a liar. But it's also a fatigue. Being fully visible is a constant pressure.",
                "The sun at noon casts no shadow. But that also means it can't last. The sun has to tilt, and shadows have to grow back. Your task isn't to hold noon forever — it's to accept the tilt. The sun going down is not the sun failing.",
                "A mature Bing-Wu is someone who can dim the light on purpose. Who doesn't always burn at full capacity. Who can sometimes be the sunlight on a cloudy day. That's when you stop being someone who burns people and become the temperature they want to stay in.",
            ],
            "shadows": [
                "Constant maximum output eats your body and mind. Burnout is your nearest shadow.",
                "Your intensity overwhelms people, and deep conversations rarely happen around you.",
                "You don't allow yourself to say, 'I'm running lower lately.'",
            ],
            "advice": [
                "This week, ask yourself once: am I at max output or at a reasonable output?",
                "Deliberately set up one situation where things run fine without you.",
                "Practice being a cloudy-day sun. Sitting quietly for a day is also a way of being.",
                "Don't deny your intensity — but treat the recovery after it as equally important.",
            ],
            "keywords": ["noon light", "magnetic presence", "transparent heat", "dialing the light"],
        },
        "丙戌": {
            "pillar": "丙戌",
            "hero": "You're a campfire on a hill. Built to burn long — a place where anyone can warm up.",
            "narrative": [
                "You carry warmth and stability together. Other Bing-day people burn in their own ways; yours is anchored to the ground. That's why you aren't just hot — you're the kind of warmth people can stay in for a long time.",
                "You have a natural talent for caring for people. Just as a campfire draws people near, people naturally gather around you. It's not because you do something special. It's because being there is enough to comfort them. That's rarer than it sounds.",
                "The trouble is that 'everyone's warmth' can burn you out. If you keep giving warmth without stopping, your own fire eventually goes out. Even a campfire needs fuel. Ask yourself: what is my fuel, and when did I last feed it?",
                "A mature Bing-Xu is someone who knows how to give warmth with boundaries. Open to anyone, but open in a way that doesn't burn you. Your fire was built to burn long — so how long it burns is your real worth.",
            ],
            "shadows": [
                "You care for others and forget your own fuel.",
                "Your warmth can tip into control.",
                "You hold everyone up without rest, then suddenly go completely dark.",
            ],
            "advice": [
                "This week, write down three things that are your fuel. If none, you can't burn long.",
                "Ask one of the people you care for to care for you this time.",
                "Separate the warmth you give because they want it from the warmth you give because you want to give.",
                "Leave at least one ember for yourself before you go out completely.",
            ],
            "keywords": ["long fire", "solid warmth", "power of care", "boundaries that hold"],
        },
    },
}


def main() -> int:
    ap = argparse.ArgumentParser(description="丙 일간 5일주 추가")
    ap.add_argument("--force", action="store_true", help="이미 있어도 덮어쓰기")
    args = ap.parse_args()

    print("=== 丙 일간 5일주 추가 (丙子·丙寅·丙辰·丙午·丙戌) ===")
    created = skipped = 0
    for lang in ("ko", "en"):
        for pillar, data in PILLARS[lang].items():
            path = DATA / lang / "core_pillars" / f"{pillar}.json"
            if path.exists() and not args.force:
                print(f"  ⏭️  [{lang}] {pillar}.json 이미 존재 (건너뜀)")
                skipped += 1
                continue
            if path.exists():
                bak = _backup(path)
                print(f"  📦 [{lang}] {pillar}.json 백업: {bak.name}")
            _write_json(path, data)
            print(f"  ✅ [{lang}] {pillar}.json 생성")
            created += 1

    print(f"\n완료: 생성 {created}개 / 건너뜀 {skipped}개")
    print("\n검증:")
    print("  pytest tests/test_core_pillar_content.py -v")
    print("  pytest -q")
    print("\n서버가 실행 중이라면 재시작 필수(캐시 무효화).")
    return 0


if __name__ == "__main__":
    sys.exit(main())