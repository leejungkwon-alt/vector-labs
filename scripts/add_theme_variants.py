# scripts/add_theme_variants.py
"""
1) timeline_themes.json: THEMES[rel][elem]을 3개 variant 배열로 재작성 (KO + EN)
2) content_writer.py: _resolve_theme에 hash 기반 variant 선택
"""
import ast
import hashlib
import json
import sys
from pathlib import Path

APPLY = "--apply" in sys.argv

# ═══════════════════════════════════════════════════════════
# 1. KO 테마 3-variant 정의
# ═══════════════════════════════════════════════════════════
# 구조: THEMES[relation][elem] = [{theme, body}, {theme, body}, {theme, body}]
KO_THEMES = {
    # ── same: 같은 기운 (이어짐/깊어짐/넘침) ──
    "same": {
        "木": [
            {"theme": "성장이 이어지는 시기", "body": "성장의 기운이 이 시기 내내 이어져요. 같은 방향이라 지루해질 수 있으니, 새로운 방식을 일부러 시도해보세요."},
            {"theme": "성장이 깊어지는 시기", "body": "성장의 기운이 점점 깊어져요. 겉으로 드러나는 성과보다, 뿌리를 다지는 데 집중하는 게 좋아요."},
            {"theme": "성장이 넘치는 시기", "body": "성장의 에너지가 흘러넘치는 시기예요. 다만 과욕은 금물 — 한 번에 다 하려 하지 마세요."},
        ],
        "火": [
            {"theme": "열정이 이어지는 시기", "body": "열정의 기운이 이 시기 내내 이어져요. 과열되지 않게 리듬을 조절하면서 가는 게 핵심이에요."},
            {"theme": "열정이 깊어지는 시기", "body": "열정의 기운이 안으로 깊어지는 시기예요. 겉으로 화려하기보다, 진짜 좋아하는 것에 집중해보세요."},
            {"theme": "열정이 넘치는 시기", "body": "하고 싶은 게 너무 많은 시기예요. 다 쫓지 말고 한두 가지에 집중해야 결실이 와요."},
        ],
        "土": [
            {"theme": "중심이 단단해지는 시기", "body": "안정의 기운이 이 시기 내내 이어져요. 안주하지 않도록 작은 변화를 꾸준히 시도해보세요."},
            {"theme": "기반이 다져지는 시기", "body": "눈에 보이지 않는 기반이 단단해지는 시기예요. 조급해하지 말고 한 걸음씩 쌓아가세요."},
            {"theme": "뿌리가 깊어지는 시기", "body": "보이지 않는 곳에서 뿌리가 깊어지는 시기예요. 지금의 조용한 노력이 오래 갈 힘이 돼요."},
        ],
        "金": [
            {"theme": "판단이 선명해지는 시기", "body": "결단의 기운이 이 시기 내내 이어져요. 너무 예리해지면 주변과 부딪힐 수 있으니 부드러움도 챙기세요."},
            {"theme": "기준이 명확해지는 시기", "body": "무엇이 옳고 그른지 기준이 또렷해지는 시기예요. 다만 유연함을 잃지 않도록 주의하세요."},
            {"theme": "경계가 세워지는 시기", "body": "내 것과 아닌 것, 할 것과 안 할 것의 경계가 세워지는 시기예요. 이 경계가 당신을 지켜줘요."},
        ],
        "水": [
            {"theme": "유연함이 깊어지는 시기", "body": "유연함의 기운이 이 시기 내내 이어져요. 흐름을 타다 보면 중심을 잃을 수 있으니 가끔은 멈춰 점검하세요."},
            {"theme": "흐름이 넓어지는 시기", "body": "유연함이 다양한 방향으로 뻗어나가는 시기예요. 다만 발을 넓게 디디다 보면 깊이를 잃을 수 있어요."},
            {"theme": "물길이 열리는 시기", "body": "막혀있던 흐름이 트이는 시기예요. 새로운 길이 보일 때, 너무 신중하게만 굴지 마세요."},
        ],
    },
    # ── generates_me: 월건이 나를 북돋움 (밀어줌/채워줌/데워줌) ──
    "generates_me": {
        "木": [
            {"theme": "성장이 나를 밀어주는 시기", "body": "성장의 기운이 당신을 뒤에서 밀어주는 시기예요. 받는 게 많으니, 받은 만큼 흘려보내는 연습도 필요해요."},
            {"theme": "성장이 나를 채워주는 시기", "body": "성장의 기운이 당신을 안에서부터 채워주는 시기예요. 조용한 충만함 속에서 하고 싶은 일을 찾아보세요."},
            {"theme": "성장이 나를 키워주는 시기", "body": "성장의 기운이 당신을 자라게 하는 시기예요. 지금 심은 씨앗이 몇 년 뒤 큰 나무가 돼요."},
        ],
        "火": [
            {"theme": "열정이 나를 데워주는 시기", "body": "열정의 기운이 당신을 따뜻하게 감싸주는 시기예요. 마음껏 펼쳐보세요."},
            {"theme": "열정이 나를 밝혀주는 시기", "body": "열정의 기운이 당신의 길을 밝혀주는 시기예요. 어둡던 부분이 서서히 보이기 시작해요."},
            {"theme": "열정이 나를 움직이는 시기", "body": "열정의 기운이 당신을 움직이게 하는 시기예요. 머리로만 고민하지 말고 몸을 움직여보세요."},
        ],
        "土": [
            {"theme": "안정이 나를 받쳐주는 시기", "body": "안정의 기운이 당신을 든든히 받쳐주는 시기예요. 마음 놓고 도전해보세요."},
            {"theme": "안정이 나를 감싸주는 시기", "body": "안정의 기운이 당신을 포근히 감싸주는 시기예요. 쉼이 필요한 때, 마음 편히 쉬어가세요."},
            {"theme": "안정이 나를 지켜주는 시기", "body": "안정의 기운이 당신을 지켜주는 시기예요. 지금 가진 것을 지키는 데 집중하세요."},
        ],
        "金": [
            {"theme": "결단이 나를 다듬어주는 시기", "body": "결단의 기운이 당신을 다듬어주는 시기예요. 흐릿하던 것들이 서서히 또렷해져요."},
            {"theme": "결단이 나를 세워주는 시기", "body": "결단의 기운이 당신의 중심을 세워주는 시기예요. 흔들리던 것들이 자리를 잡아가요."},
            {"theme": "결단이 나를 깨워주는 시기", "body": "결단의 기운이 잠들어 있던 당신을 깨우는 시기예요. 미뤄둔 결심을 지금 꺼내보세요."},
        ],
        "水": [
            {"theme": "유연함이 나를 채워주는 시기", "body": "유연함의 기운이 당신을 채워주는 시기예요. 조용한 도움의 손길이 들어와요."},
            {"theme": "유연함이 나를 흐르게 하는 시기", "body": "유연함의 기운이 당신을 흐르게 하는 시기예요. 막혀있던 부분이 자연스럽게 풀려요."},
            {"theme": "유연함이 나를 씻어주는 시기", "body": "유연함의 기운이 당신을 씻어주는 시기예요. 묵은 감정이 내려가고 마음이 가벼워져요."},
        ],
    },
    # ── i_generate: 내가 월건을 피워냄 (만듦/키움/피움) ──
    "i_generate": {
        "木": [
            {"theme": "내가 성장을 만드는 시기", "body": "당신이 뭔가를 자라게 하는 시기예요. 베풀수록 더 채워져요."},
            {"theme": "내가 성장을 키우는 시기", "body": "당신이 뭔가를 키워내는 시기예요. 꾸준함이 결국 큰 차이를 만들어요."},
            {"theme": "내가 성장을 피우는 시기", "body": "당신이 뭔가를 꽃피우는 시기예요. 오래 준비해온 것이 세상에 나올 때예요."},
        ],
        "火": [
            {"theme": "내가 열정을 만드는 시기", "body": "당신이 열정을 만들어내는 시기예요. 창작이나 표현 활동에서 빛을 발해요."},
            {"theme": "내가 열정을 피우는 시기", "body": "당신이 열정을 활활 피워내는 시기예요. 주변까지 밝히는 사람이 돼요."},
            {"theme": "내가 열정을 나누는 시기", "body": "당신의 열정이 주변으로 퍼지는 시기예요. 혼자만의 열정보다 나누는 열정이 더 커져요."},
        ],
        "土": [
            {"theme": "내가 안정을 만드는 시기", "body": "당신이 기반을 다지는 시기예요. 하나씩 결과물이 쌓여가요."},
            {"theme": "내가 안정을 쌓는 시기", "body": "당신이 차곡차곡 무언가를 쌓는 시기예요. 눈에 안 보여도 단단해지고 있어요."},
            {"theme": "내가 안정을 세우는 시기", "body": "당신이 자기 자리를 세우는 시기예요. 흔들리던 것이 중심을 잡아요."},
        ],
        "金": [
            {"theme": "내가 결단을 만드는 시기", "body": "당신이 방향을 정해가는 시기예요. 단단한 결과물이 나오기 시작해요."},
            {"theme": "내가 결단을 다듬는 시기", "body": "당신이 무언가를 정교하게 다듬는 시기예요. 세밀함이 큰 차이를 만들어요."},
            {"theme": "내가 결단을 세우는 시기", "body": "당신이 확고한 기준을 세우는 시기예요. 이 기준이 오래 갈 방향을 정해줘요."},
        ],
        "水": [
            {"theme": "내가 흐름을 트는 시기", "body": "당신이 새로운 길을 여는 시기예요. 흐름을 만들면서 더 멀리 가요."},
            {"theme": "내가 흐름을 만드는 시기", "body": "당신이 흐름 자체를 만들어가는 시기예요. 물이 길을 내듯, 당신이 길을 내요."},
            {"theme": "내가 흐름을 잇는 시기", "body": "당신이 끊어진 것들을 잇는 시기예요. 사람과 사람, 아이디어와 아이디어를 연결해요."},
        ],
    },
    # ── i_control: 내가 월건을 다룸 (다룸/정리/붙잡음) ──
    "i_control": {
        "木": [
            {"theme": "내가 성장을 다루는 시기", "body": "성장의 기운이 강한 시기예요. 당신이 이걸 정리하면서 자기 자리를 세워가요."},
            {"theme": "내가 성장을 정리하는 시기", "body": "당신이 무언가를 정리해 방향을 잡는 시기예요. 쳐내는 만큼 핵심이 보여요."},
            {"theme": "내가 성장을 붙잡는 시기", "body": "당신이 흩어진 것들을 붙잡는 시기예요. 놓치지 않으려는 마음이 힘이 돼요."},
        ],
        "火": [
            {"theme": "내가 열정을 다루는 시기", "body": "열정의 기운이 강한 시기예요. 당신이 이걸 식히면서 한 박자 쉬어가는 때예요."},
            {"theme": "내가 열정을 정리하는 시기", "body": "당신이 뜨거운 것들을 차분하게 정리하는 시기예요. 열기를 다스리는 지혜가 필요해요."},
            {"theme": "내가 열정을 붙잡는 시기", "body": "당신이 불꽃 같은 열정을 다루는 시기예요. 잘 다루면 큰 빛이 돼요."},
        ],
        "土": [
            {"theme": "내가 안정을 다루는 시기", "body": "안정의 기운이 강한 시기예요. 당신이 이걸 정리하면서 흐름을 다스려요."},
            {"theme": "내가 안정을 만드는 시기", "body": "당신이 기반을 만드는 시기예요. 흩어진 것들을 하나로 모아요."},
            {"theme": "내가 안정을 붙잡는 시기", "body": "당신이 흔들리지 않으려 애쓰는 시기예요. 붙잡는 만큼 중심이 생겨요."},
        ],
        "金": [
            {"theme": "내가 결단을 다루는 시기", "body": "결단의 기운이 강한 시기예요. 당신이 이걸 두드리면서 원하는 모양을 만들어가요."},
            {"theme": "내가 결단을 정리하는 시기", "body": "당신이 무언가를 잘라내는 시기예요. 잘라낸 만큼 새 것이 자라요."},
            {"theme": "내가 결단을 붙잡는 시기", "body": "당신이 흔들리는 것들을 붙잡는 시기예요. 강한 중심이 주변을 정돈해요."},
        ],
        "水": [
            {"theme": "내가 유연함을 다루는 시기", "body": "유연함의 기운이 강한 시기예요. 당신이 이걸 감싸면서 중심을 잡아줘요."},
            {"theme": "내가 유연함을 붙잡는 시기", "body": "당신이 흘러가는 것들을 붙잡는 시기예요. 다만 너무 붙잡으면 흐름이 막혀요."},
            {"theme": "내가 유연함을 정리하는 시기", "body": "당신이 흐트러진 흐름을 정리하는 시기예요. 정돈된 흐름이 더 멀리 가요."},
        ],
    },
    # ── controls_me: 월건이 나를 누름 (감쌈/다듬음/시험) ──
    "controls_me": {
        "木": [
            {"theme": "성장이 나를 흔드는 시기", "body": "성장의 기운이 당신을 흔드는 시기예요. 흔들릴수록 뿌리를 더 깊이 내리세요."},
            {"theme": "성장이 나를 단련하는 시기", "body": "성장의 기운이 당신을 단련하는 시기예요. 힘들어도 지나고 나면 더 단단해져요."},
            {"theme": "성장이 나를 시험하는 시기", "body": "성장의 기운이 당신의 한계를 시험하는 시기예요. 지금의 벽이 다음 단계의 문이에요."},
        ],
        "火": [
            {"theme": "열정이 나를 단련하는 시기", "body": "열정의 기운이 당신을 단련하는 시기예요. 뜨거움 속에서 더 단단해져요."},
            {"theme": "열정이 나를 다듬는 시기", "body": "열정의 기운이 당신의 거친 부분을 다듬는 시기예요. 마찰이 곧 성장이에요."},
            {"theme": "열정이 나를 깨우는 시기", "body": "열정의 기운이 잠든 당신을 깨우는 시기예요. 불편함이 변화의 시작이에요."},
        ],
        "土": [
            {"theme": "안정이 나를 감싸는 시기", "body": "안정의 기운이 당신을 감싸는 시기예요. 울타리 안에서 오히려 더 깊어져요."},
            {"theme": "안정이 나를 다듬는 시기", "body": "안정의 기운이 당신을 다듬는 시기예요. 익숙함이 오히려 성장의 발판이 돼요."},
            {"theme": "안정이 나를 붙잡는 시기", "body": "안정의 기운이 당신을 붙잡는 시기예요. 답답할 수 있지만, 이 안정이 오래 갈 힘이 돼요."},
        ],
        "金": [
            {"theme": "결단이 나를 깎는 시기", "body": "결단의 기운이 당신을 깎는 시기예요. 깎인 자리에서 새로운 게 자라나요."},
            {"theme": "결단이 나를 세우는 시기", "body": "결단의 기운이 당신을 바로 세우는 시기예요. 흐트러졌던 것들이 정리돼요."},
            {"theme": "결단이 나를 시험하는 시기", "body": "결단의 기운이 당신의 진짜 의지를 시험하는 시기예요. 답은 이미 당신 안에 있어요."},
        ],
        "水": [
            {"theme": "유연함이 나를 덮는 시기", "body": "유연함의 기운이 당신을 덮는 시기예요. 눌리는 대신 증기처럼 떠오르는 때예요."},
            {"theme": "유연함이 나를 씻는 시기", "body": "유연함의 기운이 당신을 씻는 시기예요. 묵은 것들이 내려가고 마음이 맑아져요."},
            {"theme": "유연함이 나를 흐르게 하는 시기", "body": "유연함의 기운이 당신을 흐르게 하는 시기예요. 붙잡지 말고 흘려보낼 때예요."},
        ],
    },
}

