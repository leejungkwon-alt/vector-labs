#!/usr/bin/env python3
"""
P3: 戊 6필러 stub → 완성본 교체 (EN+KO).
- 안전: 이미 narrative>2 이면 skip (재실행 안전)
- 저장 전 JSON 검증 실패 시 .bak 복구
- 완료 후 stub 잔존 재스캔
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "app/services/content/data"

CONTENT = {
    # ================================================================
    # 戊午 — 불을 품은 산 / Mountain in Fire
    # ================================================================
    "戊午": {
        "en": {
            "pillar": "戊午",
            "hero": "You're a mountain with a fire burning at its core. Quiet from the outside, warm — sometimes explosive — underneath.",
            "narrative": [
                "You carry enormous energy, but it doesn't leak out at random. You look calm — often the calmest person in the room — and yet there's something warm and pressurized moving just under the surface. When you choose to act, everyone feels it.",
                "Your engine runs on conviction. Half-measures and hedging don't move you, and you have a low tolerance for people who speak without meaning it. Once you commit, you commit fully — and that intensity is what people remember about you.",
                "Your shadow is the fire you don't regulate. Because you can hold so much in, small irritations can build into a sudden eruption that surprises everyone around you. And when you push too hard for too long, you can exhaust yourself without noticing — the mountain doesn't feel the tremors until it cracks.",
                "The mature form of this pillar is controlled warmth. Not a fire that goes out — a fire that is deliberate. You learn when to release heat in small, steady amounts, and you learn how to share some of that heat with others. When you do, your intensity stops being a risk to manage and becomes the thing that makes you unmistakable.",
            ],
            "shadows": [
                "You can hold so much in that the eventual release feels sudden and unfair to the people around you.",
                "You run at full capacity without noticing fatigue, then feel betrayed by your own exhaustion.",
                "Under pressure, you can become convinced that your read of a situation is the only correct one.",
            ],
            "advice": [
                "Once this week, name an irritation the moment you notice it — out loud, to a person who can hear it. Don't wait until it's a fire.",
                "Find one deliberate way to release heat every day. Not productivity — movement, breath, or something that uses your body.",
                "When you catch yourself running at full capacity, stop one thing. Say 'I'm choosing this' out loud, so it doesn't feel like failure.",
                "Ask one trusted person a genuinely open question. Not 'do you agree?' — 'what do you see that I don't?'",
            ],
            "keywords": ["volcanic drive", "contained intensity", "protective heat", "regulated fire"],
            "name": "Mountain in Fire",
            "name_traditional": "",
        },
        "ko": {
            "pillar": "戊午",
            "hero": "당신은 중심에 불을 품은 산입니다. 겉은 조용하지만, 그 아래에는 뜨겁게 압축된 에너지가 흐르고 있죠.",
            "narrative": [
                "당신은 큰 에너지를 지녔지만, 그것이 아무 데서나 새어 나오지 않습니다. 겉으로는 차분해 보이고, 종종 방에서 가장 침착한 사람이죠. 그런데 그 아래에는 뜨겁게 압축된 무언가가 흐르고 있습니다. 당신이 움직이기로 결정한 순간, 모두가 그것을 느낍니다.",
                "당신의 엔진은 확신 위에서 돌아갑니다. 반쪽짜리 태도나 흐릿한 말에 흔들리지 않고, 의미 없이 말하는 사람을 견디기 어려워하죠. 한 번 마음을 정하면 끝까지 밀어붙이는 그 강도가, 사람들이 당신에 대해 기억하는 것입니다.",
                "당신의 그림자는 '조절되지 않는 불'입니다. 많은 것을 안에 담아둘 수 있는 만큼, 작은 불편이 쌓여 갑작스러운 폭발로 이어질 때가 있어요. 오래도록 자신을 밀어붙이면 지치는데도 알아차리지 못합니다. 산은 갈라지기 전까지 흔들림을 느끼지 않으니까요.",
                "이 기둥의 성숙한 형태는 '절제된 온기'입니다. 꺼지는 불이 아니라, 의도해서 쓰는 불. 열을 작고 꾸준한 양으로 내보내는 법을 배우고, 그 열의 일부를 다른 사람에게 나눠 맡기는 법을 배울 때, 당신의 강도는 관리해야 할 위험이 아니라 당신을 잊을 수 없게 만드는 힘이 됩니다.",
            ],
            "shadows": [
                "너무 오래 안고 있다가, 결국 주변 사람들에게 갑작스럽고 억울하게 느껴지는 폭발로 이어질 수 있습니다.",
                "자신의 피로를 인지하지 못한 채 최대 출력으로 달리다가, 이후에 스스로의 지침에 배신감을 느낍니다.",
                "압박이 심할 때, 자신의 판단이 유일하게 옳은 것이라는 확신에 사로잡히기도 합니다.",
            ],
            "advice": [
                "이번 주에 한 번, 불편함을 알아차린 즉시 말해보세요. 들을 수 있는 사람에게, 소리 내어. 불이 될 때까지 기다리지 마세요.",
                "매일 열을 빼낼 의식적인 방법 하나를 찾으세요. 생산성이 아니라 움직임, 호흡, 혹은 몸을 쓰는 무언가.",
                "자신이 최대 출력으로 달리고 있다는 걸 깨달으면, 하나를 멈추세요. '이건 내가 선택한 것'이라고 소리 내어 말해보세요. 실패로 느껴지지 않도록요.",
                "믿을 만한 사람에게 진짜 열린 질문을 하나 해보세요. '동의해?'가 아니라 '내가 못 보는 걸 뭐가 보여?'",
            ],
            "keywords": ["화산의 추진력", "응축된 강렬함", "보호하는 열기", "조율된 불"],
            "name": "불을 품은 산",
            "name_traditional": "무오(戊午)",
        },
    },

    # ================================================================
    # 戊子 — 산 아래 샘 / Mountain Spring
    # ================================================================
    "戊子": {
        "en": {
            "pillar": "戊子",
            "hero": "You're a mountain with a spring running underneath. Solid on the surface — deep, clear water beneath.",
            "narrative": [
                "You come across as steady, unremarkable, easy to overlook. People underestimate you — until the moment a room needs someone who can actually think clearly, and you're the only one who does.",
                "Your strength is quiet insight. You read situations before they're explained, and the best decisions you make almost never come out of a meeting — they come out of silence. What looks like passivity is usually you watching the whole board before moving one piece.",
                "Your shadow is thinking past the moment. Because the water runs deep, you can keep processing until the window to act has quietly closed. And when you're uncertain, you go silent — and to everyone else, silence looks exactly like distance.",
                "The mature form of this pillar is a spring that actually flows. Insight that arrives, is spoken, and then moves on. You learn to trust the water without drowning in it — to see, to say, to act, in that order, before the tide changes.",
            ],
            "shadows": [
                "You keep thinking past the moment when a decision was still yours to make.",
                "You go quiet when you're uncertain, and people read the silence as distance.",
                "You doubt your own insight because it doesn't arrive with proof attached.",
            ],
            "advice": [
                "Once this week, act on a decision before you feel 'ready.' Notice what actually happens.",
                "Say the observation out loud even if you can't yet explain it. Let people hear the water.",
                "When you go quiet, tell one person 'I'm thinking.' Don't make them guess.",
                "Put one open question down for a day. Water settles on its own.",
            ],
            "keywords": ["hidden depth", "still waters", "quiet insight", "mountain calm"],
            "name": "Mountain Spring",
            "name_traditional": "",
        },
        "ko": {
            "pillar": "戊子",
            "hero": "당신은 아래에 맑은 샘이 흐르는 산입니다. 겉은 단단하고 무던해 보이지만, 그 아래에는 깊고 맑은 물이 흐르고 있죠.",
            "narrative": [
                "당신은 안정적이고 무던하고 지나치기 쉬운 사람으로 보입니다. 사람들은 당신을 과소평가합니다. 방 안에서 실제로 명료하게 생각할 수 있는 사람이 필요해지고, 그게 당신뿐인 순간이 오기 전까지는요.",
                "당신의 강점은 조용한 통찰입니다. 상황이 설명되기 전에 상황을 읽고, 당신이 내리는 최고의 결정은 회의에서 나오지 않습니다. 침묵에서 나옵니다. 수동적으로 보이는 것은 대개 한 조각을 움직이기 전에 판 전체를 지켜보고 있는 것입니다.",
                "당신의 그림자는 '결정적 순간을 지나서까지 생각하는 것'입니다. 물이 깊은 만큼, 행동할 창이 조용히 닫힐 때까지 계속 처리할 수 있어요. 그리고 불확실할 때 조용해지는데, 다른 사람들에게 그 침묵은 거리감과 정확히 똑같이 보입니다.",
                "이 기둥의 성숙한 형태는 '실제로 흐르는 샘'입니다. 통찰이 도착하고, 말해지고, 그리고 흘러갑니다. 물을 신뢰하되 물에 잠기지 않는 법을 배웁니다. 보고, 말하고, 행동하는 순서로, 조류가 바뀌기 전에요.",
            ],
            "shadows": [
                "결정이 아직 당신의 것일 때를 지나서까지 생각을 이어갑니다.",
                "불확실할 때 조용해지는데, 사람들은 그 침묵을 거리감으로 읽습니다.",
                "증거가 함께 오지 않는다는 이유로 스스로의 통찰을 의심합니다.",
            ],
            "advice": [
                "이번 주에 한 번, 준비됐다고 느끼기 전에 결정을 실행해보세요. 실제로 무슨 일이 일어나는지 지켜보세요.",
                "설명이 아직 안 되어도 관찰한 것을 소리 내어 말해보세요. 사람들이 물소리를 듣게 하세요.",
                "조용해질 때, 한 사람에게 '지금 생각 중이야'라고 알려주세요. 추측하게 만들지 마세요.",
                "열린 질문 하나를 하루 동안 내려놓으세요. 물은 스스로 가라앉습니다.",
            ],
            "keywords": ["숨은 깊이", "고요한 물", "조용한 통찰", "산의 평정"],
            "name": "산 아래 샘물",
            "name_traditional": "무자(戊子)",
        },
    },

    # ================================================================
    # 戊寅 — 숲을 품은 산 / Forested Mountain
    # ================================================================
    "戊寅": {
        "en": {
            "pillar": "戊寅",
            "hero": "You're a mountain with a forest growing on it. What looks like solid ground is actually a place where things can root.",
            "narrative": [
                "You read as dependable, warm, and hard to rattle. People bring problems to you before they bring them to anyone else — not because you ask them to, but because being near you makes the problem feel more tractable.",
                "Your strength is generous ground. You don't just support people — you give them the conditions to grow on their own. Teams you've led keep their culture after you leave. Projects you've started keep going after you've stepped back. That's rare, and it doesn't happen by accident.",
                "Your shadow is giving so much ground that your own foundation erodes. You say yes to the next person who needs a foothold, then quietly resent how little you have left. What feels like generosity can become a habit of staying needed — and staying needed is not the same as being loved.",
                "The mature form of this pillar is a mountain that holds the forest and still keeps its own rock. Generosity with boundaries. The forest actually grows better when the mountain is intact — and so does everyone who relies on you.",
            ],
            "shadows": [
                "You say yes to more than you can actually hold, then quietly resent the weight.",
                "You can confuse being needed with being loved.",
                "You stay available to everyone, and no one notices you're depleted.",
            ],
            "advice": [
                "Pick one thing you're supporting out of habit rather than choice. Let it go this week.",
                "Before you say yes to a request, ask yourself: 'Is this mine to carry?'",
                "Say out loud, once this week, 'I need something back.' Let someone hear it.",
                "Spend an hour on something that grows you, not someone else.",
            ],
            "keywords": ["generous ground", "lively stability", "growth enabler", "shared rooting"],
            "name": "Forested Mountain",
            "name_traditional": "",
        },
        "ko": {
            "pillar": "戊寅",
            "hero": "당신은 숲을 품은 산입니다. 단단한 땅처럼 보이지만, 실은 무언가가 뿌리내릴 수 있는 자리입니다.",
            "narrative": [
                "당신은 믿음직스럽고 따뜻하고 잘 흔들리지 않는 사람으로 읽힙니다. 사람들은 다른 누구에게보다 당신에게 먼저 문제를 가져옵니다. 당신이 부탁해서가 아니라, 당신 곁에 있으면 문제가 다루기 쉬운 것으로 느껴지기 때문이에요.",
                "당신의 강점은 너그러운 땅입니다. 당신은 사람을 지탱하는 데 그치지 않고, 스스로 자랄 조건을 만들어 줍니다. 당신이 이끌었던 팀은 당신이 떠난 뒤에도 그 문화를 지킵니다. 당신이 시작한 프로젝트는 당신이 손을 뗀 뒤에도 계속 굴러갑니다. 드문 일이고, 우연히 일어나지도 않아요.",
                "당신의 그림자는 '너무 많은 땅을 내어주다 자신의 기반이 침식되는 것'입니다. 다음 발판이 필요한 사람에게 '예'하다가, 남은 게 별로 없다는 걸 뒤늦게 알아차리죠. 너그러움처럼 느껴지는 것이 '필요한 사람으로 남는' 습관이 되기도 합니다. 그리고 필요한 사람이 되는 것은 사랑받는 것과 같지 않아요.",
                "이 기둥의 성숙한 형태는 '숲을 품으면서도 자신의 암반을 지키는 산'입니다. 경계가 있는 너그러움. 산이 온전할 때 숲은 더 잘 자랍니다. 당신에게 기대는 모든 사람도 마찬가지로요.",
            ],
            "shadows": [
                "실제로 감당할 수 있는 것보다 많은 것에 '예'하고, 그 무게에 조용히 서운해합니다.",
                "'필요한 사람'이 되는 것과 '사랑받는 것'을 혼동할 수 있습니다.",
                "누구에게나 열려 있어서, 아무도 당신이 지쳐 있다는 걸 알아차리지 못합니다.",
            ],
            "advice": [
                "선택이 아니라 습관으로 지탱하고 있는 것 하나를 고르세요. 이번 주에는 내려놓으세요.",
                "부탁에 '예'하기 전에 스스로에게 물어보세요. '이건 내가 짊어질 것인가?'",
                "이번 주에 한 번, '나도 뭔가 돌려받고 싶어'라고 소리 내어 말하세요. 누군가 듣게 하세요.",
                "다른 사람이 아니라 나를 자라게 하는 일에 한 시간을 쓰세요.",
            ],
            "keywords": ["너그러운 땅", "생생한 안정", "성장의 조력자", "함께 뿌리내림"],
            "name": "숲을 품은 산",
            "name_traditional": "무인(戊寅)",
        },
    },

    # ================================================================
    # 戊戌 — 마른 산 / Dry Mountain (魁罡)
    # ================================================================
    "戊戌": {
        "en": {
            "pillar": "戊戌",
            "hero": "You're a mountain on dry earth — one of the pillars the tradition calls a Commander. Quiet, hard to move, slow to yield.",
            "narrative": [
                "You don't announce yourself. People often register you as quiet, then realize — months later — that you were the one holding the line. That delayed recognition is part of your signature.",
                "The tradition names this pillar 魁罡, one of the four Commanders. Your strength is structural: an internal standard you don't trade away. When things get ugly, you're the person others rely on not to bend. Your steadiness is not performed — it's the actual shape of you.",
                "Your shadow is that dry earth cracks. You can hold so firmly that you stop listening, and the tension you don't show erupts as sudden anger or sudden withdrawal. You also tend to be much harsher on yourself than anyone else would ever be — the standard you refuse to impose on others, you impose on yourself without mercy.",
                "The mature form of this pillar is command without commandeering. You keep the standard and you also keep the door open — for the people still working toward it, and for yourself. When you can loosen one rule without losing the frame, your weight stops feeling like a wall and starts feeling like a harbor.",
            ],
            "shadows": [
                "You hold your position so firmly that other people's different choices start to look like errors.",
                "Unspoken tension builds until it snaps — and the people around you never see the snap coming.",
                "You judge yourself against a standard you would never impose on another human being.",
            ],
            "advice": [
                "When someone chooses differently than you would, ask: 'Is this wrong, or just not mine?'",
                "Say one small frustration out loud this week, before it becomes an eruption.",
                "Loosen one rule on purpose. Notice the world doesn't fall apart.",
                "Once this week, say to yourself: 'This is enough.' Mean it.",
            ],
            "keywords": ["魁罡 resolve", "dry endurance", "unshakable", "principled weight"],
            "name": "Dry Mountain",
            "name_traditional": "",
        },
        "ko": {
            "pillar": "戊戌",
            "hero": "당신은 마른 대지 위의 산입니다. 전통에서 '괴강(魁罡)'이라 부르는 기둥 중 하나죠. 조용하고, 쉽게 움직이지 않고, 쉽게 굽히지 않습니다.",
            "narrative": [
                "당신은 스스로를 드러내지 않습니다. 사람들은 보통 당신을 조용한 사람으로 인식하고, 몇 달 뒤에야 알아차리죠. 그 선을 지키고 있던 사람이 바로 당신이었다는 걸. 그 늦은 인식 자체가 당신의 서명입니다.",
                "전통은 이 기둥을 괴강(魁罡)이라 부르고, 네 명의 사령관 기둥 중 하나로 칩니다. 강점은 구조입니다. 쉽게 거래하지 않는 내적 기준이 있고, 상황이 험악해질 때 흔들리지 않는 사람으로 신뢰받습니다. 당신의 안정은 연기가 아니라 실제 모양입니다.",
                "당신의 그림자는 '마른 흙은 갈라진다'입니다. 너무 단단히 붙드는 나머지 듣는 것을 멈추고, 표현하지 않은 긴장이 갑작스러운 분노나 갑작스러운 물러남으로 터질 수 있어요. 그리고 자신에게는 다른 누구에게도 강요하지 않을 기준을 무자비하게 들이댑니다.",
                "이 기둥의 성숙한 형태는 '지휘하되 장악하지 않는 것'입니다. 기준은 유지하되 문은 열어둡니다. 아직 그 기준으로 걸어오고 있는 사람에게도, 그리고 당신 자신에게도요. 틀을 잃지 않으면서 규칙 하나를 느슨하게 풀 수 있을 때, 당신의 무게는 벽이 아니라 항구처럼 느껴지기 시작합니다.",
            ],
            "shadows": [
                "자신의 자리를 너무 단단히 지켜서, 다른 사람의 다른 선택이 오류처럼 보이기 시작합니다.",
                "표현하지 않은 긴장이 쌓이다 어느 순간 끊어지는데, 주변 사람들은 그 순간을 전혀 예측하지 못합니다.",
                "다른 사람에게는 절대 강요하지 않을 기준으로 자신을 심판합니다.",
            ],
            "advice": [
                "누군가 당신과 다른 선택을 할 때, 물어보세요. '이건 틀린 건가, 아니면 그냥 내 것이 아닌 건가?'",
                "이번 주에 작은 불편 하나를 소리 내어 말하세요. 폭발이 되기 전에요.",
                "일부러 규칙 하나를 느슨하게 풀어보세요. 세상이 무너지지 않는다는 걸 알아차리세요.",
                "이번 주에 한 번, 스스로에게 '이 정도면 충분해'라고 말해보세요. 진심으로요.",
            ],
            "keywords": ["괴강의 결의", "마른 인내", "흔들리지 않음", "원칙의 무게"],
            "name": "마른 산",
            "name_traditional": "무술(戊戌)",
        },
    },

    # ================================================================
    # 戊申 — 바위산 / Rocky Mountain
    # ================================================================
    "戊申": {
        "en": {
            "pillar": "戊申",
            "hero": "You're a mountain with rock running through it. Not a wall — a frame. Things take shape around you.",
            "narrative": [
                "You come across as clear, fair, and slightly formal. People trust your judgment before they know your history — which is unusual, and not something you consciously earn. It's just the shape of you.",
                "Your strength is structure. You don't just hold things up — you give them edges. Plans, teams, and decisions you touch end up with a visible skeleton, and the skeleton is what makes them work when conditions shift. You're not the loudest voice; you're the one the loudest voice eventually needs.",
                "Your shadow is a mountain too straight to bend. Your clarity can land as coldness, and your standard can become a wall others don't know how to approach. The harder problem is that you hold yourself to the same sharp standard, and it grinds you down slowly — you rarely notice until the edges start wearing inward.",
                "The mature form of this pillar is principle that holds and bends. You keep the frame and add a door. When you learn to soften the edge without losing the shape, people trust you more, not less — because they can finally get close enough to see how solid you actually are.",
            ],
            "shadows": [
                "Your clarity can land as coldness, and you rarely see it happening in the moment.",
                "You hold yourself to a standard you would call unreasonable in anyone else.",
                "You can build a structure so rigid that it stops accommodating the people it was built for.",
            ],
            "advice": [
                "Once this week, ask a question before giving the answer. Let someone else frame it first.",
                "Say one thing you feel, not just one thing you see — even in a small way.",
                "Notice who softens you. Spend more time with them.",
                "Forgive yourself for one mistake this week. Out loud, if you can.",
            ],
            "keywords": ["structured clarity", "rock-hard principle", "form-maker", "upright strength"],
            "name": "Rocky Mountain",
            "name_traditional": "",
        },
        "ko": {
            "pillar": "戊申",
            "hero": "당신은 속에 암반이 흐르는 산입니다. 벽이 아니라 골격. 당신 주변에서 사물이 형태를 갖춥니다.",
            "narrative": [
                "당신은 명료하고 공정하고 약간 격식 있는 사람으로 읽힙니다. 사람들은 당신의 이력을 알기 전에 당신의 판단을 신뢰합니다. 드문 일이고, 의식적으로 얻는 것도 아닙니다. 그냥 당신의 모양입니다.",
                "당신의 강점은 구조입니다. 당신은 사물을 지탱하는 데 그치지 않고, 모서리를 부여합니다. 당신이 손댄 계획·팀·결정에는 눈에 보이는 골격이 남고, 그 골격이 상황이 흔들릴 때 그것을 작동하게 만듭니다. 당신은 가장 목소리 큰 사람이 아니라, 결국 가장 목소리 큰 사람이 필요로 하는 사람입니다.",
                "당신의 그림자는 '휘어지기엔 너무 곧은 산'입니다. 당신의 명료함은 차가움으로 도착할 수 있고, 당신의 기준은 다른 사람이 다가갈 줄 모르는 벽이 될 수 있어요. 더 어려운 문제는, 그 날카로운 기준을 자신에게도 똑같이 들이대서 스스로를 천천히 갈아낸다는 것입니다. 모서리가 안쪽으로 닳기 시작할 때까지는 좀처럼 알아차리지 못하죠.",
                "이 기둥의 성숙한 형태는 '붙들면서도 휘어지는 원칙'입니다. 골격은 유지하되 문을 하나 냅니다. 형태를 잃지 않으면서 모서리를 부드럽게 만드는 법을 배우면, 사람들은 당신을 덜이 아니라 더 신뢰합니다. 당신이 실제로 얼마나 단단한지 볼 수 있을 만큼 가까이 올 수 있으니까요.",
            ],
            "shadows": [
                "당신의 명료함이 차가움으로 도착할 수 있는데, 그 순간을 잘 알아차리지 못합니다.",
                "다른 사람에게는 '부당하다'고 말할 기준을 자기 자신에게 그대로 적용합니다.",
                "구조를 너무 견고하게 지어서, 그 구조가 원래 위해 존재했던 사람들을 수용하지 못하게 될 수 있습니다.",
            ],
            "advice": [
                "이번 주에 한 번, 답을 주기 전에 질문을 먼저 하세요. 누군가 다른 사람이 먼저 틀을 잡게 하세요.",
                "보이는 것만 아니라 느끼는 것도 하나 말해보세요. 작게라도요.",
                "누가 당신을 부드러워지게 하는지 지켜보세요. 그 사람과 더 많은 시간을 보내세요.",
                "이번 주에 실수 하나를 용서하세요. 가능하면 소리 내어서요.",
            ],
            "keywords": ["구조적 명료", "암반의 원칙", "형태를 만드는 힘", "곧은 강도"],
            "name": "바위산",
            "name_traditional": "무신(戊申)",
        },
    },

    # ================================================================
    # 戊辰 — 용을 품은 산 / Dragon Mountain
    # ================================================================
    "戊辰": {
        "en": {
            "pillar": "戊辰",
            "hero": "You're a mountain with a dragon asleep inside it. Unremarkable to look at — until the moment it isn't.",
            "narrative": [
                "Most days you look ordinary, maybe even underwhelming. Then a decisive moment arrives, and the room realizes it's been sitting on something much heavier than it thought. People say 'Wait — that was *them*?' a lot around you.",
                "Your strength is stored potential. 辰 holds water and wood inside dry earth — an aquifer under a plain. You are a long-game player: patient, quiet, arranging things until the moment it matters, and then moving with a weight that surprises everyone including people who thought they knew you.",
                "Your shadow is a dragon that never wakes. You can spend years sketching a big picture without ever bringing it out, and after a while people stop asking what you're building. You can also wait for the perfect decisive moment so long that the ordinary moments — the ones that were actually available — pass while you're waiting.",
                "The mature form of this pillar is a mountain that wakes the dragon on purpose. You learn to show pieces of the big picture early, in small starts, so the world can see what's forming before it's finished. When you do, the weight that used to surprise people becomes the thing they came to rely on.",
            ],
            "shadows": [
                "You hold the plan so close that people stop believing there is one.",
                "You wait for the perfect decisive moment, and ordinary opportunities pass while you wait.",
                "You can sketch the big picture endlessly without shipping the small version.",
            ],
            "advice": [
                "Bring one piece of the plan into action this week — small, real, and visible.",
                "Tell one person what you're building. Kept only in your head, the dragon stays asleep.",
                "Pick one 'small first step' from the big picture. Do it today.",
                "Stop waiting for the decisive moment. Create one this week.",
            ],
            "keywords": ["dragon stillness", "stored potential", "big-picture patience", "decisive emergence"],
            "name": "Dragon Mountain",
            "name_traditional": "",
        },
        "ko": {
            "pillar": "戊辰",
            "hero": "당신은 속에 잠든 용을 품은 산입니다. 겉보기엔 평범하고, 그게 아니게 되는 순간이 오기 전까지는요.",
            "narrative": [
                "대부분의 날 당신은 평범해 보이고, 어쩌면 조금 부족해 보일 수도 있습니다. 그러다 결정적인 순간이 오면, 방 안의 모두가 알아차리죠. 자신들이 생각했던 것보다 훨씬 무거운 것 위에 앉아 있었다는 걸. '잠깐 — 그게 *그 사람*이었어?'라는 말이 당신 주변에서 자주 나옵니다.",
                "당신의 강점은 저장된 잠재력입니다. 辰은 마른 흙 안에 물과 나무를 품고 있습니다. 평원 아래의 대수층처럼요. 당신은 긴 게임의 선수입니다. 인내심 있게, 조용히, 중요한 순간이 올 때까지 판을 깔다가, 당신을 안다고 생각했던 사람들까지 놀라게 하는 무게로 움직입니다.",
                "당신의 그림자는 '영원히 깨어나지 않는 용'입니다. 몇 년 동안 큰 그림만 그리고 정작 꺼내 보여주지 않으면, 사람들은 당신이 무엇을 짓고 있는지 묻기를 멈춥니다. '결정적'인 순간을 너무 오래 기다리다가, 실제로 이용 가능했던 평범한 순간들이 그 기다림 사이로 지나가기도 합니다.",
                "이 기둥의 성숙한 형태는 '의도적으로 용을 깨우는 산'입니다. 큰 그림의 조각을 일찍, 작은 시작으로 보여주는 법을 배웁니다. 완성되기 전에 세상이 형성되고 있는 모습을 볼 수 있도록요. 그렇게 할 때, 사람들을 놀라게 하던 무게가 그들이 의지하게 되는 것이 됩니다.",
            ],
            "shadows": [
                "계획을 너무 가까이 붙들어서, 사람들은 계획이 있다는 것조차 믿지 않게 됩니다.",
                "완벽한 결정적 순간을 기다리다가, 그 사이 평범한 기회들이 스쳐 지나갑니다.",
                "큰 그림만 끝없이 그리고, 그 작은 버전조차 세상에 내놓지 않습니다.",
            ],
            "advice": [
                "이번 주에 계획의 한 조각을 실행으로 옮기세요. 작게, 실제로, 눈에 보이게.",
                "한 사람에게 당신이 무엇을 짓고 있는지 말하세요. 머릿속에만 두면 용은 잠든 채입니다.",
                "큰 그림에서 '작은 첫걸음' 하나를 고르세요. 오늘 하세요.",
                "결정적 순간을 기다리지 마세요. 이번 주에 직접 하나 만드세요.",
            ],
            "keywords": ["용의 고요", "저장된 잠재력", "큰 그림의 인내", "결정적 발현"],
            "name": "용을 품은 산",
            "name_traditional": "무진(戊辰)",
        },
    },
}


def write_pillar(pillar: str, lang: str, content: dict) -> tuple[bool, str]:
    path = DATA / lang / "core_pillars" / f"{pillar}.json"
    if not path.exists():
        return False, f"file not found: {path}"
    existing = json.loads(path.read_text(encoding="utf-8"))
    if len(existing.get("narrative", [])) > 2:
        return False, "already upgraded (narrative>2)"
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    try:
        path.write_text(
            json.dumps(content, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        shutil.copy2(bak, path)
        return False, f"failed, restored: {e}"
    return True, "ok"


def verify() -> list:
    issues = []
    for lang in ("en", "ko"):
        for f in (DATA / lang / "core_pillars").glob("*.json"):
            d = json.loads(f.read_text(encoding="utf-8"))
            if len(d.get("narrative", [])) <= 2:
                issues.append(f"{lang}/{f.stem}")
    return issues


def main() -> int:
    print("=" * 60)
    print("[P3] Stub pillars upgrade — 6 pillars × 2 langs")
    print("=" * 60)

    written = skipped = failed = 0
    for pillar, langs in CONTENT.items():
        for lang, data in langs.items():
            ok, msg = write_pillar(pillar, lang, data)
            marker = "✅" if ok else ("⏭  " if "already" in msg else "❌")
            print(f"  {marker} {lang}/{pillar}: {msg}")
            if ok:
                written += 1
            elif "already" in msg:
                skipped += 1
            else:
                failed += 1

    print(f"\n결과: 작성 {written} / 스킵 {skipped} / 실패 {failed}")

    issues = verify()
    if issues:
        print(f"\n❌ 남은 stub: {issues}")
        return 1
    print("\n✅ 모든 stub 해소")
    return 0


if __name__ == "__main__":
    sys.exit(main())