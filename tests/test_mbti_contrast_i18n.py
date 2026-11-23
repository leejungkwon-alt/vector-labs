"""사주×MBTI 대조 — 프론트 i18n 키 가드 (재발 방지).

⚠️ 이 파일은 **회귀 방지**가 목적이다. 문구의 정답을 고정하지 않고,
   "빠지면 화면에 키 문자열이 그대로 노출되는" 경우를 막는다.

   1) 프론트 코드에서 t("...") 로 쓰는 키가 locales/*.json 에 실제로 있는지
   2) MbtiContrastCard 가 요구하는 mbtiContrast.* 키가 5개 언어에 모두 있는지
   3) 서버 팩(ja/zh_cn/es)이 en 복사 + TODO-i18n 표식을 유지하는지

⚠️ 서버는 MBTI 유형을 추정하지 않는다. 사용자가 입력한 값과 사주 결을
   대조해 outward|inward|balanced 중 하나만 낸다.
"""
import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
LOCALES_DIR = FRONTEND / "src" / "locales"
CARD_PATH = FRONTEND / "src" / "components" / "sections" / "MbtiContrastCard.tsx"
DATA_DIR = ROOT / "app" / "services" / "content" / "data"

LANGS = ["ko", "en", "ja", "zh_cn", "es"]
# 실제 문구를 직접 쓰는 언어. 나머지는 en 복사 + TODO-i18n.
AUTHORED_LANGS = {"ko", "en"}

# MbtiContrastCard 가 반드시 사용해야 하는 i18n 키(카드에서 하드코딩 검사).
REQUIRED_CARD_KEYS = [
    "mbtiContrast.kicker",
    "mbtiContrast.ctaTitle",
    "mbtiContrast.ctaBody",
    "mbtiContrast.ctaButton",
    "mbtiContrast.styleNote",
    "mbtiContrast.unlockDetail",
    "mbtiContrast.disclaimer",
    "mbtiContrast.hourUnknown",
]

# `t("a.b")`, t('a.b') 형태만 잡는다(변수 키는 검사 대상에서 제외).
_T_CALL = re.compile(r"\bt\(\s*[\"']([A-Za-z0-9_.\-]+)[\"']")
# 주석은 키 수집에서 제외한다.
_COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)


def _load_locale(lang: str) -> dict:
    with open(LOCALES_DIR / f"{lang}.json", "r", encoding="utf-8") as f:
        return json.load(f)


def _lookup(dict_: dict, dotted: str):
    cur = dict_
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _has_key(dict_: dict, dotted: str) -> bool:
    return isinstance(_lookup(dict_, dotted), str)


def _t_keys_in_source(path: pathlib.Path) -> list:
    source = _COMMENT.sub("", path.read_text(encoding="utf-8"))
    return sorted(set(_T_CALL.findall(source)))


def _frontend_sources():
    """앱 소스(.ts/.tsx) — 테스트/목/빌드 산출물은 제외."""
    skip_parts = {"node_modules", "dist", "__mocks__", "android", ".vercel"}
    for path in FRONTEND.rglob("*"):
        if path.suffix not in (".ts", ".tsx"):
            continue
        rel = path.relative_to(FRONTEND)
        if skip_parts & set(rel.parts):
            continue
        if path.name.endswith((".test.ts", ".test.tsx", ".bak", ".d.ts")):
            continue
        yield path


# ============================================================
# 1) 카드가 요구하는 키는 5개 언어에 반드시 있어야 한다
# ============================================================
@pytest.mark.parametrize("lang", LANGS)
def test_card_keys_exist_in_every_locale(lang):
    locale = _load_locale(lang)
    missing = [k for k in REQUIRED_CARD_KEYS if not _has_key(locale, k)]
    assert not missing, f"{lang}.json 누락 키: {missing}"


def test_card_source_actually_uses_required_keys():
    """카드에서 키 문자열이 바뀌면 REQUIRED_CARD_KEYS 목록도 함께 갱신하도록 잠근다."""
    used = set(_t_keys_in_source(CARD_PATH))
    missing = [k for k in REQUIRED_CARD_KEYS if k not in used]
    assert not missing, f"MbtiContrastCard 가 더 이상 쓰지 않는 키: {missing}"


