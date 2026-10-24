#!/usr/bin/env python3
"""
60일주 + intensity 오버레이 콘텐츠 레이어 적용 스크립트.

사용:
    python scripts/apply_pillar_layer.py --all
    python scripts/apply_pillar_layer.py --step overlay
    python scripts/apply_pillar_layer.py --step pilot
    python scripts/apply_pillar_layer.py --step tests
    python scripts/apply_pillar_layer.py --step stubs
    python scripts/apply_pillar_layer.py --all --force   # 이미 있어도 덮어쓰기

각 단계는 멱등(idempotent). 파일 수정 전 .bak.<timestamp> 자동 백업.
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
TESTS = ROOT / "tests"


# ─────────────────────────────────────────────────────
# 공통 유틸
# ─────────────────────────────────────────────────────
def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _backup(path: Path) -> Path:
    bak = path.with_suffix(path.suffix + f".bak.{_ts()}")
    shutil.copy2(path, bak)
    return bak


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    """들여쓰기 2, 유니코드 그대로 (기존 파일과 호환)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ─────────────────────────────────────────────────────
# STEP 1: INTENSITY_OVERLAY 추가
# ─────────────────────────────────────────────────────
OVERLAY = {
    "ko": {
        "SELF_SOURCED": {
            "voice": "당신의 에너지는 안에서부터 차오릅니다. 누군가 인정해 주지 않아도 스스로 방향을 정하고 움직일 수 있는 사람이에요. 이 자기충전의 힘은 큰 무기지만, 스스로에게 요구하는 기준이 너무 높아지면 스스로를 소진시키기 쉽습니다. 아래 이야기들은 당신 안에서 출발하는 그 힘이 어떻게 구체적으로 드러나는지를 그려봅니다.",
            "advice_addon": [
                "이번 주에 스스로 결정한 일 하나를 돌아보세요. 누구의 승인 없이도 잘 굴러갔나요?",
                "자기 자신에게 요구하는 기준을 하나 낮춰보세요. 그게 번아웃 예방입니다.",
            ],
        },
        "BALANCED_CORE": {
            "voice": "당신의 에너지는 안과 밖 사이에서 균형을 잡습니다. 필요하면 스스로 나아가고, 필요하면 주변과 호흡을 맞출 줄 아는 사람이에요. 이 균형은 흔치 않은 재능이지만, '어느 쪽도 아닌 상태'로 흐르면 정체된 느낌이 들 수 있습니다. 아래 이야기들은 그 균형이 일상에서 어떻게 작동하는지를 그려봅니다.",
            "advice_addon": [
                "이번 주에 '내가 하고 싶은 것'과 '지금 필요한 것'을 한 번씩 구분해 보세요.",
                "균형은 선택의 반복입니다. 작은 선택에서 어느 쪽에 힘을 실었는지 기록해 보세요.",
            ],
        },
        "ENVIRONMENT_TUNED": {
            "voice": "당신의 에너지는 주변 환경과의 관계에서 피어납니다. 맞는 사람과 맞는 조건을 만나면 놀랄 만큼 깊어지고, 그렇지 않은 곳에서는 서서히 옅어지죠. 이 예민함은 약함이 아니라 필터입니다. 아래 이야기들은 어떤 조건에서 당신이 가장 나다워지는지를 그려봅니다.",
            "advice_addon": [
                "이번 주에 당신을 살아나게 하는 사람·장소·상황을 세 가지 적어보세요.",
                "지금 있는 환경이 당신에게 맞는지, 아니면 이미 졸업했는지 스스로에게 물어보세요.",
            ],
        },
    },
    "en": {
        "SELF_SOURCED": {
            "voice": "Your energy rises from within. You can set a direction and move on it without waiting for someone else's approval. This self-sourced drive is a major strength — but when the bar you set for yourself climbs too high, it quietly turns into burnout. The sections below describe how that internal engine shows up in concrete ways.",
            "advice_addon": [
                "This week, look back at one decision you made on your own. Did it hold up without external approval?",
                "Lower one standard you hold yourself to. That's how you prevent burnout.",
            ],
        },
        "BALANCED_CORE": {
            "voice": "Your energy balances between inside and out. You move on your own when needed, and you sync with others when the moment calls for it. That calibration is a rare gift — but when it drifts into 'neither side fully,' it can feel like standing still. The sections below describe how that balance actually works day to day.",
            "advice_addon": [
                "This week, separate 'what I want to do' from 'what this moment actually needs' — once each.",
                "Balance is built through repeated choices. Note which side you leaned into in your small decisions.",
            ],
        },
        "ENVIRONMENT_TUNED": {
            "voice": "Your energy blooms in relationship with your environment. Around the right people and conditions, you deepen remarkably; in the wrong ones, you slowly fade. That sensitivity isn't fragility — it's a filter. The sections below describe the conditions where you are most fully yourself.",
            "advice_addon": [
                "This week, write down three people, places, or situations that make you feel alive.",
                "Ask yourself whether your current environment still fits you, or whether you've already outgrown it.",
            ],
        },
    },
}