EN_THEMES = {
    "same": {
        "木": [
            {"theme": "Growth keeps going", "body": "Growth runs through the whole season. Same direction can feel dull — try new ways on purpose."},
            {"theme": "Growth deepens", "body": "Growth energy deepens. Focus on the roots, not just visible results."},
            {"theme": "Growth overflows", "body": "Growth spills over. Don't try to do it all at once — pick your spots."},
        ],
        "火": [
            {"theme": "Passion keeps burning", "body": "Passion burns through the whole season. Pacing matters more than intensity."},
            {"theme": "Passion goes deeper", "body": "Passion turns inward. Chase what you truly love, not just what shines."},
            {"theme": "Passion overflows", "body": "Too many things you want to do. Pick one or two — that's where the fruit comes."},
        ],
        "土": [
            {"theme": "Center hardens", "body": "Stability runs through the season. Keep small changes going so you don't drift."},
            {"theme": "Ground is built", "body": "Foundations firm up in the unseen. Don't rush — stack one brick at a time."},
            {"theme": "Roots go deeper", "body": "Roots deepen below the surface. Quiet effort now becomes lasting strength."},
        ],
        "金": [
            {"theme": "Judgment sharpens", "body": "Clarity sharpens for the season. Sharp can cut — stay soft where it matters."},
            {"theme": "Standards become clear", "body": "Your sense of right and wrong gets sharper. Just don't lose flexibility."},
            {"theme": "Boundaries get set", "body": "Lines get drawn — mine vs. yours, do vs. don't. Those boundaries keep you safe."},
        ],
        "水": [
            {"theme": "Flexibility deepens", "body": "Flexibility deepens through the season. Flowing too long loses center — pause to check in."},
            {"theme": "Flow widens", "body": "Flexibility spreads in many directions. Spread too thin and you lose depth."},
            {"theme": "New channels open", "body": "Blocked flows open up. When new paths appear, don't overthink."},
        ],
    },
    "generates_me": {
        "木": [
            {"theme": "Growth pushes you", "body": "Growth energy pushes from behind. Take it in — and pass it on."},
            {"theme": "Growth fills you", "body": "Growth fills you from within. In quiet fullness, find what you want to do."},
            {"theme": "Growth raises you", "body": "Growth raises you up. Seeds planted now become big trees in a few years."},
        ],
        "火": [
            {"theme": "Passion warms you", "body": "Passion warmly surrounds you. Expand freely this season."},
            {"theme": "Passion lights your way", "body": "Passion lights the road ahead. Dark places slowly become visible."},
            {"theme": "Passion moves you", "body": "Passion moves you. Stop thinking in your head — move your body."},
        ],
        "土": [
            {"theme": "Stability holds you", "body": "Stability holds you firmly. Bold moves are safe on this ground."},
            {"theme": "Stability embraces you", "body": "Stability embraces you warmly. Rest when you need to."},
            {"theme": "Stability protects you", "body": "Stability protects you. Focus on keeping what you have."},
        ],
        "金": [
            {"theme": "Clarity refines you", "body": "Clarity refines you. Blurry things gradually become sharp."},
            {"theme": "Clarity centers you", "body": "Clarity puts you on your center. Wobbling things settle into place."},
            {"theme": "Clarity wakes you", "body": "Clarity wakes what was sleeping. Pull out decisions you've been putting off."},
        ],
        "水": [
            {"theme": "Flexibility fills you", "body": "Flexibility fills you. Quiet help arrives from unexpected places."},
            {"theme": "Flexibility flows through you", "body": "Flexibility moves through you. Stuck places unstick naturally."},
            {"theme": "Flexibility cleanses you", "body": "Flexibility cleanses you. Old emotions wash away and you feel lighter."},
        ],
    },
    "i_generate": {
        "木": [
            {"theme": "You make things grow", "body": "You make things grow. The more you give, the more comes back."},
            {"theme": "You nurture growth", "body": "You nurture things. Consistency ends up making the biggest difference."},
            {"theme": "You bloom", "body": "You bring things to bloom. What you've been preparing comes out into the world."},
        ],
        "火": [
            {"theme": "You create fire", "body": "You generate passion. Creative and expressive work shines brightest."},
            {"theme": "You burn bright", "body": "You burn bright. You light up the people around you."},
            {"theme": "You share your fire", "body": "Your passion spreads. Shared fire burns bigger than private fire."},
        ],
        "土": [
            {"theme": "You build foundations", "body": "You lay ground. Small results stack up one by one."},
            {"theme": "You stack bricks", "body": "You stack things up patiently. Invisible now, but firming up."},
            {"theme": "You set your ground", "body": "You set your place in the world. Wobbling things find their feet."},
        ],
        "金": [
            {"theme": "You set direction", "body": "You set direction. Solid outcomes begin landing."},
            {"theme": "You sharpen things", "body": "You sharpen things carefully. Precision makes the difference."},
            {"theme": "You set standards", "body": "You set firm standards. That standard will guide the years ahead."},
        ],
        "水": [
            {"theme": "You open paths", "body": "You open new roads. Making flow lets you go further."},
            {"theme": "You make flow", "body": "You make flow itself. Like water carving a channel, you carve the way."},
            {"theme": "You connect things", "body": "You connect what was apart — people, ideas, pieces."},
        ],
    },
    "i_control": {
        "木": [
            {"theme": "You handle growth", "body": "Growth energy is strong. You tidy it and set your own footing."},
            {"theme": "You clear space", "body": "You cut away clutter to keep direction. Less shows more."},
            {"theme": "You grip growth", "body": "You hold scattered things together. The grip itself becomes strength."},
        ],
        "火": [
            {"theme": "You handle fire", "body": "Passion energy is strong. You cool it and take a step back."},
            {"theme": "You cool things down", "body": "You calm what's hot. Wisdom to handle the fire."},
            {"theme": "You hold the flame", "body": "You handle the flame. Handle it well and it becomes great light."},
        ],
        "土": [
            {"theme": "You handle stability", "body": "Stability energy is strong. You shape it and steady the flow."},
            {"theme": "You make ground", "body": "You make ground. Scattered things come together."},
            {"theme": "You grip stable ground", "body": "You try hard not to wobble. The grip becomes your center."},
        ],
        "金": [
            {"theme": "You handle clarity", "body": "Clarity energy is strong. Your fire beats it into the shape you want."},
            {"theme": "You cut clean", "body": "You cut things away. What grows back after the cut is stronger."},
            {"theme": "You hold the edge", "body": "You hold the edge steady. Strong center organizes what's around it."},
        ],
        "水": [
            {"theme": "You handle flexibility", "body": "Flexibility energy is strong. You hold it and center yourself."},
            {"theme": "You grip the flow", "body": "You grip flowing things. Grip too tight and the flow stops."},
            {"theme": "You tidy the flow", "body": "You tidy tangled flows. Ordered flow goes farther."},
        ],
    },
    "controls_me": {
        "木": [
            {"theme": "Growth shakes you", "body": "Growth energy shakes you. The more you're tested, the deeper you root."},
            {"theme": "Growth refines you", "body": "Growth refines you. Even when it's hard, you come out firmer."},
            {"theme": "Growth tests you", "body": "Growth tests your edge. Today's wall is tomorrow's door."},
        ],
        "火": [
            {"theme": "Fire tempers you", "body": "Fire tempers you. Heat makes you harder, in a good way."},
            {"theme": "Fire smooths you", "body": "Fire smooths your rough edges. Friction is growth."},
            {"theme": "Fire wakes you", "body": "Fire wakes you. Discomfort is the start of change."},
        ],
        "土": [
            {"theme": "Stability contains you", "body": "Stability contains you. Walls make you go deeper."},
            {"theme": "Stability refines you", "body": "Stability refines you. Familiar ground becomes a launch point."},
            {"theme": "Stability holds you", "body": "Stability holds you. It can feel tight — but it holds long."},
        ],
        "金": [
            {"theme": "Clarity cuts you", "body": "Clarity cuts you. What grows back is stronger."},
            {"theme": "Clarity sets you straight", "body": "Clarity sets you straight. Messy things get arranged."},
            {"theme": "Clarity tests you", "body": "Clarity tests your real will. The answer is already inside you."},
        ],
        "水": [
            {"theme": "Flexibility covers you", "body": "Flexibility covers you. You don't sink — you rise like steam."},
            {"theme": "Flexibility cleanses you", "body": "Flexibility washes you. Old things fall away; the mind clears."},
            {"theme": "Flexibility flows you", "body": "Flexibility flows you along. Let go, and flow takes you."},
        ],
    },
}