def test_card_keys_are_non_empty_in_all_langs():
    for lang in LANGS:
        locale = _load_locale(lang)
        for key in REQUIRED_CARD_KEYS:
            value = _lookup(locale, key)
            assert isinstance(value, str) and value.strip(), f"{lang}: '{key}' 비어 있음"


# ============================================================
# 2) 프론트 코드 전역: t("...") 키가 ko.json 에 모두 있는지
# ============================================================
def test_all_literal_t_keys_exist_in_ko():
    ko = _load_locale("ko")
    missing = {}
    for path in _frontend_sources():
        bad = [k for k in _t_keys_in_source(path) if not _has_key(ko, k)]
        if bad:
            missing[str(path.relative_to(FRONTEND))] = bad
    assert not missing, f"ko.json 에 없는 t() 키: {missing}"


def test_locale_files_share_same_key_shape():
    """5개 언어의 키 구조가 같아야 폴백으로 인한 키 노출이 없다."""

    def flatten(d, prefix=""):
        out = set()
        for k, v in d.items():
            dotted = f"{prefix}{k}"
            if isinstance(v, dict):
                out |= flatten(v, f"{dotted}.")
            else:
                out.add(dotted)
        return out

    reference = flatten(_load_locale("ko"))
    for lang in LANGS:
        keys = flatten(_load_locale(lang))
        missing = sorted(reference - keys)
        extra = sorted(keys - reference)
        assert not missing, f"{lang}.json 에 빠진 키: {missing}"
        assert not extra, f"{lang}.json 에만 있는 키: {extra}"


# ============================================================
# 3) 서버 팩: 5개 언어 존재 + 미번역 팩은 en 복사 + TODO-i18n 표식
# ============================================================
@pytest.mark.parametrize("lang", LANGS)
def test_mbti_contrast_pack_exists_for_every_lang(lang):
    path = DATA_DIR / lang / "mbti_contrast.json"
    assert path.exists(), f"{lang} 팩 없음: {path}"
    with open(path, "r", encoding="utf-8") as f:
        pack = json.load(f)
    for section in ("AXIS_MODULES", "LINK", "SLOTS", "DAY_STEM_OVERLAY"):
        assert pack.get(section), f"{lang}: {section} 비어 있음"
    assert set(pack["AXIS_MODULES"]) == {"outward", "inward", "balanced"}
    assert set(pack["LINK"]) == {"match", "contrast", "balanced"}


@pytest.mark.parametrize("lang", [l for l in LANGS if l not in AUTHORED_LANGS])
def test_translated_packs_carry_todo_marker(lang):
    """미번역 팩은 en 복사본임을 표시해야 한다(번역 누락을 조용히 넘기지 않음)."""
    with open(DATA_DIR / lang / "mbti_contrast.json", "r", encoding="utf-8") as f:
        pack = json.load(f)
    with open(DATA_DIR / "en" / "mbti_contrast.json", "r", encoding="utf-8") as f:
        en = json.load(f)
    assert "TODO-i18n" in str(pack.get("_TODO_I18N", "")), f"{lang}: _TODO_I18N 표식 없음"
    assert pack["AXIS_MODULES"] == en["AXIS_MODULES"]
    assert pack["LINK"] == en["LINK"]
    assert pack["SLOTS"] == en["SLOTS"]


# ============================================================
# 4) 판정 문구 가드: '맞다/틀리다' 단정 금지(ko/en)
# ============================================================
@pytest.mark.parametrize("lang", sorted(AUTHORED_LANGS))
def test_pack_avoids_verdict_wording(lang):
    with open(DATA_DIR / lang / "mbti_contrast.json", "r", encoding="utf-8") as f:
        text = f.read()
    # DISCLAIMER 의 '맞고 틀린 답도 없다'는 허용하고, 단정 표현만 막는다.
    forbidden = ["틀렸습니다", "틀린 사람", "맞습니다", "you are wrong", "is correct and"]
    for phrase in forbidden:
        assert phrase not in text, f"{lang}: 판정 단정 표현 발견: {phrase}"


