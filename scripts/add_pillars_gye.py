#!/usr/bin/env python3
"""
癸 일간 6일주 추가 (癸丑, 癸卯, 癸巳, 癸未, 癸酉, 癸亥).
癸는 음수(陰水)의 기운으로, 이슬과 샘처럼 섬세하고 지혜로운 성향입니다.
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
        "癸丑": {
            "name": "겨울 우물", "pillar": "癸丑",
            "hero": "당신은 얼어붙은 땅 아래의 우물입니다. 겉은 차갑고 단단하지만, 그 아래에는 마르지 않는 물이 고여 있는 사람이죠.",
            "narrative": [
                "당신은 감정을 깊이 응축하는 사람입니다. 癸丑(계축)은 차갑고 축축한 흙 위에 섬세한 물이 앉은 기둥이에요. 그래서 당신의 감수성은 겉으로 잘 드러나지 않지만, 그 안에는 아주 깊은 물이 고여 있습니다. 사람들은 당신을 '조용한 사람'으로 기억하다가, 어느 순간 당신이 한 말 한마디가 얼마나 정확했는지 뒤늦게 알아차립니다.",
                "당신의 강점은 '숨은 지혜'입니다. 말수가 적은 대신, 당신이 보는 것은 남들보다 깊습니다. 그리고 그 지혜는 저축처럼 쌓입니다. 어려운 상황에서 다른 사람들이 텅 비었을 때, 당신의 우물에는 아직 물이 남아 있어요. 그래서 당신은 위기에서 조용히 사람들을 살리는 역할을 합니다.",
                "당신의 그림자는 '너무 오래 감정을 묻어두는 것'입니다. 겨울 우물은 얼음 아래에 물이 있지만, 그 얼음이 너무 두꺼워지면 정작 필요한 순간에 물을 꺼낼 수 없습니다. 당신은 감정을 잘 꺼내지 않아서, 주변 사람들이 당신의 진심을 모릅니다. 그리고 결정적인 순간에도 '조금만 더 참아보자' 하며 물을 꺼내지 못합니다.",
                "성숙한 癸丑은 '얼음을 스스로 깨는 사람'입니다. 감정과 지혜를 깊이 간직하되, 필요한 순간에는 스스로 얼음을 깨고 물을 꺼낼 줄 아는 사람. 그때 당신의 조용함은 거리감이 아니라, 사람들이 의지하고 싶은 깊은 안정이 됩니다."
            ],
            "shadows": [
                "감정을 너무 오래 묻어두어, 주변 사람들이 당신의 진심을 모릅니다.",
                "결정할 순간에도 '조금만 더 참아보자' 하며 미룹니다.",
                "자신의 지혜를 스스로 인정하지 않아, 늘 부족한 느낌에 시달립니다."
            ],
            "advice": [
                "이번 주에 한 번, 평소 묻어두던 감정을 조금 꺼내 보여주세요. 작은 것도 괜찮습니다.",
                "결정해야 할 것 하나를 골라, 정해진 기한 안에 반드시 결정하세요.",
                "당신이 아는 지혜 하나를 누군가에게 알려주세요. 나눌 때 우물은 마르지 않습니다.",
                "겨울 우물에도 봄은 옵니다. 지금이 덜 빛나는 시기라면, 그건 당신의 실패가 아니라 계절입니다."
            ],
            "keywords": ["겨울 우물", "숨은 지혜", "감정의 응축", "얼음 깨기"]
        },
        "癸卯": {
            "name": "봄비 내리는 정원", "pillar": "癸卯",
            "hero": "당신은 봄비가 내리는 정원입니다. 조용히 스며드는 물처럼, 당신은 사람과 일이 자라도록 조용히 돕는 사람이죠.",
            "narrative": [
                "당신은 성장을 지원하는 사람입니다. 癸卯(계묘)는 水가 木을 낳는 기둥이에요. 봄비가 나무를 키우듯, 당신은 조용히 스며들어 사람과 프로젝트가 자라도록 돕습니다. 화려한 리더십이 아니라, 뒤에서 물을 대는 사람이에요. 그래서 당신이 지나간 자리는 조금씩 더 초록이 되어 있습니다.",
                "당신의 강점은 '섬세한 창조'입니다. 큰 폭발보다는 꾸준한 빛으로 아이디어를 키우고, 사람을 북돋우고, 관계를 자라게 합니다. 그래서 당신과 함께 일한 사람들은 시간이 지나서야 '그때 그 사람 덕분이었구나' 하고 알아차립니다. 당신의 기여는 늘 사후에 인정됩니다.",
                "당신의 그림자는 '자신의 성장을 자꾸 미루는 것'입니다. 봄비는 나무를 위해 내리지만, 정작 자신은 땅속으로 스며들어 사라집니다. 당신도 마찬가지예요. 다른 사람의 성장을 돕다가, 정작 자신의 성장은 계속 뒤로 미룹니다. 그리고 그렇게 자란 사람이 떠나면, 이유를 알 수 없는 상실감이 밀려옵니다.",
                "성숙한 癸卯는 '자신도 정원의 일부임을 아는 사람'입니다. 다른 사람을 키우는 동시에 자신도 자라는 사람. 그때 당신의 봄비는 한 번 내리고 마는 계절이 아니라, 몇 년 동안 계속 사람을 살리는 단비가 됩니다."
            ],
            "shadows": [
                "다른 사람의 성장을 돕다가, 자신의 성장은 계속 미룹니다.",
                "당신이 키운 사람이 떠나면, 이유를 알 수 없는 상실감에 시달립니다.",
                "자신의 기여를 너무 낮게 봐서, 스스로에게 인색해집니다."
            ],
            "advice": [
                "이번 주에 자신의 성장을 위해 쓸 시간을 먼저 달력에 넣어두세요.",
                "다른 사람을 돕기 전에, '이건 그 사람이 스스로 할 수 있는 일인가'를 물어보세요.",
                "당신이 키운 사람이 떠나면, '이건 성장의 증거다'라고 스스로에게 말해주세요.",
                "당신의 봄비를 나눌 사람과, 당신과 함께 봄비를 맞을 사람을 구분해 보세요."
            ],
            "keywords": ["봄비", "섬세한 창조", "성장 지원", "함께 자람"]
        },
        "癸巳": {
            "name": "안개 낀 호수", "pillar": "癸巳",
            "hero": "당신은 안개 낀 호수입니다. 표면은 흐릿하지만, 그 아래에는 뜨거운 물이 흐르는 사람이죠.",
            "narrative": [
                "당신은 감성과 열기를 동시에 지닌 사람입니다. 癸巳(계사)는 섬세한 물 위에 뜨거운 불기운이 앉은 기둥이에요. 그래서 당신은 겉으로 보기에는 조용하고 부드러운데, 안에는 뜨거운 열정이 흐르고 있습니다. 사람들은 당신을 '온화한 사람'으로 기억하다가, 어느 순간 당신이 보여주는 열정의 강도에 놀랍니다.",
                "당신의 강점은 '감성과 실용의 결합'입니다. 癸는 감수성이고 巳는 실용적 실행력이에요. 그래서 당신은 감정을 느끼면서도 그것을 실제 행동으로 옮길 줄 압니다. 사람들은 당신이 '따뜻하면서도 정확한 사람'이라고 느낍니다. 이 결합은 흔하지 않아요.",
                "당신의 그림자는 '안개 속에 갇히는 것'입니다. 안개 낀 호수는 아름답지만, 방향을 잃기 쉽습니다. 당신은 감정과 생각이 뒤엉켜서, 정작 결정해야 할 순간에 명확하게 판단하지 못할 때가 있어요. 그리고 안의 뜨거운 열기가 쌓이다가, 어느 순간 걷잡을 수 없이 터져 나옵니다. 평소의 온화함과 대비되어, 주변이 크게 당황하죠.",
                "성숙한 癸巳는 '안개를 스스로 걷는 사람'입니다. 감성과 열기를 유지하되, 결정할 때는 안개를 걷고 선명하게 볼 줄 아는 사람. 그때 당신의 이중성은 흔들림이 아니라, 사람들이 의지하고 싶은 깊은 온기가 됩니다."
            ],
            "shadows": [
                "감정과 생각이 뒤엉켜서, 결정해야 할 순간에 판단이 흐려집니다.",
                "뜨거운 열기를 계속 감추다가, 어느 순간 폭발합니다.",
                "겉과 속의 온도차로 인해, 사람들이 당신을 오해합니다."
            ],
            "advice": [
                "이번 주에 결정해야 할 것 하나를 골라, 안개를 걷고 명확하게 판단해 보세요.",
                "당신의 뜨거운 열기를 말로 꺼내 보여주세요. 좋아하는 것, 원하는 것.",
                "감정이 올라올 때, '이건 지금 표현할 때인가, 조금 더 다듬을 때인가' 스스로에게 물어보세요.",
                "가까운 사람에게 '나는 겉으로는 조용해 보여도 속으로는 뜨거워'라고 한 번 설명해 주세요."
            ],
            "keywords": ["안개 낀 호수", "감성과 실용", "숨은 열기", "선명한 판단"]
        },
        "癸未": {
            "name": "마른 땅의 이슬", "pillar": "癸未",
            "hero": "당신은 여름의 마른 땅 위에 내린 이슬입니다. 희소하지만, 그 몇 방울이 생명을 살리는 사람이죠.",
            "narrative": [
                "당신은 절제와 인내의 사람입니다. 癸未(계미)는 여름의 건조한 흙 위에 섬세한 물이 앉은 기둥이에요. 마른 땅 위의 이슬은 많지 않습니다. 하지만 그 몇 방울이 하루를 버티게 하죠. 당신의 지혜도 그렇습니다. 말수가 적고 화려하지 않지만, 그 한마디가 사람을 살립니다.",
                "당신의 강점은 '희소한 지혜'입니다. 당신은 필요 이상으로 많이 말하지 않고, 필요할 때 정확히 말합니다. 그래서 당신의 말은 무게가 있습니다. 조직에서 '이 사람이 말하면 뭔가 있다'는 평가가 붙는 이유입니다. 당신은 양이 아니라 질로 승부하는 사람이에요.",
                "당신의 그림자는 '너무 절제하는 것'입니다. 마른 땅의 이슬은 아껴 써야 하지만, 아끼기만 하면 정작 필요한 순간에 증발해 버립니다. 당신은 자신을 너무 아껴서, 정작 필요한 순간에 자신을 드러내지 못합니다. 그리고 인내가 지나쳐서, 이미 끝난 일을 계속 붙들고 있기도 하죠.",
                "성숙한 癸未는 '아낄 때와 쓸 때를 아는 사람'입니다. 자신의 지혜와 에너지를 절제하되, 필요한 순간에는 아낌없이 쓸 줄 아는 사람. 그때 당신의 희소함은 위축이 아니라, 사람들이 찾아오는 깊은 지혜가 됩니다."
            ],
            "shadows": [
                "너무 절제해서, 정작 필요한 순간에 자신을 드러내지 못합니다.",
                "인내가 지나쳐서, 이미 끝난 일을 계속 붙들고 있습니다.",
                "자신의 지혜를 아껴두다가, 정작 필요한 사람에게 전하지 못합니다."
            ],
            "advice": [
                "이번 주에 아껴두던 지혜 하나를, 필요한 사람에게 아낌없이 전해보세요.",
                "결정해야 할 것 하나를 골라, 이번 주 안에 결정하세요.",
                "당신이 붙들고 있는 것 세 가지를 적어보세요. 그중 하나는 놓아도 됩니다.",
                "자신을 위한 작은 소비 하나를 이번 주에 만들어 보세요. 시간이든 돈이든."
            ],
            "keywords": ["마른 땅의 이슬", "절제의 지혜", "희소한 목소리", "아낌과 사용"]
        },
        "癸酉": {
            "name": "달빛 비친 우물", "pillar": "癸酉",
            "hero": "당신은 달빛이 비친 우물입니다. 조용히 빛나며, 그 빛으로 사람들의 마음을 비추는 사람이죠.",
            "narrative": [
                "당신은 정밀한 감수성의 사람입니다. 癸酉(계유)는 섬세한 물 위에 세공된 금속이 앉은 기둥이에요. 달빛이 우물에 비치면 그 안이 환해지듯, 당신의 감수성은 아주 정확합니다. 사람들은 당신이 이상하게 '내 마음을 다 읽는 것 같다'고 느낍니다.",
                "당신의 강점은 '세공된 지혜'입니다. 癸의 감수성과 酉의 정밀함이 만나면, 아주 예리하면서도 섬세한 통찰이 만들어집니다. 당신은 사람의 마음을 정확하게 읽고, 그 사람에게 필요한 것을 정확하게 짚어냅니다. 이건 흔한 재능이 아니에요. 당신의 조언은 늘 정확한 곳을 찌릅니다.",
                "당신의 그림자는 '완벽한 감수성의 부담'입니다. 정밀한 감수성은 아름답지만, 그만큼 세상의 흐트러짐이 크게 느껴집니다. 당신은 사람의 아픔을 자기 것처럼 느끼고, 완벽하지 않은 관계에 오래 마음이 걸립니다. 그리고 그 정밀함이 스스로에게도 향해서, 완벽하지 않은 자신을 용서하지 못합니다.",
                "성숙한 癸酉는 '감수성을 다스리는 사람'입니다. 예리한 감수성을 유지하되, 그 감수성이 자신을 소모시키지 않도록 조율할 줄 아는 사람. 그때 당신의 정밀함은 압박이 아니라, 사람들이 찾아오는 깊은 이해가 됩니다."
            ],
            "shadows": [
                "사람의 아픔을 자기 것처럼 느껴서, 감정적으로 지칩니다.",
                "완벽하지 않은 관계에 오래 마음이 걸려, 놓아주기 어렵습니다.",
                "정밀함이 스스로에게 향해서, 완벽하지 않은 자신을 용서하지 못합니다."
            ],
            "advice": [
                "이번 주에 한 번, 누군가의 감정을 대신 느끼지 않도록 의식적으로 거리를 두세요.",
                "완벽하지 않은 관계 하나를 골라, 그 불완전함을 그대로 받아들여 보세요.",
                "자신에게 '이 정도면 충분해'라고 말할 순간을 하나 만들어 두세요.",
                "당신의 감수성을 소모하지 않도록, 혼자만의 회복 시간을 규칙적으로 확보하세요."
            ],
            "keywords": ["달빛 우물", "정밀한 감수성", "세공된 지혜", "깊은 이해"]
        },
        "癸亥": {
            "name": "깊은 겨울 강", "pillar": "癸亥",
            "hero": "당신은 깊은 겨울 강입니다. 표면은 조용하지만, 그 아래에서는 광활한 물줄기가 흐르는 사람이죠.",
            "narrative": [
                "당신은 癸 중에서도 가장 순수한 癸입니다. 癸亥(계해)는 癸의 록(祿) 자리에 癸가 앉은, 물 기운이 두 겹으로 겹친 기둥이에요. 그래서 당신의 직관은 흔들리지 않고, 당신의 지혜는 광활하며, 당신의 감수성은 깊습니다. 사람들은 당신 앞에서 이상하게 '이 사람은 뭔가 다르다'는 인상을 받습니다.",
                "당신의 강점은 '광활한 직관'입니다. 표면만 보는 사람들과 달리 당신은 사건 아래의 흐름을 봅니다. 결정을 서두르지 않고, 충분히 흐르게 한 뒤에 내리는 판단은 대체로 맞습니다. 그래서 당신은 조직에서 '큰 판단을 맡길 수 있는 사람'으로 통합니다.",
                "당신의 그림자는 '너무 깊이 흘러가는 것'입니다. 겨울 강은 조용하지만, 물이 너무 깊으면 정작 필요한 순간에 표면으로 떠오르지 못합니다. 당신은 생각과 감정을 너무 깊이 담아두어서, 주변 사람들이 당신의 진심을 잘 모릅니다. 그리고 그 깊이가 때로는 고립이 됩니다.",
                "성숙한 癸亥는 '깊이에서 표면으로 떠오를 줄 아는 사람'입니다. 깊은 지혜를 유지하되, 필요할 때는 표면으로 떠올라 사람들과 만날 줄 아는 사람. 그때 당신의 깊이는 거리감이 아니라, 사람들이 의지하고 싶은 지혜가 됩니다."
            ],
            "shadows": [
                "생각과 감정을 너무 깊이 담아두어, 주변 사람들이 당신의 진심을 모릅니다.",
                "깊은 사고가 때로는 고립이 됩니다.",
                "직관이 너무 강해서, 논리로 설명하기 어려운 판단을 내릴 때가 있습니다."
            ],
            "advice": [
                "이번 주에 한 번, 당신의 깊은 생각을 표면으로 꺼내 보여주세요.",
                "당신의 직관을 믿되, 그것을 다른 사람에게 설명할 언어도 함께 준비해 두세요.",
                "당신이 깊이 담아둔 감정 중 하나를, 믿을 만한 사람에게 꺼내 보세요.",
                "겨울 강에도 봄은 옵니다. 지금이 덜 빛나는 시기라면, 그건 당신의 실패가 아니라 계절입니다."
            ],
            "keywords": ["순수 癸", "깊은 겨울 강", "광활한 직관", "깊이와 표면"]
        }
    },
    "en": {
        "癸丑": {
            "name": "Winter Well", "pillar": "癸丑",
            "hero": "You're a well beneath frozen ground. Cold and hard on the surface, with water that never runs dry underneath.",
            "narrative": [
                "You condense feeling deep inside. 癸丑 is delicate water resting on cold, damp earth. Your sensitivity doesn't show on the surface, but the well beneath it is very deep. People remember you as quiet — and then one day they realize how exact a single thing you said was.",
                "Your strength is hidden wisdom. You don't talk much, but what you see runs deeper than most. And your wisdom accumulates like savings. In a crisis, when everyone else has run dry, your well still has water. That's why you quietly keep people alive in hard seasons.",
                "Your shadow is storing feeling too long. A winter well still has water under the ice, but if the ice gets too thick, you can't draw the water when it's needed. You don't bring feelings out easily, so the people around you don't know your heart. And when a decisive moment comes, you tell yourself, 'Hold on a little longer' — and don't draw.",
                "A mature Gye-Chou breaks their own ice. Keeping the feelings and the wisdom deep, and knowing how to draw them up when the moment actually calls. Then your quietness stops being distance and becomes the kind of stability people want to lean on."
            ],
            "shadows": [
                "Storing feeling so long that people never learn your heart.",
                "Postponing decisions with 'just a little longer.'",
                "Not recognizing your own wisdom, always feeling insufficient."
            ],
            "advice": [
                "Once this week, bring one stored feeling up. Small is fine.",
                "Pick one decision and make it by a fixed deadline.",
                "Share one piece of your wisdom with someone. The well doesn't dry when shared.",
                "Winter wells have springs too. If you're in a dim season, that's a season, not a failure."
            ],
            "keywords": ["winter well", "hidden wisdom", "condensed feeling", "breaking the ice"]
        },
        "癸卯": {
            "name": "Spring Rain Garden", "pillar": "癸卯",
            "hero": "You're a garden in spring rain. Quietly seeping water — and quiet is exactly how you help people and things grow.",
            "narrative": [
                "You help growth happen. 癸卯 is water giving birth to wood. Like spring rain feeding trees, you seep in quietly so people and projects can grow. Not flashy leadership — the one watering from behind. The places you've passed through are a little greener.",
                "Your strength is delicate creation. Not big explosions — steady light that develops ideas, encourages people, and grows relationships. People who've worked with you realize, months later, 'that was because of them.' Your contribution is always recognized after the fact.",
                "Your shadow is postponing your own growth. Spring rain falls for the trees and then disappears into the earth. You help other people grow while continuing to push your own growth back. And when someone you cultivated leaves, a loss you can't quite name arrives.",
                "A mature Gye-Mao knows they're part of the garden too. Growing yourself in the same season you grow others. Then your spring rain isn't a one-season event — it becomes years of steady rainfall that keeps people alive."
            ],
            "shadows": [
                "Helping others grow while postponing your own growth indefinitely.",
                "Feeling loss you can't name when someone you cultivated leaves.",
                "Valuing your contribution so low that you're stingy with yourself."
            ],
            "advice": [
                "Put your own growth on the calendar first this week.",
                "Before helping, ask: can this person do this themselves?",
                "When someone leaves, tell yourself: this is proof of growth.",
                "Separate the people you share rain with from the people who share rain with you."
            ],
            "keywords": ["spring rain", "delicate creation", "growing support", "growing together"]
        },
        "癸巳": {
            "name": "Misty Lake", "pillar": "癸巳",
            "hero": "You're a misty lake. Blurry on the surface, with hot water running underneath.",
            "narrative": [
                "You hold feeling and heat together. 癸巳 is delicate water with hot fire resting on it. You look gentle on the surface while a hot current runs inside. People remember you as warm — and then are surprised by the intensity you can show.",
                "Your strength is combining feeling with practicality. 癸 is sensitivity, 巳 is practical execution. You can feel something and put it into real action. People find you warm and precise at once. That combination is rare.",
                "Your shadow is getting stuck in the mist. A misty lake is beautiful, but it's easy to lose direction. Feelings and thoughts tangle together, and at the moment a decision is needed you can't see clearly. And the heat that piles up inside eventually bursts out suddenly, surprising everyone who knew you as calm.",
                "A mature Gye-Si clears their own mist. Keeping the feeling and the heat, and seeing clearly when a decision is actually required. Then your duality stops being a shake and becomes the kind of deep warmth people want to lean on."
            ],
            "shadows": [
                "Feelings and thoughts tangled at the moment a decision is needed.",
                "Suppressed heat that eventually bursts out.",
                "The gap between surface and interior makes people misread you."
            ],
            "advice": [
                "Pick one decision to make this week and clear the mist before you make it.",
                "Say one of your hot feelings out loud. What you love, what you want.",
                "When emotion rises, ask: is this the moment to express it, or to give it more shape?",
                "Tell someone close, 'I look quiet but I run hot inside.' It clears years of misreading."
            ],
            "keywords": ["misty lake", "feeling and practice", "hidden heat", "clear judgment"]
        },
        "癸未": {
            "name": "Dew on Dry Earth", "pillar": "癸未",
            "hero": "You're dew on summer's dry earth. Rare — and a few drops of it are enough to keep something alive.",
            "narrative": [
                "You're the person of restraint and patience. 癸未 is delicate water resting on dry summer earth. Dew on dry earth isn't much, but those few drops make the day bearable. Your wisdom works the same way. You don't say much, and it isn't flashy, but one line of it keeps someone alive.",
                "Your strength is rare wisdom. You don't speak more than necessary, and when you speak you're exact. So your words carry weight. That's why organizations say, 'If this person speaks, something's there.' You win on quality, not quantity.",
                "Your shadow is restraint taken too far. Dew on dry earth should be used carefully — but if you only conserve it, it evaporates just when it's needed. You're so careful with yourself that you can't show up when the moment actually calls. And patience taken too far means holding onto something that's already over.",
                "A mature Gye-Wei knows when to save and when to spend. Conserving wisdom and energy, and spending them without holding back when it matters. Then your rarity stops being withdrawal and becomes the kind of deep wisdom people come looking for."
            ],
            "shadows": [
                "So restrained that you can't show up when the moment needs you.",
                "Patience carried so far that you keep holding something that's already over.",
                "Conserving your wisdom and never delivering it to the people who need it."
            ],
            "advice": [
                "Once this week, deliver one piece of wisdom without holding it back.",
                "Pick one decision and make it this week.",
                "List three things you're holding. One of them can be put down.",
                "Create one small spend on yourself this week — time or money."
            ],
            "keywords": ["dew on dry earth", "restraint", "rare voice", "saving and spending"]
        },
        "癸酉": {
            "name": "Moonlit Well", "pillar": "癸酉",
            "hero": "You're a well lit by the moon. Quietly shining, and your light shows other people their own hearts.",
            "narrative": [
                "You have precise sensitivity. 癸酉 is delicate water with crafted metal resting on it. Moonlight on a well brightens the water inside — and your sensitivity is exact like that. People feel oddly 'understood' around you.",
                "Your strength is refined wisdom. 癸's sensitivity meeting 酉's precision makes very sharp, very delicate insight. You read people's hearts accurately, and you name what they need. This is a rare gift. Your advice always hits a true spot.",
                "Your shadow is the weight of perfect sensitivity. Precise sensitivity is beautiful, but it makes the world's messiness land very hard. You feel other people's pain as your own, and imperfect relationships stay with you a long time. And that precision also turns inward — you can't forgive yourself for not being perfect.",
                "A mature Gye-You governs the sensitivity. Keeping the sharpness, and calibrating so it doesn't deplete you. Then your precision stops being pressure and becomes the kind of deep understanding people come to you for."
            ],
            "shadows": [
                "Feeling other people's pain as your own until you're emotionally exhausted.",
                "Staying attached to imperfect relationships, unable to release them.",
                "Precision turned inward, unable to forgive your own imperfection."
            ],
            "advice": [
                "Once this week, consciously step back from one person's emotion.",
                "Pick one imperfect relationship and accept the imperfection as it is.",
                "Create a moment this week where you say 'this is enough' to yourself.",
                "Set up regular recovery time so your sensitivity isn't depleted."
            ],
            "keywords": ["moonlit well", "precise sensitivity", "refined wisdom", "deep understanding"]
        },
        "癸亥": {
            "name": "Deep Winter River", "pillar": "癸亥",
            "hero": "You're a deep winter river. Quiet on the surface, with a vast waterway running underneath.",
            "narrative": [
                "You're the purest form of 癸. 癸亥 is 癸 sitting in its own 祿 (Lu) — double water, layered on itself. So your intuition doesn't shake, your wisdom is wide, and your sensitivity is deep. People sense in your presence that this person is different.",
                "Your strength is wide intuition. Where others see only the surface, you see the flow underneath. You don't rush to conclusions, and the conclusions you arrive at after letting things run are usually right. So organizations end up trusting you with big judgments.",
                "Your shadow is flowing too deep. A winter river is quiet, but if the water is too deep it can't surface when it needs to. You hold thoughts and feelings too deep, so people around you don't know your heart. And that depth sometimes becomes isolation.",
                "A mature Gye-Hai knows how to rise from the depth to the surface. Keeping the deep wisdom, and coming up to meet people when the moment calls. Then your depth stops being distance and becomes the kind of wisdom people want to lean on."
            ],
            "shadows": [
                "Holding thoughts and feelings too deep, so people don't learn your heart.",
                "Depth that becomes isolation.",
                "Intuition so strong that you make calls you can't easily explain."
            ],
            "advice": [
                "Once this week, bring one deep thought up to the surface.",
                "Trust the intuition, and prepare language to explain it to others.",
                "Take one deep feeling out of the well and share it with someone you trust.",
                "Winter rivers have springs too. If this is a dim season, it's a season, not a failure."
            ],
            "keywords": ["pure 癸", "deep winter river", "wide intuition", "depth and surface"]
        }
    }
}


def main() -> int:
    ap = argparse.ArgumentParser(description="癸 일간 6일주 추가")
    ap.add_argument("--force", action="store_true", help="스텁 덮어쓰기")
    args = ap.parse_args()

    print("=== 癸 일간 6일주 추가 (癸丑, 癸卯, 癸巳, 癸未, 癸酉, 癸亥) ===")
    
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