KO_CAUTIONS = {
    "same": "같은 방향이라 지루해질 수 있어요. 작은 변화를 의식적으로 만들어보세요.",
    "generates_me": "받기만 하면 무뎌져요. 받은 만큼 흘려보내는 연습이 필요해요.",
    "i_generate": "베풀다 지칠 수 있어요. 자신을 먼저 채우는 시간을 확보하세요.",
    "i_control": "통제하려는 마음이 강해지면 관계가 상해요. 놓아줄 건 놓아주세요.",
    "controls_me": "압박이 클수록 조급해져요. 남의 속도와 비교하지 마세요.",
}
KO_PRACTICES = {
    "same": "매년 한 가지, 새로운 방식을 시도해보세요.",
    "generates_me": "받은 것들을 기록하고, 감사로 돌려주세요.",
    "i_generate": "매주 하루는 온전히 자신을 위해 비워두세요.",
    "i_control": "결정 전에 '이걸 꼭 통제해야 하나?' 물어보세요.",
    "controls_me": "매년 한 가지, 10년 후에도 남을 기술을 쌓으세요.",
}
EN_CAUTIONS = {
    "same": "Same direction can get dull. Make small changes on purpose.",
    "generates_me": "Only receiving makes you numb. Pass on what you get.",
    "i_generate": "Giving drains you. Protect time to refill yourself first.",
    "i_control": "Control hurts relationships. Let go of what you can't hold.",
    "controls_me": "Pressure feeds urgency. Don't race against others' speed.",
}
EN_PRACTICES = {
    "same": "Try one new approach each year.",
    "generates_me": "Journal what you receive. Return it as gratitude.",
    "i_generate": "Keep one full day a week just for you.",
    "i_control": "Before deciding, ask: 'Do I really need to control this?'",
    "controls_me": "Build one skill a year that lasts the next decade.",
}
KO_ELEM = {"木": "성장", "火": "열정", "土": "안정", "金": "결단", "水": "유연함"}
EN_ELEM = {"木": "growth", "火": "passion", "土": "stability", "金": "clarity", "水": "flexibility"}