def step_overlay(force: bool = False) -> None:
    print("\n=== [1/4] INTENSITY_OVERLAY 추가 ===")
    for lang in ("ko", "en"):
        path = DATA / lang / "core.json"
        if not path.exists():
            print(f"  ❌ {path} 없음, 건너뜀")
            continue

        data = _read_json(path)
        if "INTENSITY_OVERLAY" in data and not force:
            print(f"  ⏭️  [{lang}] 이미 INTENSITY_OVERLAY 있음 (건너뜀, --force로 덮어쓰기)")
            continue

        bak = _backup(path)
        data["INTENSITY_OVERLAY"] = OVERLAY[lang]
        _write_json(path, data)
        print(f"  ✅ [{lang}] INTENSITY_OVERLAY 추가 (백업: {bak.name})")


# ─────────────────────────────────────────────────────
# STEP 2: 파일럿 일주 파일 (丙申, 庚午)
# ─────────────────────────────────────────────────────
PILOT_PILLARS = {
    "ko": {
        "丙申": {
            "pillar": "丙申",
            "hero": "당신은 바위 위에 내리쬐는 태양입니다. 뜨거운 빛을 뿜어내면서도, 발밑은 단단한 광물로 받쳐져 있죠.",
            "narrative": [
                "당신 안에는 두 개의 서로 다른 결이 함께 흐릅니다. 하나는 따뜻함과 표현의 결 — 사람을 끌어당기고, 분위기를 밝히고, 함께하고 싶게 만드는 힘이지요. 다른 하나는 예리함과 구조의 결 — 흐릿한 것을 잘라내고, 경계를 정확히 그리고, 진짜와 가짜를 구분하는 힘입니다. 이 둘이 한 사람 안에서 뒤섞여 있다는 사실이, 당신을 설명하기 어려운 사람으로 만듭니다.",
                "관계에서는 다정한데 어딘가 선명합니다. 상대를 따뜻하게 감싸다가도, 선을 넘으면 단호하게 잘라내죠. 일에서는 열정적이면서도 정밀합니다. 큰 그림을 그리며 사람들을 이끌다가도, 디테일 하나를 놓치지 않고 집어냅니다. 이 이중성 덕분에 당신은 '부드러운 사람'과 '무서운 사람'이라는 두 가지 평가를 동시에 받곤 합니다. 둘 다 당신입니다.",
                "이 두 결을 한쪽으로 통일하려 하지 마세요. 대신 서로에게 자리를 내주는 연습을 해보세요. 열정이 앞서는 순간에는 예리함에게 '이게 진짜 맞는 방향인가?'를 물어보고, 예리함이 앞서는 순간에는 열정에게 '이걸 함께할 사람은 누구인가?'를 물어보세요. 이 두 목소리가 번갈아 나올 때, 당신의 결단은 더 오래갑니다.",
                "당신의 그림자는 '너무 빨리 잘라내는 것'과 '너무 오래 따뜻하게 감싸는 것' 사이를 오갑니다. 상처받을까 봐 선을 먼저 긋거나, 관계를 지키려다 정작 자신을 소진시키죠. 이 두 그림자를 다루는 열쇠는 '지금 이 관계에서 내가 지키고 싶은 것'을 말로 꺼내는 것입니다. 잘라야 할 것과 안아야 할 것을 스스로에게 설명할 수 있을 때, 당신의 이중성은 더 이상 흔들림이 아니라 깊이가 됩니다.",
            ],
            "shadows": [
                "상대가 미처 말을 꺼내기 전에 관계의 선을 먼저 긋고, 나중에 후회할 때가 있습니다.",
                "다정함으로 모든 갈등을 덮으려다, 정작 자신의 서운함을 오래 묵혀둡니다.",
                "예리함이 앞서면 말이 칼이 됩니다. 옳은 말이지만 상처가 되는 순간을 알아채세요.",
            ],
            "advice": [
                "결정을 내리기 전에 스스로에게 물어보세요. '이건 열정이 앞선 건가, 예리함이 앞선 건가?'",
                "서운함이 생기면 24시간 안에 꺼내보세요. 묵혀두면 예리함이 칼이 됩니다.",
                "이번 주에 다정함과 단호함을 번갈아 써야 하는 상황을 하나 골라 연습해 보세요.",
                "당신이 감싸고 있는 사람 중 한 명에게, 당신도 위로가 필요하다고 말해보세요.",
            ],
            "keywords": ["따뜻한 결단", "예리한 다정함", "빛과 광물", "열정적 정밀"],
        },
        "庚午": {
            "pillar": "庚午",
            "hero": "당신은 제련로 안의 검입니다. 뜨거운 열기 속에서 오히려 더 선명해지는 사람이죠.",
            "narrative": [
                "당신은 원칙과 열정이 한 몸에 있는 사람입니다. 무언가를 결정할 때, 감정에 휘둘리기보다 기준에 따라 판단하려 하죠. 그런데 그 기준이 차가운 계산이 아니라 뜨거운 신념에서 나옵니다. '이건 옳다' 혹은 '이건 아니다'라는 판단이, 당신 안에서 먼저 불처럼 타오른 뒤에 언어로 나옵니다.",
                "일에서는 단호함이 먼저 보입니다. 흐릿한 논의를 잘라내고, 결정을 내리고, 책임을 집니다. 사람들은 당신에게 '결정해 주는 사람'의 역할을 맡기곤 합니다. 관계에서도 마찬가지예요. 애매한 것을 견디기 어려워하고, 좋아하는 것과 싫어하는 것을 분명히 표현합니다. 이 선명함이 사람들에게는 신뢰이자 때로는 부담입니다.",
                "당신의 과제는 '뜨거운 기준'과 '냉정한 판단'을 구분하는 것입니다. 뜨거운 기준은 당신의 가치관이고, 냉정한 판단은 그 가치관을 실행하는 도구예요. 두 개를 섞으면 옳은 말이 상처가 되고, 두 개를 분리하면 단호함이 존중으로 바뀝니다. 결정을 내리기 전에 '이건 내가 옳다고 믿는 것인가, 아니면 지금 이 상황에서 가장 정확한 판단인가?'를 물어보세요.",
                "이 감각이 자리 잡으면, 당신의 강렬함은 사람들을 밀어내는 힘이 아니라 끌어당기는 중력이 됩니다. 원칙을 지키면서도 사람을 살피는 사람, 뜨거운 열정을 품으면서도 차분하게 실행하는 사람 — 이게 성숙한 庚午의 모습입니다. 그 방향으로 조금씩 걸어가면 됩니다.",
            ],
            "shadows": [
                "옳다는 확신이 강할 때, 상대의 입장을 들을 여지를 스스로 차단합니다.",
                "감정을 '판단'으로 포장해서 말할 때가 있습니다. 그건 기준이 아니라 서운함입니다.",
                "쉬지 않고 결정을 내리다 보면, 정작 자신의 피로를 인정하지 못합니다.",
            ],
            "advice": [
                "결정을 내리기 전에 '이건 내 가치관인가, 지금 이 상황의 최선인가?'를 한 번씩 구분해 보세요.",
                "이번 주에 상대의 의견을 끝까지 듣고 나서 판단하는 연습을 한 번 해보세요.",
                "결정 후에는 스스로에게 회복 시간을 주세요. 강한 결단 뒤에는 강한 휴식이 필요합니다.",
                "당신이 존경하는 사람 한 명에게, 최근의 고민을 털어놓아 보세요. 혼자 다 짊어질 필요 없습니다.",
            ],
            "keywords": ["뜨거운 원칙", "선명한 결단", "열정적 냉정", "책임의 무게"],
        },
    },
    "en": {
        "丙申": {
            "pillar": "丙申",
            "hero": "You're a sun above a stone. You radiate warmth from above while standing on something hard and clear beneath you.",
            "narrative": [
                "Two distinct threads run through you at once. One is warmth and expression — the pull that draws people in, brightens a room, and makes others want to be near you. The other is precision and structure — the ability to cut through blur, draw clean lines, and tell what's real from what isn't. Having both in one person is what makes you hard to describe.",
                "In relationships you're tender but distinct. You hold people warmly, but the moment a line is crossed, you cut with clarity. At work you're passionate and meticulous at once. You paint the big picture and lead people through it, then catch the one detail everyone else missed. This duality means you're often called both 'the soft one' and 'the scary one' — by different people, on the same day. Both are true.",
                "Don't try to unify these into one voice. Instead, practice giving each its turn. When passion is leading, ask the precise part of you, 'Is this really the right direction?' When precision is leading, ask the warm part, 'Who is this really for?' When those two voices alternate, your decisions last longer.",
                "Your shadow moves between 'cutting too soon' and 'warming for too long.' You draw boundaries early to avoid being hurt, or you keep softening to hold a relationship and end up exhausted. The key to both shadows is naming what you actually want to protect in this particular moment. When you can explain to yourself what to cut and what to hold, your duality stops being instability and becomes depth.",
            ],
            "shadows": [
                "You sometimes draw a line before the other person has had a chance to speak — and regret it later.",
                "You use warmth to smooth over conflict, then quietly carry the hurt for weeks.",
                "When your precision leads, your words can turn into knives. Right, but sharp.",
            ],
            "advice": [
                "Before a decision, ask: is passion leading, or precision?",
                "Say what's bothering you within 24 hours. Bury it, and precision sharpens into a blade.",
                "This week, pick one situation that calls for both warmth and firmness. Practice switching deliberately.",
                "Tell one of the people you're holding that you need holding too.",
            ],
            "keywords": ["warm resolve", "precise tenderness", "light and mineral", "passionate precision"],
        },
        "庚午": {
            "pillar": "庚午",
            "hero": "You're a blade inside a forge. The heat doesn't soften you — it makes you clearer.",
            "narrative": [
                "You're someone whose principles and passion live in the same body. When you decide something, you try to judge by a standard rather than by mood. But that standard isn't cold calculation — it comes from a conviction that burns hot. 'This is right' or 'this is not' ignites in you first, and only then becomes words.",
                "At work, what shows first is decisiveness. You cut through vague discussions, make calls, and take responsibility. People tend to hand you the role of 'the one who decides.' It's the same in relationships. You find ambiguity hard to sit with, and you express what you like and dislike clearly. That clarity reads to others as trust — and sometimes as pressure.",
                "Your task is to separate the 'hot standard' from the 'cool judgment.' The hot standard is your values. The cool judgment is the tool that executes those values. Mix them, and a right word becomes a wound. Separate them, and decisiveness becomes respect. Before a decision, ask: 'Is this what I believe is right, or is this the most accurate read of this situation right now?'",
                "Once that distinction settles in, your intensity stops pushing people away and starts pulling them in. Someone who holds principles and still sees people. Someone who carries heat and still executes calmly. That is the mature form of this pillar. You don't have to get there all at once — just keep walking in that direction.",
            ],
            "shadows": [
                "When your certainty is strong, you close the door on hearing the other person out.",
                "You sometimes dress up emotion as 'judgment.' That's not a standard — that's hurt.",
                "Deciding nonstop wears you down, and you often can't admit your own fatigue.",
            ],
            "advice": [
                "Before deciding, ask once: is this my values, or is this the best call for this specific moment?",
                "This week, listen all the way through before you judge — just once.",
                "Give yourself recovery time after a hard decision. Strong calls need strong rest.",
                "Tell one person you respect about something you're wrestling with. You don't have to carry it all alone.",
            ],
            "keywords": ["hot principles", "clear resolve", "passionate cool", "weight of responsibility"],
        },
    },
}


