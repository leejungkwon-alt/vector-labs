#!/usr/bin/env python3
"""
庚 일간 5일주 추가 (庚子, 庚寅, 庚辰, 庚申, 庚戌).
庚午는 이미 존재. 庚은 양금(陽金)의 기운으로, 원칙과 결단, 예리함의 성향입니다.
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
        "庚子": {
            "name": "깊은 호수의 검", "pillar": "庚子",
            "hero": "당신은 깊은 호수 아래 가라앉은 검입니다. 수면 위로 번뜩이지 않아도, 물속에서 가장 정확한 곳을 알고 있는 사람이죠.",
            "narrative": [
                "당신은 생각의 깊이가 말의 양보다 훨씬 큰 사람입니다. 회의에서 조용히 앉아 있어도, 머릿속에서는 이미 판 전체가 그려져 있어요. 남들이 앞다투어 말할 때, 당신은 그중 누구의 말이 진짜인지 조용히 저울질하고 있습니다.",
                "당신의 강점은 '정확한 표현'입니다. 말수가 적은 대신, 한마디를 꺼낼 때 그 무게가 남다릅니다. 물(水) 기운이 금(金)을 만나 흐르듯, 당신의 예리함은 소리치지 않고 스며듭니다. 사람들은 나중에야 '그때 그 한마디가 맞았어'라고 알아차리죠.",
                "당신의 그림자는 '너무 깊이 가라앉는 것'입니다. 생각이 많아지고, 감정이 안으로만 흐르면, 주변 사람들은 당신이 무슨 생각을 하는지 알 수 없어 답답해합니다. '차갑다'거나 '속을 모르겠다'는 말을 들은 적 있다면, 그건 당신이 무심해서가 아니라 너무 깊이 생각하기 때문이에요.",
                "성숙한 庚子는 '차갑지 않게 정확한 사람'입니다. 예리함을 유지하되, 그 예리함을 사람을 향해 겨누지 않고 문제를 향해 겨누는 사람. 그때 당신의 깊이는 더 이상 거리감이 아니라, 사람들이 의지하고 싶은 지혜가 됩니다."
            ],
            "shadows": [
                "생각이 너무 깊어서, 정작 필요한 순간에 말을 꺼내지 못할 때가 있습니다.",
                "감정을 안으로만 삭이다 보니, 주변 사람들이 당신의 진심을 알기 어려워합니다.",
                "혼자 판단하고 결론을 내리는 습관 때문에, 협업에서 신뢰를 쌓기까지 시간이 걸립니다."
            ],
            "advice": [
                "이번 주에 한 번, 결론이 완벽하지 않아도 말로 꺼내보세요. 완성도보다 타이밍이 중요할 때가 있습니다.",
                "당신이 조용히 판단한 것을 하나 골라, 왜 그렇게 생각했는지 누군가에게 설명해 보세요.",
                "혼자만의 시간을 규칙적으로 확보하되, 그 시간에 '비우는 연습'도 함께 하세요. 분석이 아니라 그냥 쉬는 것.",
                "가까운 사람에게 '나는 원래 생각이 많아서 말이 느려'라고 한 번 설명해 주세요. 그게 큰 오해를 풉니다."
            ],
            "keywords": ["깊은 통찰", "정확한 한마디", "조용한 판단", "차가운 명료함"]
        },
        "庚寅": {
            "name": "숲을 여는 검", "pillar": "庚寅",
            "hero": "당신은 숲을 베어 길을 여는 검입니다. 나무를 쓰러뜨리는 게 아니라, 지나갈 수 있는 길을 만들어내는 사람이죠.",
            "narrative": [
                "당신은 행동이 생각보다 앞서는 사람입니다. 기회가 보이면 주저하지 않고 움직이고, 결정이 빠릅니다. '일단 해보고 다듬자'가 몸에 배어 있어서, 시작하는 단계에서 남들보다 훨씬 앞서갑니다.",
                "당신의 강점은 '추진력'입니다. 금(金)이 목(木)을 베듯, 당신은 뭉개지는 상황을 깔끔하게 잘라냅니다. 답답한 회의, 미적거리는 사람, 결론 없는 논의를 당신은 몇 마디로 정리합니다. 사람들은 당신 덕분에 일이 굴러간다고 느끼죠.",
                "당신의 그림자는 '너무 빨리 벤다'는 것입니다. 앞만 보고 달리다 보면, 뒤에 남은 사람들, 상처받은 감정, 아직 자라날 씨앗들을 놓칩니다. 개척자에게 늘 따라붙는 말이 '혼자 다 해먹는다'는 것인데, 그건 당신의 의도가 아니라 속도의 문제입니다.",
                "성숙한 庚寅은 '베어야 할 것과 키워야 할 것을 구분하는 사람'입니다. 다 자랄 시간을 주고, 그 사이에 다른 일을 하며 인내할 줄 아는 사람. 그때 당신의 추진력은 사람들을 끌어당기고, 당신이 지나간 자리에는 길이 남습니다."
            ],
            "shadows": [
                "빠른 결정이 때로는 주변 사람들의 준비 시간을 무시합니다.",
                "혼자 앞서가다 보면, 팀원들이 따라오지 못해 고립될 수 있습니다.",
                "속도에 익숙해져서, 느린 과정을 견디지 못하고 중간에 포기합니다."
            ],
            "advice": [
                "이번 주에 결정을 내리기 전, 관련된 사람 한 명에게 먼저 물어보세요. '이거 어떻게 생각해?'",
                "당신이 벌여놓은 일 중 하나는 이번 주에 일부러 마무리하지 말고, 그대로 두세요. 다 자라게 하는 연습입니다.",
                "누군가 느리게 움직일 때, 그 사람이 '왜' 느린지 한 번 물어보세요. 대부분은 이유가 있습니다.",
                "당신이 이끄는 프로젝트에 '내가 없어도 굴러가는' 부분을 하나 만들어 두세요. 그게 진짜 리더십입니다."
            ],
            "keywords": ["개척", "속도", "길을 여는 힘", "추진력"]
        },
        "庚辰": {
            "name": "용의 동굴 속 검", "pillar": "庚辰",
            "hero": "당신은 용의 동굴에 보관된 검입니다. 겉으로는 묵직한 땅 아래 숨어 있지만, 세상이 흔들릴 때 비로소 꺼내지는 사람이죠.",
            "narrative": [
                "당신은 쉽게 드러나지 않는 힘의 사람입니다. 겉으로 보면 무던하고 평범해 보이는데, 어느 순간 결정적인 자리에서 무게가 드러납니다. 사람들은 나중에 '그 사람이 그런 사람이었어?'라며 놀라죠. 庚辰(경진)은 명리에서 가장 강한 기둥 중 하나인 魁罡(괴강)에 속합니다.",
                "당신은 원칙과 기준이 분명하고, 그 기준을 쉽게 바꾸지 않습니다. 이 단단함은 조직에서 큰 신뢰를 만들어요. 다들 흔들릴 때 당신은 흔들리지 않으니까요. 조용히, 그러나 확실하게 중심을 지키는 사람입니다.",
                "당신의 그림자는 '평소 너무 잘 참는 것'입니다. 검을 계속 칼집에 넣어두면, 꺼내야 할 순간에 오히려 감정이 터지거나, 반대로 결정적일 때 힘을 못 씁니다. 주변 사람들은 당신이 '늘 괜찮은 사람'이라고 생각하다가, 어느 순간 단호해진 당신을 보고 당황합니다.",
                "성숙한 庚辰은 '칼집에 넣을 때와 꺼낼 때를 아는 사람'입니다. 평소에는 넉넉하게 품되, 필요할 때는 정확하게 꺼내 쓰는 사람. 그때 당신의 존재감은 위압이 아니라, 사람들이 믿고 기댈 수 있는 힘이 됩니다."
            ],
            "shadows": [
                "평소 감정을 잘 드러내지 않다가, 결정적일 때 갑자기 단호해져 주변을 당황시킵니다.",
                "원칙을 너무 강하게 지키다 보면, 사람보다 규칙이 앞서는 것처럼 보일 수 있습니다.",
                "스스로에게도 '괜찮은 척'을 강요해서, 정작 자신의 피로를 인정하지 못합니다."
            ],
            "advice": [
                "이번 주에 한 번, 평소 참고 있던 작은 서운함을 꺼내보세요. 폭발 전에 미리 나누는 겁니다.",
                "결정을 내려야 할 때, '이건 원칙의 문제인가, 내가 지금 지친 것인가'를 한 번 구분해 보세요.",
                "당신이 늘 해결해 온 일 하나를 이번 주엔 다른 사람에게 맡겨보세요. 당신이 빠져도 굴러간다는 걸 확인하는 연습입니다.",
                "믿을 만한 한 사람에게 '요즘 좀 무거워'라고 말해보세요. 그 한마디가 검을 다시 벼리는 시간을 만들어 줍니다."
            ],
            "keywords": ["괴강", "숨은 힘", "원칙의 중심", "결정적 무게"]
        },
        "庚申": {
            "name": "두 번 벼려낸 강철", "pillar": "庚申",
            "hero": "당신은 두 번 벼려낸 강철검입니다. 부러지지 않으려고 태어났고, 흔들리는 세상 속에서 가장 단단한 기준이 되는 사람이죠.",
            "narrative": [
                "당신은 庚 중에서도 가장 순수한 庚입니다. 庚申(경신)은 庚의 록(祿) 자리에 庚이 앉은, 금(金) 기운이 두 겹으로 겹친 기둥이에요. 그래서 당신의 기준은 흔들리지 않고, 당신의 판단은 명확하며, 당신의 태도는 흔들리지 않는 강철 같습니다.",
                "당신은 옳고 그름을 정확하게 봅니다. 애매한 것을 견디지 못하고, 부당한 것을 그냥 넘기지 못합니다. 이 예리함 덕분에 당신은 조직에서 '믿을 수 있는 사람'으로 통하고, 사람들은 중요한 순간에 당신에게 판단을 맡깁니다.",
                "당신의 그림자는 '칼이 모든 것을 벤다'는 것입니다. 옳은 말도 타이밍이 틀리면 상처가 되고, 단호함이 지나치면 냉정으로 읽힙니다. 그리고 그 칼은 자신에게도 향합니다. 스스로에게 너무 높은 기준을 세우고, 그 기준에 못 미치는 자신을 용서하지 못하죠.",
                "성숙한 庚申은 '칼날을 지키는 데 쓰는 사람'입니다. 약한 사람을 지키고, 원칙을 세우고, 흔들리는 사람에게 기준이 되어주는 사람. 그때 당신의 강철은 두렵지 않고, 사람들이 기대고 싶은 기둥이 됩니다."
            ],
            "shadows": [
                "정확한 지적이 때로는 상대에게 상처로 남습니다. 옳음과 다정함은 다릅니다.",
                "자신에게도 냉정한 잣대를 들이대서, 작은 실수에도 오래 자신을 괴롭힙니다.",
                "주변 사람들이 당신 앞에서 긴장하거나, 실수를 감추려는 경향이 생깁니다."
            ],
            "advice": [
                "지적하기 전에 한 번, '이 말이 지금 이 사람에게 약이 될까, 칼이 될까'를 물어보세요.",
                "이번 주에 한 번은 일부러 '이 정도면 충분해'라고 자신에게 말해주세요. 어떤 결과물이든요.",
                "당신이 인정하는 사람 한 명에게, 당신의 약한 부분을 하나 꺼내보세요. 강철도 사람이라는 걸 스스로에게 허락하는 연습입니다.",
                "판단이 필요할 때, '이건 옳은가'뿐 아니라 '이게 지금 도움이 되는가'도 함께 물어보세요. 그 두 질문이 당신의 칼을 더 정교하게 만듭니다."
            ],
            "keywords": ["순수 강철", "명확한 기준", "흔들리지 않음", "정교한 칼날"]
        },
        "庚戌": {
            "name": "마른 땅의 검", "pillar": "庚戌",
            "hero": "당신은 마른 대지 위에 세워진 검입니다. 타오르는 열정이 아니라, 꺾이지 않는 원칙으로 세상을 마주하는 사람이죠.",
            "narrative": [
                "당신은 庚辰(경진)과 함께 魁罡(괴강)에 속하는 강한 기둥입니다. 다만 庚辰이 습한 땅(辰) 위에 있다면, 당신은 마른 땅(戌) 위에 있어요. 그래서 당신의 강함은 더 건조하고, 더 단호하고, 더 원칙적입니다. 흔들리지 않는 대신, 꺾이지도 않죠.",
                "당신은 내면에 강한 신념과 도덕적 기준을 지니고 있습니다. '이건 옳고 저건 그르다'는 판단이 명확하고, 그 기준을 타협하지 않습니다. 이 태도 덕분에 당신은 위기 상황에서 사람들이 의지하는 중심이 되고, 조직에서 '이 사람은 선을 넘지 않는다'는 신뢰를 얻습니다.",
                "당신의 그림자는 '칼집을 잊는 것'입니다. 戌은 화(火)의 저장고이기도 해서, 안에 뜨거운 열이 쌓여 있습니다. 그 열이 제어되지 않으면, 당신의 단호함은 갑자기 폭발하는 분노로 바뀔 수 있습니다. 그리고 당신의 원칙은 때로 다른 사람에게는 '너무 높은 벽'이 됩니다.",
                "성숙한 庚戌은 '원칙과 온기를 함께 지닌 사람'입니다. 기준을 지키되, 그 기준에 이르지 못하는 사람을 이해할 줄 아는 사람. 그때 당신의 건조함은 더 이상 냉정함이 아니라, 사람들이 안심하고 기댈 수 있는 단단함이 됩니다."
            ],
            "shadows": [
                "원칙을 너무 강하게 지키다 보면, 다른 사람의 다름을 '틀림'으로 판단하기 쉽습니다.",
                "안에 쌓인 열이 갑자기 폭발하면, 평소의 단호함과 대비되어 주변이 크게 당황합니다.",
                "스스로에게도 관대하지 못해, 자신이 지친 것을 인정하지 못하고 계속 밀어붙입니다."
            ],
            "advice": [
                "다른 사람의 선택이 당신의 원칙과 다를 때, '이건 틀린 게 아니라 다른 것일 수 있다'고 한 번만 생각해 보세요.",
                "이번 주에 한 번, 평소 참고 있던 분노나 서운함을 조용히 꺼내보세요. 폭발 전에 배출하는 연습입니다.",
                "당신이 '이건 옳지 않아'라고 판단한 상황에서, 그 판단이 당신의 지침 때문인지 원칙 때문인지 구분해 보세요.",
                "당신이 지키는 원칙 중 하나를 이번 주에는 조금 느슨하게 풀어보세요. 세상이 무너지지 않는다는 걸 확인하는 겁니다."
            ],
            "keywords": ["괴강", "원칙의 강철", "건조한 결단", "숨은 열기"]
        }
    },
    "en": {
        "庚子": {
            "name": "Blade in the Deep Lake", "pillar": "庚子",
            "hero": "You're a blade resting at the bottom of a deep lake. You don't flash above the surface — you simply know, from below, exactly where the cut belongs.",
            "narrative": [
                "You think deeper than you speak. In a meeting, you can sit in silence while everyone else talks over each other, and still see the whole board before anyone else does. You're not quiet because you have nothing to say. You're quiet because you're already weighing which voice in the room is actually true.",
                "Your strength is precision. Metal flowing into water — the blade doesn't shout, it seeps. You say one thing, and weeks later people realize it was the thing that mattered. Your words land because you don't waste them.",
                "Your shadow is sinking too deep. When the thinking gets heavier and the feelings only flow inward, people around you can't tell what's happening inside you. If you've ever been called cold or hard to read, it's not because you don't care — it's because you care so far down the current doesn't reach the surface.",
                "A mature Geng-Ja is sharp without being cold. The same edge, but aimed at the problem instead of the person. When you get there, your depth stops being distance and becomes the kind of wisdom people want to lean on."
            ],
            "shadows": [
                "Thinking so deeply that you don't speak when speaking is what the moment needed.",
                "Holding emotions in until people around you can't read your care.",
                "Deciding alone out of habit, so it takes longer than it should for others to trust you."
            ],
            "advice": [
                "Once this week, say the thing out loud even if it isn't fully formed. Timing matters more than polish.",
                "Pick one judgment you've kept silent. Explain to someone why you see it the way you do.",
                "Keep your solitude, but add a practice of emptying — not analyzing. Just letting the water settle.",
                "Tell someone close, 'I think a lot before I speak.' That one sentence clears up years of misreading."
            ],
            "keywords": ["deep insight", "precise words", "quiet judgment", "cool clarity"]
        },
        "庚寅": {
            "name": "Blade Opening the Forest", "pillar": "庚寅",
            "hero": "You're a blade clearing a path through a forest. Not felling trees for the sake of it — opening the way so others can walk.",
            "narrative": [
                "You move before you've finished thinking. When an opening appears, you take it. Your decisions come fast, and 'start first, refine later' is already wired into you. That puts you miles ahead of most people at the beginning of things.",
                "Your strength is momentum. Metal cuts wood — you don't negotiate with a mess. You clear it. Long meetings without conclusions, people circling the same point, projects that won't move: a few sentences from you and they're done. People feel the project move because of you.",
                "Your shadow is cutting too fast. You're so focused on the forward line that you leave behind people, hurt feelings, and seeds that hadn't sprouted yet. Pioneers always get called 'the one who does it alone.' It's not your intention — it's your speed.",
                "A mature Geng-In knows the difference between what to cut and what to grow. Someone who lets things take their time, and uses that waiting window to work on something else. Then your momentum pulls people in, and the place you passed through has a road in it."
            ],
            "shadows": [
                "Fast decisions sometimes ignore the preparation time others need.",
                "Moving ahead alone can isolate you from the very team you're leading.",
                "You're so used to speed that you abandon slow processes halfway through."
            ],
            "advice": [
                "Before deciding something, ask one relevant person this week: 'How do you see it?'",
                "Pick one thing you've set in motion and deliberately leave it unfinished this week. Let it grow.",
                "When someone moves slowly, ask once why. Usually there's a reason you didn't see.",
                "Build one part of your project that runs without you. That's real leadership."
            ],
            "keywords": ["pioneering", "speed", "opening paths", "momentum"]
        },
        "庚辰": {
            "name": "Sword in the Dragon's Lair", "pillar": "庚辰",
            "hero": "You're a sword kept in a dragon's lair. Hidden under solid earth most of the time — drawn only when the world needs a blade.",
            "narrative": [
                "Your power doesn't announce itself. You can look unremarkable at a glance, and then at one decisive moment your weight shows. People say later, 'Wait — that person was that person?' In classical Saju, Geng-Jin is one of the four 魁罡 (Commander) pillars — among the strongest in the system.",
                "You have clear principles, and you don't bend them easily. That firmness builds enormous trust in organizations — when everyone else is wavering, you aren't. You hold the center, quietly and unmistakably.",
                "Your shadow is enduring too much, too long. A sword that stays sheathed for too long either explodes out when it shouldn't, or fails to draw when it should. People assume you're the one who's always fine — and then your sudden firmness catches them off guard.",
                "A mature Geng-Jin knows when to sheath and when to draw. Generous most of the time, precise when it counts. Then your presence stops feeling intimidating and becomes the thing people rely on."
            ],
            "shadows": [
                "Holding feelings in so long that your sudden decisiveness catches others off guard.",
                "Following principles so closely that rules seem to matter more than people.",
                "Forcing yourself to seem fine, and losing track of your own fatigue."
            ],
            "advice": [
                "Once this week, say a small irritation out loud before it grows into a blow-up.",
                "Before a hard call, ask: is this the principle talking, or is this me being tired?",
                "Hand off one thing you usually solve yourself. Watch it run without you.",
                "Tell one trusted person, 'It's been heavy lately.' That sentence sharpens the blade again."
            ],
            "keywords": ["魁罡", "hidden strength", "principled center", "decisive weight"]
        },
        "庚申": {
            "name": "Twice-Forged Steel", "pillar": "庚申",
            "hero": "You're steel forged twice. You were made not to break — to be the one steady line in a world that won't hold still.",
            "narrative": [
                "You're the purest form of Geng. Geng-Shin is Geng sitting on its own 祿 (Lu) — double metal, layered on itself. So your standard doesn't shift, your judgment is clean, and your stance is steel. Not because you're trying to be — because that's the shape you were made in.",
                "You see right and wrong with unusual accuracy. Ambiguity bothers you, and injustice is something you cannot just walk past. This sharpness makes you the person an organization trusts to call the hard thing, and people bring you the decisions they can't make alone.",
                "Your shadow is a blade that cuts everything. A right word at the wrong moment becomes a wound. Firmness taken too far reads as cold. And the blade also turns inward — you hold yourself to a standard you'd never demand of another human being, and you don't forgive yourself when you fall short.",
                "A mature Geng-Shin uses the blade to protect. Protecting the ones who can't protect themselves, holding the line, being the reference point for people who are wavering. Then your steel stops being intimidating — it becomes the pillar people want to stand near."
            ],
            "shadows": [
                "Accurate criticism sometimes lands as a wound. Being right and being kind are different jobs.",
                "Holding yourself to a standard you'd never impose on anyone else.",
                "People around you get tense, or start hiding their mistakes, in your presence."
            ],
            "advice": [
                "Before correcting someone, ask once: will this be medicine for them right now, or a blade?",
                "Once this week, say to yourself, 'This is enough.' Whatever the result is.",
                "Tell one person you respect a place where you're not strong. Let steel be human for a moment.",
                "When you judge something, ask both: 'Is this right?' and 'Is this useful right now?' The two questions sharpen the edge."
            ],
            "keywords": ["pure steel", "clear standard", "unshakeable", "precise edge"]
        },
        "庚戌": {
            "name": "Blade on Dry Earth", "pillar": "庚戌",
            "hero": "You're a blade planted on dry earth. Not a blade of passion — a blade of unbroken principle.",
            "narrative": [
                "You share the 魁罡 (Commander) pillar with Geng-Jin — but where Geng-Jin sits on wet earth, you sit on dry. So your strength is drier, more decisive, more principled. You don't waver. But you don't bend either.",
                "You carry a strong moral compass. 'This is right, that is not' is clear to you, and you don't trade it away. That makes you the center people lean on in a crisis, and the person in an organization who everyone knows won't cross a line.",
                "Your shadow is forgetting the sheath. 戌 (Xu) is the storage of fire — there's a hot interior inside that dry earth. If that heat isn't governed, your firmness can suddenly erupt as anger. And your standard, held too tightly, becomes an impossibly high wall to the people around you.",
                "A mature Geng-Xu holds principle and warmth together. Keeping the standard while understanding the people who can't reach it yet. Then your dryness stops being coldness and becomes the kind of solidity people rest against."
            ],
            "shadows": [
                "Holding principle so tightly that other people's differences look like errors.",
                "Stored heat that erupts suddenly, catching everyone off guard.",
                "Being so strict with yourself that you can't admit you're tired."
            ],
            "advice": [
                "When someone chooses differently than you would, ask once: is this wrong, or just not mine?",
                "Once this week, name a small resentment out loud before it becomes an eruption.",
                "Ask: is this judgment coming from my values, or from my exhaustion?",
                "Loosen one rule this week on purpose. Confirm the world doesn't fall apart."
            ],
            "keywords": ["魁罡", "principled steel", "dry resolve", "hidden heat"]
        }
    }
}


def main() -> int:
    ap = argparse.ArgumentParser(description="庚 일간 5일주 추가")
    ap.add_argument("--force", action="store_true", help="스텁 덮어쓰기")
    args = ap.parse_args()

    print("=== 庚 일간 5일주 추가 (庚子, 庚寅, 庚辰, 庚申, 庚戌) ===")
    print("    (庚午는 이미 존재 — 건너뜀)")
    
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