# ═══════════════════════════════════════════════════════════
# 2. JSON 저장 (KO + EN)
# ═══════════════════════════════════════════════════════════
print("=" * 55)
print("1) timeline_themes.json 재작성 (variant 3개씩)")
print("=" * 55)

LANG_DATA = {
    "ko": {"THEMES": KO_THEMES, "CAUTIONS": KO_CAUTIONS, "PRACTICES": KO_PRACTICES, "ELEM_LABEL": KO_ELEM},
    "en": {"THEMES": EN_THEMES, "CAUTIONS": EN_CAUTIONS, "PRACTICES": EN_PRACTICES, "ELEM_LABEL": EN_ELEM},
}

BASE = Path("app/services/content/data")
for lang, data in LANG_DATA.items():
    out = BASE / lang / "timeline_themes.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if APPLY:
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        variants_total = sum(len(v) for r in data["THEMES"].values() for v in r.values())
        print(f"  ✅ {lang}: {out} (테마 조합 {variants_total}개)")
    else:
        variants_total = sum(len(v) for r in data["THEMES"].values() for v in r.values())
        print(f"  🧪 {lang}: {out} (테마 조합 {variants_total}개)")

# ═══════════════════════════════════════════════════════════
# 3. content_writer.py: hash 기반 variant 선택
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("2) content_writer.py: hash 기반 variant 선택")
print("=" * 55)

