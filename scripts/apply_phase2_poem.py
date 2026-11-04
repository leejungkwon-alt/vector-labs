#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2: 시조(時調) 카드 기능 자동 적용 스크립트.

적용 내용:
  1. app/engine/elements.py       — 用神 × 월건 5관계 판정 함수 추가
  2. app/services/content_writer.py — poem 해석 생성 (_resolve_poem)
  3. app/services/entitlements.py — lucky_code.poem 게이팅
  4. data/poems.json              — 25편 시조 데이터 신규 생성

실행:
  cd C:\\Users\\lenovo\\Desktop\\SAJU
  python scripts\\apply_phase2_poem.py
"""
import json
import shutil
import sys

from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUP_SUFFIX = f".bak_phase2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _backup(path: Path):
    if path.exists():
        bak = path.with_name(path.name + BACKUP_SUFFIX)
        shutil.copy2(path, bak)
        print(f"  [backup] {bak.name}")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str):
    path.write_text(text, encoding="utf-8")


# ============================================================
# 1) elements.py — 5관계 판정
# ============================================================
ELEMENTS_ADDITION = '''

# ============================================================
# Phase 2: 시조 카드 — 用神 × 월건 5관계 판정
# ============================================================

# 월지 → 계절 오행 인덱스 (0=木, 1=火, 2=土, 3=金, 4=水)
BRANCH_SEASON_ELEMENT_IDX = {
    "寅": 0, "卯": 0,
    "巳": 1, "午": 1,
    "申": 3, "酉": 3,
    "亥": 4, "子": 4,
    "辰": 2, "戌": 2, "丑": 2, "未": 2,
}

POEM_RELATION_KR = {
    "same": "同",
    "generates_me": "生我",
    "i_generate": "我生",
    "i_control": "我剋",
    "controls_me": "剋我",
}


def month_branch_to_season_idx(branch_char: str):
    """월지 → 계절 오행 인덱스 (0~4). 미지원 글자면 None."""
    return BRANCH_SEASON_ELEMENT_IDX.get(branch_char)


def classify_yongsin_month_relation(yongsin_idx: int, month_idx: int) -> str:
    """用神 인덱스와 월건 인덱스의 5관계 판정.

    반환: same | generates_me | i_generate | i_control | controls_me
    """
    if yongsin_idx == month_idx:
        return "same"
    if element_generates(month_idx, yongsin_idx):
        return "generates_me"
    if element_generates(yongsin_idx, month_idx):
        return "i_generate"
    if element_controls(yongsin_idx, month_idx):
        return "i_control"
    if element_controls(month_idx, yongsin_idx):
        return "controls_me"
    return "same"
'''


def patch_elements():
    path = ROOT / "app" / "engine" / "elements.py"
    text = _read(path)
    if "classify_yongsin_month_relation" in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already patched")
        return
    _backup(path)
    _write(path, text + ELEMENTS_ADDITION)
    print(f"[OK]   {path.relative_to(ROOT)} (+5관계 판정)")


# ============================================================
# 2) content_writer.py — _resolve_poem
# ============================================================
CONTENT_WRITER_ADDITION = '''

# ============================================================
# Phase 2: 시조 카드 해석 (Poem Card)
# ============================================================
import json as _poem_json
from functools import lru_cache as _poem_lru
from pathlib import Path as _PoemPath

_POEM_JSON_PATH = _PoemPath(__file__).resolve().parents[2] / "data" / "poems.json"


@_poem_lru(maxsize=1)
def _load_poems() -> list:
    if not _POEM_JSON_PATH.exists():
        return []
    try:
        with open(_POEM_JSON_PATH, "r", encoding="utf-8") as f:
            return _poem_json.load(f).get("poems", [])
    except Exception:
        return []


def _resolve_poem(profile: dict, lang: str, power_sig: str, content_map: dict):
    """用神 × 월건 5관계 → poems.json 매칭."""
    from app.engine.elements import (
        ELEMENT_NAMES,
        month_branch_to_season_idx,
        classify_yongsin_month_relation,
        POEM_RELATION_KR,
    )

    yong_elem = content_map.get(power_sig, {}).get("element", "")
    if yong_elem not in ELEMENT_NAMES:
        return None
    yong_idx = ELEMENT_NAMES.index(yong_elem)

    month_pillar = (profile.get("pillars") or {}).get("month_pillar", "")
    if not isinstance(month_pillar, str) or len(month_pillar) != 2:
        return None
    month_idx = month_branch_to_season_idx(month_pillar[1])
    if month_idx is None:
        return None

    relation = classify_yongsin_month_relation(yong_idx, month_idx)

    poems = _load_poems()
    match = next(
        (p for p in poems
         if p.get("element_idx") == yong_idx and p.get("relation") == relation),
        None,
    )
    if not match:
        return None

    tr_all = match.get("translations", {})
    fallback_lang = "ko" if lang == "ko" else "en"
    tr = (tr_all.get(lang) or tr_all.get(fallback_lang)
          or tr_all.get("ko") or {})
    title_map = match.get("title", {})
    title = (title_map.get(lang) or title_map.get(fallback_lang)
             or title_map.get("ko") or match.get("id", ""))

    return {
        "id": match["id"],
        "element": match["element"],
        "element_idx": yong_idx,
        "relation": relation,
        "relation_kr": POEM_RELATION_KR[relation],
        "title": title,
        "sijo_ko": match.get("sijo_ko", ""),
        "romanization": match.get("romanization", ""),
        "interpretation": tr.get("interpretation", ""),
        "practice": tr.get("practice", ""),
        "calligraphy_image": match.get("calligraphy_image", ""),
        "wallpaper_image": match.get("wallpaper_image", ""),
        "keywords": match.get("keywords", []),
        "tier": match.get("tier", "premium"),
    }
'''


def patch_content_writer():
    path = ROOT / "app" / "services" / "content_writer.py"
    text = _read(path)
    if "_resolve_poem" in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already patched")
        return
    _backup(path)

    old_return = '        "watch_out": watch_out,\n    }'
    new_return = ('        "watch_out": watch_out,\n'
                  '        "poem": _resolve_poem(profile, lang, power_sig, content_map),\n'
                  '    }')
    if text.count(old_return) != 1:
        print(f"[ERR]  lucky_code return anchor not unique: {text.count(old_return)}")
        sys.exit(1)
    text = text.replace(old_return, new_return, 1)
    _write(path, text + CONTENT_WRITER_ADDITION)
    print(f"[OK]   {path.relative_to(ROOT)} (+_resolve_poem)")


# ============================================================
# 3) entitlements.py — poem_gate
# ============================================================
def patch_entitlements():
    path = ROOT / "app" / "services" / "entitlements.py"
    text = _read(path)
    if "poem_gate" in text:
        print(f"[SKIP] {path.relative_to(ROOT)} already patched")
        return
    _backup(path)

    old_keep = '    "lucky_code": {\n        "keep": {"id", "title", "hero"},'
    new_keep = '    "lucky_code": {\n        "keep": {"id", "title", "hero", "poem"},'
    if text.count(old_keep) != 1:
        print(f"[ERR]  lucky_code keep anchor not unique: {text.count(old_keep)}")
        sys.exit(1)
    text = text.replace(old_keep, new_keep, 1)

    old_pw = ('        "include_power_minimal": True,'
              '   # power에서 signature/element/keywords만 노출')
    new_pw = (old_pw + '\n'
              '        "poem_gate": {\n'
              '            "locked_fields": {"wallpaper_image", "collection"},\n'
              '        },')
    if text.count(old_pw) != 1:
        print(f"[ERR]  include_power_minimal anchor not unique: {text.count(old_pw)}")
        sys.exit(1)
    text = text.replace(old_pw, new_pw, 1)

    old_hint = '            "power.domains",'
    new_hint = ('            "power.domains",\n'
                '            "poem.wallpaper_image", "poem.collection",')
    if text.count(old_hint) < 1:
        print(f"[ERR]  power.domains anchor not found")
        sys.exit(1)
    text = text.replace(old_hint, new_hint, 1)

    old_tail = '\n    return teaser, locked'
    new_tail = ('''\n
    # 6) poem 게이팅 (free: wallpaper/collection 잠금)
    if "poem_gate" in rule and isinstance(teaser.get("poem"), dict):
        locked_poem = rule["poem_gate"]["locked_fields"]
        teaser["poem"] = {
            k: (None if k in locked_poem else v)
            for k, v in teaser["poem"].items()
        }
        teaser["poem"]["locked_fields"] = sorted(locked_poem)

    return teaser, locked''')
    if text.count(old_tail) != 1:
        print(f"[ERR]  _apply_teaser_rule tail anchor not unique: {text.count(old_tail)}")
        sys.exit(1)
    text = text.replace(old_tail, new_tail, 1)

    _write(path, text)
    print(f"[OK]   {path.relative_to(ROOT)} (+poem_gate)")


# ============================================================
# 4) poems.json — 25편
# ============================================================
_PINYIN = ["mok", "hwa", "to", "geum", "su"]


def _mk(idx, elem, rel, rel_kr, title_ko, title_en,
        sijo, rom, keywords,
        interp_ko, prac_ko, interp_en, prac_en):
    pid = f"{_PINYIN[idx]}_{rel}"
    return {
        "id": pid,
        "element_idx": idx,
        "element": elem,
        "relation": rel,
        "relation_kr": rel_kr,
        "title": {"ko": title_ko, "en": title_en},
        "sijo_ko": sijo,
        "romanization": rom,
        "translations": {
            "ko": {"interpretation": interp_ko, "practice": prac_ko},
            "en": {"interpretation": interp_en, "practice": prac_en},
        },
        "calligraphy_image": f"/assets/poems/{pid}_calligraphy.png",
        "wallpaper_image": f"/assets/poems/{pid}_wallpaper.png",
        "keywords": keywords,
        "tier": "premium",
    }


POEMS = [
    _mk(0, "木", "same", "同", "같은 결", "The Same Grain",
        "새순이 새순을 만나\n말없이 가지를 뻗고\n봄은 그 사이로 흐른다",
        "saesuni saesuneul manna / malleopsi gajireul ppeotgo / bomeun geu sairo heureunda",
        ["공명", "가지", "봄"],
        "당신의 木 기운은 월건의 木과 같은 결로 공명합니다. 같은 방향의 힘이 서로를 북돋웁니다.",
        "오늘 아무 말 없이 10분, 같은 방향으로 걷기.",
        "Your Wood resonates with the Wood of the month. Two forces in the same direction lift each other.",
        "Walk for 10 minutes today in one direction, without a word."),
    _mk(0, "木", "generates_me", "生我", "강에서 온 편지", "Letter from the River",
        "겨울 강이 얼음을 풀고\n뿌리 끝에 물을 보내니\n나는 그제야 잎이 된다",
        "gyeoul gangi eoreumeul pulgo / ppuri kkeute mureul bonaeni / naneun geujeya ipi doenda",
        ["물길", "뿌리", "잎"],
        "월건의 水가 당신의 木을 길러냅니다. 보이지 않는 도움을 받고 있는 시기입니다.",
        "최근 도움을 준 사람에게 짧은 감사 인사.",
        "The Water of the month nourishes your Wood. You are being quietly supported.",
        "Send a short thank-you to someone who helped you recently."),
    _mk(0, "木", "i_generate", "我生", "봄의 끝에서", "At the End of Spring",
        "새순이 강을 건네\n불꽃으로 피어나고\n나는 그 사이에 서 있다",
        "saesuni gangeul geonne / bulkkocheuro pieonago / naneun geu saie seo itda",
        ["건넘", "피어남", "불꽃"],
        "당신의 木이 월건의 火를 피워냅니다. 당신의 표현이 세상을 밝히는 시기입니다.",
        "오늘 누군가에게 당신의 생각을 글로 전하기.",
        "Your Wood kindles the Fire of the month. Your expression is what lights the world right now.",
        "Put one of your thoughts into words and send it to someone today."),
    _mk(0, "木", "i_control", "我剋", "뿌리의 일", "The Work of Roots",
        "나무가 흙을 붙잡아\n제 몸을 세우는 법\n흙은 그 무게를 견딘다",
        "namuga heulgeul butjaba / je momeul seuneun beop / heulgeun geu mugeoreul gyeondinda",
        ["세움", "붙잡음", "무게"],
        "당신의 木이 월건의 土를 붙잡습니다. 스스로 중심을 세우는 시기입니다.",
        "미뤄둔 결정 하나를 오늘 확정.",
        "Your Wood holds the Earth of the month. This is a season for standing your own ground.",
        "Finalize one decision you have been postponing."),
    _mk(0, "木", "controls_me", "剋我", "가지치기", "Pruning",
        "서리 내린 새벽에\n누가 내 가지를 치는가\n잘린 자리에서 봄이 온다",
        "seori naerin saebyeoge / nuga nae gajireul chineunga / jallin jarieseo bomi onda",
        ["가지치기", "서리", "잘림"],
        "월건의 金이 당신의 木을 다듬습니다. 잘림이 곧 성장입니다.",
        "오늘 거절해야 할 일 한 가지 정하기.",
        "The Metal of the month prunes your Wood. The cut is the growth.",
        "Choose one thing to say no to today."),
    _mk(1, "火", "same", "同", "같은 불꽃", "The Same Flame",
        "불꽃이 불꽃을 만나\n더 크게 타오르고\n밤이 그 빛을 삼킨다",
        "bulkkoci bulkkocheul manna / deo keuge taoreugo / bami geu biceul samkinda",
        ["타오름", "밤", "빛"],
        "당신의 火 기운이 월건의 火와 함께 타오릅니다. 과열을 조심하되 열정은 지키세요.",
        "오늘 한 번, 의도적으로 쉬어가기.",
        "Your Fire rises with the Fire of the month. Guard against overheating, but keep the flame.",
        "Pause on purpose, once today."),
    _mk(1, "火", "generates_me", "生我", "장작의 마음", "The Heart of Kindling",
        "나무가 제 몸을 내어\n불에게 길을 열어주니\n불은 나무를 기억한다",
        "namuga je momeul naeeo / burege gireul yeoreojuni / bureun namureul gieokhanda",
        ["장작", "내어줌", "기억"],
        "월건의 木이 당신의 火에 장작을 댑니다. 받는 기운이 큰 시기입니다.",
        "좋아하는 책 한 페이지 천천히 읽기.",
        "The Wood of the month feeds your Fire. You are receiving a great deal.",
        "Read one page of a favorite book, slowly."),
    _mk(1, "火", "i_generate", "我生", "재의 자리", "Where Ash Rests",
        "다 탄 자리에 앉아\n재가 흙이 되는 것을\n나는 오래 바라보았다",
        "da tan jarie anja / jaega heulgi doeneun geoseul / naneun orae baraboatda",
        ["재", "흙", "바라봄"],
        "당신의 火가 월건의 土에 재를 남깁니다. 결과물이 쌓이는 시기입니다.",
        "최근 시작한 일의 중간 점검.",
        "Your Fire leaves ash in the Earth of the month. Results are accumulating.",
        "Do a mid-point check on something you recently started."),
    _mk(1, "火", "i_control", "我剋", "불의 손", "Hand of Fire",
        "불이 쇠를 두드려\n제 모양을 만들어 내니\n쇠는 뜨거움을 기억한다",
        "buri soereul dudeuryeo / je moyangeul mandeureo naeni / soeneun tteugeoumeul gieokhanda",
        ["두드림", "모양", "뜨거움"],
        "당신의 火가 월건의 金을 두드립니다. 원하는 모양을 만드는 시기입니다.",
        "손으로 무언가 만들기 (요리/그림/글).",
        "Your Fire hammers the Metal of the month. This is a season to shape what you want.",
        "Make something with your hands today: cook, draw, or write."),
    _mk(1, "火", "controls_me", "剋我", "물의 노래", "Song of Water",
        "물이 내 불을 덮어도\n나는 재가 되지 않네\n김으로 하늘을 오른다",
        "muri nae bureul deopeodo / naneun jaega doeji anne / gimeuro haneureul oreunda",
        ["김", "덮임", "하늘"],
        "월건의 水가 당신의 火를 덮습니다. 눌림 속에서 김처럼 올라가세요.",
        "깊게 숨 쉬기, 5분 명상.",
        "The Water of the month covers your Fire. Rise like steam from beneath the weight.",
        "Breathe deeply. Five minutes of quiet."),
    _mk(2, "土", "same", "同", "같은 땅", "The Same Ground",
        "흙이 흙을 만나서\n조용히 산을 이루고\n나는 그 위에 앉는다",
        "heulgi heulgeul mannaseo / joyonghi saneul irugo / naneun geu wie anjneunda",
        ["산", "조용함", "앉음"],
        "당신의 土 기운이 월건의 土와 함께 산을 이룹니다. 조용히 쌓이는 시기입니다.",
        "오늘 아무것도 안 해도 괜찮은 시간 1시간.",
        "Your Earth forms a mountain with the Earth of the month. Quiet accumulation.",
        "Give yourself one hour today where doing nothing is enough."),
    _mk(2, "土", "generates_me", "生我", "재에서 온 흙", "Soil from Ash",
        "다 탄 불의 자리에서\n흙이 천천히 일어나\n나의 발을 받쳐 준다",
        "da tan burui jarieseo / heulgi cheoncheonhi ireona / naui bareul batchyeo junda",
        ["재", "일어남", "받침"],
        "월건의 火가 당신의 土를 따뜻하게 합니다. 받쳐주는 기운이 강한 시기입니다.",
        "따뜻한 차 한 잔 천천히.",
        "The Fire of the month warms your Earth. Strong support surrounds you.",
        "Sip a warm cup of tea, slowly."),
    _mk(2, "土", "i_generate", "我生", "흙속의 씨앗", "Seed in the Soil",
        "흙이 제 몸을 갈아\n단단한 쇠를 길러내니\n나는 그 소리를 듣는다",
        "heulgi je momeul gara / dandanhan soereul gireonaeni / naneun geu sorireul deunneunda",
        ["씨앗", "단단함", "소리"],
        "당신의 土가 월건의 金을 길러냅니다. 단단한 결과가 나오는 시기입니다.",
        "오늘 결정한 일 하나를 끝까지 완수.",
        "Your Earth raises the Metal of the month. Solid results take shape.",
        "Finish one thing you decided to do today."),
    _mk(2, "土", "i_control", "我剋", "둑의 일", "The Work of the Bank",
        "흙이 물길을 붙잡아\n논배미를 만드니\n물은 제 길을 찾아간다",
        "heulgi mulgireul butjaba / nonbae mireul mandeuni / mureun je gireul chajaganda",
        ["둑", "물길", "논"],
        "당신의 土가 월건의 水에 둑이 됩니다. 흐름을 정돈하는 시기입니다.",
        "정리 안 된 공간 한 곳 정리.",
        "Your Earth banks the Water of the month. This is a season for channeling the flow.",
        "Tidy one cluttered corner of your space."),
    _mk(2, "土", "controls_me", "剋我", "다져지는 땅", "Tamping the Earth",
        "나무 뿌리 뻗어와\n단단한 흙을 가르고\n흙은 다시 봄을 품는다",
        "namu ppuri ppeodeowa / dandanhan heulgeul gareugo / heulgeun dasi bomeul pumneunda",
        ["단단함", "경계", "성장"],
        "월건의 木이 당신의 土를 가릅니다. 다져지는 시기입니다.",
        "오늘 예상치 못한 요청에 한 번 거절.",
        "The Wood of the month breaks through your Earth. You are being compacted into strength.",
        "Say no once today to an unexpected request."),
    _mk(3, "金", "same", "同", "같은 결", "The Same Grain",
        "쇠가 쇠를 만나서\n서로를 벼려내고\n빛이 그 사이로 흐른다",
        "soega soereul mannaseo / seororeul byeoryeo naego / bici geu sairo heureunda",
        ["벼림", "빛", "결"],
        "당신의 金 기운이 월건의 金과 서로를 벼립니다. 예리해지는 시기입니다.",
        "오늘 날카로워지지 않도록 한 번 참기.",
        "Your Metal sharpens the Metal of the month. This is a season of edge.",
        "Hold back once today from sharpening a conversation."),
    _mk(3, "金", "generates_me", "生我", "흙의 선물", "Gift of Earth",
        "오랜 흙이 나를 품어\n단단한 몸을 주시니\n나는 빛을 받기 시작한다",
        "orae heulgi nareul pumeo / dandanhan momeul jusini / naneun biceul batgi sijakhanda",
        ["품음", "단단함", "빛"],
        "월건의 土가 당신의 金을 품습니다. 안정된 기반 위에 서 있습니다.",
        "오래 미뤄둔 정리 하나 끝내기.",
        "The Earth of the month cradles your Metal. You stand on stable ground.",
        "Finish one task you have been putting off."),
    _mk(3, "金", "i_generate", "我生", "서릿길", "Frosty Path",
        "서리 끝에 맺힌 물이\n강으로 흘러가니\n나는 그 길을 지킨다",
        "seori kkeute maechin muri / gangeuro heulleogani / naneun geu gireul jikinda",
        ["서리", "강", "길"],
        "당신의 金이 월건의 水를 만듭니다. 흐름을 트는 시기입니다.",
        "아이디어 하나를 오늘 글로 남기기.",
        "Your Metal gives rise to the Water of the month. You open new flows.",
        "Write down one idea today."),
    _mk(3, "金", "i_control", "我剋", "낫의 노래", "Song of the Sickle",
        "낫이 풀을 베어 내어\n밭을 정돈하니\n풀은 다시 봄을 기다린다",
        "naci pureul beeo naeeo / bateul jeongdonhani / pureun dasi bomeul gidarinda",
        ["낫", "정돈", "봄"],
        "당신의 金이 월건의 木을 벱니다. 정돈하는 시기입니다.",
        "오늘 버려야 할 것 세 가지 정하기.",
        "Your Metal cuts the Wood of the month. This is a season for clearing.",
        "Name three things you will let go of today."),
    _mk(3, "金", "controls_me", "剋我", "쇠의 기억", "Memory of Iron",
        "불이 나를 두드려\n제 모양을 만들고\n나는 뜨거움을 기억한다",
        "buri nareul dudeuryeo / je moyangeul mandeulgo / naneun tteugeoumeul gieokhanda",
        ["두드림", "모양", "기억"],
        "월건의 火가 당신의 金을 두드립니다. 단련되는 시기입니다.",
        "힘든 일 하나를 오늘 아침에 먼저 처리.",
        "The Fire of the month hammers your Metal. You are being tempered.",
        "Do the hard thing first, this morning."),
    _mk(4, "水", "same", "同", "같은 물결", "The Same Wave",
        "물이 물을 만나서\n큰 강을 이루고\n나는 그 소리를 듣는다",
        "muri mureul mannaseo / keun gangeul irugo / naneun geu sorireul deunneunda",
        ["강", "소리", "물결"],
        "당신의 水 기운이 월건의 水와 강을 이룹니다. 깊어지는 시기입니다.",
        "오늘 혼자 조용히 걷는 시간 20분.",
        "Your Water forms a river with the Water of the month. This is a season of depth.",
        "Take a quiet 20-minute walk alone today."),
    _mk(4, "水", "generates_me", "生我", "서리에서 온 물", "Water from Frost",
        "서리 끝에 맺힌 물이\n내 몸으로 흘러와\n나는 다시 흐르기 시작한다",
        "seori kkeute maechin muri / nae momeuro heulleowa / naneun dasi heureugi sijakhanda",
        ["서리", "흐름", "시작"],
        "월건의 金이 당신의 水를 만듭니다. 새로운 흐름이 시작됩니다.",
        "오늘 처음 해보는 작은 시도 하나.",
        "The Metal of the month gives rise to your Water. A new flow is beginning.",
        "Try one small new thing today."),
    _mk(4, "水", "i_generate", "我生", "봄을 부르는 물", "Water Calling Spring",
        "물이 땅속을 흐르며\n뿌리를 두드리니\n새순이 눈을 뜬다",
        "muri ttangsogeul heureumyeo / ppurireul dudeurini / saesuni nuneul tteunda",
        ["땅속", "뿌리", "새순"],
        "당신의 水가 월건의 木을 기릅니다. 새싹을 키우는 시기입니다.",
        "오래 키워온 아이디어 하나를 한 걸음 진행.",
        "Your Water nourishes the Wood of the month. This is a season for sprouting.",
        "Move one long-cherished idea forward, one step."),
    _mk(4, "水", "i_control", "我剋", "물의 손", "Hand of Water",
        "물이 불을 덮으며\n재를 적시니\n불은 김으로 하늘을 오른다",
        "muri bureul deopeumyeo / jaereul jeoksini / bureun gimeuro haneureul oreunda",
        ["덮임", "김", "하늘"],
        "당신의 水가 월건의 火를 덮습니다. 열기를 식히는 시기입니다.",
        "오늘 뜨거운 논쟁에서 한 발 물러나기.",
        "Your Water covers the Fire of the month. This is a season for cooling.",
        "Step back once today from a heated argument."),
    _mk(4, "水", "controls_me", "剋我", "둑 안의 물", "Water Within the Bank",
        "흙이 나를 감싸안아\n제 길을 만들고\n나는 그 안에서 깊어진다",
        "heulgi nareul gamssaana / je gireul mandeulgo / naneun geu aneseo gipeojinda",
        ["둑", "감쌈", "깊이"],
        "월건의 土가 당신의 水를 가둡니다. 둑 안에서 깊어지는 시기입니다.",
        "오늘 답을 미루고 질문만 세 가지 적기.",
        "The Earth of the month banks your Water. You deepen within the bounds.",
        "Postpone the answer. Write three questions instead."),
]


def write_poems_json():
    path = ROOT / "data" / "poems.json"
    if path.exists():
        print(f"[SKIP] {path.relative_to(ROOT)} already exists "
              f"({path.stat().st_size} bytes)")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "poems": POEMS,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[OK]   {path.relative_to(ROOT)} ({len(POEMS)}편)")


# ============================================================
# 5) 검증
# ============================================================
def verify():
    print("\n=== 검증 ===")
    try:
        from app.engine.elements import (
            classify_yongsin_month_relation,
            BRANCH_SEASON_ELEMENT_IDX,
            ELEMENT_NAMES,
        )
    except Exception as e:
        print(f"[FAIL] import elements: {e}")
        return False

    cases = [
        (0, 0, "same"),
        (0, 4, "generates_me"),
        (0, 1, "i_generate"),
        (0, 2, "i_control"),
        (0, 3, "controls_me"),
        (4, 0, "i_generate"),
        (1, 4, "controls_me"),
    ]
    ok = True
    for y, m, expected in cases:
        got = classify_yongsin_month_relation(y, m)
        status = "PASS" if got == expected else "FAIL"
        if got != expected:
            ok = False
        print(f"  [{status}] 用神={ELEMENT_NAMES[y]} 월건={ELEMENT_NAMES[m]} "
              f"→ {got} (기대 {expected})")

    for branch, expected_idx in [("寅", 0), ("午", 1), ("辰", 2), ("酉", 3), ("子", 4)]:
        got = BRANCH_SEASON_ELEMENT_IDX.get(branch)
        if got != expected_idx:
            print(f"  [FAIL] {branch} → {got} (기대 {expected_idx})")
            ok = False

    try:
        from app.services.content_writer import _load_poems
        poems = _load_poems()
        print(f"  [INFO] poems.json 로드: {len(poems)}편")
        if len(poems) < 25:
            print(f"  [WARN] 25편 미만")
    except Exception as e:
        print(f"  [FAIL] _load_poems: {e}")
        ok = False

    return ok


# ============================================================
# main
# ============================================================
def main():
    print("=" * 60)
    print("Phase 2: 시조(時調) 카드 기능 적용")
    print("=" * 60)
    print(f"ROOT = {ROOT}\n")

    patch_elements()
    patch_content_writer()
    patch_entitlements()
    write_poems_json()

    ok = verify()

    print("\n" + "=" * 60)
    if ok:
        print("[SUCCESS] 모든 패치 적용 완료")
        print("=" * 60)
        print("""
다음 단계:
  1. 로컬 테스트:  uvicorn app.main:app --reload
  2. curl 확인:
       curl -X POST http://localhost:8000/api/v1/saju/report ^
         -H "Content-Type: application/json" ^
         -d "{\\"birth_date\\":\\"1990-05-15\\",\\"birth_time\\":\\"14:30:00\\",\\"timezone_str\\":\\"Asia/Seoul\\",\\"lang\\":\\"ko\\"}"
       → sections.lucky_code.poem 확인
  3. Cloud Run 재배포
""")
    else:
        print("[FAIL] 검증 실패 — 위 로그 확인")
        sys.exit(1)


if __name__ == "__main__":
    main()