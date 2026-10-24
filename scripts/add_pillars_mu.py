#!/usr/bin/env python3
"""
戊 일간 6일주 추가 (戊子, 戊寅, 戊辰, 戊午, 戊申, 戊戌).
戊는 무토(산)의 기운으로, 묵직하고 신뢰를 주는 성향입니다.
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


# ✅ 추가: 한자 → 한글 독음 (traditional 포맷 유지용)
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
        "戊子": {
            "name": "호수 위의 산", "pillar": "戊子",
            "hero": "당신은 깊고 고요한 호수를 품은 거대한 산입니다. 겉은 흔들림 없이 묵직하지만, 내면에는 깊은 감정의 물결이 흐르죠.",
            "narrative": [
                "당신은 누구에게나 든든한 버팀목 같은 사람입니다. 쉽게 흔들리지 않고, 어떤 상황에서도 중심을 잡아주죠. 사람들은 당신의 묵직함에 안도하고, 당신의 곁에서 안정을 찾습니다.",
                "하지만 그 거대한 산 아래에는 깊은 호수가 숨어 있습니다. 당신은 겉으로 감정을 크게 드러내지 않지만, 내면에서는 수많은 생각과 감정의 파도가 일렁이고 있어요. 사람들이 당신을 '무뚝뚝하다'거나 '속을 알 수 없다'고 느끼는 이유입니다.",
                "당신의 과제는 이 산과 호수를 분리하지 않는 것입니다. 강하다는 이유로 감정을 억누르면, 그 물은 점점 더 깊고 어두워집니다. 가끔은 산이 무너질 것처럼, 당신의 약한 감정을 꺼내 보여주세요.",
                "성숙한 戊子는 '단단함과 깊이를 동시에 가진 사람'입니다. 흔들리지 않는 중심을 유지하면서도, 내면의 물결을 스스로 인정하고 흘려보낼 줄 아는 사람. 그때 당신의 고요함은 더 이상 회피가 아니라, 진짜 평화가 됩니다."
            ],
            "shadows": [
                "감정을 숨기다 보니, 주변 사람들이 당신의 힘듦을 알아채지 못합니다.",
                "속마음을 말하지 않아 오해를 사거나, 혼자만의 외로움을 키웁니다.",
                "무뚝뚝한 태도로 인해 친밀감을 형성하는 데 시간이 오래 걸립니다."
            ],
            "advice": [
                "가까운 사람에게 '사실 나는 이런 생각을 하고 있어'라고 속마음을 조금씩 꺼내보세요.",
                "혼자만의 시간을 통해 내면의 물결을 정리하는 루틴을 만드세요.",
                "감정을 억누르는 것이 강함이 아니라는 것을 기억하세요."
            ],
            "keywords": ["단단한 산", "깊은 호수", "묵직한 안정", "내면의 물결"]
        },
        "戊寅": {
            "name": "숲을 키우는 산", "pillar": "戊寅",
            "hero": "당신은 거대한 숲을 품고 있는 산입니다. 스스로 자라나며, 그 숲이 무성해지도록 든든한 터전을 제공하죠.",
            "narrative": [
                "당신은 성장과 포용의 사람입니다. 산이 나무를 키우듯, 당신은 주변 사람들의 성장을 돕고 그들이 뻗어 나갈 수 있도록 지원합니다. 당신의 곁에 있으면 사람들은 이상하게 '더 나아질 수 있을 것 같다'는 확신을 얻습니다.",
                "당신은 현실적이면서도 비전이 있습니다. 땅에 발을 딛고 있지만, 그 위에서 무성하게 자라날 숲의 미래를 그립니다. 그래서 사업이나 조직을 이끌 때, 사람들은 당신의 든든함과 비전을 동시에 신뢰합니다.",
                "당신의 그림자는 '남의 성장에 자신을 다 쏟는 것'입니다. 숲이 무성해지도록 물과 영양분을 주다 보면, 정작 산 자체의 체력은 고갈될 수 있습니다. 당신의 성장도 그만큼 중요하다는 것을 잊지 마세요.",
                "성숙한 戊寅은 '자신도 숲의 일부임을 아는 사람'입니다. 당신이 키우는 사람들과 함께, 당신 자신도 자라고 있다는 것을 인정할 때, 당신의 산은 더욱 생명력으로 가득 차게 됩니다."
            ],
            "shadows": [
                "타인의 성장을 돕느라 정작 자신의 발전은 뒤로 미룹니다.",
                "자신이 키운 사람이 떠나면 배신감을 느낍니다.",
                "너무 많은 책임을 짊어지려다 번아웃이 옵니다."
            ],
            "advice": [
                "이번 주에는 당신 자신의 발전을 위해 투자할 시간을 확보하세요.",
                "주변 사람들에게 모든 것을 다 해주지 말고, 스스로 성장할 기회를 주세요.",
                "당신의 성장도 숲의 일부라는 사실을 기억하고, 스스로를 칭찬해 주세요."
            ],
            "keywords": ["성장의 터전", "든든한 지원", "비전 있는 산", "함께 자라남"]
        },
        "戊辰": {
            "name": "거대한 산맥", "pillar": "戊辰",
            "hero": "당신은 끝없이 이어진 거대한 산맥입니다. 그 어떤 외풍에도 흔들리지 않는 압도적인 존재감을 지녔죠.",
            "narrative": [
                "당신은 단호함과 신뢰의 표본입니다. 한 번 마음먹은 일은 반드시 해내고, 맡은 바 책임을 끝까지 집니다. 사람들은 당신의 이런 묵직함과 확고함에 깊은 신뢰를 보냅니다.",
                "당신은 자기 확신이 강한 사람입니다. 쉽게 흔들리지 않기 때문에, 복잡한 문제를 정면으로 돌파하는 힘이 있습니다. 조직을 이끌거나 큰 프로젝트를 진두지휘할 때 당신의 진가가 발휘됩니다.",
                "당신의 그림자는 '고집과 경직성'입니다. 산맥이 움직이지 않듯, 당신도 자신의 방식이 틀렸다는 것을 인정하기 어려워할 때가 있습니다. 때로는 유연하게 물러서는 것이 더 큰 산을 만드는 길입니다.",
                "성숙한 戊辰은 '단단함 속에 유연함을 품은 사람'입니다. 확고한 중심을 잡되, 필요할 때는 태도를 바꿀 줄 아는 지혜를 갖출 때, 당신의 산맥은 더욱 풍요로워집니다."
            ],
            "shadows": [
                "자신의 의견이 틀렸을 때도 쉽게 인정하지 못합니다.",
                "다른 사람의 의견을 무시하거나 무시하는 태도로 비칠 수 있습니다.",
                "변화가 필요한 상황에서도 고집을 부려 기회를 놓칩니다."
            ],
            "advice": [
                "결정을 내리기 전에 '혹시 내가 놓치고 있는 게 있을까?'를 한 번 더 생각해 보세요.",
                "다른 사람의 의견을 끝까지 경청하는 연습을 하세요.",
                "유연함은 약함이 아니라, 더 큰 산을 만드는 지혜입니다."
            ],
            "keywords": ["거대한 산맥", "단호한 신뢰", "확고한 중심", "유연한 지혜"]
        },
        "戊午": {
            "name": "불을 품은 산", "pillar": "戊午",
            "hero": "당신은 거대한 산속에 뜨거운 용암을 품고 있는 화산입니다. 겉은 고요하지만, 내면에는 뜨거운 열정이 흐르죠.",
            "narrative": [
                "당신은 겉으로 보기엔 차분하고 무뚝뚝해 보이지만, 내면에는 누구보다 뜨거운 열정을 품고 있는 사람입니다. 이 이중성 때문에 처음 만나는 사람들은 당신을 오해하기 쉽습니다.",
                "당신은 한 번 불붙으면 무섭게 집중합니다. 좋아하는 일이나 목표를 향해서는 엄청난 에너지를 쏟아붓고, 쉽게 포기하지 않습니다. 이 열정은 당신을 성공으로 이끄는 가장 강력한 원동력입니다.",
                "당신의 그림자는 '감정의 폭발'입니다. 용암이 쌓이다 보면, 어느 순간 걷잡을 수 없이 터져 나옵니다. 평소에 감정을 억누르기보다, 조금씩 표현하고 배출하는 습관을 들여야 합니다.",
                "성숙한 戊午는 '열정을 다스리는 사람'입니다. 뜨거운 열정을 품되, 그것이 주변을 태우지 않도록 조절할 줄 아는 사람. 그때 당신의 열정은 사람들을 끌어당기는 강력한 중력이 됩니다."
            ],
            "shadows": [
                "평소 참다가 폭발하면 주변 사람들에게 큰 상처를 줍니다.",
                "자신의 열정을 주변에 강요하거나 압도할 때가 있습니다.",
                "겉과 속의 온도 차이 때문에 사람들이 당신을 이해하기 어려워합니다."
            ],
            "advice": [
                "화가 나거나 서운할 때 즉시 표현하는 연습을 하세요. 폭발을 막는 길입니다.",
                "당신의 열정을 긍정적인 에너지로 승화시킬 취미나 운동을 찾으세요.",
                "가끔은 당신의 뜨거운 내면을 주변 사람들에게 솔직하게 보여주세요."
            ],
            "keywords": ["화산", "숨겨진 열정", "뜨거운 집중", "감정의 조절"]
        },
        "戊申": {
            "name": "광맥을 품은 산", "pillar": "戊申",
            "hero": "당신은 단단한 암석 아래 귀한 보석과 광맥을 품고 있는 산입니다. 숨겨진 가치와 예리함을 지녔죠.",
            "narrative": [
                "당신은 실용적이면서도 날카로운 사람입니다. 겉으로는 무던해 보이지만, 상황의 본질을 꿰뚫어 보는 예리한 눈을 지녔습니다. 사람들은 당신이 가진 이 숨겨진 날카로움에 놀라곤 합니다.",
                "당신은 자원을 관리하고 가치를 창출하는 데 탁월한 재능이 있습니다. 산이 광물을 품듯, 당신은 주변의 유용한 자원과 정보를 모아 실질적인 결과물을 만들어냅니다. 사업이나 재무 관리에 재능이 있습니다.",
                "당신의 그림자는 '지나친 계산'입니다. 예리함이 지나치면 모든 것을 따지고 계산하게 되어, 관계가 메말라버릴 수 있습니다. 모든 상황을 이익과 손해로만 판단하지 않도록 주의하세요.",
                "성숙한 戊申은 '가치와 따뜻함을 함께 나누는 사람'입니다. 당신의 예리한 통찰력으로 실질적인 성과를 내되, 그 과정에서 사람들의 마음까지 살필 줄 알 때, 당신은 진짜 리더가 됩니다."
            ],
            "shadows": [
                "모든 것을 이익과 손해로 따지다 보면 정이 떨어집니다.",
                "타인의 의도를 지나치게 의심하거나 계산적으로 대할 수 있습니다.",
                "예리함이 독설로 변해 주변에 상처를 줄 때가 있습니다."
            ],
            "advice": [
                "가끔은 계산 없이, 그냥 마음 가는 대로 행동해 보세요.",
                "주변 사람들의 감정에 조금 더 신경 쓰고 공감해 주세요.",
                "당신의 예리함을 타인을 돕는 데 사용해 보세요."
            ],
            "keywords": ["숨겨진 보석", "예리한 통찰", "실질적 가치", "자원 관리"]
        },
        "戊戌": {
            "name": "굳건한 요새", "pillar": "戊戌",
            "hero": "당신은 성벽처럼 든든하게 주변을 지키는 요새입니다. 신뢰와 책임감으로 무장한 사람이죠.",
            "narrative": [
                "당신은 책임감과 의리의 표본입니다. 한 번 믿으면 끝까지 가고, 내 사람을 향한 보호 본능이 아주 강합니다. 당신의 곁에 있는 사람들은 당신이 뒤에서 든든히 지켜주고 있다는 사실을 알고 안심합니다.",
                "당신은 원칙과 규율을 중시합니다. 옳고 그름이 분명하고, 선을 넘는 것을 싫어합니다. 이런 태도 덕분에 당신은 조직에서 신뢰받는 핵심 인물이 되곤 합니다.",
                "당신의 그림자는 '지나친 경계와 배타성'입니다. 요새가 외부인을 막듯, 당신도 자신의 마음속에 들어오는 사람을 지나치게 경계할 때가 있습니다. 너무 높은 성벽은 당신 자신을 외롭게 만듭니다.",
                "성숙한 戊戌은 '문을 열 줄 아는 요새'입니다. 평소에는 든든하게 지키되, 필요할 때는 성문을 열어 사람들을 받아들이고 마음을 나누는 사람. 그때 당신의 든든함은 더 큰 사랑과 신뢰를 낳습니다."
            ],
            "shadows": [
                "지나친 경계심 때문에 사람들과 깊은 친밀감을 형성하기 어렵습니다.",
                "고집이 세고 융통성이 없어 보일 때가 있습니다.",
                "감정을 잘 표현하지 않아, 무뚝뚝하다는 오해를 받습니다."
            ],
            "advice": [
                "이번 주에 평소보다 마음을 조금 더 열고, 믿을 만한 사람에게 고민을 털어놓아 보세요.",
                "자신의 원칙을 고수하되, 다른 사람의 다름을 인정하는 연습을 하세요.",
                "가끔은 당신이 힘들 때 주변 사람들에게 기대보세요."
            ],
            "keywords": ["요새", "강한 책임감", "의리", "보호 본능"]
        }
    },
    "en": {
        "戊子": {
            "name": "Mountain over the Lake", "pillar": "戊子",
            "hero": "You are a massive mountain cradling a deep, still lake. Unshakable on the outside, with deep emotional currents underneath.",
            "narrative": [
                "You are the rock people rely on. You rarely waver, and you anchor the center of any situation. People find immense comfort in your presence.",
                "Beneath that massive mountain lies a deep lake. You don't show emotion loudly, but internally, many thoughts and feelings ripple. This is why people sometimes see you as stoic or hard to read.",
                "Your task is to not separate the mountain from the lake. Suppressing feelings because you must be 'strong' only makes the water deeper and darker. Let the mountain show a crack sometimes, and reveal your vulnerable feelings.",
                "A mature Mu-Ja is someone with both solidity and depth. Holding your center while acknowledging and letting flow your inner waters. Then your calm is no longer avoidance—it's true peace."
            ],
            "shadows": [
                "Hiding your emotions means people don't notice when you're struggling.",
                "Not speaking your mind causes misunderstandings and deepens your loneliness.",
                "A stoic demeanor makes it take a long time to build intimacy."
            ],
            "advice": [
                "Share one true thought with someone close—just a little bit of your inner world.",
                "Create a routine to clear your inner waters by spending time alone.",
                "Remember that suppressing emotion is not strength."
            ],
            "keywords": ["solid mountain", "deep lake", "heavy stability", "inner ripples"]
        },
        "戊寅": {
            "name": "Mountain Nurturing the Forest", "pillar": "戊寅",
            "hero": "You are a mountain holding a vast forest. You grow yourself while providing the ground for the forest to thrive.",
            "narrative": [
                "You are about growth and inclusion. Just as the mountain grows the trees, you help those around you grow and reach out. People feel a strange sense of 'I can be better' when they are around you.",
                "You are practical and visionary. Your feet are on the ground, but you picture the lush future of the forest that will grow above. That's why people trust your groundedness and your vision when you lead.",
                "Your shadow is giving yourself entirely to others' growth. Watering and feeding the forest can drain the mountain's energy. Remember your own growth matters just as much.",
                "A mature Mu-In knows they are part of the forest too. When you admit you're growing alongside the people you nurture, your mountain fills with even more vitality."
            ],
            "shadows": [
                "Postponing your own development while helping others grow.",
                "Feeling betrayed when someone you cultivated leaves.",
                "Taking on too many responsibilities and burning out."
            ],
            "advice": [
                "Set aside time this week to invest in your own growth.",
                "Give people the chance to grow on their own instead of doing everything for them.",
                "Remind yourself that your growth is part of the forest, and praise yourself for it."
            ],
            "keywords": ["grounds for growth", "solid support", "visionary mountain", "growing together"]
        },
        "戊辰": {
            "name": "Massive Mountain Range", "pillar": "戊辰",
            "hero": "You are an endless mountain range. An overwhelming presence that does not shake in any wind.",
            "narrative": [
                "You are the model of decisiveness and trust. What you set your mind to gets done, and you carry your responsibilities to the end. People put deep faith in your gravity and resolve.",
                "You are highly self-assured. Because you don't waver easily, you have the power to push through complex problems head-on. Your worth shines when you lead a team or command a large project.",
                "Your shadow is stubbornness and rigidity. Like a mountain range that does not move, you find it hard to admit you might be wrong. Sometimes, flexing is how you build a bigger mountain.",
                "A mature Mu-Jin is someone with flexibility inside firmness. When you keep your solid center but can shift your approach, your range becomes richer."
            ],
            "shadows": [
                "Finding it hard to admit fault even when you're wrong.",
                "Coming off as dismissive of others' opinions.",
                "Sticking to your guns during times that call for change, losing opportunities."
            ],
            "advice": [
                "Before deciding, ask once more, 'What might I be missing?'",
                "Practice listening to other people's opinions all the way through.",
                "Flexibility is not weakness—it's the wisdom of building bigger mountains."
            ],
            "keywords": ["massive range", "decisive trust", "solid center", "flexible wisdom"]
        },
        "戊午": {
            "name": "Mountain Holding Fire", "pillar": "戊午",
            "hero": "You are a volcano harboring hot magma inside a great mountain. Quiet outside, but with a fiery passion flowing within.",
            "narrative": [
                "You look calm and stoic on the outside, but you carry the hottest passion inside. This duality makes it easy for people to misread you when they first meet you.",
                "Once you ignite, you focus fiercely. You pour immense energy into what you love and don't give up. This passion is your strongest force for success.",
                "Your shadow is emotional eruption. When magma builds up, it explodes. Instead of bottling feelings, build the habit of expressing them little by little.",
                "A mature Mu-Wu is someone who governs their passion. Carrying hot fire but knowing how to keep it from burning others. Then your passion becomes a powerful gravity that draws people in."
            ],
            "shadows": [
                "Bottling it up and then exploding, leaving deep wounds on those around you.",
                "Forcing your passion on others or overwhelming them.",
                "The temperature difference between inside and outside makes you hard to understand."
            ],
            "advice": [
                "Practice expressing anger or hurt immediately. That prevents explosions.",
                "Find a hobby or exercise to sublimate your passion into positive energy.",
                "Show your fiery inner self honestly to those around you sometimes."
            ],
            "keywords": ["volcano", "hidden passion", "fierce focus", "governing emotion"]
        },
        "戊申": {
            "name": "Mountain of Ore", "pillar": "戊申",
            "hero": "You are a mountain holding precious gems and ore beneath solid rock. You carry hidden value and sharpness.",
            "narrative": [
                "You are pragmatic and sharp. You seem easygoing, but you have a keen eye that pierces through to the essence of things. People are often surprised by this hidden sharpness.",
                "You have a rare talent for managing resources and creating value. Like a mountain holding minerals, you gather useful resources and information to produce tangible results. You have a head for business or finance.",
                "Your shadow is over-calculation. Sharpness taken too far means calculating everything, which dries up relationships. Take care not to judge every situation only by profit and loss.",
                "A mature Mu-Shen shares both value and warmth. Producing real results with your sharp insight, while also minding people's hearts along the way, is what makes you a true leader."
            ],
            "shadows": [
                "Calculating everything by profit and loss makes you seem cold.",
                "Being overly suspicious or calculating about others' intentions.",
                "Sharpness turns into sharp words that hurt those around you."
            ],
            "advice": [
                "Sometimes, just act on what feels right without calculating.",
                "Pay more attention to the emotions of those around you and empathize.",
                "Use your sharpness to help others."
            ],
            "keywords": ["hidden gems", "sharp insight", "tangible value", "resource management"]
        },
        "戊戌": {
            "name": "Impenetrable Fortress", "pillar": "戊戌",
            "hero": "You are a fortress that guards those around you like a city wall. You are armed with trust and responsibility.",
            "narrative": [
                "You are the model of responsibility and loyalty. Once you trust someone, you go all the way, and your protective instinct for your people is fierce. Those around you find peace knowing you're guarding their back.",
                "You value principles and discipline. Right and wrong are clear, and you hate crossing lines. Because of this, you often become the trusted key figure in an organization.",
                "Your shadow is excessive boundaries and exclusivity. Like a fortress keeping outsiders out, you guard your heart too closely. Walls that are too high leave you lonely.",
                "A mature Mu-Xu is a fortress that knows how to open its gates. Guarding solidly in ordinary times, but opening the gates and sharing your heart when needed. Then your security gives birth to greater love and trust."
            ],
            "shadows": [
                "Excessive wariness makes deep intimacy hard to form.",
                "You can seem stubborn and inflexible.",
                "Not expressing emotions well leads to being misread as cold."
            ],
            "advice": [
                "Open your heart a little more this week. Share a worry with someone you trust.",
                "Hold your principles while practicing accepting others' differences.",
                "Sometimes, lean on those around you when you're struggling."
            ],
            "keywords": ["fortress", "strong responsibility", "loyalty", "protective instinct"]
        }
    }
}


def main() -> int:
    ap = argparse.ArgumentParser(description="戊 일간 6일주 추가")
    ap.add_argument("--force", action="store_true", help="스텁 덮어쓰기")
    args = ap.parse_args()

    print("=== 戊 일간 6일주 추가 (戊子, 戊寅, 戊辰, 戊午, 戊申, 戊戌) ===")
    
    # 1. JSON 파일 생성
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

    # 2. pillar_names.json 업데이트
    for lang in ("ko", "en"):
        names_path = DATA / lang / "pillar_names.json"
        if names_path.exists():
            names_data = json.loads(names_path.read_text(encoding="utf-8"))
            for pillar, p_data in PILLARS[lang].items():
                names_data[pillar] = {
                    "name": p_data["name"],
                    "traditional": f"{_reading(pillar)}({pillar})"   # ✅ 수정: 무자(戊子) 형식
                }
            _write_json(names_path, names_data)
            print(f"  - [{lang}] pillar_names.json 업데이트 완료")

    print("\n✅ 완료. 검증:")
    print("  pytest -q")
    return 0

if __name__ == "__main__":
    sys.exit(main())