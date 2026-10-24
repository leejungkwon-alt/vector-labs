#!/usr/bin/env python3
"""
乙 일간 6일주 추가 (乙丑, 乙卯, 乙巳, 乙未, 乙酉, 乙亥). — 마지막 계열
乙은 음목(陰木)의 기운으로, 덩굴과 꽃처럼 유연하고 지속적인 성향입니다.
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
        "乙丑": {
            "name": "얼어붙은 땅의 덩굴", "pillar": "乙丑",
            "hero": "당신은 얼어붙은 땅 아래 살아 있는 덩굴입니다. 겉은 단단한 흙이지만, 그 아래에서 조용히 다음 봄을 준비하는 사람이죠.",
            "narrative": [
                "당신은 감정을 응축하며 지속하는 사람입니다. 乙丑(을축)은 차갑고 축축한 흙 위에 부드러운 덩굴이 앉은 기둥이에요. 겨울 흙 아래의 덩굴은 겉으로 보이지 않지만, 뿌리는 살아서 봄을 기다립니다. 당신도 그렇습니다. 조용해 보이지만, 안에서 멈추지 않고 조금씩 자라고 있어요.",
                "당신의 강점은 '조용한 지속'입니다. 화려하지 않아도 멈추지 않고, 눈에 띄지 않아도 계속 자랍니다. 이건 아주 드문 능력이에요. 많은 사람들이 시작은 화려하지만 중간에 포기합니다. 당신은 반대로, 시작은 조용하지만 오래갑니다. 그리고 그 끝에서 단단한 결실을 만들어냅니다.",
                "당신의 그림자는 '너무 오래 참는 것'입니다. 얼어붙은 땅의 덩굴은 봄이 오기를 기다리지만, 그 봄이 오지 않으면 계속 얼어 있게 됩니다. 당신은 감정을 너무 오래 참고, 서운함을 너무 오래 묻어둡니다. 그리고 그 감정이 쌓이면, 어느 순간 덩굴이 흙을 뚫고 나오듯 갑자기 터져 나옵니다.",
                "성숙한 乙丑은 '기다림과 표현을 함께 아는 사람'입니다. 겨울을 견디되, 봄이 왔을 때는 주저 없이 꽃을 피우는 사람. 그때 당신의 조용함은 위축이 아니라, 사람들이 의지하고 싶은 깊은 안정이 됩니다."
            ],
            "shadows": [
                "감정을 너무 오래 묻어두어, 주변 사람들이 당신의 진심을 모릅니다.",
                "인내가 지나쳐서, 이미 끝난 일을 계속 붙들고 있습니다.",
                "서운함이 쌓이면, 갑자기 터져 나와 주변이 당황합니다."
            ],
            "advice": [
                "이번 주에 한 번, 평소 묻어두던 서운함을 조금씩 꺼내보세요.",
                "당신이 지금 붙들고 있는 것 세 가지를 적어보세요. 그중 하나는 놓아도 됩니다.",
                "봄이 왔는지 스스로에게 물어보세요. 왔다면, 주저 없이 꽃을 피우세요.",
                "자신에게 '이 정도면 충분히 잘했어'라고 말할 순간을 하나 만들어 두세요."
            ],
            "keywords": ["겨울 덩굴", "조용한 지속", "감정의 응축", "봄의 준비"]
        },
        "乙卯": {
            "name": "봄 들판의 풀꽃", "pillar": "乙卯",
            "hero": "당신은 봄 들판의 풀꽃입니다. 작아 보여도, 그 어떤 봄도 당신보다 강하게 피지 못하는 사람이죠.",
            "narrative": [
                "당신은 乙 중에서도 가장 순수한 乙입니다. 乙卯(을묘)는 乙의 록(祿) 자리에 乙이 앉은, 목 기운이 두 겹으로 겹친 기둥이에요. 그래서 당신의 성장력은 압도적이고, 당신의 적응력은 뛰어나며, 당신의 유연함은 흔들리지 않습니다. 사람들은 당신 앞에서 이상하게 '이 사람은 봄이구나'라는 인상을 받습니다.",
                "당신의 강점은 '압도적 성장력'입니다. 당신은 어떤 환경에서도 자라납니다. 척박한 땅에서도, 돌밭에서도, 심지어 콘크리트 틈에서도. 봄 들판의 풀꽃이 그러하듯, 당신은 생존의 본능이 강합니다. 그리고 그 생존이 단지 버티는 게 아니라, 꽃을 피우는 방향으로 나아갑니다.",
                "당신의 그림자는 '너무 유연해서 흔들리는 것'입니다. 봄 들판의 풀꽃은 유연하지만, 바람이 너무 강하면 방향을 잃습니다. 당신은 유연함이 지나쳐서, 정작 중요한 순간에 자신의 중심을 잃을 때가 있어요. 그리고 다른 사람들의 바람에 흔들려서, 정작 자신이 원하는 것을 놓치기도 합니다.",
                "성숙한 乙卯는 '유연하되 중심을 지키는 사람'입니다. 어떤 바람에도 흔들리지 않는 뿌리를 유지하되, 그 위에서는 유연하게 흔들릴 줄 아는 사람. 그때 당신의 봄은 한 번 피고 마는 계절이 아니라, 매년 다시 피는 들판이 됩니다."
            ],
            "shadows": [
                "유연함이 지나쳐서, 정작 중요한 순간에 중심을 잃습니다.",
                "다른 사람들의 바람에 흔들려, 자신이 원하는 것을 놓칩니다.",
                "성장력이 너무 강해서, 정작 어디로 자라야 할지 방향을 잃을 때가 있습니다."
            ],
            "advice": [
                "이번 주에 당신의 '뿌리'가 무엇인지 적어보세요. 그게 당신의 중심입니다.",
                "다른 사람의 요구에 흔들릴 때, '이게 내가 원하는 건가, 아니면 남이 원하는 건가' 물어보세요.",
                "성장하고 싶은 방향 하나를 정하고, 이번 주에 그 방향으로 작은 움직임을 하나 만드세요.",
                "당신의 봄을 함께 맞이할 사람을 찾으세요. 혼자 피는 꽃보다, 함께 피는 들판이 더 아름답습니다."
            ],
            "keywords": ["순수 乙", "압도적 성장", "봄의 들판", "중심 잡기"]
        },
        "乙巳": {
            "name": "꽃피는 화단", "pillar": "乙巳",
            "hero": "당신은 꽃이 피어나는 화단입니다. 다채로운 색으로 주변을 물들이는, 창의성의 사람이죠.",
            "narrative": [
                "당신은 표현과 창의의 사람입니다. 乙巳(을사)는 부드러운 덩굴이 뜨거운 불기운 위에 앉은 기둥이에요. 木이 火를 만나면 꽃이 핍니다. 당신의 창의성이 그래요. 조용한 성장을 넘어서, 다채로운 색으로 표현합니다. 사람들은 당신 곁에서 '이 사람은 뭔가 다르다'는 인상을 받습니다.",
                "당신의 강점은 '다채로운 표현력'입니다. 당신은 자신의 감정과 생각을 다채롭게 표현합니다. 그림, 글, 말, 행동—어떤 방식이든 당신의 표현에는 색이 있어요. 그리고 그 색은 사람들을 끌어당깁니다. 이건 흔한 재능이 아닙니다. 많은 사람들이 표현을 두려워하지만, 당신은 표현 자체가 자연스러워요.",
                "당신의 그림자는 '표현에 사로잡히는 것'입니다. 꽃이 피는 화단은 아름답지만, 꽃만 피우다 보면 뿌리를 잊습니다. 당신은 표현에 집중하다가 정작 자신의 체력이나 근본을 놓칠 때가 있어요. 그리고 표현이 인정받지 못하면, 오래 상처받습니다.",
                "성숙한 乙巳는 '표현과 근본을 함께 아는 사람'입니다. 꽃을 피우되, 그 꽃을 지탱하는 뿌리와 흙을 소중히 여기는 사람. 그때 당신의 창의성은 일시적인 꽃이 아니라, 매년 다시 피는 정원이 됩니다."
            ],
            "shadows": [
                "표현에 집중하다가, 정작 자신의 근본을 놓칩니다.",
                "표현이 인정받지 못하면, 오래 상처받습니다.",
                "다채로운 표현이 지나쳐서, 주변 사람들이 당신의 진심을 파악하기 어려워합니다."
            ],
            "advice": [
                "이번 주에 자신의 근본을 돌보는 시간을 하나 만드세요. 표현 없는 시간입니다.",
                "표현이 인정받지 못해도 괜찮다는 걸 스스로에게 허락하세요. 표현 자체가 가치입니다.",
                "당신의 표현 중 하나를 골라, 그 이면의 진심을 누군가에게 설명해 보세요.",
                "당신의 창의성을 함께 나눌 사람을 찾으세요. 혼자 피는 꽃보다, 함께 피는 정원이 더 풍요롭습니다."
            ],
            "keywords": ["다채로운 표현", "창의성", "꽃피는 화단", "표현과 근본"]
        },
        "乙未": {
            "name": "마른 초원의 넝쿨", "pillar": "乙未",
            "hero": "당신은 마른 초원에 뻗은 넝쿨입니다. 척박한 땅에서도 끈질기게 살아남는, 생명력의 사람이죠.",
            "narrative": [
                "당신은 인내와 생명력의 사람입니다. 乙未(을미)는 부드러운 덩굴이 여름의 건조한 흙 위에 앉은 기둥이에요. 마른 초원에 넝쿨이 뻗으면, 땅은 척박하지만 넝쿨은 살아남습니다. 당신의 생명력이 그래요. 어떤 환경에서도 완전히 죽지 않습니다. 뿌리를 내리고, 다시 자랍니다.",
                "당신의 강점은 '끈질긴 생명력'입니다. 당신은 어려운 상황에서 포기하지 않습니다. 다른 사람들이 지쳐 쓰러질 때도, 당신은 조금씩 다시 자랍니다. 그리고 이건 단순한 인내가 아니라, 유연함입니다. 넝쿨이 바위를 만나면 피해가고, 가뭄을 만나면 깊이 뿌리내리듯, 당신은 상황에 맞춰 살아남는 방법을 찾아냅니다.",
                "당신의 그림자는 '너무 오래 버티는 것'입니다. 마른 초원의 넝쿨은 살아남지만, 그 환경이 너무 오래 지속되면 결국 지칩니다. 당신은 안 좋은 환경에서도 '더 버티면 되지' 하며 계속 견딥니다. 그리고 그 사이에 정작 자신의 성장은 멈춰 있습니다.",
                "성숙한 乙未는 '버틸 것과 옮길 것을 구분하는 사람'입니다. 어려운 환경을 견디되, 그 환경이 자신을 죽이는 곳이라면 옮겨갈 줄 아는 사람. 그때 당신의 생명력은 단순한 인내가 아니라, 지혜로운 생존이 됩니다."
            ],
            "shadows": [
                "안 좋은 환경에서도 '더 버티면 되지' 하며 계속 견딥니다.",
                "생명력이 지나쳐, 정작 자신이 지친 것을 인정하지 못합니다.",
                "환경을 바꿀 수 있는데도, 익숙함 때문에 계속 머무릅니다."
            ],
            "advice": [
                "이번 주에 '내가 지금 버티고 있는 환경이 나를 살리는가, 아니면 죽이는가' 물어보세요.",
                "자신의 피로를 인정하세요. 버티는 것도 에너지를 씁니다.",
                "환경을 바꿀 수 있는데도 계속 머물고 있는 곳은 없는지 돌아보세요.",
                "당신의 생명력을 자신의 성장을 위해 쓰세요. 남을 위해서만 쓰지 마세요."
            ],
            "keywords": ["마른 초원", "끈질긴 생명력", "유연한 인내", "환경 바꾸기"]
        },
        "乙酉": {
            "name": "단정한 정원의 꽃", "pillar": "乙酉",
            "hero": "당신은 단정하게 가꾼 정원의 꽃입니다. 아름다움을 위해 스스로를 다듬을 줄 아는, 세련된 사람이죠.",
            "narrative": [
                "당신은 정밀한 미감의 사람입니다. 乙酉(을유)는 부드러운 덩굴이 세공된 금속 위에 앉은 기둥이에요. 金은 木을 벱니다. 그래서 당신은 부드러우면서도 날카롭습니다. 아름다움을 추구하되, 그 아름다움이 정확해야 한다고 느낍니다. 단정한 정원의 꽃이 그러하듯, 당신은 아름다움에 기준이 있어요.",
                "당신의 강점은 '세련된 완성도'입니다. 당신이 손대는 것에는 늘 정성이 배어 있습니다. 화려하지 않아도 단정하고, 소박해도 완성도가 있어요. 사람들은 당신이 만든 것, 당신이 고른 것에서 이상하게 '이 사람 손을 거쳤구나' 싶은 결을 느낍니다. 이건 흔한 재능이 아닙니다.",
                "당신의 그림자는 '완벽주의가 관계를 가로막는 것'입니다. 단정한 정원의 꽃은 아름답지만, 흐트러진 것에는 어울리지 않습니다. 당신의 기준은 당신에게는 자연스럽지만, 다른 사람에게는 벽이 됩니다. 그리고 그 기준이 자신에게도 향해서, 완벽하지 않은 자신을 용서하지 못합니다.",
                "성숙한 乙酉는 '기준을 관대함과 함께 쓰는 사람'입니다. 아름다움을 유지하되, 그 아름다움에 이르지 못하는 사람을 이해할 줄 아는 사람. 그때 당신의 세련됨은 압박이 아니라, 사람들이 배우고 싶어 하는 아름다움이 됩니다."
            ],
            "shadows": [
                "완벽하지 않은 결과물에 오래 마음이 걸립니다.",
                "다른 사람에게도 같은 기준을 적용해서, 의도치 않게 상처를 줍니다.",
                "완벽하지 않은 자신을 오래 용서하지 못합니다."
            ],
            "advice": [
                "이번 주에 일부러 80%에서 멈추는 연습을 한 번 해보세요.",
                "다른 사람의 결과물을 볼 때, '이건 내 기준이 아니라 이 사람의 기준이다'를 먼저 떠올려 보세요.",
                "당신이 자주 던지는 '왜 이 정도밖에'를 '무엇을 해냈지'로 한 번 바꿔보세요.",
                "자신에게 '이 정도면 충분해'라고 말할 순간을 하나 만들어 두세요."
            ],
            "keywords": ["단정한 미감", "세련된 완성도", "정밀한 아름다움", "기준과 관대함"]
        },
        "乙亥": {
            "name": "물가의 버들", "pillar": "乙亥",
            "hero": "당신은 물가에 늘어진 버들입니다. 부드럽게 흔들리며, 그 흔들림으로 사람들의 마음을 어루만지는 사람이죠.",
            "narrative": [
                "당신은 유연한 지혜의 사람입니다. 乙亥(을해)는 부드러운 덩굴이 깊은 물 위에 앉은 기둥이에요. 水生木—물이 나무를 키웁니다. 물가의 버들은 물을 만나 더 유연해지고, 그 유연함으로 바람에도 잘 견딥니다. 당신의 지혜가 그래요. 부드러워 보이지만, 어떤 바람에도 꺾이지 않습니다.",
                "당신의 강점은 '부드러운 적응력'입니다. 당신은 어떤 환경에도 자연스럽게 스며듭니다. 사람들은 당신 곁에서 '이 사람은 편안하다'는 인상을 받습니다. 그리고 그 편안함은 당신의 유연함에서 나옵니다. 당신은 다른 사람을 압도하지 않고, 그 사람의 리듬에 맞춰 조용히 흐릅니다.",
                "당신의 그림자는 '유연함이 우유부단이 되는 것'입니다. 물가의 버들은 유연하지만, 너무 유연하면 방향이 없습니다. 당신은 결정해야 할 순간에도 '물 흐르듯이' 하며 미룰 때가 있어요. 그리고 자신의 의견을 잘 드러내지 않아서, 주변 사람들이 당신의 진짜 생각을 모릅니다.",
                "성숙한 乙亥는 '유연하되 결정할 줄 아는 사람'입니다. 부드러움을 유지하되, 필요할 때는 단호하게 결정할 줄 아는 사람. 그때 당신의 유연함은 우유부단이 아니라, 사람들이 의지하고 싶은 지혜가 됩니다."
            ],
            "shadows": [
                "유연함이 우유부단이 되어, 결정해야 할 순간에 미룹니다.",
                "자신의 의견을 잘 드러내지 않아, 주변 사람들이 당신의 진짜 생각을 모릅니다.",
                "다른 사람의 리듬에 맞추다가, 정작 자신의 리듬을 잃습니다."
            ],
            "advice": [
                "이번 주에 결정해야 할 것 하나를 골라, 정해진 기한 안에 결정하세요.",
                "당신의 의견을 하나 골라, 누군가에게 명확하게 표현해 보세요.",
                "자신의 리듬을 돌아보세요. 당신은 지금 어떤 속도로 살고 싶나요?",
                "물가의 버들도 뿌리가 있습니다. 당신의 뿌리를 확인하고, 그 위에서 흔들리세요."
            ],
            "keywords": ["물가 버들", "유연한 지혜", "부드러운 적응", "결정의 용기"]
        }
    },
    "en": {
        "乙丑": {
            "name": "Vine in Frozen Ground", "pillar": "乙丑",
            "hero": "You're a vine alive beneath frozen ground. Solid soil on the surface — and underneath, quiet preparation for the next spring.",
            "narrative": [
                "You condense feeling and keep going. 乙丑 is soft vine resting on cold, damp earth. A winter vine is invisible above ground, but its roots are alive and waiting for spring. That's you. You look quiet, but inside you're slowly growing.",
                "Your strength is quiet continuity. You don't need to be flashy, and you don't stop. You grow even when no one sees. This is a rare ability. Many people start loud and quit midway. You start quiet and last. And at the end, you produce something solid.",
                "Your shadow is enduring too long. A vine in frozen ground waits for spring — but if spring never comes, the vine stays frozen. You hold feelings too long and bury hurt too long. And when those feelings pile up, one day the vine breaks through the soil all at once.",
                "A mature Yi-Chou knows both patience and expression. Enduring winter, and flowering without hesitation when spring arrives. Then your quietness stops being withdrawal and becomes the kind of stability people lean on."
            ],
            "shadows": [
                "Holding feelings so long that people around you never learn your heart.",
                "Patience carried so far that you keep holding something that's already over.",
                "When hurt piles up, it bursts out and startles everyone."
            ],
            "advice": [
                "Once this week, bring a small kept hurt up.",
                "List three things you're holding. One of them can be put down.",
                "Ask yourself if spring has arrived. If it has, flower without hesitation.",
                "Say to yourself, 'I did well enough.' Once this week."
            ],
            "keywords": ["winter vine", "quiet continuity", "condensed feeling", "spring preparation"]
        },
        "乙卯": {
            "name": "Wildflowers of Spring", "pillar": "乙卯",
            "hero": "You're a wildflower in a spring field. Small, and no spring blooms more strongly than you.",
            "narrative": [
                "You're the purest form of 乙. 乙卯 is 乙 sitting in its own 祿 (Lu) — double wood, layered on itself. Your growth is overwhelming, your adaptability is remarkable, your flexibility doesn't shake. People sense in your presence: this person is spring itself.",
                "Your strength is overwhelming growth. You grow anywhere. Barren ground, stony soil, even through cracks in concrete. Like the wildflower in a spring field, your survival instinct is strong. And the survival doesn't just endure — it moves toward flowering.",
                "Your shadow is being so flexible that you lose direction. A wildflower is flexible, but a strong wind makes it lose direction. Your flexibility carried too far means you lose your center at the moment it matters. And the winds of other people's wishes blow you around, so you lose what you actually wanted.",
                "A mature Yi-Mao is flexible without losing the center. A root that no wind can move, and above it, flexibility. Then your spring isn't a season that passes — it becomes a field that blooms again every year."
            ],
            "shadows": [
                "Flexibility taken so far that you lose the center when it counts.",
                "Blown around by other people's winds, losing what you actually wanted.",
                "Such strong growth that you can lose direction about where to grow."
            ],
            "advice": [
                "Write down what your 'root' is this week. That's your center.",
                "When other people's requests pull at you, ask: is this what I want, or what they want?",
                "Pick one direction you want to grow and take one small step this week.",
                "Find someone to greet spring with you. A field blooms more beautifully together than alone."
            ],
            "keywords": ["pure 乙", "overwhelming growth", "spring field", "holding the center"]
        },
        "乙巳": {
            "name": "Blooming Flowerbed", "pillar": "乙巳",
            "hero": "You're a flowerbed in bloom. You color everything around you in many shades — a person of creativity.",
            "narrative": [
                "You're about expression and creativity. 乙巳 is soft vine sitting on hot fire. Wood meeting fire blooms. That's your creativity — past quiet growth, into multicolored expression. People sense in your presence: this person has something else.",
                "Your strength is multicolored expression. You express your feelings and thoughts in many ways — drawing, writing, speech, action. Whatever form it takes, your expression has color. And the color draws people in. That's rare. Many people fear expression, but for you it's natural.",
                "Your shadow is getting caught up in expression. A blooming flowerbed is beautiful, but if you only bloom, you forget the root. You focus on expression and miss your own stamina and foundation. And when expression isn't recognized, you're hurt for a long time.",
                "A mature Yi-Si knows both expression and foundation. Blooming, and honoring the root and soil that hold the bloom. Then your creativity isn't a one-time flower — it becomes a garden that blooms every year."
            ],
            "shadows": [
                "Focusing on expression while missing the foundation.",
                "Getting hurt for a long time when expression isn't recognized.",
                "Expressing so diversely that people can't grasp your real intent."
            ],
            "advice": [
                "Set aside time this week for your foundation — no expression in it.",
                "Give yourself permission: expression has value even without recognition.",
                "Pick one piece of expression and explain its underlying truth to someone.",
                "Find someone to share your creativity with. A garden blooms more beautifully together."
            ],
            "keywords": ["multicolored expression", "creativity", "blooming flowerbed", "expression and foundation"]
        },
        "乙未": {
            "name": "Vine on Dry Meadow", "pillar": "乙未",
            "hero": "You're a vine spreading across a dry meadow. Even on barren ground, you survive — a person of remarkable vitality.",
            "narrative": [
                "You're the person of endurance and life force. 乙未 is soft vine on dry summer earth. A vine on a dry meadow — the ground is poor, but the vine survives. Your life force is like that. It doesn't die completely in any environment. It puts down roots and grows again.",
                "Your strength is persistent life force. You don't give up in hard situations. Even when others fall over in exhaustion, you slowly grow again. And it's not simple patience — it's flexibility. A vine goes around a rock, and in a drought roots deeper. So do you: you find the way to survive that fits the situation.",
                "Your shadow is enduring too long. A vine on dry meadow survives, but if the environment lasts too long, it eventually wears out. You tell yourself 'a bit longer will be fine' in bad situations and keep enduring. And your own growth is paused the whole time.",
                "A mature Yi-Wei knows the difference between enduring and moving. Enduring hard environments, and moving on when the environment is killing you. Then your life force isn't just patience — it's wise survival."
            ],
            "shadows": [
                "Telling yourself 'a bit longer' in bad environments and enduring too long.",
                "Such strong life force that you can't admit you're tired.",
                "Staying put in an environment you could change, out of familiarity."
            ],
            "advice": [
                "Ask this week: does the environment I'm in give me life, or take it?",
                "Acknowledge your fatigue. Enduring takes energy too.",
                "Check whether there's an environment you could change but haven't.",
                "Spend your vitality on your own growth, not only on others."
            ],
            "keywords": ["dry meadow", "persistent life force", "flexible endurance", "changing environments"]
        },
        "乙酉": {
            "name": "Flower in a Neat Garden", "pillar": "乙酉",
            "hero": "You're a flower in a neatly kept garden. A refined person who trims yourself for beauty.",
            "narrative": [
                "You have precise aesthetic sense. 乙酉 is soft vine sitting on crafted metal. Metal cuts wood — so you're soft and sharp at once. You want beauty, and you want it exact. Like a flower in a neat garden, you have standards for your beauty.",
                "Your strength is refined completion. Whatever you touch carries visible care. Not necessarily flashy, but neatly done. Not necessarily elaborate, but finished. People feel a signature on what you make and what you choose.",
                "Your shadow is perfectionism blocking connection. A flower in a neat garden is beautiful, but it doesn't sit well with disorder. Your standard is natural to you — but to others it's a wall. And that standard turns on you, so you can't forgive your own imperfection.",
                "A mature Yi-You uses standards with generosity. Keeping the beauty, and understanding the people who can't reach it yet. Then your refinement stops being pressure and becomes the kind of beauty people want to learn."
            ],
            "shadows": [
                "Imperfect results stay with you for a long time.",
                "Applying the same standard to others, unintentionally wounding them.",
                "Unable to forgive your own imperfection for a long time."
            ],
            "advice": [
                "Once this week, stop at 80%. Any result.",
                "Before looking at someone else's work, remind yourself: that's their bar, not mine.",
                "Turn 'why only this much?' into 'what did I actually make?'",
                "Say 'this is enough' to yourself once this week."
            ],
            "keywords": ["neat aesthetic", "refined completion", "precise beauty", "standard and generosity"]
        },
        "乙亥": {
            "name": "Willow by the Water", "pillar": "乙亥",
            "hero": "You're a willow by the water. Swaying softly, and through that swaying, touching people's hearts.",
            "narrative": [
                "You have flexible wisdom. 乙亥 is soft vine sitting on deep water. Water grows wood — a willow by the water gets softer and more flexible, and that flexibility helps it hold up in the wind. Your wisdom is like that. Soft to look at, unbroken by any wind.",
                "Your strength is soft adaptability. You fit into any environment naturally. People feel at ease around you. That ease comes from your flexibility. You don't push past other people — you flow quietly into their rhythm.",
                "Your shadow is flexibility becoming indecision. A willow is flexible, but too much flexibility means no direction. You can delay a decision with 'let it flow' when the moment needs a choice. And you don't often show your opinions, so people don't know what you actually think.",
                "A mature Yi-Hai is flexible and decisive. Keeping the softness, and being firm when a decision is actually required. Then your flexibility stops being indecision and becomes the kind of wisdom people lean on."
            ],
            "shadows": [
                "Flexibility becoming indecision at moments that needed a decision.",
                "Not showing opinions, so people don't learn what you actually think.",
                "Matching other people's rhythm and losing your own."
            ],
            "advice": [
                "Pick one decision to make this week and make it by a fixed deadline.",
                "Express one of your opinions clearly to someone.",
                "Look at your own rhythm. At what pace do you want to live?",
                "A willow has roots. Confirm your roots, and sway from there."
            ],
            "keywords": ["willow by water", "flexible wisdom", "soft adaptation", "courage to decide"]
        }
    }
}


def main() -> int:
    ap = argparse.ArgumentParser(description="乙 일간 6일주 추가 — 마지막 계열")
    ap.add_argument("--force", action="store_true", help="스텁 덮어쓰기")
    args = ap.parse_args()

    print("=== 乙 일간 6일주 추가 (乙丑, 乙卯, 乙巳, 乙未, 乙酉, 乙亥) — 마지막 계열 ===")
    
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

    print("\n🎉🎉🎉 60일주 전체 완성! 🎉🎉🎉")
    print("\n✅ 완료. 검증:")
    print("  pytest -q")
    return 0

if __name__ == "__main__":
    sys.exit(main())