# ============================================================
# 5) 문구 개선 루브릭: 전문용어 금지 + 한 문장 25자 안팎(ko/en)
# ============================================================
# 전문용어 금지 목록(사용자 지시: 원국·결·기운·용신 등). 사람들이 쓰는 말로만.
JARGON_BANNED = {
    "ko": ["원국", "용신", "기운", "식상", "편관", "정관", "상관격", "격국", "신강", "신약", "층위", "명식", "천간", "지지"],
    "en": ["won-guk", "yongsin", "useful god", "chart energy", "layer beneath", "day master"],
}
# 한 문장 길이 상한(25자 안팎 + 호흡 여유).
MAX_KO_SENTENCE = 33
MAX_EN_WORDS = 22

# 카드에 크게 보이는 축 모듈·링크(헤드라인/본문). SLOTS 는 프리미엄 상세라 길이만 완화.
RUBRIC_SECTIONS = ("AXIS_MODULES", "LINK")


def _rubric_strings(pack):
    for section in RUBRIC_SECTIONS:
        for key, entry in pack[section].items():
            yield f"{section}.{key}.label", entry.get("label")
            yield f"{section}.{key}.headline", entry.get("headline")
            yield f"{section}.{key}.body", entry.get("body")


@pytest.mark.parametrize("lang", sorted(AUTHORED_LANGS))
def test_pack_has_no_jargon(lang):
    with open(DATA_DIR / lang / "mbti_contrast.json", "r", encoding="utf-8") as f:
        pack = json.load(f)
    allowed = {"결"}  # '결'은 브랜드(gyeol)이며 전문용어 금지 대상에서 제외
    found = []
    for name, value in _rubric_strings(pack):
        if not value:
            continue
        for term in JARGON_BANNED[lang]:
            if term in allowed:
                continue
            if term in value:
                found.append(f"{name}: '{term}'")
    assert not found, f"{lang} 전문용어 발견: {found}"


@pytest.mark.parametrize("lang", sorted(AUTHORED_LANGS))
def test_pack_sentences_stay_short(lang):
    with open(DATA_DIR / lang / "mbti_contrast.json", "r", encoding="utf-8") as f:
        pack = json.load(f)
    too_long = []
    for name, value in _rubric_strings(pack):
        if not value or "." not in value:
            continue
        for sentence in [s.strip() for s in value.split(".") if s.strip()]:
            if lang == "ko":
                # 글자 수 기준: 공백 포함 길이
                if len(sentence) > MAX_KO_SENTENCE:
                    too_long.append(f"{name} ({len(sentence)}자): {sentence}")
            else:
                words = len(sentence.split())
                if words > MAX_EN_WORDS:
                    too_long.append(f"{name} ({words}w): {sentence}")
    assert not too_long, f"{lang} 문장이 너무 김: {too_long}"


def test_contrast_link_keeps_both_sides_tone():
    """'사주는 ~라고 하지만 본인은 ~' 톤 유지: 어느 한쪽도 틀리다고 하지 않는다."""
    with open(DATA_DIR / "ko" / "mbti_contrast.json", "r", encoding="utf-8") as f:
        ko = json.load(f)
    with open(DATA_DIR / "en" / "mbti_contrast.json", "r", encoding="utf-8") as f:
        en = json.load(f)
    assert "하지만 본인은" in ko["LINK"]["contrast"]["body"]
    assert "but you may feel" in en["LINK"]["contrast"]["body"]
    for pack in (ko, en):
        assert "틀렸" not in pack["LINK"]["contrast"]["body"]
        assert "wrong" not in pack["LINK"]["contrast"]["body"].lower()

@pytest.mark.parametrize("lang", sorted(AUTHORED_LANGS))
def test_pack_avoids_verdict_wording(lang):
    with open(DATA_DIR / lang / "mbti_contrast.json", "r", encoding="utf-8") as f:
        text = f.read()
    # DISCLAIMER 의 '맞고 틀린 답도 없다'는 허용하고, 단정 표현만 막는다.
    forbidden = ["틀렸습니다", "틀린 사람", "맞습니다", "you are wrong", "is correct and"]
    for phrase in forbidden:
        assert phrase not in text, f"{lang}: 판정 단정 표현 발견: {phrase}"