def step_pilot(force: bool = False) -> None:
    print("\n=== [2/4] 파일럿 일주 (丙申, 庚午) 생성 ===")
    for lang in ("ko", "en"):
        for pillar, data in PILOT_PILLARS[lang].items():
            path = DATA / lang / "core_pillars" / f"{pillar}.json"
            if path.exists() and not force:
                print(f"  ⏭️  [{lang}] {pillar} 이미 존재 (건너뜀, --force로 덮어쓰기)")
                continue
            if path.exists():
                _backup(path)
            _write_json(path, data)
            print(f"  ✅ [{lang}] {pillar}.json 생성")


# ─────────────────────────────────────────────────────
# STEP 3: 테스트 파일
# ─────────────────────────────────────────────────────
TEST_SOURCE = '''"""일주(60) + intensity(3) 콘텐츠 레이어 테스트."""
import pathlib

from app.engine.calculator import calculate_saju
from app.semantic.tagger import build_semantic_profile
from app.services.content_writer import write_core_section
from app.services.content.loader import load_pack

DATA_ROOT = (
    pathlib.Path(__file__).resolve().parents[1]
    / "app" / "services" / "content" / "data"
)


def _profile(birth_date, birth_time, gender="M"):
    return build_semantic_profile(calculate_saju(
        birth_date=birth_date, birth_time=birth_time,
        birth_location="seoul", correction_mode="lmt",
        jasi_boundary=23, gender=gender,
    ))


def test_1974_day_pillar_is_bingshen():
    p = _profile("1974-02-24", "05:30:00")
    assert p["pillars"]["day_pillar"] == "丙申"


def test_1990_day_pillar_is_gengwu():
    p = _profile("1990-05-05", "14:30:00")
    assert p["pillars"]["day_pillar"] == "庚午"


def test_bingshen_uses_pillar_content():
    p = _profile("1974-02-24", "05:30:00")
    sec = write_core_section(p, lang="ko")
    assert sec["pillar"] == "丙申"
    assert sec["content_source"] == "pillar"
    assert "바위 위" in sec["hero"] or "태양" in sec["hero"]


def test_gengwu_uses_pillar_content_en():
    p = _profile("1990-05-05", "14:30:00")
    sec = write_core_section(p, lang="en")
    assert sec["pillar"] == "庚午"
    assert sec["content_source"] == "pillar"
    assert "forge" in sec["hero"].lower()


def test_same_stem_different_pillar_differ():
    """丙申과 庚午는 다른 hero/narrative (스텁이 아닌 파일럿이므로)."""
    p74 = write_core_section(_profile("1974-02-24", "05:30:00"), lang="ko")
    p90 = write_core_section(_profile("1990-05-05", "14:30:00"), lang="ko")
    assert p74["pillar"] != p90["pillar"]
    assert p74["hero"] != p90["hero"]
    assert p74["narrative"] != p90["narrative"]


def test_missing_pillar_file_falls_back(monkeypatch):
    """일주 파일이 없으면 10×3 fallback으로 넘어가야 함."""
    import app.services.content_writer as cw
    original = cw.load_pack

    def patched(lang, section):
        if section.startswith("core_pillars/"):
            raise KeyError("simulated missing")
        return original(lang, section)

    monkeypatch.setattr(cw, "load_pack", patched)
    sec = write_core_section(_profile("1974-02-24", "05:30:00"), lang="ko")
    assert sec["content_source"] == "intensity_fallback"
    assert sec["intensity_label"] == "자기충전형"
    assert len(sec["narrative"]) >= 3


def test_intensity_voice_is_prepended():
    p = _profile("1974-02-24", "05:30:00")
    sec = write_core_section(p, lang="ko")
    overlay = load_pack("ko", "core")["INTENSITY_OVERLAY"]["SELF_SOURCED"]
    assert sec["narrative"][0] == overlay["voice"]


def test_intensity_advice_addon_included():
    p = _profile("1974-02-24", "05:30:00")
    sec = write_core_section(p, lang="ko")
    overlay = load_pack("ko", "core")["INTENSITY_OVERLAY"]["SELF_SOURCED"]
    for extra in overlay["advice_addon"]:
        assert extra in sec["advice"]


def test_cover_tagline_unchanged():
    """일주 파일럿이 tagline을 override하지 않아야 함 (기존 cover 테스트 보호)."""
    from app.services.content_writer import _build_cover
    cover = _build_cover(_profile("1974-02-24", "05:30:00"), "en")
    assert cover["archetype"]["tagline"] == "You warm rooms by existing in them."
    assert cover["archetype"]["name"] == "The Radiator"


def test_intensity_overlay_complete_in_both_langs():
    """3개 intensity overlay가 두 언어에 모두 존재."""
    for lang in ("ko", "en"):
        pack = load_pack(lang, "core")
        overlay = pack.get("INTENSITY_OVERLAY", {})
        for key in ("SELF_SOURCED", "BALANCED_CORE", "ENVIRONMENT_TUNED"):
            assert key in overlay, f"{lang} missing overlay: {key}"
            assert overlay[key].get("voice"), f"{lang}/{key} voice empty"
            assert overlay[key].get("advice_addon"), f"{lang}/{key} advice_addon empty"
'''