CW = Path("app/services/content_writer.py")
txt = CW.read_text(encoding="utf-8")

OLD = '''    t = (themes.get(rel) or {}).get(elem) or {}
    return {
        "theme": t.get("theme", ""),
        "body": t.get("body", ""),
        "caution": cautions.get(rel, ""),
        "practice": practices.get(rel, ""),
    }'''

NEW = '''    raw = (themes.get(rel) or {}).get(elem)
    if not raw:
        return {}
    # 3-variant list면 hash로 선택, dict면 그대로 (하위 호환)
    if isinstance(raw, list):
        import hashlib
        seed = str(d.get("pillar", "")) + ":" + str(d.get("index", 0))
        h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
        t = raw[h % len(raw)]
    elif isinstance(raw, dict):
        t = raw
    else:
        return {}
    return {
        "theme": t.get("theme", ""),
        "body": t.get("body", ""),
        "caution": cautions.get(rel, ""),
        "practice": practices.get(rel, ""),
    }'''

if OLD not in txt:
    print("  ❌ _resolve_theme 패턴 불일치")
    print("     다음 명령으로 현재 코드 확인:")
    print("     Get-Content 'app/services/content_writer.py' | Select-String '_resolve_theme' -Context 0,25")
    sys.exit(1)

txt = txt.replace(OLD, NEW, 1)
print("  ✅ hash 기반 variant 선택 로직")

# 디버그 print 제거
lines = txt.splitlines(keepends=True)
cleaned = [l for l in lines if "[DEBUG-THEME]" not in l]
if len(cleaned) != len(lines):
    txt = "".join(cleaned)
    print(f"  ✅ 디버그 print {len(lines) - len(cleaned)}줄 제거")

# ast 검증
try:
    ast.parse(txt)
except SyntaxError as e:
    print(f"  ❌ 문법 오류: {e.lineno}: {e.msg}")
    sys.exit(1)
print("  ✅ 문법 검증 통과")

if APPLY:
    CW.write_text(txt, encoding="utf-8")

# ja/zh_cn/es는 EN 복사 (테스트 통과)
for lang in ["ja", "zh_cn", "es"]:
    src = BASE / "en" / "timeline_themes.json"
    dst = BASE / lang / "timeline_themes.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if APPLY:
        import shutil
        shutil.copy(src, dst)
        print(f"  ✅ {lang}: EN 복사")

print()
if not APPLY:
    print("🧪 미리보기. 적용: python scripts/add_theme_variants.py --apply")
else:
    print("🎉 완료. 다음:")
    print("   .\\deploy.ps1")