def step_tests(force: bool = False) -> None:
    print("\n=== [3/4] 테스트 파일 생성 ===")
    path = TESTS / "test_core_pillar_content.py"
    if path.exists() and not force:
        print(f"  ⏭️  이미 존재 (건너뜀, --force로 덮어쓰기): {path.name}")
        return
    if path.exists():
        _backup(path)
    path.write_text(TEST_SOURCE, encoding="utf-8")
    print(f"  ✅ {path.name} 생성")


# ─────────────────────────────────────────────────────
# STEP 4: 나머지 58개 뼈대
# ─────────────────────────────────────────────────────
STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"


def _all_60_pillars() -> list[str]:
    return [f"{STEMS[i % 10]}{BRANCHES[i % 12]}" for i in range(60)]


def step_stubs(force: bool = False) -> None:
    print("\n=== [4/4] 나머지 일주 뼈대 생성 ===")
    for lang in ("ko", "en"):
        d = DATA / lang / "core_pillars"
        d.mkdir(parents=True, exist_ok=True)
        created = 0
        skipped = 0
        for pillar in _all_60_pillars():
            path = d / f"{pillar}.json"
            if path.exists() and not force:
                skipped += 1
                continue
            if path.exists():
                _backup(path)
            _write_json(path, {
                "pillar": pillar,
                "hero": "",
                "narrative": [],
                "shadows": [],
                "advice": [],
                "keywords": [],
            })
            created += 1
        print(f"  [{lang}] 생성 {created}개 / 건너뜀 {skipped}개 (총 60개)")


# ─────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────
STEPS = {
    "overlay": step_overlay,
    "pilot": step_pilot,
    "tests": step_tests,
    "stubs": step_stubs,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="60일주 + intensity 오버레이 레이어 적용")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="모든 단계 실행")
    g.add_argument("--step", choices=list(STEPS.keys()), help="특정 단계만 실행")
    ap.add_argument("--force", action="store_true", help="이미 존재해도 덮어쓰기")
    args = ap.parse_args()

    if args.all:
        for fn in STEPS.values():
            fn(force=args.force)
    else:
        STEPS[args.step](force=args.force)

    print("\n✅ 완료. 다음 명령으로 검증하세요:")
    print("   pytest tests/test_core_pillar_content.py -v")
    print("   pytest -q")
    return 0


if __name__ == "__main__":
    sys.exit(main())